# Kiosco Moni

Sistema de gestión de stock y ventas para un kiosco escolar.

## Instalación para producción (NSSM)

### 1. Descargar NSSM
1. Ir a https://nssm.cc/download
2. Descargar la versión más reciente (win64)
3. Extraer el ZIP y copiar `nssm.exe` a `C:\Windows\System32\`

### 2. Registrar como servicio de Windows

Abrir terminal como **Administrador** y ejecutar:

```
nssm install KioscoMoni
```

En la ventana que se abre, completar:

| Campo | Valor |
|-------|-------|
| Path | `C:\Users\Asus\Desktop\kiosco-moni\venv\Scripts\python.exe` |
| Startup directory | `C:\Users\Asus\Desktop\kiosco-moni` |
| Arguments | `app.py` |

En la pestaña **Details**:
- Display name: `Kiosco Moni`

Clic en **Install service**.

### 3. Iniciar el servicio

```cmd
nssm start KioscoMoni
```

### 4. Comandos útiles

```cmd
nssm start KioscoMoni      # Iniciar
nssm stop KioscoMoni       # Detener
nssm restart KioscoMoni   # Reiniciar (después de actualizar código)
nssm remove KioscoMoni     # Desinstalar servicio
```

### 5. Abrir automáticamente al iniciar Windows

```
Win + R → shell:startup → Enter
```

Crear acceso directo con destino: `http://localhost:5000`

---

## Instalación para desarrollo

```cmd
# Crear entorno virtual
python -m venv venv

# Activar
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python app.py
```

Luego abrir http://localhost:5000

---

## Actualizar después de cambios

Si actualizaste el código y usas NSSM:

```cmd
nssm restart KioscoMoni
```

Si usas el .bat, simplemente cerralo y volvé a abrirlo.
