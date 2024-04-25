import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from PyPDF2 import PdfReader

class NodoArbol:
    def __init__(self, palabra):
        self.palabra = palabra
        self.repeticiones = 1
        self.valor = self.calcular_valor()
        self.izquierda = None
        self.derecha = None

    def calcular_valor(self):
        valor = 0
        for letra in self.palabra:
            valor += ord(letra.lower()) - 96
        return valor * self.repeticiones

class ArbolBinarioBusqueda:
    def __init__(self):
        self.raiz = None

    def insertar(self, palabra):
        palabra = palabra.lower()
        if not self.raiz:
            self.raiz = NodoArbol(palabra)
        else:
            self._insertar_recursivo(palabra, self.raiz)

    def _insertar_recursivo(self, palabra, nodo):
        palabra = palabra.lower()
        if palabra == nodo.palabra:
            nodo.repeticiones += 1
        elif palabra < nodo.palabra:
            if nodo.izquierda is None:
                nodo.izquierda = NodoArbol(palabra)
            else:
                self._insertar_recursivo(palabra, nodo.izquierda)
        else:
            if nodo.derecha is None:
                nodo.derecha = NodoArbol(palabra)
            else:
                self._insertar_recursivo(palabra, nodo.derecha)

    def recorrido_inorden(self, nodo, lista):
        if nodo:
            self.recorrido_inorden(nodo.izquierda, lista)
            lista.append(nodo)
            self.recorrido_inorden(nodo.derecha, lista)

class IndexadorPalabras:
    def __init__(self, master):
        self.master = master
        self.master.title("Indexador de Palabras")

        self.arbol = ArbolBinarioBusqueda()
        self.num_archivos_cargados = 0

        self.frame_principal = tk.Frame(master)
        self.frame_principal.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.frame_principal, width=1200, height=700, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar_vertical = ttk.Scrollbar(self.frame_principal, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar_vertical.pack(side=tk.RIGHT, fill=tk.Y)

        self.scrollbar_horizontal = ttk.Scrollbar(self.frame_principal, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scrollbar_horizontal.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas.configure(yscrollcommand=self.scrollbar_vertical.set, xscrollcommand=self.scrollbar_horizontal.set)

        self.label = tk.Label(master, text="Cargar documento:", font=("Arial", 14))
        self.label.pack()

        self.button_cargar = tk.Button(master, text="Cargar", font=("Arial", 14), command=self.cargar_documento)
        self.button_cargar.pack()

        self.x_offset = 100  # Espacio entre nodos en el eje X
        self.y_offset = 50
        self.node_radius = 20
        self.zoom_factor = 1.0

        self.tamano_maximo = 10 * 1024 * 1024

    def cargar_documento(self):
        if self.num_archivos_cargados >= 10:
            messagebox.showwarning("Advertencia", "Ya has cargado el máximo de archivos (10)")
            return

        filepath = filedialog.askopenfilename()
        if filepath:
            if os.path.getsize(filepath) > self.tamano_maximo:
                messagebox.showwarning("Advertencia", "El archivo seleccionado excede el tamaño máximo permitido (10 MB)")
                return
            self.procesar_documento(filepath)
        else:
            messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo")

    def procesar_documento(self, filepath):
        try:
            if filepath.endswith(".pdf"):
                with open(filepath, "rb") as file:
                    pdf_reader = PdfReader(file)
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        palabras = self.extraer_palabras(text)
                        for palabra in palabras:
                            if palabra:
                                self.arbol.insertar(palabra)
            else:
                messagebox.showwarning("Advertencia", "Solo se pueden cargar archivos PDF")

            self.num_archivos_cargados += 1
            self.dibujar_arbol()
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar el archivo: {str(e)}")

    def extraer_palabras(self, texto):
        palabras = texto.split()
        palabras_sin_espacios = [palabra.strip(",.!?;:_") for palabra in palabras]
        return [palabra for palabra in palabras_sin_espacios if palabra and not palabra.startswith("_")]

    def dibujar_arbol(self):
        self.canvas.delete("all")
        nodos = []
        self.arbol.recorrido_inorden(self.arbol.raiz, nodos)
        nodos.sort(key=lambda x: x.valor)  # Ordenar los nodos por su valor
        self.min_valor = min(nodos, key=lambda x: x.valor).valor
        self.max_valor = max(nodos, key=lambda x: x.valor).valor
        nivel = self.calcular_niveles(self.arbol.raiz)
        for nodo in nodos:
            x = self.x_offset + 800 * (nodo.valor - self.min_valor) / (self.max_valor - self.min_valor)
            y = self.y_offset + 100 * nivel[nodo]
            self.dibujar_nodo(nodo, x, y)

    def dibujar_nodo(self, nodo, x, y):
        self.canvas.create_oval(x - self.node_radius, y - self.node_radius,
                                x + self.node_radius, y + self.node_radius,
                                fill="white", outline="black")
        self.canvas.create_text(x, y, text=nodo.palabra, font=("Arial", 12, "bold"))

        if nodo.repeticiones > 1:
            self.canvas.create_text(x, y + 20, text=f"Repeticiones: {nodo.repeticiones}", font=("Arial", 10, "italic"), fill="gray")

        nivel = self.calcular_niveles(self.arbol.raiz)
        if nodo.izquierda:
            x_izquierda = self.x_offset + 800 * (nodo.izquierda.valor - self.min_valor) / (self.max_valor - self.min_valor)
            y_izquierda = self.y_offset + 100 * nivel[nodo.izquierda]
            self.canvas.create_line(x, y, x_izquierda, y_izquierda, arrow=tk.LAST)

        if nodo.derecha:
            x_derecha = self.x_offset + 800 * (nodo.derecha.valor - self.min_valor) / (self.max_valor - self.min_valor)
            y_derecha = self.y_offset + 100 * nivel[nodo.derecha]
            self.canvas.create_line(x, y, x_derecha, y_derecha, arrow=tk.LAST)

    def calcular_niveles(self, nodo, nivel=0, niveles=None):
        if niveles is None:
            niveles = {}
        if nodo:
            niveles[nodo] = nivel
            self.calcular_niveles(nodo.izquierda, nivel + 1, niveles)
            self.calcular_niveles(nodo.derecha, nivel + 1, niveles)
        return niveles

    def zoom_in(self, event):
        self.zoom_factor *= 1.1
        self.canvas.scale(tk.ALL, event.x, event.y, 1.1, 1.1)

    def zoom_out(self, event):
        self.zoom_factor /= 1.1
        self.canvas.scale(tk.ALL, event.x, event.y, 0.9, 0.9)

def main():
    root = tk.Tk()
    indexador = IndexadorPalabras(root)
    root.bind("<Control-plus>", indexador.zoom_in)
    root.bind("<Control-minus>", indexador.zoom_out)
    root.mainloop()

if __name__ == "__main__":
    main()
