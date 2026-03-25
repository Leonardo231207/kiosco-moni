# Sistema de Gestión de Kiosco Escolar

## Descripción del proyecto
App web local para gestión de stock y ventas de un kiosco dentro de un colegio primario/secundario.
Usuarios finales: personas sin conocimientos técnicos (tía y primo del desarrollador).
Prioridades: velocidad, simplicidad, estabilidad. Funciona 100% offline.

## Stack tecnológico
- **Backend:** Python + Flask
- **Base de datos:** SQLite (archivo local) + SQLAlchemy como ORM
- **Frontend:** HTML + CSS + JavaScript vanilla (sin frameworks)
- **Códigos de barras:** python-barcode + Pillow
- **PDFs:** ReportLab
- **Imágenes de productos:** Open Food Facts API (opcional, requiere internet)
- **Logging:** Python logging + RotatingFileHandler

## Cómo correr el proyecto

**Para el usuario final:** Hacer doble clic en `iniciar_kiosco.bat`. El script se encarga de todo automáticamente.

**Para desarrollo:**
```bash
# 1. Crear entorno virtual (solo la primera vez)
python -m venv venv

# 2. Activar entorno virtual
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

# 3. Instalar dependencias (solo la primera vez o cuando cambie requirements.txt)
pip install -r requirements.txt

# 4. Iniciar la app
python app.py
```
La app abre automáticamente en http://localhost:5000

## Estructura del proyecto
```
kiosco/
  app.py                  # Entry point Flask
  config.py               # Configuración (DB path, puerto, nivel de log)
  models.py               # Modelos SQLAlchemy
  routes/
    productos.py          # CRUD de productos
    stock.py              # Consulta y carga de stock
    modo_recreo.py        # Lógica del Modo Recreo
    codigos.py            # Generación e impresión de planilla de códigos
    recetas.py            # Gestión de materia prima y recetas
  templates/
    base.html             # Layout común con navegación
    productos/
    stock/
    modo_recreo/
    codigos/
    recetas/
  static/
    css/
    js/
    imagenes/             # Fotos de productos (NO va al repo)
    codigos_barras/       # Imágenes PNG de códigos generados (NO va al repo)
  logs/
    kiosco_errors.log     # Log de errores (NO va al repo)
  iniciar_kiosco.bat      # Script de inicio Windows
  requirements.txt
  CLAUDE.md               # Este archivo
```

## Modelo de base de datos

### productos
| Campo | Tipo | Notas |
|-------|------|-------|
| id | INTEGER PK | |
| nombre | TEXT | NOT NULL |
| codigo_barras | TEXT | UNIQUE, NOT NULL |
| codigo_tipo | TEXT | 'externo' o 'interno' |
| foto_path | TEXT | Nullable |
| precio_venta | REAL | NOT NULL |
| precio_costo | REAL | Calculado desde receta si aplica |
| activo | INTEGER | 1=activo, 0=baja (soft delete) |
| creado_en | TEXT | Timestamp |
| actualizado_en | TEXT | Timestamp |

### stock
| Campo | Tipo | Notas |
|-------|------|-------|
| id | INTEGER PK | |
| producto_id | INTEGER | FK -> productos.id |
| cantidad_actual | INTEGER | |
| actualizado_en | TEXT | Timestamp |

### movimientos_stock
| Campo | Tipo | Notas |
|-------|------|-------|
| id | INTEGER PK | |
| producto_id | INTEGER | FK -> productos.id |
| tipo | TEXT | 'venta', 'carga', 'ajuste', 'correccion' |
| cantidad | INTEGER | Positivo o negativo |
| origen | TEXT | 'modo_recreo', 'carga_manual', 'ajuste' |
| timestamp | TEXT | |
| notas | TEXT | Nullable |

### materia_prima
| Campo | Tipo | Notas |
|-------|------|-------|
| id | INTEGER PK | |
| nombre | TEXT | UNIQUE, NOT NULL |
| unidad | TEXT | 'kg', 'g', 'l', 'ml', 'unidad' |
| precio_por_unidad | REAL | NOT NULL |
| activo | INTEGER | 1=activo, 0=baja |
| actualizado_en | TEXT | Timestamp |

### recetas
| Campo | Tipo | Notas |
|-------|------|-------|
| id | INTEGER PK | |
| producto_id | INTEGER | FK -> productos.id |
| materia_prima_id | INTEGER | FK -> materia_prima.id |
| cantidad | REAL | Por unidad producida |
| notas | TEXT | Nullable |

## Módulos y estado de desarrollo

### [ ] 1. Base de datos y modelos (EMPEZAR AQUÍ)
Crear todos los modelos SQLAlchemy según el esquema de arriba.
Incluir función `init_db()` que cree las tablas si no existen.

### [ ] 2. Sistema de logging
Configurar antes que cualquier otra cosa.
Archivo: `logs/kiosco_errors.log`
Rotación: 1MB máximo, 3 backups.
Nivel configurable en config.py: DEBUG en desarrollo, ERROR en producción.

