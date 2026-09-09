import sqlite3
import datetime
import math
import pandas as pd
# Este módulo gestiona un inventario simple usando SQLite.
# La base de datos se guarda en un archivo llamado 'inventario.db'.
# Cada producto tiene nombre, cantidad, precio, costo, unidad y un marcado de eliminación lógica.


def inicializar_db():
    #Crea las tablas necesarias si aún no existen.
    with sqlite3.connect('inventario.db') as conn:
        cur = conn.cursor()

        # Tabla de productos: almacena la información principal del inventario.
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Productos (
                ID_Producto INTEGER PRIMARY KEY AUTOINCREMENT,
                Nombre TEXT NOT NULL,
                Cantidad REAL NOT NULL,
                Precio REAL NOT NULL,
                Costo REAL NOT NULL,
                Tipo_unidad TEXT NOT NULL,
                IsDeleted INTEGER NOT NULL DEFAULT 0,
                ID_Visible INTEGER UNIQUE
            );
        ''')

        # Tabla de historial: guarda los registros de compra y venta.
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Historial (
                ID_Operacion INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_Producto INTEGER,
                Fecha TEXT,
                Tipo_operacion TEXT,
                Cantidad_involucrada REAL,
                Monto_operacion REAL,
                FOREIGN KEY (ID_Producto) REFERENCES Productos(ID_Producto)
            );
        ''')
        cur.execute("PRAGMA table_info(Productos)")
        columnas_productos = {columna[1] for columna in cur.fetchall()}
        if "ID_Visible" not in columnas_productos:
            cur.execute("ALTER TABLE Productos ADD COLUMN ID_Visible INTEGER")
        cur.execute("UPDATE Productos SET ID_Visible = ID_Producto WHERE ID_Visible IS NULL")
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_productos_id_visible ON Productos(ID_Visible)")
        conn.commit()


def _validar_numero(valor, nombre):
    #Comprueba que un valor sea numérico y no sea infinito ni NaN.
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser un número válido")

    valor_float = float(valor)
    if math.isnan(valor_float) or math.isinf(valor_float):
        raise ValueError(f"{nombre} no puede ser NaN ni infinito")

    return valor_float


def ConvertirFecha(fecha, nombre):
    #Convierte una fecha en texto o datetime a un objeto datetime válido.
    if isinstance(fecha, datetime.datetime):
        return fecha

    if isinstance(fecha, datetime.date):
        return datetime.datetime.combine(fecha, datetime.time.min)

    if not isinstance(fecha, str) or not fecha.strip():
        raise ValueError(f"{nombre} es obligatoria")

    fecha_str = fecha.strip()
    formatos = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%Y/%m/%d"
    ]

    for formato in formatos:
        try:
            return datetime.datetime.strptime(fecha_str, formato)
        except ValueError:
            continue

    raise ValueError(f"{nombre} debe tener un formato válido (YYYY-MM-DD o YYYY-MM-DD HH:MM:SS)")


def CrearProducto(id_visible, nombre, cantidad, precio, costo, tipo_unidad):
    #Crea un producto nuevo y lo guarda en la base de datos.
    if not isinstance(id_visible, int) or isinstance(id_visible, bool) or id_visible <= 0:
        raise ValueError("El ID visible debe ser un número entero positivo")

    if not isinstance(nombre, str) or not nombre.strip():
        raise ValueError("El nombre es obligatorio")

    cantidad_val = _validar_numero(cantidad, "La cantidad")
    precio_val = _validar_numero(precio, "El precio")
    costo_val = _validar_numero(costo, "El costo")

    if cantidad_val < 0:
        raise ValueError("La cantidad no puede ser negativa")

    if precio_val < 0 or costo_val < 0:
        raise ValueError("El precio y el costo no pueden ser negativos")

    if not isinstance(tipo_unidad, str) or not tipo_unidad.strip():
        raise ValueError("El tipo de unidad es obligatorio")

    nombre_limpio = nombre.strip()
    tipo_unidad_limpio = tipo_unidad.strip()

    with sqlite3.connect('inventario.db') as conn:
        cur = conn.cursor()
        cur.execute('''SELECT ID_Producto FROM Productos WHERE ID_Visible = ?;''', (id_visible,))
        if cur.fetchone() is not None:
            raise ValueError("El ID visible ya está asignado a otro producto")
        cur.execute(
            '''
            INSERT INTO Productos (Nombre, Cantidad, Precio, Costo, Tipo_unidad, IsDeleted, ID_Visible)
            VALUES (?, ?, ?, ?, ?, 0, ?)
            ''',
            (nombre_limpio, cantidad_val, precio_val, costo_val, tipo_unidad_limpio, id_visible)
        )
        conn.commit()


