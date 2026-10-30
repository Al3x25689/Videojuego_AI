"""Memoria Pokémon 4.0: presentación adaptable sobre la lógica de turnos original."""

import random
import math
from time import monotonic
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

ASSETS = Path(__file__).resolve().parent / "assets"
POKEMON = (
    'gardevoir', 'gengar', 'pikachu', 'lucario',
    'charizard', 'dragonite', 'eevee', 'umbreon',
    'absol', 'riolu', 'bulbasaur', 'squirtle',
    'mew', 'espeon', 'tyranitar', 'metagross',
)
NIVELES = {"Principiante": (4, 4), "Intermedio": (8, 4), "Avanzado": (16, 8)}
LIMITES = {"Principiante": None, "Intermedio": 240, "Avanzado": 180}
AYUDAS = {"Principiante": 3, "Intermedio": 2, "Avanzado": 1}
VERDE, ORO, CREMA = "#173c38", "#f6d76b", "#f5edce"


class JuegoMemoria:
    def __init__(self, ventana, reloj=monotonic):
        self.ventana = ventana
        ventana.title("Memoria Pokémon · Versión 4.0")
        ventana.geometry("1000x800")
        ventana.minsize(360, 320)
        ventana.configure(bg=VERDE)
        ventana.resizable(True, True)
        self.pendiente = None
        self.ayuda_pendiente = None
        self.ayuda_activa = False
        self.ayudas_restantes = 0
        self.ajuste_pendiente = None
        self.reloj = reloj
        self.temporizador_pendiente = None
        self.fin_tiempo = None
        self.segundos_restantes = None
        self.partida_id = 0
        self.activa = False
        self.resultado = None
        self.panel_resultado = None
        self.nivel = None
        self.cartas, self.seleccionadas = [], []
        self.encontradas = set()
        self.bloqueado = False
        self.botones, self.casillas = [], []
        self.imagenes = self.cargar_imagenes()
        self.cache_escalas = {}
        self.escala = None
        self.fondo_escala = None
        self.estado = tk.StringVar()
        self.texto_tiempo = tk.StringVar()
        self.texto_ayuda = tk.StringVar()
        self.texto_pantalla = tk.StringVar(value="PANTALLA COMPLETA")
        self.crear_interfaz()
        ventana.bind("<Configure>", self.programar_ajuste)
        ventana.bind("<Escape>", self.salir_pantalla_completa)
        ventana.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.mostrar_menu()

    def cargar_imagenes(self):
        """Comprueba los recursos locales sin sustituir archivos faltantes."""
        nombres = ("fondo", "reverso") + POKEMON
        faltantes = [str(ASSETS / f"{nombre}.png") for nombre in nombres
                     if not (ASSETS / f"{nombre}.png").is_file()]
        if faltantes:
            raise FileNotFoundError("Faltan recursos gráficos:\n" + "\n".join(faltantes))
        return {nombre: tk.PhotoImage(master=self.ventana, file=str(ASSETS / f"{nombre}.png"))
                for nombre in nombres}

    def boton(self, padre, texto, comando):
        """Mantiene los botones nuevos dentro de la paleta original."""
        return tk.Button(padre, text=texto, command=comando, bg="#ffe27a", fg=VERDE,
                         activebackground="#fff0ae", font=("Courier New", 11, "bold"),
                         padx=10, pady=7, relief="raised", bd=3, cursor="hand2")

    def crear_interfaz(self):
        """Separa cabecera, área desplazable y controles siempre accesibles."""
        self.fondo = tk.Canvas(self.ventana, highlightthickness=0, bg=VERDE)
        self.fondo.place(x=0, y=0, relwidth=1, relheight=1)
        self.fondo_item = self.fondo.create_image(0, 0, anchor="nw", image=self.imagenes["fondo"])
        self.ventana.columnconfigure(0, weight=1)
        self.ventana.rowconfigure(1, weight=1)
        self.cabecera = tk.Frame(self.ventana, bg=VERDE, highlightbackground=ORO,
                                highlightthickness=3)
        self.cabecera.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 6))
        self.titulo = tk.Label(self.cabecera, text="MEMORIA POKÉMON", bg=VERDE,
                               fg="#ffe27a", font=("Courier New", 26, "bold"))
        self.titulo.pack(pady=(8, 3))
        self.contador = tk.Label(self.cabecera, textvariable=self.estado, bg=VERDE, fg="white",
                                 font=("Courier New", 11, "bold"))
        self.contador.pack(pady=(0, 6))
        self.temporizador_label = tk.Label(self.cabecera, textvariable=self.texto_tiempo,
                                           bg=VERDE, fg=CREMA,
                                           font=("Courier New", 12, "bold"))
        self.area = tk.Frame(self.ventana, bg=VERDE, highlightbackground=ORO,
                            highlightthickness=3)
        self.area.grid(row=1, column=0, sticky="nsew", padx=16, pady=6)
        self.area.rowconfigure(0, weight=1)
        self.area.columnconfigure(0, weight=1)
        self.lienzo = tk.Canvas(self.area, bg=VERDE, highlightthickness=0)
        self.lienzo.grid(row=0, column=0, sticky="nsew")
        self.barra_y = tk.Scrollbar(self.area, orient="vertical", command=self.lienzo.yview)
        self.barra_y.grid(row=0, column=1, sticky="ns")
        self.barra_x = tk.Scrollbar(self.area, orient="horizontal", command=self.lienzo.xview)
        self.barra_x.grid(row=1, column=0, sticky="ew")
        self.lienzo.configure(xscrollcommand=self.barra_x.set, yscrollcommand=self.barra_y.set)
        self.tablero = tk.Frame(self.lienzo, bg=VERDE)
        self.tablero_item = self.lienzo.create_window(0, 0, anchor="nw", window=self.tablero)
        self.lienzo.bind("<Configure>", self.programar_ajuste)
        self.lienzo.bind("<MouseWheel>", self.desplazar)
        self.controles = tk.Frame(self.ventana, bg=VERDE, highlightbackground=ORO,
                                 highlightthickness=2)
        self.controles.grid(row=2, column=0, sticky="ew", padx=16, pady=(6, 12))
        self.reiniciar = self.boton(self.controles, "NUEVA PARTIDA", self.nueva_partida)
        self.menu_boton = self.boton(self.controles, "VOLVER AL MENÚ", self.mostrar_menu)
        self.pantalla_boton = self.boton(self.controles, "", self.alternar_pantalla_completa)
        self.pantalla_boton.configure(textvariable=self.texto_pantalla)
        # Icono de ojo en píxeles: no depende de fuentes emoji ni de recursos nuevos.
        self.icono_ojo = tk.PhotoImage(master=self.ventana, width=20, height=14)
        patron = ("      ######      ", "   ###      ###   ", " ##    ####    ## ",
                  "#     ######     #", " ##    ####    ## ", "   ###      ###   ",
                  "      ######      ")
        for y, fila in enumerate(patron, start=3):
            for x, pixel in enumerate(fila, start=1):
                if pixel == "#":
                    self.icono_ojo.put(VERDE, (x, y))
        self.ayuda_boton = self.boton(self.controles, "", self.usar_ayuda)
        self.ayuda_boton.configure(textvariable=self.texto_ayuda, image=self.icono_ojo,
                                    compound="left", disabledforeground="#68756a")
        self.organizar_controles()

    def cancelar_turno(self):
        """Invalida la partida y cancela cartas, reloj y ajustes pendientes."""
        self.partida_id += 1
        self.activa = False
        for atributo in ("pendiente", "temporizador_pendiente", "ayuda_pendiente", "ajuste_pendiente"):
            evento = getattr(self, atributo)
            if evento is not None:
                self.ventana.after_cancel(evento)
                setattr(self, atributo, None)
        self.seleccionadas = []
        self.bloqueado = False
        self.ayuda_activa = False
        self.actualizar_ayuda()

    def limpiar_tablero(self):
        """Destruye casillas anteriores y restablece el desplazamiento."""
        for hijo in self.tablero.winfo_children():
            hijo.destroy()
        self.botones, self.casillas = [], []
        self.panel_resultado = None
        self.lienzo.xview_moveto(0)
        self.lienzo.yview_moveto(0)

    def mostrar_menu(self):
        """Permite elegir otra dificultad sin conservar eventos anteriores."""
        self.cancelar_turno()
        self.limpiar_tablero()
        self.nivel = None
        self.ayudas_restantes = 0
        self.resultado = None
        self.fin_tiempo = None
        self.segundos_restantes = None
        self.texto_tiempo.set("")
        self.temporizador_label.pack_forget()
        self.cartas = []
        self.encontradas = set()
        self.estado.set("Selecciona una dificultad")
        for nombre, (pares, _) in NIVELES.items():
            opcion = self.boton(self.tablero, nombre.upper(), lambda n=nombre: self.iniciar_nivel(n))
            opcion.pack(fill="x", padx=24, pady=(14, 4))
            limite = LIMITES[nombre]
            detalle = "sin límite" if limite is None else f"{limite // 60} minutos"
            tk.Label(self.tablero, text=f"{pares} parejas · {detalle}", bg=VERDE,
                     fg=CREMA, font=("Courier New", 11)).pack(pady=(0, 5))
        self.organizar_controles()
        self.programar_ajuste()

    def iniciar_nivel(self, nombre):
        """Selecciona los Pokémon y la distribución correspondientes al nivel."""
        self.nivel = nombre
        self.total_pares, self.columnas = NIVELES[nombre]
        self.nueva_partida()

    def nueva_partida(self):
        """Conserva la dificultad y mezcla nuevamente los pares originales."""
        if self.nivel is None:
            return
        self.cancelar_turno()
        self.limpiar_tablero()
        self.resultado = None
        self.ayudas_restantes = AYUDAS[self.nivel]
        self.activa = True
        self.temporizador_label.pack(pady=(0, 6))
        self.cartas = list(POKEMON[:self.total_pares]) * 2
        random.shuffle(self.cartas)
        self.encontradas = set()
        self.estado.set(f"{self.nivel} · Pares encontrados: 0 de {self.total_pares}")
        self.escala = None
        for indice in range(len(self.cartas)):
            casilla = tk.Frame(self.tablero, bg=VERDE)
            casilla.grid(row=indice // self.columnas, column=indice % self.columnas)
            casilla.grid_propagate(False)
            boton = tk.Button(casilla, relief="flat", bd=0, highlightthickness=0,
                              cursor="hand2", bg="#244b70", activebackground=ORO,
                              command=lambda i=indice: self.descubrir(i))
            boton.grid(padx=6, pady=6)
            boton.bind("<MouseWheel>", self.desplazar)
            self.botones.append(boton)
            self.casillas.append(casilla)
        self.organizar_controles()
        self.ajustar_presentacion()
        self.iniciar_temporizador()

    def organizar_controles(self):
        """Acomoda la ayuda sin cortar los controles en ventanas pequeñas."""
        botones = (self.reiniciar, self.menu_boton, self.ayuda_boton, self.pantalla_boton)
        ancho = self.ventana.winfo_width()
        for boton in botones:
            boton.grid_forget()
            boton.configure(font=("Courier New", 9 if ancho < 760 else 11, "bold"),
                            padx=5 if ancho < 760 else 10, pady=4 if ancho < 760 else 7)
        for col in range(4):
            self.controles.columnconfigure(col, weight=0)
        if self.nivel is None or self.resultado is not None:
            self.pantalla_boton.grid(row=0, column=0, padx=4, pady=4)
            self.controles.columnconfigure(0, weight=1)
        elif ancho < 600:
            self.reiniciar.grid(row=0, column=0, padx=3, pady=3, sticky="ew")
            self.menu_boton.grid(row=0, column=1, padx=3, pady=3, sticky="ew")
            self.ayuda_boton.grid(row=1, column=0, columnspan=2, padx=3, pady=3, sticky="ew")
            self.pantalla_boton.grid(row=2, column=0, columnspan=2, padx=3, pady=3, sticky="ew")
            for col in (0, 1):
                self.controles.columnconfigure(col, weight=1)
        elif ancho < 1100:
            for i, boton in enumerate(botones):
                boton.grid(row=i // 2, column=i % 2, padx=3, pady=3, sticky="ew")
            for col in (0, 1):
                self.controles.columnconfigure(col, weight=1)
        else:
            for col, boton in enumerate(botones):
                boton.grid(row=0, column=col, padx=4, pady=3, sticky="ew")
                self.controles.columnconfigure(col, weight=1)
        self.actualizar_ayuda()

    def actualizar_ayuda(self):
        """Sincroniza el contador y la disponibilidad con el estado del turno."""
        disponible = (self.activa and self.resultado is None and self.ayudas_restantes > 0
                       and not self.ayuda_activa and not self.seleccionadas
                       and not self.bloqueado and self.pendiente is None)
        self.texto_ayuda.set(f"Vistazo rápido ({self.ayudas_restantes})")
        self.ayuda_boton.configure(state=tk.NORMAL if disponible else tk.DISABLED)

    def usar_ayuda(self):
        """Revela las cartas pendientes durante dos segundos sin pausar el reloj."""
        if not self.activa or self.tiempo_agotado():
            return
        if (self.ayudas_restantes <= 0 or self.ayuda_activa or self.seleccionadas
                or self.bloqueado or self.pendiente is not None):
            return
        self.ayudas_restantes -= 1
        self.ayuda_activa = True
        self.bloqueado = True
        for indice in range(len(self.cartas)):
            if indice not in self.encontradas:
                self.actualizar_carta(indice)
        self.actualizar_ayuda()
        partida = self.partida_id
        self.ayuda_pendiente = self.ventana.after(2000, lambda: self.finalizar_ayuda(partida))

    def finalizar_ayuda(self, partida):
        """Oculta el vistazo solo si todavía pertenece a la misma partida."""
        if partida != self.partida_id or not self.activa or not self.ayuda_activa:
            return
        if self.tiempo_agotado():
            return
        self.ayuda_pendiente = None
        self.ayuda_activa = False
        self.bloqueado = False
        for indice in range(len(self.cartas)):
            if indice not in self.encontradas:
                self.actualizar_carta(indice)
        self.actualizar_ayuda()

    def programar_ajuste(self, evento=None):
        """Agrupa eventos de tamaño; nunca altera el estado de las cartas."""
        if evento is not None and evento.widget not in (self.ventana, self.lienzo):
            return
        if self.ajuste_pendiente is not None:
            self.ventana.after_cancel(self.ajuste_pendiente)
        self.ajuste_pendiente = self.ventana.after(70, self.ajustar_presentacion)

    def ajustar_presentacion(self):
        """Escala con vecino más cercano y ofrece desplazamiento si no cabe."""
        if self.ajuste_pendiente is not None:
            self.ventana.after_cancel(self.ajuste_pendiente)
            self.ajuste_pendiente = None
        self.organizar_controles()
        w, h = max(1, self.lienzo.winfo_width()), max(1, self.lienzo.winfo_height())
        self.contador.configure(wraplength=max(250, self.ventana.winfo_width()-60))
        self.titulo.configure(font=("Courier New", 16 if self.ventana.winfo_width() < 650 else 26, "bold"))
        if self.nivel is not None and self.resultado is None:
            filas = len(self.cartas) // self.columnas
            opciones = ((1, 2), (3, 4), (1, 1), (5, 4), (3, 2))
            escala = opciones[0]
            for n, d in opciones:
                if (148*n//d+12)*self.columnas <= w and (172*n//d+12)*filas <= h:
                    escala = n, d
            if escala != self.escala:
                if escala not in self.cache_escalas:
                    n, d = escala
                    self.cache_escalas[escala] = {
                        nombre: imagen.zoom(n).subsample(d)
                        for nombre, imagen in self.imagenes.items() if nombre != "fondo"
                    }
                self.escala = escala
                n, d = escala
                for casilla, boton in zip(self.casillas, self.botones):
                    casilla.configure(width=148*n//d+12, height=172*n//d+12)
                    boton.configure(width=148*n//d, height=172*n//d)
                for i in range(len(self.botones)):
                    self.actualizar_carta(i)
        self.tablero.update_idletasks()
        tw, th = self.tablero.winfo_reqwidth(), self.tablero.winfo_reqheight()
        self.lienzo.coords(self.tablero_item, max(0, (w-tw)//2), max(0, (h-th)//2))
        self.lienzo.configure(scrollregion=(0, 0, max(w, tw), max(h, th)))
        # La misma imagen de fondo cubre la ventana conservando su proporción.
        vw, vh = max(1, self.ventana.winfo_width()), max(1, self.ventana.winfo_height())
        factor = max(4, (vw*4+919)//920, (vh*4+739)//740)
        if factor != self.fondo_escala:
            self.fondo_visible = self.imagenes["fondo"].subsample(4).zoom(factor)
            self.fondo.itemconfigure(self.fondo_item, image=self.fondo_visible)
            self.fondo_escala = factor
        self.fondo.coords(self.fondo_item, (vw-self.fondo_visible.width())//2,
                          (vh-self.fondo_visible.height())//2)

    def actualizar_carta(self, indice):
        """El bloqueo lógico de clics evita deshabilitar y puntear la imagen."""
        abierta = self.ayuda_activa or indice in self.seleccionadas or indice in self.encontradas
        nombre = self.cartas[indice] if abierta else "reverso"
        imagen = self.cache_escalas[self.escala][nombre]
        self.botones[indice].configure(image=imagen,
                                       bg=CREMA if abierta else "#244b70",
                                       state=tk.NORMAL)

    def desplazar(self, evento):
        """La rueda desplaza el tablero; Mayús permite desplazamiento horizontal."""
        mover = self.lienzo.xview_scroll if evento.state & 1 else self.lienzo.yview_scroll
        mover(-1 if evento.delta > 0 else 1, "units")
        return "break"

    def alternar_pantalla_completa(self):
        """Alterna la pantalla sin reiniciar ni descubrir cartas."""
        activa = not bool(self.ventana.attributes("-fullscreen"))
        self.ventana.attributes("-fullscreen", activa)
        self.texto_pantalla.set("SALIR DE PANTALLA COMPLETA" if activa else "PANTALLA COMPLETA")
        self.programar_ajuste()

    def salir_pantalla_completa(self, evento=None):
        """ESC restaura la ventana y conserva la partida actual."""
        self.ventana.attributes("-fullscreen", False)
        self.texto_pantalla.set("PANTALLA COMPLETA")
        self.programar_ajuste()

    def iniciar_temporizador(self):
        """Usa una fecha límite monotónica para evitar deriva entre callbacks."""
        limite = LIMITES[self.nivel]
        self.fin_tiempo = None if limite is None else self.reloj() + limite
        self.segundos_restantes = limite
        self.temporizador_label.configure(fg=CREMA)
        self.actualizar_temporizador(self.partida_id)

    def actualizar_temporizador(self, partida):
        """Actualiza MM:SS y descarta callbacks de partidas anteriores."""
        if partida != self.partida_id or not self.activa:
            return
        if self.temporizador_pendiente is not None:
            self.ventana.after_cancel(self.temporizador_pendiente)
            self.temporizador_pendiente = None
        if self.fin_tiempo is None:
            self.texto_tiempo.set("Sin límite de tiempo")
            return
        self.segundos_restantes = max(0, math.ceil(self.fin_tiempo - self.reloj()))
        minutos, segundos = divmod(self.segundos_restantes, 60)
        self.texto_tiempo.set(f"Tiempo restante: {minutos:02d}:{segundos:02d}")
        self.temporizador_label.configure(fg="#ff7770" if self.segundos_restantes <= 15 else CREMA)
        if self.segundos_restantes == 0:
            self.terminar_partida("derrota")
        else:
            self.temporizador_pendiente = self.ventana.after(
                100, lambda: self.actualizar_temporizador(partida))

    def tiempo_agotado(self):
        """Comprueba el límite también al hacer clic y al resolver una pareja."""
        if self.activa and self.fin_tiempo is not None and self.reloj() >= self.fin_tiempo:
            self.terminar_partida("derrota")
            return True
        return False

    def programar_turno(self, demora, accion):
        """Protege los eventos de cartas mediante el identificador de partida."""
        partida = self.partida_id
        def resolver():
            if partida == self.partida_id and self.activa:
                self.pendiente = None
                accion()
        self.pendiente = self.ventana.after(demora, resolver)

    def mostrar_victoria(self):
        """Finaliza la partida con el mismo panel integrado que la derrota."""
        self.terminar_partida("victoria")

    def terminar_partida(self, resultado):
        """Detiene los eventos y reemplaza el tablero por el resultado local."""
        if not self.activa:
            return
        if self.fin_tiempo is not None:
            self.segundos_restantes = max(0, math.ceil(self.fin_tiempo - self.reloj()))
            if self.segundos_restantes == 0:
                resultado = "derrota"
            minutos, segundos = divmod(self.segundos_restantes, 60)
            self.texto_tiempo.set(f"Tiempo restante: {minutos:02d}:{segundos:02d}")
            self.temporizador_label.configure(fg="#ff7770" if self.segundos_restantes <= 15 else CREMA)
        pares = len(self.encontradas) // 2
        self.cancelar_turno()
        self.resultado = resultado
        self.bloqueado = True
        self.limpiar_tablero()
        titulo = "¡HAS GANADO!" if resultado == "victoria" else "GAME OVER"
        self.estado.set(f"{self.nivel} · Parejas encontradas: {pares} de {self.total_pares}")
        self.panel_resultado = tk.Frame(self.tablero, bg=VERDE,
                                        highlightbackground=ORO, highlightthickness=3)
        self.panel_resultado.pack(padx=8, pady=8)
        tk.Label(self.panel_resultado, text=titulo, bg=VERDE,
                 fg="#ffe27a" if resultado == "victoria" else "#ff7770",
                 font=("Courier New", 18, "bold")).pack(padx=10, pady=(16, 10))
        datos = [f"Dificultad: {self.nivel}", f"Parejas: {pares} de {self.total_pares}"]
        if resultado == "victoria" and self.segundos_restantes is not None:
            minutos, segundos = divmod(self.segundos_restantes, 60)
            datos.append(f"Tiempo restante: {minutos:02d}:{segundos:02d}")
        tk.Label(self.panel_resultado, text="\n".join(datos), bg=VERDE, fg=CREMA,
                 font=("Courier New", 11), wraplength=260).pack(padx=8, pady=6)
        self.resultado_reiniciar = self.boton(self.panel_resultado, "Nueva partida", self.nueva_partida)
        self.resultado_reiniciar.pack(padx=10, pady=6, fill="x")
        self.resultado_menu = self.boton(self.panel_resultado, "Volver al menú", self.mostrar_menu)
        self.resultado_menu.pack(padx=10, pady=(6, 16), fill="x")
        self.organizar_controles()
        self.programar_ajuste()

    def cerrar(self):
        """Cancela eventos propios antes de destruir la aplicación."""
        self.cancelar_turno()
        if self.ajuste_pendiente is not None:
            self.ventana.after_cancel(self.ajuste_pendiente)
            self.ajuste_pendiente = None
        self.ventana.destroy()

    def descubrir(self, indice):
        if not self.activa or self.tiempo_agotado() or self.bloqueado or indice in self.encontradas or indice in self.seleccionadas:
            return
        self.seleccionadas.append(indice)
        self.actualizar_carta(indice)
        self.actualizar_ayuda()
        if len(self.seleccionadas) == 2:
            self.bloqueado = True
            primera, segunda = self.seleccionadas
            if self.cartas[primera] == self.cartas[segunda]:
                # Una pausa breve permite ver el par antes de retirarlo.
                self.programar_turno(250, self.retirar_par)
            else:
                self.programar_turno(1000, self.ocultar_cartas)

    def retirar_par(self):
        if not self.activa or self.tiempo_agotado():
            return
        self.pendiente = None
        for indice in self.seleccionadas:
            self.encontradas.add(indice)
            self.botones[indice].grid_remove()
        self.seleccionadas = []
        self.bloqueado = False
        pares = len(self.encontradas) // 2
        self.estado.set(f"{self.nivel} · Pares encontrados: {pares} de {self.total_pares}")
        if pares == self.total_pares:
            self.estado.set("¡Has ganado! Encontraste todos los pares.")
            self.mostrar_victoria()
        self.actualizar_ayuda()

    def ocultar_cartas(self):
        if not self.activa or self.tiempo_agotado():
            return
        self.pendiente = None
        anteriores = self.seleccionadas
        self.seleccionadas = []
        for indice in anteriores:
            self.actualizar_carta(indice)
        self.bloqueado = False
        self.actualizar_ayuda()


if __name__ == "__main__":
    raiz = tk.Tk()
    try:
        JuegoMemoria(raiz)
    except (FileNotFoundError, tk.TclError) as error:
        messagebox.showerror("No se pudo iniciar el juego", str(error), parent=raiz)
        raiz.destroy()
    else:
        raiz.mainloop()