### [ ] 3. CRUD de productos
- Listado con foto miniatura, nombre, stock actual, precio
- Formulario de alta con todos los campos
- Edición de producto (todos los campos menos código externo)
- Soft delete (campo activo=0, nunca borrar físicamente)

### [ ] 4. Lógica de códigos de barras
- Código externo: validar unicidad al ingresar
- Código interno: generar EAN-13 con prefijo '2' + 11 dígitos + dígito de control
- Detectar colisión automáticamente y reasignar código interno si hay conflicto
- Mostrar aviso al usuario si se reasignó un código

### [ ] 5. Consulta y carga de stock
- Vista de todos los productos con indicador visual: verde (ok), amarillo (<5 unidades), rojo (0)
- Buscador por nombre o código
- Carga de stock en 3 pasos: seleccionar → ingresar cantidad → confirmar
- Registrar movimiento en movimientos_stock con origen 'carga_manual'

### [ ] 6. Modo Recreo (MÓDULO CRÍTICO)
- Pantalla fullscreen, fondo oscuro, texto grande
- Campo de captura siempre en foco (autofocus + re-focus después de cada escaneo)
- Al detectar código: descontar 1 del stock + registrar en movimientos_stock
- Mostrar nombre y foto del producto durante 2.5 segundos
- Si stock = 0: alerta sonora + mensaje "STOCK AGOTADO", NO descontar
- Si código no existe: mensaje "CÓDIGO NO RECONOCIDO", NO descontar
- Contador de ventas de la sesión
- Procesamiento < 200ms desde recepción del código
- Botón "SALIR" en esquina, no en el centro

### [ ] 7. Módulo de recetas y costos
- ABM de materia prima (nombre, unidad, precio por unidad)
- Definición de receta por producto: lista de ingredientes + cantidades
- Cálculo automático de costo al guardar receta o al actualizar precio de ingrediente
- Vista de rentabilidad: costo / precio venta / margen por unidad

### [ ] 8. Planilla de códigos de barras
- Listado de productos con código interno (tipo='interno')
- Generar PDF en grilla (2-3 columnas) con imagen del código y nombre
- Listo para imprimir

### [ ] 9. Búsqueda de imagen en Open Food Facts
- Al crear producto, botón "Buscar imagen en internet"
- Buscar por nombre o código de barras en Open Food Facts API
- Si encuentra: mostrar preview y preguntar "¿Usar esta foto?"
- Si no hay internet o no encuentra: ocultar el botón automáticamente
- Funcionalidad secundaria, implementar al final

### [ ] 10. Script de inicio (.bat)
```bat
@echo off
cd /d "%~dp0"
call venv\Scripts\activate
start "" http://localhost:5000
python app.py
```

## Decisiones de diseño importantes
- **Sin usuarios ni login:** sistema monousuario, sin pantalla de acceso
- **Soft delete siempre:** nunca borrar productos de la BD, usar activo=0
- **Transacciones atómicas:** toda operación de stock debe ser una transacción SQLAlchemy
- **EAN-13 prefijo '2':** estándar GS1 reservado para uso interno, los lectores lo reconocen
- **SQLite local:** no requiere servidor, fácil backup (copiar el .db), migrable a PostgreSQL sin cambiar lógica
- **Sin frameworks JS:** vanilla JS para máxima velocidad y sin dependencias
- **Errores amigables:** nunca mostrar stack traces al usuario, capturar todo con el logger

## Mensajes de error para el usuario (usar estos exactos)
- Código ya existe: `"Este código ya está registrado para el producto '[NOMBRE]'"`
- Código no reconocido: `"Código no reconocido. Verificar que el producto esté cargado."`
- Stock agotado: `"ATENCIÓN: [NOMBRE] no tiene stock disponible."`
- Error al guardar: `"No se pudo guardar. Intentalo de nuevo o avisale a Leo."`
- Campo vacío: `"Completá el campo '[NOMBRE DEL CAMPO]' para continuar."`

## Estado actual
> **Actualizar esta sección en cada sesión de trabajo antes de hacer commit.**

- Fecha último update: 2026-03-25
- Último módulo completado: Módulos 1-10 (base completa con CRUD, stock, modo recreo, recetas, códigos, logging, script inicio automático)
- Próximo paso: Probar que todo funcione correctamente
- Issues conocidos: ninguno

## Contexto de negocio
- Kiosco escolar, colegio primario y secundario
- Recreos de ~15 minutos = momento de máxima demanda (El Modo Recreo resuelve esto)
- Productos con código de barras de fábrica: gaseosas, jugos, galletitas, etc.
- Productos sin código: sanguchitos, tartas, facturas (se les genera código interno)
- Lector de códigos de barras USB (funciona como teclado) pendiente de compra
- La app debe poder usarla una persona mayor sin conocimientos técnicos
