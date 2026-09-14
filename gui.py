import customtkinter as ctk
import main
import calendar
import datetime
from tkinter import ttk, messagebox

class SistemaInventarioGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la raíz
        self.title("Sistema de Gestión de Inventario")
        self.geometry("1000x600")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Configuración del grid principal (2 columnas, 1 fila)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Panel lateral (Sidebar para Menús)
        self.frame_menu = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.frame_menu.grid(row=0, column=0, sticky="nsew")
        self.frame_menu.grid_rowconfigure(5, weight=1)

        self.label_titulo = ctk.CTkLabel(self.frame_menu, text="MENÚ PRINCIPAL", font=ctk.CTkFont(size=18, weight="bold"))
        self.label_titulo.grid(row=0, column=0, padx=20, pady=(20, 20))

        self.btn_inventario = ctk.CTkButton(self.frame_menu, text="Consultar Inventario", command=self.mostrar_inventario)
        self.btn_inventario.grid(row=1, column=0, padx=20, pady=10)

        self.btn_movimientos = ctk.CTkButton(self.frame_menu, text="Registrar Movimiento", command=self.mostrar_movimientos)
        self.btn_movimientos.grid(row=2, column=0, padx=20, pady=10)

        self.btn_informes = ctk.CTkButton(self.frame_menu, text="Generar Informes", command=self.mostrar_informes)
        self.btn_informes.grid(row=3, column=0, padx=20, pady=10)

        self.btn_configuracion = ctk.CTkButton(self.frame_menu, text="Configuración", command=self.mostrar_configuracion)
        self.btn_configuracion.grid(row=4, column=0, padx=20, pady=10)

        # Contenedor principal de datos (Donde operará cada módulo)
        self.frame_principal = ctk.CTkFrame(self, corner_radius=10)
        self.frame_principal.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.label_bienvenida = ctk.CTkLabel(self.frame_principal, text="Seleccione una opción del menú lateral", font=ctk.CTkFont(size=24))
        self.label_bienvenida.pack(expand=True)

        self.umbral_stock = 5.0
        self.mostrar_inventario()

    def limpiar_frame_principal(self):
        # Destruye los widgets actuales para limpiar la pantalla antes de cargar el nuevo módulo
        for widget in self.frame_principal.winfo_children():
            widget.destroy()

    def leer_numero(self, valor, nombre):
        texto = valor.strip().replace(",", ".")
        if not texto:
            raise ValueError(f"Escribe {nombre}.")
        try:
            return float(texto)
        except ValueError:
            raise ValueError(f"{nombre.capitalize()} debe ser un número válido.")

    def leer_entero(self, valor, nombre):
        texto = valor.strip()
        if not texto:
            raise ValueError(f"Escribe {nombre}.")
        try:
            return int(texto)
        except ValueError:
            raise ValueError(f"{nombre.capitalize()} debe ser un número entero.")

    def mostrar_inventario(self):
        self.limpiar_frame_principal()
        
        # Título del módulo
        ctk.CTkLabel(self.frame_principal, text="Módulo: Consultas de Inventario", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        self.entry_busqueda_inventario = ctk.CTkEntry(
            self.frame_principal,
            placeholder_text="Buscar por ID o nombre...",
            width=320
        )
        self.entry_busqueda_inventario.pack(anchor="w", padx=20, pady=(0, 5))
        self.entry_busqueda_inventario.bind("<KeyRelease>", self.filtrar_inventario)

        frame_formulario = ctk.CTkFrame(self.frame_principal)
        frame_formulario.pack(fill="x", padx=20, pady=(0, 10))
        for columna in range(4):
            frame_formulario.grid_columnconfigure(columna, weight=1)

        ctk.CTkLabel(
            frame_formulario,
            text="Registrar Nuevo Producto",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=0, columnspan=4, pady=(10, 5))

        self.entry_id_visible = ctk.CTkEntry(
            frame_formulario,
            placeholder_text="ID (obligatorio)",
            width=200
        )
        self.entry_id_visible.grid(row=1, column=0, padx=10, pady=10)

        self.entry_nombre = ctk.CTkEntry(
            frame_formulario,
            placeholder_text="Nombre del Producto",
            width=200
        )
        self.entry_nombre.grid(row=1, column=1, padx=10, pady=10)

        self.entry_cantidad = ctk.CTkEntry(
            frame_formulario,
            placeholder_text="Cantidad Inicial",
            width=200
        )
        self.entry_cantidad.grid(row=1, column=2, padx=10, pady=10)

        self.entry_precio = ctk.CTkEntry(
            frame_formulario,
            placeholder_text="Precio de Venta",
            width=200
        )
        self.entry_precio.grid(row=1, column=3, padx=10, pady=10)

        self.entry_costo = ctk.CTkEntry(
            frame_formulario,
            placeholder_text="Costo de Compra",
            width=200
        )
        self.entry_costo.grid(row=2, column=0, padx=10, pady=10)

        self.entry_unidad = ctk.CTkComboBox(
            frame_formulario,
            values=["pz", "kg", "g", "l", "ml", "m", "cm"],
            width=200
        )
        self.entry_unidad.set("")
        self.entry_unidad.grid(row=2, column=1, padx=10, pady=10)

        ctk.CTkButton(
            frame_formulario,
            text="Guardar Producto",
            command=self.ejecutar_crear_producto,
            fg_color="green"
        ).grid(row=2, column=2, padx=10, pady=10, sticky="ew")

        ctk.CTkButton(
            frame_formulario,
            text="Eliminar Seleccionado",
            command=self.ejecutar_eliminar_producto,
            fg_color="#b3261e"
        ).grid(row=2, column=3, padx=10, pady=10, sticky="ew")

        self.label_mensaje = ctk.CTkLabel(frame_formulario, text="", text_color="red")
        self.label_mensaje.grid(row=3, column=0, columnspan=4, pady=5)
        
        # Contenedor para la tabla
        frame_tabla = ctk.CTkFrame(self.frame_principal)
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Configuración de estilo estricto para homologar ttk con CustomTkinter oscuro
        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure("Treeview", 
        background="white", 
        foreground="black", 
        fieldbackground="white", 
        borderwidth=0,
        font=("Arial", 12),
        rowheight=30)
        estilo.configure("Treeview.Heading", 
        background="#1f538d", 
        foreground="white", 
        font=("Arial", 12, "bold"))
        estilo.map("Treeview", background=[("selected", "#bcd7f5")], foreground=[("selected", "black")])
        
        # Definición de columnas excluyendo IsDeleted
        columnas = ("ID", "Nombre", "Cantidad", "Precio", "Costo", "Unidad", "Estado")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=15)
        self.tabla.tag_configure("stock_bajo", foreground="#c62828")
        
        anchos = {"ID": 50, "Nombre": 220, "Cantidad": 100, "Precio": 100, "Costo": 100, "Unidad": 100, "Estado": 120}
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=anchos[col], anchor="center")
            
        # Implementación de barra de desplazamiento vertical
        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.tabla.pack(side="left", fill="both", expand=True)
        # Invocación a la base de datos
        self.cargar_datos_inventario()
        
    def ejecutar_crear_producto(self):
        nombre = self.entry_nombre.get()
        unidad = self.entry_unidad.get()

        import main
        try:
            if not unidad.strip():
                raise ValueError("La unidad de medida es obligatoria")

            cantidad = self.leer_numero(self.entry_cantidad.get(), "la cantidad")
            precio = self.leer_numero(self.entry_precio.get(), "el precio")
            costo = self.leer_numero(self.entry_costo.get(), "el costo")
            id_visible = self.leer_entero(self.entry_id_visible.get(), "el ID")

            # El backend se encargará de las validaciones matemáticas estandarizadas
            main.CrearProducto(id_visible, nombre, cantidad, precio, costo, unidad)
            
            # Notificar éxito, actualizar la tabla y purgar los campos
            self.label_mensaje.configure(text="Producto registrado con éxito", text_color="green")
            self.cargar_datos_inventario()
            
            self.entry_nombre.delete(0, 'end')
            self.entry_id_visible.delete(0, 'end')
            self.entry_cantidad.delete(0, 'end')
            self.entry_precio.delete(0, 'end')
            self.entry_costo.delete(0, 'end')
            self.entry_unidad.set("")
        except ValueError as error_backend:
            # Interceptar y desplegar el error generado por las reglas de negocio del backend
            self.label_mensaje.configure(text=str(error_backend), text_color="red")

    def ejecutar_eliminar_producto(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            self.label_mensaje.configure(text="Selecciona un producto para eliminar", text_color="red")
            return

        valores = self.tabla.item(seleccion[0], "values")
        id_producto = int(valores[0])
        nombre_producto = valores[1]

        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Deseas eliminar el producto '{nombre_producto}'?"
        )
        if not confirmar:
            return

        try:
            main.EliminarProducto(id_producto)
            self.label_mensaje.configure(text="Producto eliminado correctamente", text_color="green")
            self.cargar_datos_inventario()
        except ValueError as error_backend:
            self.label_mensaje.configure(text=str(error_backend), text_color="red")

    def cargar_datos_inventario(self):
        # Purga de datos residuales en la vista
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
            
        # Extracción e inserción de datos desde el backend
        import main  # Asegúrese de que el nombre coincida con su archivo backend
        productos = main.ConsultarInventario()
        texto_busqueda = self.entry_busqueda_inventario.get().strip().lower()
        stock_maximo = max((producto[2] for producto in productos), default=0)
        limite_alerta = stock_maximo * self.umbral_stock / 100
        
        for prod in productos:
            if texto_busqueda and (
                texto_busqueda not in str(prod[0]).lower()
                and texto_busqueda not in prod[1].lower()
            ):
                continue
            # prod contiene (ID_Producto, Nombre, Cantidad, Precio, Costo, Tipo_unidad, IsDeleted)
            # Se omite el índice 6 (IsDeleted) para la visualización del usuario
            stock_bajo = stock_maximo > 0 and prod[2] <= limite_alerta
            estado = "⚠ Bajo" if stock_bajo else ""
            valores = (prod[0], prod[1], prod[2], f"${prod[3]:.2f}", f"${prod[4]:.2f}", prod[5], estado)
            etiquetas = ("stock_bajo",) if stock_bajo else ()
            self.tabla.insert("", "end", values=valores, tags=etiquetas)

    def filtrar_inventario(self, _evento=None):
        self.cargar_datos_inventario()

    def mostrar_configuracion(self):
        self.limpiar_frame_principal()
        ctk.CTkLabel(
            self.frame_principal,
            text="Módulo: Configuración",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=15)

        frame_umbral = ctk.CTkFrame(self.frame_principal)
        frame_umbral.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(frame_umbral, text="Porcentaje mínimo para alertar:").grid(
            row=0, column=0, padx=10, pady=15
        )
        self.entry_umbral_stock = ctk.CTkEntry(frame_umbral, width=180)
        self.entry_umbral_stock.insert(0, str(self.umbral_stock))
        self.entry_umbral_stock.configure(placeholder_text="Porcentaje (0 a 100)")
        self.entry_umbral_stock.grid(row=0, column=1, padx=10, pady=15)
        ctk.CTkButton(
            frame_umbral,
            text="Guardar umbral",
            command=self.ejecutar_actualizar_umbral,
            width=160
        ).grid(row=0, column=2, padx=10, pady=15)

        frame_edicion = ctk.CTkFrame(self.frame_principal)
        frame_edicion.pack(fill="x", padx=20, pady=10)
        for columna in range(4):
            frame_edicion.grid_columnconfigure(columna, weight=1)
        ctk.CTkLabel(
            frame_edicion,
            text="Editar producto seleccionado",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=0, columnspan=4, pady=(10, 5))

        self.tabla_configuracion = ttk.Treeview(
            self.frame_principal,
            columns=("ID", "Nombre", "Cantidad", "Precio", "Costo", "Unidad", "Estado"),
            show="headings",
            height=7
        )
        self.tabla_configuracion.tag_configure("eliminado", foreground="#777777")
        for columna in ("ID", "Nombre", "Cantidad", "Precio", "Costo", "Unidad", "Estado"):
            self.tabla_configuracion.heading(columna, text=columna)
            self.tabla_configuracion.column(columna, width=125, anchor="center")
        self.tabla_configuracion.pack(fill="both", expand=True, padx=20, pady=10)
        self.tabla_configuracion.bind("<<TreeviewSelect>>", self.cargar_producto_configuracion)

        frame_acciones = ctk.CTkFrame(self.frame_principal)
        frame_acciones.pack(fill="x", padx=20, pady=(0, 10))
        ctk.CTkButton(
            frame_acciones,
            text="Restaurar seleccionado",
            command=self.ejecutar_restaurar_producto,
            width=200
        ).pack(side="left", padx=10, pady=8)
        ctk.CTkButton(
            frame_acciones,
            text="Eliminar definitivamente",
            command=self.ejecutar_eliminar_definitivo,
            fg_color="#8b0000",
            hover_color="#5c0000",
            width=220
        ).pack(side="left", padx=10, pady=8)
        self.entry_config_id = ctk.CTkEntry(frame_edicion, placeholder_text="ID", width=100)
        self.entry_config_id.grid(row=1, column=0, padx=8, pady=10)
        self.entry_config_nombre = ctk.CTkEntry(frame_edicion, placeholder_text="Nombre", width=180)
        self.entry_config_nombre.grid(row=1, column=1, padx=8, pady=10)
        self.entry_config_cantidad = ctk.CTkEntry(frame_edicion, placeholder_text="Cantidad", width=130)
        self.entry_config_cantidad.grid(row=1, column=2, padx=8, pady=10)
        self.entry_config_precio = ctk.CTkEntry(frame_edicion, placeholder_text="Precio", width=130)
        self.entry_config_precio.grid(row=1, column=3, padx=8, pady=10)
        self.entry_config_costo = ctk.CTkEntry(frame_edicion, placeholder_text="Costo", width=130)
        self.entry_config_costo.grid(row=2, column=0, padx=8, pady=10)
        self.combo_config_unidad = ctk.CTkComboBox(
            frame_edicion,
            values=["pz", "kg", "g", "l", "ml", "m", "cm"],
            width=130
        )
        self.combo_config_unidad.grid(row=2, column=1, padx=8, pady=10)
        ctk.CTkButton(
            frame_edicion,
            text="Guardar cambios",
            command=self.ejecutar_editar_producto,
            fg_color="green",
            width=160
        ).grid(row=2, column=2, columnspan=2, padx=8, pady=10, sticky="ew")

        self.label_mensaje_configuracion = ctk.CTkLabel(frame_edicion, text="", text_color="red")
        self.label_mensaje_configuracion.grid(row=3, column=0, columnspan=4, pady=5)
        self.cargar_datos_configuracion()

    def ejecutar_actualizar_umbral(self):
        try:
            umbral = self.leer_numero(self.entry_umbral_stock.get(), "el porcentaje mínimo")
            if umbral < 0 or umbral > 100:
                raise ValueError("El porcentaje debe estar entre 0 y 100")
            self.umbral_stock = umbral
            self.label_mensaje_configuracion.configure(
                text="Porcentaje de alerta actualizado", text_color="green"
            )
            self.cargar_datos_configuracion()
            if hasattr(self, "tabla") and self.tabla.winfo_exists():
                self.cargar_datos_inventario()
        except ValueError as error_backend:
            self.label_mensaje_configuracion.configure(text=str(error_backend), text_color="red")

    def cargar_datos_configuracion(self):
        for fila in self.tabla_configuracion.get_children():
            self.tabla_configuracion.delete(fila)
        for producto in main.ConsultarTodosLosProductos():
            eliminado = producto[7] == 1
            estado = "Eliminado" if eliminado else "Activo"
            valores = producto[1:7] + (estado,)
            etiquetas = ("eliminado",) if eliminado else ()
            self.tabla_configuracion.insert(
                "", "end", iid=str(producto[0]), values=valores, tags=etiquetas
            )

    def cargar_producto_configuracion(self, _evento=None):
        seleccion = self.tabla_configuracion.selection()
        if not seleccion:
            return
        valores = self.tabla_configuracion.item(seleccion[0], "values")
        campos = (
            (self.entry_config_id, valores[0]),
            (self.entry_config_nombre, valores[1]),
            (self.entry_config_cantidad, valores[2]),
            (self.entry_config_precio, valores[3]),
            (self.entry_config_costo, valores[4]),
        )
        for campo, valor in campos:
            campo.delete(0, "end")
            campo.insert(0, str(valor).replace("$", ""))
        self.combo_config_unidad.set(valores[5])

    def ejecutar_editar_producto(self):
        seleccion = self.tabla_configuracion.selection()
        if not seleccion:
            self.label_mensaje_configuracion.configure(
                text="Selecciona un producto para editar", text_color="red"
            )
            return
        try:
            valores = self.tabla_configuracion.item(seleccion[0], "values")
            main.ActualizarProducto(
                self.leer_entero(valores[0], "el ID actual"),
                self.leer_entero(self.entry_config_id.get(), "el nuevo ID"),
                self.entry_config_nombre.get(),
                self.leer_numero(self.entry_config_cantidad.get(), "la cantidad"),
                self.leer_numero(self.entry_config_precio.get(), "el precio"),
                self.leer_numero(self.entry_config_costo.get(), "el costo"),
                self.combo_config_unidad.get()
            )
            self.label_mensaje_configuracion.configure(
                text="Producto actualizado correctamente", text_color="green"
            )
            self.cargar_datos_configuracion()
        except ValueError as error_backend:
            self.label_mensaje_configuracion.configure(text=str(error_backend), text_color="red")

    def ejecutar_restaurar_producto(self):
        seleccion = self.tabla_configuracion.selection()
        if not seleccion:
            self.label_mensaje_configuracion.configure(
                text="Selecciona un producto para restaurar", text_color="red"
            )
            return
        valores = self.tabla_configuracion.item(seleccion[0], "values")
        if valores[6] != "Eliminado":
            self.label_mensaje_configuracion.configure(
                text="El producto seleccionado ya está activo", text_color="red"
            )
            return
        if not messagebox.askyesno(
            "Confirmar restauración",
            f"¿Deseas restaurar el producto '{valores[1]}'?"
        ):
            return
        try:
            main.RestaurarProducto(self.leer_entero(valores[0], "el ID"))
            self.label_mensaje_configuracion.configure(
                text="Producto restaurado correctamente", text_color="green"
            )
            self.cargar_datos_configuracion()
        except ValueError as error_backend:
            self.label_mensaje_configuracion.configure(text=str(error_backend), text_color="red")

    def ejecutar_eliminar_definitivo(self):
        seleccion = self.tabla_configuracion.selection()
        if not seleccion:
            self.label_mensaje_configuracion.configure(
                text="Selecciona un producto para eliminar", text_color="red"
            )
            return
        valores = self.tabla_configuracion.item(seleccion[0], "values")
        if not messagebox.askyesno(
            "Eliminar definitivamente",
            f"Se eliminará '{valores[1]}' y su historial. Esta acción no se puede deshacer. ¿Continuar?"
        ):
            return
        try:
            main.EliminarProductoDefinitivamente(
                self.leer_entero(valores[0], "el ID")
            )
            self.label_mensaje_configuracion.configure(
                text="Producto eliminado definitivamente", text_color="green"
            )
            self.cargar_datos_configuracion()
        except ValueError as error_backend:
            self.label_mensaje_configuracion.configure(text=str(error_backend), text_color="red")

    def ejecutar_reiniciar_ids(self):
        if not messagebox.askyesno(
            "Reiniciar IDs",
            "Esta acción solo se puede hacer con el inventario vacío. ¿Deseas continuar?"
        ):
            return
        try:
            main.ReiniciarIdsProductos()
            self.label_mensaje_configuracion.configure(
                text="Numeración de productos reiniciada", text_color="green"
            )
        except ValueError as error_backend:
            self.label_mensaje_configuracion.configure(text=str(error_backend), text_color="red")

    def mostrar_movimientos(self):
        self.limpiar_frame_principal()
        ctk.CTkLabel(
            self.frame_principal,
            text="Módulo: Registro de Compras y Ventas",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)

        frame_formulario = ctk.CTkFrame(self.frame_principal)
        frame_formulario.pack(fill="x", padx=20, pady=6)
        for columna in range(5):
            frame_formulario.grid_columnconfigure(columna, weight=1)

        ctk.CTkLabel(
            frame_formulario,
            text="🔍",
            font=ctk.CTkFont(size=18)
        ).grid(row=0, column=0, padx=(8, 0), pady=8)

        self.entry_busqueda_producto = ctk.CTkEntry(
            frame_formulario,
            placeholder_text="Buscar producto por ID o nombre",
            width=190
        )
        self.entry_busqueda_producto.grid(row=0, column=1, padx=(4, 6), pady=8, sticky="ew")
        self.entry_busqueda_producto.bind("<KeyRelease>", self.filtrar_productos_movimiento)

        self.frame_sugerencias_producto = ctk.CTkFrame(
            frame_formulario,
            fg_color="transparent",
            height=1
        )
        self.frame_sugerencias_producto.grid(row=1, column=1, columnspan=4, padx=(4, 6), sticky="ew")

        self.combo_tipo_movimiento = ctk.CTkComboBox(
            frame_formulario,
            values=["compra", "venta"],
            width=160
        )
        self.combo_tipo_movimiento.set("compra")
        self.combo_tipo_movimiento.grid(row=0, column=2, padx=6, pady=8)

        self.entry_cantidad_movimiento = ctk.CTkEntry(frame_formulario, placeholder_text="Cantidad", width=150)
        self.entry_cantidad_movimiento.grid(row=0, column=3, padx=6, pady=8)

        ctk.CTkButton(
            frame_formulario,
            text="Registrar Movimiento",
            command=self.ejecutar_registrar_movimiento,
            fg_color="#1f538d"
        ).grid(row=0, column=4, padx=(6, 8), pady=8)

        self.label_mensaje_movimiento = ctk.CTkLabel(frame_formulario, text="", text_color="red")
        self.label_mensaje_movimiento.grid(row=2, column=0, columnspan=5, pady=3)

        frame_historial = ctk.CTkFrame(self.frame_principal)
        frame_historial.pack(fill="both", expand=True, padx=20, pady=10)
        ctk.CTkLabel(
            frame_historial,
            text="Historial de movimientos",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        columnas = ("ID", "Producto", "Fecha", "Tipo", "Cantidad", "Monto")
        self.tabla_historial = ttk.Treeview(
            frame_historial,
            columns=columnas,
            show="headings"
        )
        anchos = {
            "ID": 90,
            "Producto": 180,
            "Fecha": 155,
            "Tipo": 90,
            "Cantidad": 100,
            "Monto": 110
        }
        for columna in columnas:
            self.tabla_historial.heading(columna, text=columna)
            self.tabla_historial.column(columna, width=anchos[columna], anchor="center")
        self.tabla_historial.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=(0, 10))

        scrollbar = ttk.Scrollbar(
            frame_historial,
            orient="vertical",
            command=self.tabla_historial.yview
        )
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=(0, 10))
        self.tabla_historial.configure(yscrollcommand=scrollbar.set)
        self.cargar_productos_movimiento()
        self.cargar_historial()

    def ejecutar_registrar_movimiento(self):
        try:
            producto_seleccionado = self.entry_busqueda_producto.get()
            if " - " not in producto_seleccionado:
                raise ValueError("No hay un producto disponible para operar")
            id_producto = int(producto_seleccionado.split(" - ", 1)[0])
            cantidad = self.leer_numero(self.entry_cantidad_movimiento.get(), "la cantidad")
            tipo_operacion = self.combo_tipo_movimiento.get()
            main.RegistrarMovimiento(id_producto, tipo_operacion, cantidad)
            self.label_mensaje_movimiento.configure(
                text="Movimiento registrado correctamente",
                text_color="green"
            )
            self.entry_cantidad_movimiento.delete(0, "end")
            self.cargar_productos_movimiento()
            self.cargar_historial()
        except (ValueError, TypeError) as error_backend:
            self.label_mensaje_movimiento.configure(text=str(error_backend), text_color="red")

    def cargar_productos_movimiento(self):
        self.productos_movimiento = main.ConsultarInventario()
        self.filtrar_productos_movimiento()

    def filtrar_productos_movimiento(self, _evento=None):
        texto = self.entry_busqueda_producto.get().strip().lower()
        for widget in self.frame_sugerencias_producto.winfo_children():
            widget.destroy()
        if not texto:
            return

        opciones = [
            f"{producto[0]} - {producto[1]}"
            for producto in self.productos_movimiento
            if texto in str(producto[0]).lower() or texto in producto[1].lower()
        ]
        for opcion in opciones[:5]:
            ctk.CTkButton(
                self.frame_sugerencias_producto,
                text=opcion,
                anchor="w",
                height=28,
                fg_color="#3a3a3a",
                hover_color="#1f538d",
                command=lambda opcion=opcion: self.seleccionar_producto_movimiento(opcion)
            ).pack(fill="x", pady=1)

    def seleccionar_producto_movimiento(self, producto):
        self.entry_busqueda_producto.delete(0, "end")
        self.entry_busqueda_producto.insert(0, producto)
        for widget in self.frame_sugerencias_producto.winfo_children():
            widget.destroy()

    def cargar_historial(self):
        for fila in self.tabla_historial.get_children():
            self.tabla_historial.delete(fila)
        for movimiento in main.ConsultarHistorial():
            valores = (
                movimiento[1],
                movimiento[2] or "Producto eliminado",
                movimiento[3],
                movimiento[4].capitalize(),
                movimiento[5],
                f"${movimiento[6]:.2f}"
            )
            self.tabla_historial.insert("", "end", values=valores)

    def mostrar_informes(self):
        self.limpiar_frame_principal()
        ctk.CTkLabel(
            self.frame_principal,
            text="Módulo: Exportación de Informes",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=15)

        frame_formulario = ctk.CTkFrame(self.frame_principal)
        frame_formulario.pack(fill="x", padx=20, pady=10)
        for columna in range(5):
            frame_formulario.grid_columnconfigure(columna, weight=1)

        frame_fecha_inicio = ctk.CTkFrame(frame_formulario, fg_color="transparent")
        frame_fecha_inicio.grid(row=0, column=0, padx=10, pady=12)
        self.entry_fecha_inicio = ctk.CTkEntry(frame_fecha_inicio, width=150)
        self.entry_fecha_inicio.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.entry_fecha_inicio.configure(state="readonly")
        self.entry_fecha_inicio.pack(side="left")
        ctk.CTkButton(
            frame_fecha_inicio,
            text="▼",
            command=lambda: self.abrir_calendario(self.entry_fecha_inicio),
            width=35,
            height=28
        ).pack(side="left", padx=(4, 0))

        frame_fecha_fin = ctk.CTkFrame(frame_formulario, fg_color="transparent")
        frame_fecha_fin.grid(row=0, column=1, padx=10, pady=12)
        self.entry_fecha_fin = ctk.CTkEntry(frame_fecha_fin, width=150)
        self.entry_fecha_fin.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.entry_fecha_fin.configure(state="readonly")
        self.entry_fecha_fin.pack(side="left")
        ctk.CTkButton(
            frame_fecha_fin,
            text="▼",
            command=lambda: self.abrir_calendario(self.entry_fecha_fin),
            width=35,
            height=28
        ).pack(side="left", padx=(4, 0))

        ctk.CTkButton(
            frame_formulario,
            text="Consultar Informe",
            command=self.ejecutar_consultar_informe,
            width=180
        ).grid(row=0, column=2, padx=10, pady=12)

        self.entry_archivo_informe = ctk.CTkEntry(
            frame_formulario,
            placeholder_text="Nombre del archivo Excel",
            width=220
        )
        self.entry_archivo_informe.grid(row=1, column=0, padx=10, pady=12)
        self.entry_archivo_informe.insert(0, "informe_inventario.xlsx")

        ctk.CTkButton(
            frame_formulario,
            text="Exportar a Excel",
            command=self.ejecutar_exportar_informe,
            width=180,
            fg_color="green"
        ).grid(row=1, column=1, padx=10, pady=12)

        self.label_mensaje_informe = ctk.CTkLabel(frame_formulario, text="", text_color="red")
        self.label_mensaje_informe.grid(row=1, column=2, columnspan=2, padx=10, pady=12)

        frame_tabla = ctk.CTkFrame(self.frame_principal)
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

        columnas = ("ID", "Fecha", "Tipo", "Cantidad", "Monto")
        self.tabla_informe = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
        for columna in columnas:
            self.tabla_informe.heading(columna, text=columna)
            self.tabla_informe.column(columna, width=155, anchor="center")
        self.tabla_informe.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_informe.yview)
        scrollbar.pack(side="right", fill="y")
        self.tabla_informe.configure(yscrollcommand=scrollbar.set)

    def ejecutar_consultar_informe(self):
        try:
            registros = main.CrearInforme(
                self.entry_fecha_inicio.get(),
                self.entry_fecha_fin.get()
            )
            for fila in self.tabla_informe.get_children():
                self.tabla_informe.delete(fila)
            for registro in registros:
                self.tabla_informe.insert("", "end", values=registro[1:])
            self.label_mensaje_informe.configure(
                text=f"{len(registros)} movimiento(s) encontrado(s)",
                text_color="green"
            )
        except ValueError as error_backend:
            self.label_mensaje_informe.configure(text=str(error_backend), text_color="red")

    def ejecutar_exportar_informe(self):
        try:
            nombre_archivo = self.entry_archivo_informe.get().strip()
            main.ExportarInformeExcel(
                self.entry_fecha_inicio.get(),
                self.entry_fecha_fin.get(),
                nombre_archivo
            )
            self.label_mensaje_informe.configure(
                text=f"Informe exportado: {nombre_archivo}",
                text_color="green"
            )
        except (ValueError, OSError) as error_backend:
            self.label_mensaje_informe.configure(text=str(error_backend), text_color="red")

    def abrir_calendario(self, campo_fecha):
        self.campo_fecha_calendario = campo_fecha
        hoy = datetime.date.today()
        self.mes_calendario = getattr(self, "mes_calendario", hoy.replace(day=1))
        if hasattr(self, "ventana_calendario") and self.ventana_calendario.winfo_exists():
            self.ventana_calendario.destroy()

        self.ventana_calendario = ctk.CTkToplevel(self)
        self.ventana_calendario.title("Seleccionar fecha")
        self.ventana_calendario.geometry("300x300")
        self.ventana_calendario.resizable(False, False)
        self.ventana_calendario.grab_set()
        self.actualizar_calendario()

    def actualizar_calendario(self):
        for widget in self.ventana_calendario.winfo_children():
            widget.destroy()

        encabezado = ctk.CTkFrame(self.ventana_calendario)
        encabezado.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(
            encabezado,
            text="<",
            width=40,
            command=self.calendario_mes_anterior
        ).pack(side="left")
        ctk.CTkLabel(
            encabezado,
            text=self.mes_calendario.strftime("%B %Y").capitalize(),
            font=ctk.CTkFont(weight="bold")
        ).pack(side="left", expand=True)
        ctk.CTkButton(
            encabezado,
            text=">",
            width=40,
            command=self.calendario_mes_siguiente
        ).pack(side="right")

        calendario_frame = ctk.CTkFrame(self.ventana_calendario)
        calendario_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        for columna, dia in enumerate(("Lu", "Ma", "Mi", "Ju", "Vi", "Sa", "Do")):
            ctk.CTkLabel(calendario_frame, text=dia, width=35).grid(row=0, column=columna, padx=1, pady=3)

        for fila, semana in enumerate(calendar.monthcalendar(self.mes_calendario.year, self.mes_calendario.month), start=1):
            for columna, dia in enumerate(semana):
                if dia:
                    fecha = self.mes_calendario.replace(day=dia)
                    ctk.CTkButton(
                        calendario_frame,
                        text=str(dia),
                        width=35,
                        command=lambda fecha=fecha: self.seleccionar_fecha_calendario(fecha)
                    ).grid(row=fila, column=columna, padx=1, pady=1)

    def seleccionar_fecha_calendario(self, fecha):
        self.campo_fecha_calendario.configure(state="normal")
        self.campo_fecha_calendario.delete(0, "end")
        self.campo_fecha_calendario.insert(0, fecha.strftime("%Y-%m-%d"))
        self.campo_fecha_calendario.configure(state="readonly")
        self.ventana_calendario.destroy()

    def calendario_mes_anterior(self):
        if self.mes_calendario.month == 1:
            self.mes_calendario = self.mes_calendario.replace(
                year=self.mes_calendario.year - 1, month=12
            )
        else:
            self.mes_calendario = self.mes_calendario.replace(month=self.mes_calendario.month - 1)
        self.actualizar_calendario()

    def calendario_mes_siguiente(self):
        if self.mes_calendario.month == 12:
            self.mes_calendario = self.mes_calendario.replace(
                year=self.mes_calendario.year + 1, month=1
            )
        else:
            self.mes_calendario = self.mes_calendario.replace(month=self.mes_calendario.month + 1)
        self.actualizar_calendario()

if __name__ == "__main__":
    app = SistemaInventarioGUI()
    app.mainloop()