def ConsultarInventario():
    #Devuelve todos los productos activos que no han sido eliminados.
    with sqlite3.connect('inventario.db') as conn:
        cur = conn.cursor()
        cur.execute('''SELECT ID_Visible, Nombre, Cantidad, Precio, Costo, Tipo_unidad, IsDeleted
                   FROM Productos WHERE IsDeleted = 0;''')
        return cur.fetchall()


def ConsultarHistorial():
    #Devuelve todos los movimientos registrados, del más reciente al más antiguo.
    with sqlite3.connect('inventario.db') as conn:
        cur = conn.cursor()
        cur.execute(
            '''
            SELECT h.ID_Operacion, p.ID_Visible, p.Nombre, h.Fecha,
            h.Tipo_operacion, h.Cantidad_involucrada, h.Monto_operacion
            FROM Historial h
            LEFT JOIN Productos p ON p.ID_Producto = h.ID_Producto
            ORDER BY h.ID_Operacion DESC;
            '''
        )
        return cur.fetchall()


def ConsultarTodosLosProductos():
    #Devuelve productos activos y eliminados para tareas de administración.
    with sqlite3.connect('inventario.db') as conn:
        cur = conn.cursor()
        cur.execute('''SELECT ID_Producto, ID_Visible, Nombre, Cantidad, Precio, Costo, Tipo_unidad, IsDeleted
                   FROM Productos ORDER BY IsDeleted, ID_Visible;''')
        return cur.fetchall()


def RestaurarProducto(id_producto):
    #Restaura un producto eliminado lógicamente.
    if not isinstance(id_producto, int) or isinstance(id_producto, bool) or id_producto <= 0:
        raise ValueError("El ID del producto es inválido")

    with sqlite3.connect('inventario.db') as conn:
        cur = conn.cursor()
        cur.execute(
            '''UPDATE Productos SET IsDeleted = 0 WHERE ID_Visible = ? AND IsDeleted = 1;''',
            (id_producto,)
        )
        if cur.rowcount == 0:
            raise ValueError("El producto no existe o ya está activo")
        conn.commit()


def EliminarProductoDefinitivamente(id_producto):
    #Elimina permanentemente un producto y sus movimientos históricos.
    if not isinstance(id_producto, int) or isinstance(id_producto, bool) or id_producto <= 0:
        raise ValueError("El ID del producto es inválido")

    with sqlite3.connect('inventario.db') as conn:
        cur = conn.cursor()
        cur.execute('''SELECT ID_Producto FROM Productos WHERE ID_Visible = ?;''', (id_producto,))
        producto = cur.fetchone()
        if producto is None:
            raise ValueError("El producto no existe")

        id_producto_real = producto[0]
        cur.execute('''DELETE FROM Historial WHERE ID_Producto = ?;''', (id_producto_real,))
        cur.execute('''DELETE FROM Productos WHERE ID_Producto = ?;''', (id_producto_real,))
        conn.commit()


def ReiniciarIdsProductos():
    #Reinicia la numeración cuando no quedan productos en la tabla.
    with sqlite3.connect('inventario.db') as conn:
        cur = conn.cursor()
        cur.execute('''SELECT COUNT(*) FROM Productos;''')
        if cur.fetchone()[0] != 0:
            raise ValueError("Elimina definitivamente todos los productos antes de reiniciar los IDs")

        cur.execute('''DELETE FROM sqlite_sequence WHERE name = 'Productos';''')
        conn.commit()


