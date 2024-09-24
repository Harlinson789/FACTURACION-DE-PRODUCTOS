import sqlite3
import tkinter as tk
from tkinter import messagebox, StringVar, ttk
from fpdf import FPDF  # Importar FPDF
import re
from datetime import datetime

# Configurar la base de datos
def init_db():
    conn = sqlite3.connect('productos.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            marca TEXT NOT NULL,
            precio REAL NOT NULL,
            categoria TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY,
            documento TEXT NOT NULL,
            nombre TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Función para agregar un producto
def add_product():
    nombre = entry_nombre.get()
    marca = entry_marca.get()
    precio = entry_precio.get()
    categoria = entry_categoria.get()

    # Validar que todos los campos estén llenos
    if not nombre or not marca or not precio or not categoria:
        messagebox.showwarning("Advertencia", "Por favor, completa todos los campos.")
        return

    # Validar que el nombre no tenga caracteres extraños
    if not re.match("^[a-zA-Z0-9 ]*$", nombre):  # Solo permite letras, números y espacios
        messagebox.showwarning("Advertencia", "El nombre solo puede contener letras, números y espacios.")
        return

    # Validar que el precio sea un número
    try:
        precio = float(precio)
        conn = sqlite3.connect('productos.db')
        c = conn.cursor()
        c.execute('INSERT INTO productos (nombre, marca, precio, categoria) VALUES (?, ?, ?, ?)',
                  (nombre, marca, precio, categoria))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Producto añadido con éxito.")
        clear_entries()
        load_products()  # Cargar productos en el desplegable
    except ValueError:
        messagebox.showerror("Error", "Por favor, ingresa un precio válido.")

# Limpiar campos de entrada
def clear_entries():
    entry_nombre.delete(0, tk.END)
    entry_marca.delete(0, tk.END)
    entry_precio.delete(0, tk.END)
    entry_categoria.delete(0, tk.END)

# Cargar productos en el desplegable
def load_products():
    conn = sqlite3.connect('productos.db')
    c = conn.cursor()
    c.execute("SELECT nombre FROM productos")
    productos = [row[0] for row in c.fetchall()]
    combo_productos['values'] = productos
    conn.close()

# Función para agregar el producto seleccionado a la lista de compra
def add_to_cart():
    selected_product = combo_productos.get()
    cantidad = entry_cantidad.get()

    if not selected_product:
        messagebox.showwarning("Advertencia", "Por favor, selecciona un producto.")
        return

    if not cantidad.isdigit() or int(cantidad) <= 0:
        messagebox.showwarning("Advertencia", "Por favor, ingresa una cantidad válida.")
        return

    conn = sqlite3.connect('productos.db')
    c = conn.cursor()
    c.execute("SELECT nombre, precio FROM productos WHERE nombre=?", (selected_product,))
    product_data = c.fetchone()
    conn.close()

    if product_data:
        product_name, product_price = product_data
        total_price = float(product_price) * int(cantidad)
        lista_compras.insert(tk.END, f"{product_name} (x{cantidad}): ${total_price:.2f}")

# Función para generar la factura
def generate_invoice():
    cliente_doc = entry_cliente_doc.get()  # Obtener documento del cliente
    if not cliente_doc:
        messagebox.showwarning("Advertencia", "Por favor, ingresa el documento del cliente.")
        return

    # Crear el objeto PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Agregar información del cliente
    pdf.cell(200, 10, txt=f"Factura para el cliente: {cliente_doc}", ln=True)

    # Agregar productos a la factura
    total = 0
    for item in lista_compras.get(0, tk.END):
        pdf.cell(200, 10, txt=item, ln=True)
        # Extraer el precio total de cada item
        _, total_price = item.rsplit(": $", 1)
        total += float(total_price)

    # Agregar total
    pdf.cell(200, 10, txt=f"Total: ${total:.2f}", ln=True)

    # Guardar el archivo PDF
    pdf_file_name = f"factura_{cliente_doc}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(pdf_file_name)

    messagebox.showinfo("Éxito", f"Factura generada: {pdf_file_name}")

# Crear interfaz
app = tk.Tk()
app.title("Facturación de Productos")

# Entradas para productos
tk.Label(app, text="Nombre:").grid(row=0, column=0)
entry_nombre = tk.Entry(app)
entry_nombre.grid(row=0, column=1)

tk.Label(app, text="Marca:").grid(row=1, column=0)
entry_marca = tk.Entry(app)
entry_marca.grid(row=1, column=1)

tk.Label(app, text="Precio:").grid(row=2, column=0)
entry_precio = tk.Entry(app)
entry_precio.grid(row=2, column=1)

tk.Label(app, text="Categoría:").grid(row=3, column=0)
entry_categoria = tk.Entry(app)
entry_categoria.grid(row=3, column=1)

# Botón para agregar producto
btn_agregar = tk.Button(app, text="Agregar Producto", command=add_product)
btn_agregar.grid(row=4, columnspan=2)

# Desplegable para seleccionar productos
tk.Label(app, text="Seleccionar Producto:").grid(row=5, column=0)
combo_productos = ttk.Combobox(app)
combo_productos.grid(row=5, column=1)

# Entrada para cantidad
tk.Label(app, text="Cantidad:").grid(row=6, column=0)
entry_cantidad = tk.Entry(app)
entry_cantidad.grid(row=6, column=1)

# Botón para agregar el producto seleccionado a la lista de compra
btn_agregar_carrito = tk.Button(app, text="Agregar al Carrito", command=add_to_cart)
btn_agregar_carrito.grid(row=7, columnspan=2)

# Lista para mostrar productos seleccionados
tk.Label(app, text="Productos en Carrito:").grid(row=8, column=0)
lista_compras = tk.Listbox(app, width=50)
lista_compras.grid(row=9, columnspan=2)

# Entradas para cliente
tk.Label(app, text="Documento del Cliente:").grid(row=10, column=0)
entry_cliente_doc = tk.Entry(app)
entry_cliente_doc.grid(row=10, column=1)

# Botón para generar factura
btn_generar_factura = tk.Button(app, text="Generar Factura", command=generate_invoice)
btn_generar_factura.grid(row=11, columnspan=2)

# Inicializar base de datos y cargar productos
init_db()
load_products()

# Ejecutar la aplicación
app.mainloop()
