"""Juego de memoria de cuatro pares, construido con Tkinter."""

import random
import tkinter as tk
from tkinter import messagebox


class JuegoMemoria:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Juego de memoria")
        self.ventana.resizable(False, False)
        self.pendiente = None
        self.cartas = []
        self.seleccionadas = []
        self.encontradas = set()
        self.bloqueado = False

        tk.Label(ventana, text="Encuentra los 4 pares", font=("Arial", 18)).pack(pady=12)
        self.estado = tk.StringVar()
        tk.Label(ventana, textvariable=self.estado, font=("Arial", 11)).pack()
        tablero = tk.Frame(ventana)
        tablero.pack(padx=16, pady=12)
        self.botones = []
        for indice in range(8):
            boton = tk.Button(
                tablero, text="?", width=7, height=3,
                font=("Arial", 20, "bold"),
                command=lambda i=indice: self.descubrir(i),
            )
            boton.grid(row=indice // 4, column=indice % 4, padx=5, pady=5)
            self.botones.append(boton)
        tk.Button(ventana, text="Nueva partida", command=self.nueva_partida).pack(pady=(0, 16))
        self.nueva_partida()

    def nueva_partida(self):
        # Cancelar el temporizador evita que un turno anterior afecte la partida nueva.
        if self.pendiente is not None:
            self.ventana.after_cancel(self.pendiente)
            self.pendiente = None
        self.cartas = list("ABCD") * 2
        random.shuffle(self.cartas)
        self.seleccionadas = []
        self.encontradas = set()
        self.bloqueado = False
        self.estado.set("Pares encontrados: 0 de 4")
        for boton in self.botones:
            boton.config(text="?", state=tk.NORMAL)
            boton.grid()

    def descubrir(self, indice):
        if self.bloqueado or indice in self.encontradas or indice in self.seleccionadas:
            return
        self.botones[indice].config(text=self.cartas[indice], state=tk.DISABLED)
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
            messagebox.showinfo("¡Has ganado!", "¡Encontraste los 4 pares!", parent=self.ventana)

    def ocultar_cartas(self):
        self.pendiente = None
        for indice in self.seleccionadas:
            self.botones[indice].config(text="?", state=tk.NORMAL)
        self.seleccionadas = []
        self.bloqueado = False


if __name__ == "__main__":
    raiz = tk.Tk()
    JuegoMemoria(raiz)
    raiz.mainloop()