def ActualizarProducto(id_producto, nuevo_id_producto, nombre, cantidad, precio, costo, tipo_unidad):
    #Actualiza los datos editables de un producto activo.
    if not isinstance(id_producto, int) or isinstance(id_producto, bool) or id_producto <= 0:
        raise ValueError("El ID del producto es inválido")
    if not isinstance(nuevo_id_producto, int) or isinstance(nuevo_id_producto, bool) or nuevo_id_producto <= 0:
        raise ValueError("El nuevo ID debe ser un número entero positivo")

    if not isinstance(nombre, str) or not nombre.strip():
        raise ValueError("El nombre es obligatorio")

    cantidad_val = _validar_numero(cantidad, "La cantidad")
    precio_val = _validar_numero(precio, "El precio")
    costo_val = _validar_numero(costo, "El costo")

    if cantidad_val < 0:
        raise ValueError("La cantidad no puede ser negativa")

    if precio_val < 0 or costo_val < 0:
        raise ValueError("El precio y el costo no pueden ser negativos")

    if not isinstance(tipo_unidad, str) or not tipo_unidad.strip():
        raise ValueError("El tipo de unidad es obligatorio")

    with sqlite3.connect('inventario.db') as conn:
        cur = conn.cursor()
        cur.execute(
            '''SELECT ID_Producto FROM Productos WHERE ID_Visible = ? AND IsDeleted = 0;''',
            (id_producto,)
        )
        producto = cur.fetchone()
        if producto is None:
            raise ValueError("El producto no existe o ya fue eliminado")
        id_producto_real = producto[0]
        if nuevo_id_producto != id_producto:
            cur.execute('''SELECT ID_Producto FROM Productos WHERE ID_Visible = ?;''', (nuevo_id_producto,))
            if cur.fetchone() is not None:
                raise ValueError("El nuevo ID ya está asignado a otro producto")
        cur.execute(
            '''
            UPDATE Productos
            SET ID_Visible = ?, Nombre = ?, Cantidad = ?, Precio = ?, Costo = ?, Tipo_unidad = ?
            WHERE ID_Producto = ? AND IsDeleted = 0;
            ''',
            (nuevo_id_producto, nombre.strip(), cantidad_val, precio_val, costo_val, tipo_unidad.strip(), id_producto_real)
        )
        if cur.rowcount == 0:
            raise ValueError("El producto no existe o ya fue eliminado")
        conn.commit()


def EliminarProducto(id_producto):
    #Marca un producto como eliminado sin borrarlo físicamente de la base de datos.
    if not isinstance(id_producto, int) or isinstance(id_producto, bool) or id_producto <= 0:
        raise ValueError("El ID del producto es inválido")

    with sqlite3.connect('inventario.db') as conn:
        cur = conn.cursor()
        cur.execute('''SELECT ID_Producto FROM Productos WHERE ID_Visible = ? AND IsDeleted = 0;''', (id_producto,))
        if cur.fetchone() is None:
            raise ValueError("El producto no existe o ya fue eliminado")

        cur.execute('''UPDATE Productos SET IsDeleted = 1 WHERE ID_Visible = ?;''', (id_producto,))
        conn.commit()


