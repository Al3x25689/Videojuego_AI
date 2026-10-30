"""Juego de memoria de cuatro pares, construido con Tkinter."""

import random
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

ASSETS = Path(__file__).resolve().parent / "assets"
POKEMON = ("gardevoir", "gengar", "pikachu", "lucario")


class JuegoMemoria:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Memoria Pokémon · Edición pixel")
        self.ventana.geometry("920x740")
        self.ventana.configure(bg="#183c38")
        self.victoria = None
        self.imagenes = self.cargar_imagenes()
        self.ventana.resizable(False, False)
        self.pendiente = None
        self.cartas = []
        self.seleccionadas = []
        self.encontradas = set()
        self.bloqueado = False

        fondo = tk.Canvas(ventana, width=920, height=740, highlightthickness=0)
        fondo.pack(fill="both", expand=True)
        fondo.create_image(0, 0, image=self.imagenes["fondo"], anchor="nw")
        fondo.create_rectangle(74, 22, 846, 145, fill="#173c38", outline="#f6d76b", width=4)
        fondo.create_text(460, 58, text="MEMORIA POKÉMON", fill="#ffe27a",
                          font=("Courier New", 28, "bold"))
        fondo.create_text(460, 94, text="Encuentra los 4 pares · ¡Atrápalos con tu memoria!",
                          fill="#f6f4dc", font=("Courier New", 12, "bold"))
        self.estado = tk.StringVar()
        contador = tk.Label(ventana, textvariable=self.estado, bg="#173c38", fg="#ffffff",
                            font=("Courier New", 12, "bold"))
        fondo.create_window(460, 123, window=contador)
        tablero = tk.Frame(ventana, bg="#173c38", padx=12, pady=12,
                           highlightbackground="#f6d76b", highlightthickness=4)
        fondo.create_window(460, 374, window=tablero)
        self.botones = []
        for indice in range(8):
            # Cada casilla conserva su espacio cuando desaparece un par.
            casilla = tk.Frame(tablero, width=170, height=194, bg="#173c38")
            casilla.grid(row=indice // 4, column=indice % 4)
            casilla.grid_propagate(False)
            boton = tk.Button(
                casilla, image=self.imagenes["reverso"], width=148, height=172,
                bg="#244b70", activebackground="#ffe27a", relief="flat", bd=3,
                cursor="hand2", takefocus=True,
                command=lambda i=indice: self.descubrir(i),
            )
            boton.grid(padx=8, pady=8)
            self.botones.append(boton)
        reiniciar = tk.Button(ventana, text="NUEVA PARTIDA", command=self.nueva_partida,
                              bg="#ffe27a", fg="#173c38", activebackground="#fff0ae",
                              font=("Courier New", 15, "bold"), padx=24, pady=10,
                              relief="raised", bd=4, cursor="hand2")
        fondo.create_window(460, 631, window=reiniciar)
        fondo.create_text(460, 689, text="Selecciona dos cartas por turno",
                          fill="#142f32", font=("Courier New", 12, "bold"))
        self.nueva_partida()

    def cargar_imagenes(self):
        """Carga PNG locales; informa los archivos que faltan sin sustituirlos."""
        nombres = ("fondo", "reverso") + POKEMON
        faltantes = [str(ASSETS / f"{nombre}.png") for nombre in nombres
                     if not (ASSETS / f"{nombre}.png").is_file()]
        if faltantes:
            raise FileNotFoundError("Faltan recursos gráficos:\n" + "\n".join(faltantes))
        return {nombre: tk.PhotoImage(master=self.ventana, file=str(ASSETS / f"{nombre}.png"))
                for nombre in nombres}

    def mostrar_victoria(self):
        self.victoria = tk.Toplevel(self.ventana)
        self.victoria.title("¡Victoria, entrenador!")
        self.victoria.configure(bg="#173c38", padx=28, pady=24)
        self.victoria.resizable(False, False)
        self.victoria.transient(self.ventana)
        tk.Label(self.victoria, text="★ ¡HAS GANADO! ★", bg="#173c38", fg="#ffe27a",
                 font=("Courier New", 22, "bold")).pack(pady=8)
        tk.Label(self.victoria, text="Encontraste los 4 pares.\n¡Excelente memoria, entrenador!",
                 bg="#173c38", fg="white", font=("Courier New", 12)).pack(pady=12)
        tk.Button(self.victoria, text="Nueva partida", command=self.nueva_partida,
                  bg="#ffe27a", font=("Courier New", 12, "bold"), padx=15, pady=8).pack()

    def nueva_partida(self):
        if self.victoria is not None:
            if self.victoria.winfo_exists():
                self.victoria.destroy()
            self.victoria = None
        # Cancelar el temporizador evita que un turno anterior afecte la partida nueva.
        if self.pendiente is not None:
            self.ventana.after_cancel(self.pendiente)
            self.pendiente = None
        self.cartas = list(POKEMON) * 2
        random.shuffle(self.cartas)
        self.seleccionadas = []
        self.encontradas = set()
        self.bloqueado = False
        self.estado.set("Pares encontrados: 0 de 4")
        for boton in self.botones:
            boton.config(image=self.imagenes["reverso"], state=tk.NORMAL)
            boton.grid()

    def descubrir(self, indice):
        if self.bloqueado or indice in self.encontradas or indice in self.seleccionadas:
            return
        self.botones[indice].config(image=self.imagenes[self.cartas[indice]], state=tk.DISABLED)
        self.seleccionadas.append(indice)
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
        self.estado.set(f"Pares encontrados: {pares} de 4")
        if pares == 4:
            self.estado.set("¡Has ganado! Encontraste todos los pares.")
            self.mostrar_victoria()

    def ocultar_cartas(self):
        self.pendiente = None
        for indice in self.seleccionadas:
            self.botones[indice].config(image=self.imagenes["reverso"], state=tk.NORMAL)
        self.seleccionadas = []
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
