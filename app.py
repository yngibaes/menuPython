from tkinter import Tk, ttk, Frame, Label, Button, Text, messagebox as mb, Spinbox
import os
import sqlite3 as sql
import datetime as dt

Ahora = dt.datetime.now()
fechaHora = Ahora.strftime('%Y-%m-%d %H:%M:%S')

def create_tables():
    """Crear tablas de la base de datos"""
    conn = sql.connect('restaurante')
    cursor = conn.cursor()
    # Tabla de orden
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orden (
        id INTEGER PRIMARY KEY,
        mesa INTEGER
        )
    """)

    # Tabla de producto
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS producto (
            id INTEGER PRIMARY KEY,
            nombre TEXT,
            precio REAL,
            costo REAL,
            tipo TEXT,
            categoria_id INT,
            FOREIGN KEY (categoria_id) REFERENCES categoria(id)
            )
        """)

    #Tabla intermedia
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS producto_orden (
            producto_id INT,
            orden_id INT,
            fecha_hora DATETIME,
            FOREIGN KEY (producto_id) REFERENCES producto(id),
            FOREIGN KEY (orden_id) REFERENCES orden(id)
            )
        """) 

    # Tabla de categoría
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categoria (
            id INTEGER PRIMARY KEY,
            nombre TEXT
        )
    """)

    cursor.execute("INSERT INTO categoria (nombre) VALUES ('Bebidas no alcohol'), ('Cervezas'), ('Pastas'), ('Entrada'), ('Postres')")

    cursor.execute("INSERT INTO producto(nombre, precio, costo, tipo, categoria_id) VALUES ('Agua', 18, 12, 'Bebida', 1), ('Coca Cola', 20, 15, 'Bebida', 1), ('Corona', 25, 20, 'Bebida', 2), ('Ensalada Cesar', 30, 25, 'Comida', 4), ('Pasta 4 Quesos', 45, 40, 'Comida', 3), ('Tiramisú', 30, 25, 'Comida', 5)")

    conn.commit()

def connect():
    """Conexión a la base de datos SQLite"""
    try:
        if not os.path.exists('restaurante'):
            create_tables()# Crear tablas si no existen
            mb.showinfo("Base de Datos", "Creada.")
        else:
            mb.showinfo("Base de Datos", "La base de datos ya existe.")
        mb.showinfo("Conexión Exitosa", "Conexión a la base de datos establecida correctamente.")
    except Exception as e:
        mb.showerror("Error de Conexión", f"No se pudo conectar a la base de datos: {str(e)}")


def get_ultimo_pedido():
    """Obtener el último pedido de la base de datos"""
    cursor.execute("SELECT MAX(orden_id) FROM producto_orden")
    ultimo_orden_id = cursor.fetchone()[0]

    if ultimo_orden_id is not None:
        cursor.execute("""
            SELECT orden_id, producto.nombre
            FROM producto_orden
            JOIN producto ON producto_orden.producto_id = producto.id
            WHERE producto_orden.orden_id = ?
        """, (ultimo_orden_id,))
        return cursor.fetchall()
    else:
        return []

def setPedido():
    """Establecer el pedido en la interfaz e insertar en la base de datos"""
    ind = 0
    
    #Crear la orden para poder enviarla a la table intermedia.
    conn = sql.connect('restaurante')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orden (mesa) VALUES (1)")
    conn.commit()

    # Capturar el ID de la orden que se acaba de crear
    orden_id = cursor.lastrowid
    print(f"El ID de la orden creada es: {orden_id}")
    print("----------------------------------")

    print('Su pedido es el siguiente:')
    for j, k in zip(comNum, bebNum):
        print(comida[ind],':',j.get())
        print(bebida[ind],':',k.get())

    print("----------------------------------")
    print("Enviar pedido a la base de datos:")
    for j, k in zip(comNum, bebNum):
        """Se llaman los id de los productos"""
        com = cursor.execute("SELECT id FROM producto WHERE nombre = ?", (comida[ind],))
        comida_id = com.fetchone()
        bebi = cursor.execute("SELECT id FROM producto WHERE nombre = ?", (bebida[ind],))
        bebida_id = bebi.fetchone()
        
        # Se llama la cantidad de veces que se seleccionó el producto bebida
        if comida_id is not None and int(j.get()) > 0:
            for _ in range(int(j.get())): # Insertar la cantidad de veces que se seleccionó
                print(f"El producto {comida[ind]} tiene un ID: {comida_id[0]}")
                cursor.execute("""INSERT INTO producto_orden (producto_id, orden_id, fecha_hora) VALUES (?, ?, ?)""", (comida_id[0], orden_id, fechaHora))
                print(f"Enviando {comida[ind]} a la base de datos...")
        else:
            if comida_id is None and int(j.get()) <= 0:
                print(f"El producto {comida[ind]} no existe en la base de datos o no fue seleccionado")


        # Se llama la cantidad de veces que se seleccionó el producto bebida
        if bebida_id is not None and int(k.get()) > 0:
            for _ in range(int(k.get())): # Insertar la cantidad de veces que se seleccionó
                print(f"El producto {bebida[ind]} tiene un ID: {bebida_id[0]}")
                cursor.execute("""INSERT INTO producto_orden (producto_id, orden_id, fecha_hora) VALUES (?, ?, ?)""", (bebida_id[0], orden_id, fechaHora))
                print(f"Enviando {bebida[ind]} a la base de datos...")
        else:
            if bebida_id is None and int(k.get()) <= 0:
               print(f"El producto {bebida[ind]} no existe en la base de datos o no fue seleccionado")

        ind += 1
        conn.commit()