def RegistrarMovimiento(id_producto, tipo_operacion, cantidad_operacion):
    #Registra una compra o venta y actualiza el stock del producto.
    if not isinstance(id_producto, int) or isinstance(id_producto, bool) or id_producto <= 0:
        raise ValueError("El ID del producto es inválido")

    if not isinstance(tipo_operacion, str):
        raise ValueError("El tipo de operación es inválido")

    # Normalizamos la operación para aceptar entradas como 'Venta', ' venta ' o 'VENTA'.
    tipo_operacion = tipo_operacion.strip().lower()
    if tipo_operacion not in ('venta', 'compra'):
        raise ValueError("Tipo de operación inválido")

    cantidad_operacion_val = _validar_numero(cantidad_operacion, "La cantidad")
    if cantidad_operacion_val <= 0:
        raise ValueError("La cantidad debe ser mayor que cero")

    with sqlite3.connect('inventario.db') as conn:
        cur = conn.cursor()

        # BEGIN IMMEDIATE bloquea la base de datos para esta transacción.
        # Esto ayuda a evitar inconsistencias si dos operaciones se ejecutan a la vez.
        conn.execute('BEGIN IMMEDIATE')
        cur.execute('''SELECT ID_Producto, Precio, Costo, Cantidad FROM Productos
                   WHERE ID_Visible = ? AND IsDeleted = 0;''', (id_producto,))
        resultado = cur.fetchone()

        if resultado is None:
            raise ValueError("No se encontró el producto")

        id_producto_real, precio, costo, cantidad_actual = resultado

        if tipo_operacion == 'venta':
            if cantidad_operacion_val > cantidad_actual:
                raise ValueError("No hay suficiente stock")
            cambio_stock = -cantidad_operacion_val
            monto_operacion = precio * cantidad_operacion_val
        else:
            cambio_stock = cantidad_operacion_val
            monto_operacion = costo * cantidad_operacion_val

        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            # Actualiza el stock y guarda el movimiento de historial en la misma transacción.
            cur.execute(
                '''UPDATE Productos SET Cantidad = Cantidad + ? WHERE ID_Producto = ? AND IsDeleted = 0;''',
                (cambio_stock, id_producto_real)
            )
            cur.execute(
                '''INSERT INTO Historial (ID_Producto, Fecha, Tipo_operacion, Cantidad_involucrada, Monto_operacion)
                VALUES (?, ?, ?, ?, ?);''',
                (id_producto_real, fecha, tipo_operacion, cantidad_operacion_val, monto_operacion)
            )
            conn.commit()
        except sqlite3.Error:
            conn.rollback()
            raise ValueError("No se pudo guardar el movimiento. Inténtalo de nuevo.")


def CrearInforme(fecha_inicio, fecha_fin):
    #Devuelve todos los registros dentro de un rango de fechas.
    inicio = ConvertirFecha(fecha_inicio, "La fecha de inicio")
    fin = ConvertirFecha(fecha_fin, "La fecha de fin")

    if inicio > fin:
        raise ValueError("La fecha de inicio no puede ser mayor que la fecha final")

    inicio_texto = inicio.strftime("%Y-%m-%d 00:00:00")
    fin_texto = fin.strftime("%Y-%m-%d 23:59:59")

    with sqlite3.connect('inventario.db') as conn:
        cur = conn.cursor()
        cur.execute('''SELECT * FROM Historial WHERE Fecha BETWEEN ? AND ?;''', (inicio_texto, fin_texto))
        return cur.fetchall()


def ConsultarStockInsuficiente(cantidad_minima):
    #Muestra los productos cuyo stock es menor o igual a una cantidad dada.
    cantidad_minima_val = _validar_numero(cantidad_minima, "La cantidad mínima")
    if cantidad_minima_val < 0:
        raise ValueError("La cantidad mínima no puede ser negativa")

    with sqlite3.connect('inventario.db') as conn:
        cur = conn.cursor()
        cur.execute('''SELECT * FROM Productos WHERE Cantidad <= ? AND IsDeleted = 0;''', (cantidad_minima_val,))
        return cur.fetchall()


def ExportarInformeExcel(fecha_inicio, fecha_fin, nombre_archivo):
    #Exporta el informe de registros a un archivo Excel.
    registros = CrearInforme(fecha_inicio, fecha_fin)
    if not registros:
        raise ValueError("No hay registros en el rango de fechas especificado")

    df = pd.DataFrame(registros, columns=['ID_Operacion', 'ID_Producto', 'Fecha', 'Tipo_operacion', 'Cantidad_involucrada', 'Monto_operacion'])
    df.to_excel(nombre_archivo, index=False)

# Se ejecuta al importar el archivo para asegurar que la base de datos exista.
inicializar_db()


