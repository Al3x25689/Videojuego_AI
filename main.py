"""Memoria Pokémon 3.0: presentación adaptable sobre la lógica de turnos original."""

import random
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
NIVELES = {"Fácil": (4, 4), "Medio": (8, 4), "Difícil": (16, 8)}
VERDE, ORO, CREMA = "#173c38", "#f6d76b", "#f5edce"


class JuegoMemoria:
    def __init__(self, ventana):
        self.ventana = ventana
        ventana.title("Memoria Pokémon · Versión 3.0")
        ventana.geometry("1000x800")
        ventana.minsize(360, 320)
        ventana.configure(bg=VERDE)
        ventana.resizable(True, True)
        self.pendiente = None
        self.ajuste_pendiente = None
        self.victoria = None
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
        self.contador.pack(pady=(0, 8))
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
        self.organizar_controles()

    def cancelar_turno(self):
        """Cancela el único evento de cartas antes de cambiar de partida."""
        if self.pendiente is not None:
            self.ventana.after_cancel(self.pendiente)
            self.pendiente = None
        if self.victoria is not None:
            if self.victoria.winfo_exists():
                self.victoria.destroy()
            self.victoria = None
        self.seleccionadas = []
        self.bloqueado = False

    def limpiar_tablero(self):
        """Destruye casillas anteriores y restablece el desplazamiento."""
        for hijo in self.tablero.winfo_children():
            hijo.destroy()
        self.botones, self.casillas = [], []
        self.lienzo.xview_moveto(0)
        self.lienzo.yview_moveto(0)

    def mostrar_menu(self):
        """Permite elegir otra dificultad sin conservar eventos anteriores."""
        self.cancelar_turno()
        self.limpiar_tablero()
        self.nivel = None
        self.cartas = []
        self.encontradas = set()
        self.estado.set("Selecciona una dificultad")
        for nombre, (pares, _) in NIVELES.items():
            opcion = self.boton(self.tablero, nombre.upper(), lambda n=nombre: self.iniciar_nivel(n))
            opcion.pack(fill="x", padx=24, pady=(14, 4))
            tk.Label(self.tablero, text=f"{pares} parejas · {pares * 2} cartas", bg=VERDE,
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

    def organizar_controles(self):
        """Envuelve los controles en ventanas estrechas sin ocultarlos."""
        for boton in (self.reiniciar, self.menu_boton, self.pantalla_boton):
            boton.grid_forget()
        for col in range(3):
            self.controles.columnconfigure(col, weight=0)
        if self.nivel is None:
            self.pantalla_boton.grid(row=0, column=0, padx=6, pady=5)
            self.controles.columnconfigure(0, weight=1)
        else:
            estrecha = self.ventana.winfo_width() < 760
            for i, boton in enumerate((self.reiniciar, self.menu_boton, self.pantalla_boton)):
                boton.grid(row=i if estrecha else 0, column=0 if estrecha else i,
                           padx=4, pady=3, sticky="ew")
                self.controles.columnconfigure(0 if estrecha else i, weight=1)

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
        if self.nivel is not None:
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
        abierta = indice in self.seleccionadas or indice in self.encontradas
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

    def mostrar_victoria(self):
        """El panel temático utiliza la cantidad de pares del nivel actual."""
        self.victoria = tk.Toplevel(self.ventana)
        self.victoria.title("¡Victoria, entrenador!")
        self.victoria.configure(bg=VERDE, padx=14, pady=16)
        self.victoria.transient(self.ventana)
        tk.Label(self.victoria, text="★ ¡HAS GANADO! ★", bg=VERDE, fg="#ffe27a",
                 font=("Courier New", 18, "bold")).pack(pady=8)
        tk.Label(self.victoria, text=f"{self.nivel}: {self.total_pares} pares encontrados.\n¡Excelente memoria!",
                 bg=VERDE, fg="white", font=("Courier New", 11)).pack(pady=8)
        self.boton(self.victoria, "Nueva partida", self.nueva_partida).pack(pady=4)
        self.boton(self.victoria, "Volver al menú", self.mostrar_menu).pack(pady=4)
        self.victoria.bind("<Escape>", self.salir_pantalla_completa)
        self.victoria.lift()

    def cerrar(self):
        """Cancela eventos propios antes de destruir la aplicación."""
        self.cancelar_turno()
        if self.ajuste_pendiente is not None:
            self.ventana.after_cancel(self.ajuste_pendiente)
            self.ajuste_pendiente = None
        self.ventana.destroy()

    def descubrir(self, indice):
        if self.nivel is None or self.bloqueado or indice in self.encontradas or indice in self.seleccionadas:
            return
        self.seleccionadas.append(indice)
        self.actualizar_carta(indice)
        if len(self.seleccionadas) == 2:
            self.bloqueado = True
            primera, segunda = self.seleccionadas
            if self.cartas[primera] == self.cartas[segunda]:
                # Una pausa breve permite ver el par antes de retirarlo.
                self.pendiente = self.ventana.after(250, self.retirar_par)
            else:
                self.pendiente = self.ventana.after(1000, self.ocultar_cartas)

    def retirar_par(self):
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

    def ocultar_cartas(self):
        self.pendiente = None
        anteriores = self.seleccionadas
        self.seleccionadas = []
        for indice in anteriores:
            self.actualizar_carta(indice)
        self.bloqueado = False


if __name__ == "__main__":
    raiz = tk.Tk()
    try:
        JuegoMemoria(raiz)
    except (FileNotFoundError, tk.TclError) as error:
        messagebox.showerror("No se pudo iniciar el juego", str(error), parent=raiz)
        raiz.destroy()
    else:
        raiz.mainloop()
