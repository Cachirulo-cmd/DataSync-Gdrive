# DataSync — Backup automático a Google Drive

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)

Script de Python que comprime la carpeta `Documents` del usuario, calcula su hash SHA-256 para verificar integridad, y la sube automáticamente a una carpeta de Google Drive usando OAuth2. Funciona en cualquier PC con Windows sin necesidad de iniciar sesión cada vez.

---

## Tabla de Contenidos

- [¿Cómo funciona?](#cómo-funciona)
- [Archivos del proyecto](#archivos-del-proyecto)
- [Requisitos](#requisitos)
- [Configuración paso a paso](#configuración-paso-a-paso)
- [Uso](#uso)
- [Portabilidad a otras PCs](#portabilidad-a-otras-pcs)
- [.gitignore recomendado](#gitignore-recomendado)
- [Consideraciones de seguridad](#consideraciones-de-seguridad)
- [Troubleshooting](#troubleshooting)
- [🚀 Roadmap / Próximas Mejoras (v2.0)](#-roadmap--próximas-mejoras-v20)

---

## ¿Cómo funciona?

```
PC Windows
    │
    ├─ 1. Comprime ~/Documents → backup_HOSTNAME_delta.zip
    ├─ 2. Calcula SHA-256 del zip
    ├─ 3. Se autentica con Google usando el refresh token embebido
    ├─ 4. Sube el zip a la carpeta de Google Drive configurada
    └─ 5. Elimina el zip local si la subida fue exitosa
```

Cada backup incluye el nombre del equipo en el archivo (ej. `backup_PC-SALA_delta.zip`), lo que permite distinguir fácilmente los backups de distintas máquinas en la misma carpeta de Drive.

---

## Archivos del proyecto

```
DataSync/
├── svc_datasync.py     # Script principal de backup
├── obtener_token.py    # Script auxiliar para obtener el refresh token (una sola vez)
├── client_secret.json  # Credenciales OAuth descargadas de Google Cloud (no compartir, no subir a GitHub)
└── sync_service.log    # Log generado automáticamente al ejecutar (ignorado por .gitignore)
```

---

## Requisitos

- Python 3.8 o superior
- Cuenta de Google personal (Gmail)

### Dependencias

```powershell
pip install google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib
```

---

## Configuración paso a paso

### 1. Crear proyecto en Google Cloud Console

1. Ve a [console.cloud.google.com](https://console.cloud.google.com)
2. En el selector de proyectos (barra superior) → **Proyecto nuevo**
3. Asigna un nombre, por ejemplo `mi-backup-drive`, y haz clic en **Crear**

---

### 2. Habilitar la Google Drive API

1. Con tu proyecto seleccionado, ve al menú ☰ → **APIs y servicios** → **Biblioteca**
2. Busca **Google Drive API**
3. Haz clic en ella → **Habilitar**

---

### 3. Configurar la pantalla de consentimiento OAuth

1. Ve a **Google Auth Platform** → **Información de la marca**
2. Completa los campos requeridos:
   - **Nombre de la app**: `Backup Sync` (o cualquier nombre)
   - **Correo de asistencia**: tu correo de Google
   - **Información de contacto del desarrollador**: tu correo de Google
3. Haz clic en **Guardar y continuar**
4. En la sección **Permisos (Scopes)** → **Agregar o quitar permisos**, busca y agrega:
   ```
   https://www.googleapis.com/auth/drive.file
   ```
5. Haz clic en **Guardar y continuar**
6. En **Público** selecciona **Usuarios externos**
7. En **Usuarios de prueba** agrega tu cuenta personal de Gmail
8. Guarda y continúa hasta el final

---

### 4. Crear las credenciales OAuth

1. Ve a **Google Auth Platform** → **Clientes** → **Crear cliente**
2. En **Tipo de aplicación** selecciona **Aplicación de escritorio**
3. Asigna un nombre, por ejemplo `backup-sync-desktop`
4. Haz clic en **Crear**
5. Descarga el JSON generado y renómbralo a `client_secret.json`
6. Colócalo en la misma carpeta que `obtener_token.py`

> ⚠️ **No subas `client_secret.json` a GitHub.** Agrégalo a tu `.gitignore`.

---

### 5. Configurar la carpeta de Google Drive

1. Ve a [drive.google.com](https://drive.google.com)
2. Crea una carpeta nueva, por ejemplo `Backups-PC_DataSync`
3. Abre la carpeta y copia el **ID** de la URL:
   ```
   https://drive.google.com/drive/folders/1ABC2DEF3GHI  ← este es el ID
   ```

---

### 6. Obtener el refresh token (una sola vez)

Este paso se realiza **una única vez**. El refresh token obtenido no expira y se embebe directamente en el script.

1. Asegúrate de tener `client_secret.json` en la misma carpeta
2. Ejecuta:
   ```powershell
   python obtener_token.py
   ```
3. Se abrirá el navegador automáticamente — inicia sesión con tu cuenta de Google y acepta los permisos
4. En la terminal aparecerán tus 3 valores:
   ```
   REFRESH TOKEN : 1//0fbF8...
   CLIENT ID     : 79818...apps.googleusercontent.com
   CLIENT SECRET : GOCSPX-...
   ```

---

### 7. Configurar svc_datasync.py

Abre `svc_datasync.py` y rellena la sección de configuración con los valores obtenidos:

```python
DRIVE_FOLDER_ID = "TU_FOLDER_ID_AQUI"       # ID copiado del paso 5
CLIENT_ID       = "TU_CLIENT_ID_AQUI"        # Obtenido con obtener_token.py
CLIENT_SECRET   = "TU_CLIENT_SECRET_AQUI"    # Obtenido con obtener_token.py
REFRESH_TOKEN   = "TU_REFRESH_TOKEN_AQUI"    # Obtenido con obtener_token.py
```

> ⚠️ **No subas `svc_datasync.py` con tus credenciales reales a GitHub.**

---

## Uso

Una vez configurado, ejecuta el script con:

```powershell
python svc_datasync.py
```

El progreso queda registrado en `sync_service.log`, en la misma carpeta del script:

```
2026-04-13 18:13:26 - INFO - Iniciando backup desde: C:\Users\TuUsuario\Documents
2026-04-13 18:14:32 - INFO - Paquete creado: backup_PC-SALA_delta.zip (29983041 bytes) | SHA-256: 9000cc...
2026-04-13 18:14:32 - INFO - Subiendo a Google Drive...
2026-04-13 18:14:36 - INFO - Subida exitosa: 'backup_PC-SALA_delta.zip' (ID: 1XyZ...)
2026-04-13 18:14:36 - INFO - Archivo local eliminado. Sincronización completada.
```

---

## Portabilidad a otras PCs

El refresh token no expira, por lo que el script configurado funciona en cualquier PC sin repetir el proceso de autorización. Para usarlo en una nueva PC, copia `svc_datasync.py` (ya con tus valores configurados) e instala las dependencias:

```powershell
pip install google-api-python-client google-auth google-auth-httplib2
```

> `obtener_token.py` y `client_secret.json` solo son necesarios la primera vez. No hacen falta para ejecutar el backup.

---

## .gitignore recomendado

Crea un archivo `.gitignore` en la raíz del proyecto con este contenido para evitar subir archivos sensibles o innecesarios por accidente:

```
client_secret.json
sync_service.log
*.zip
__pycache__/
.venv/
```

---

## Consideraciones de seguridad

- El `REFRESH_TOKEN`, `CLIENT_ID` y `CLIENT_SECRET` dan acceso a tu Google Drive. **No compartas ni publiques `svc_datasync.py` con tus credenciales reales.**
- El script solo tiene permisos sobre `drive.file` — únicamente puede ver y modificar los archivos que él mismo crea. No tiene acceso al resto de tu Drive.
- Si en algún momento crees que tus credenciales se comprometieron, puedes revocarlas desde **Google Cloud Console → Credenciales** y generar nuevas.

---

## Troubleshooting

### "Google no ha verificado esta aplicación" al ejecutar `obtener_token.py`

Es el aviso más frecuente al usar OAuth en modo testing y **no indica ningún problema real**. Aparece porque el proyecto de Google Cloud aún no ha pasado por el proceso de verificación oficial de Google, algo completamente normal para uso personal o en desarrollo.

Para continuar sin problemas:

1. En la pantalla de advertencia, haz clic en **"Configuración avanzada"** (o "Advanced" si el navegador está en inglés)
2. Luego haz clic en el enlace **"Ir a [nombre de tu app] (no seguro)"**
3. Acepta los permisos solicitados con normalidad

> ℹ️ Este aviso solo aparece durante el paso de obtención del token (`obtener_token.py`). Una vez que tienes el `REFRESH_TOKEN`, el script de backup (`svc_datasync.py`) se autentica de forma silenciosa y no abre ningún navegador.

---

## 🚀 Roadmap / Próximas Mejoras (v2.0)

Actualmente estoy trabajando en la versión 2.0 para transformar este script en una herramienta de backup de alto rendimiento y nivel profesional. Las mejoras planeadas incluyen:

* **Filtrado Inteligente de Archivos:** Implementación de una **Whitelist** para respaldar únicamente archivos con valor real (como `.docx`, `.pdf`, `.xlsx`, `.pptx`, `.txt`, `key`, `.wallet`). Esto evitará la inclusión de caché, instaladores y archivos temporales.
* **Límite de Tamaño Crítico:** Exclusión automática de archivos que superen los **50 MB** (como archivos `.iso` o videos pesados) para garantizar subidas rápidas y un uso eficiente del almacenamiento.
* **Gestión de Cargas (Greedy Packing):** Uso del algoritmo *First Fit Decreasing* para dividir el respaldo en múltiples volúmenes ZIP de tamaño controlado. Esto previene errores con archivos gigantes y permite una restauración más granular.
* **Subidas en Paralelo (Threading):** Integración de `ThreadPoolExecutor` con un rango de 3 a 5 hilos para subir partes del backup simultáneamente. Esta mejora reducirá drásticamente el tiempo total de sincronización.
* **Ofuscación de Credenciales:** Implementación de técnicas de protección ligera (Base64 o XOR) para evitar que los tokens sean visibles directamente en el código fuente.

> [!IMPORTANT]
> **Nota sobre seguridad:** La ofuscación planificada es una medida de disuasión básica y no constituye seguridad criptográfica real. El objetivo a largo plazo es la migración a variables de entorno o gestores de secretos.