# --- Root Tk ---
root = Tk()
root.title('Gestor de Pedidos')
root.iconbitmap('icon.ico')
style = ttk.Style()
style.theme_use('winnative')
#themes:('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')

# --- Root Config ---
appw = 440
apph = 370
screenw = root.winfo_screenwidth()
screenh = root.winfo_screenheight()
x = (screenw//2)-(appw//2)
y = (screenh//2)-(apph//2)
root.geometry(f'{appw}x{apph}+{x}+{y}')
root.resizable(width=False, height=False)
fnt = ('cascadia code', 10, 'normal')

# --- Tabs Config ---
mainTabs = ttk.Notebook(root)
ordenarTab = Frame(mainTabs)
ordenarTab.config(bg='seashell3')
mainTabs.pack(expand=1, fill='both')


# ----- Conectar a la base de datos -----
pedidoTab = Frame(mainTabs)
pedidoTab.config(bg='seashell3')
mainTabs.add(pedidoTab, text='Conectar base de datos')

Label(pedidoTab, text='Conectar a la base de datos:', 
                    font=('cascadia code', 12, 'bold'), 
                    bg='seashell3').grid(padx=10, pady=20)

Button(pedidoTab, text='Conectar', font=('cascadia code', 12, 'bold'), bg='palegreen4', command=connect).grid(padx=160, pady=5)


# ----- TAB ORDENAR -----
mainTabs.add(ordenarTab, text='Ordenar')
Label(ordenarTab, text='¿Que desea ordenar?', 
                    font=('cascadia code', 12, 'bold'), 
                    bg='seashell3').grid(row=0, column=1, padx=10, pady=20)

# --- Sección de Comidas ---
Label(ordenarTab, text='Comidas:', 
                    font=('cascadia code', 10, 'italic', 'bold'), 
                    bg='seashell3').grid(row=2, column=0, padx=10, pady=10)

# --- Obtener datos de la base de datos - Comida ---
conn = sql.connect('restaurante')
cursor = conn.cursor()
sqlquerycom = 'SELECT nombre FROM producto WHERE tipo = "Comida"'
cursor.execute(sqlquerycom)
resultscom = cursor.fetchall()
comida = list(map(lambda x: x[0], resultscom))

comNum = []
incrementCol = 0

for i, j in enumerate(comida):
    Label(ordenarTab, text=j, bg='seashell3', font=fnt).grid(row=3, column=incrementCol, padx=10)
    comNum.append(Spinbox(ordenarTab, font=fnt, width=3, justify='center', from_=0, to=100))
    comNum[i].grid(row=4, column=incrementCol, pady=10)
    incrementCol += 1

# --- Sección de Bebidas ---
Label(ordenarTab, text='Bebidas:', 
                    font=('cascadia code', 10, 'italic', 'bold'), 
                    bg='seashell3').grid(row=5, column=0, padx=10)

# --- Obtener datos de la base de datos - Bebidas ---
sqlquerybebi = 'SELECT nombre FROM producto WHERE tipo = "Bebida"'
cursor.execute(sqlquerybebi)
resultsbebi = cursor.fetchall()
bebida = list(map(lambda x: x[0], resultsbebi))

bebNum = []
incrementCol = 0
for i, j in enumerate(bebida):
    Label(ordenarTab, text=j, bg='seashell3', font=fnt).grid(row=6, column=incrementCol, padx=5, pady=10)
    bebNum.append(Spinbox(ordenarTab, font=fnt, width=2, justify='center', from_=0, to=100))
    bebNum[i].grid(row=7, column=incrementCol, pady=10)
    incrementCol += 1

Button(ordenarTab, text='Ordenar', font=('cascadia code', 12, 'bold'), bg='palegreen4', 
                    relief='flat',command=setPedido).grid(row=8, column=1, pady=10)


# ----- TAB PEDIDOS -----
pedidoTab = Frame(mainTabs)
pedidoTab.config(bg='seashell3')
mainTabs.add(pedidoTab, text='Ver Pedido')

# --- Sección de Pedidos ---
Label(pedidoTab, text='Último pedido:', 
                    font=('cascadia code', 12, 'bold'), 
                    bg='seashell3').grid(row=0, column=1, padx=1, pady=3)

# Recupera último pedido de la base de datos
ultimo_pedido = get_ultimo_pedido()

# Crea un widget de texto para mostrar los pedidos
widgetPedido = Text(pedidoTab)
widgetPedido.config(width=40, height=8, font=('cascadia code', 10))
widgetPedido.grid(row=1, column=1, padx=5, pady=10)

# Muestra el pedido en el widget de texto
if ultimo_pedido:
    for id_orden, producto_nombre in ultimo_pedido:
        widgetPedido.insert('end', f"{id_orden}: {producto_nombre}\n")
else:
    widgetPedido.insert('end', "No hay pedidos.\n")

# Deshabilita el widget de texto para que los usuarios no puedan editar los pedidos
widgetPedido.config(state='disabled')

root.mainloop()