# Sistema de Gestión de Inventario y Punto de Control

Aplicación de escritorio completa desarrollada en **Python** para el control de inventarios, registro transaccional de compras/ventas y generación automatizada de reportes financieros en Excel. Diseñada bajo una arquitectura que separa la lógica de negocio y persistencia de datos (`main.py`) de la interfaz gráfica de usuario (`gui.py`).

---

## Características Principales

* **Gestión CRUD con Borrado Lógico (*Soft Delete*):** Registro, lectura, edición y baja lógica de productos mediante la bandera `IsDeleted`, permitiendo restaurar artículos dados de baja sin comprometer la integridad referencial del historial de operaciones.
* **Transacciones Atómicas y Seguras:** Uso de bloqueos inmediatos (`BEGIN IMMEDIATE`) y manejo de `rollback` en **SQLite** para evitar condiciones de carrera o inconsistencias en el stock durante el registro de ventas y compras.
* **Sistema de Alertas de Stock Crítico:** Cálculo dinámico del umbral porcentual configurable que resalta visualmente en la tabla (`⚠ Bajo`) aquellos productos que requieren reabastecimiento.
* **Búsqueda Predictiva y Autocompletado:** Filtrado en tiempo real (`<KeyRelease>`) tanto en el catálogo general como en el módulo de registro de movimientos por ID visible o nombre del artículo.
* **Auditoría y Exportación a Excel:** Módulo de consulta por rango de fechas mediante un calendario emergente interactivo propio, con capacidad de exportar el historial financiero directamente a archivos `.xlsx` usando **Pandas**.

---

## Tecnologías y Herramientas

* **Lenguaje:** Python 3.x
* **Interfaz Gráfica (GUI):** `CustomTkinter` (Modo Oscuro) y `tkinter.ttk` (`Treeview`)
* **Base de Datos:** `SQLite3` (Relacional, índices únicos y llaves foráneas)
* **Procesamiento de Datos y Reportes:** `Pandas`, `datetime`, `calendar`

---

## Estructura del Proyecto

```text
├── gui.py               # Interfaz gráfica modular (Vistas: Inventario, Movimientos, Informes, Configuración)
├── main.py              # Backend, validaciones de negocio, consultas SQL y exportación con Pandas
├── inventario.db        # Base de datos SQLite (se autogenera al iniciar el sistema)
└── README.md            # Documentación del proyecto
```

---

## Instalación y Ejecución

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Osii29/nombre-de-tu-repo-inventario.git
   cd nombre-de-tu-repo-inventario
   ```

2. **Instalar las dependencias necesarias:**
   *(Nota: `openpyxl` es requerido por Pandas para exportar archivos `.xlsx`)*
   ```bash
   pip install customtkinter pandas openpyxl
   ```

3. **Ejecutar la aplicación:**
   ```bash
   python gui.py
   ```

---

## Módulos del Sistema

1. **Consultar Inventario:** Alta de productos con validaciones numéricas estrictas, buscador instantáneo, visualización tabular e indicadores de alerta de stock.
2. **Registrar Movimiento:** Ingreso de operaciones de `compra` (incrementa stock y calcula costo) o `venta` (valida disponibilidad de inventario, descuenta stock y calcula ingreso).
3. **Generar Informes:** Selector de fechas interactivo para auditar flujos de efectivo en periodos específicos y exportarlos a hojas de cálculo de Excel.
4. **Configuración:** Ajuste del porcentaje mínimo de alerta, edición directa de productos, restauración de elementos en papelera y eliminación definitiva de registros.

---

## Autor

**Osiel Carapia Ruiz**  
*Ingeniería en Computación – UNAM (FES Aragón)*  
[LinkedIn](https://www.linkedin.com/in/osielcarapiaruiz) | [GitHub](https://github.com/Osii29)