# R&A Organizador

Aplicación de escritorio para **organizar archivos por tipo y extensión** de forma sencilla, sin tener que crear carpetas manualmente ni utilizar comandos. Seleccionas una carpeta, revisas una vista previa y confirmas la organización.

La aplicación mueve los archivos a subcarpetas según su extensión (PDF, JPG, MP3, ZIP, etc.). No elimina archivos ni modifica su contenido.

## Características

- Organiza automáticamente los archivos de una carpeta por extensión.
- Crea una subcarpeta para cada tipo de archivo (por ejemplo, `PDF`, `JPG`, `MP3` o `SIN_EXTENSION`).
- Analiza la carpeta antes de realizar cambios y muestra una vista previa con el número de archivos de cada tipo.
- Solicita confirmación antes de mover los archivos.
- Evita sobrescribir archivos cuando encuentra nombres repetidos: añade un sufijo numérico.
- Muestra el progreso de la organización y permite abrir la carpeta al terminar.
- Incluye un banner informativo que puede actualizarse mediante una configuración remota.

## Descarga

La forma más fácil de usar la aplicación es descargar la versión ya preparada, sin instalar Python ni ningún otro programa:

1. Entra en la sección [Releases](../../releases) de este repositorio.
2. Abre la versión más reciente.
3. En el apartado **Assets**, descarga el archivo `.zip` (por ejemplo, `RyA_Organizador.zip`). No descargues el código fuente (`Source code`).
4. Cuando termine la descarga, abre el archivo ZIP y extrae su contenido en una carpeta de tu ordenador. Puedes utilizar la opción **Extraer todo** de Windows.
5. Entra en la carpeta extraída y haz doble clic en `RyA_Organizador.exe`.

¡Eso es todo! No necesitas instalar Python ni utilizar GitHub para nada más.

> **Aviso de Windows:** como el ejecutable no está firmado digitalmente, Windows SmartScreen o tu antivirus podrían mostrar una advertencia la primera vez. Descarga el archivo únicamente desde la sección Releases de este repositorio. Si Windows muestra SmartScreen, comprueba el origen del archivo antes de decidir si deseas ejecutarlo.

## Uso

1. Abre `RyA_Organizador.exe`.
2. Pulsa **ELEGIR...** y selecciona la carpeta que quieres organizar.
3. Pulsa **Analizar archivos**. La aplicación mostrará cuántos archivos hay de cada tipo, sin mover nada todavía.
4. Revisa la vista previa.
5. Si estás de acuerdo, pulsa **Confirmar y organizar** y acepta el mensaje de confirmación.
6. Espera a que termine el proceso. Al finalizar, puedes abrir la carpeta organizada directamente desde el aviso.

**Importante:** esta versión organiza únicamente los archivos que están directamente dentro de la carpeta seleccionada. No entra en las subcarpetas que ya existan.

Los archivos se mueven a carpetas con el nombre de su extensión. Por ejemplo:

```text
Mi carpeta/
├── PDF/
│   ├── documento.pdf
│   └── factura.pdf
├── JPG/
│   └── vacaciones.jpg
├── MP3/
│   └── canción.mp3
└── ZIP/
    └── archivos.zip
```

Si ya existe un archivo con el mismo nombre en la carpeta de destino, la aplicación conserva ambos añadiendo un número al nombre del archivo.

## Ejecutar desde el código fuente

Esta sección está pensada para personas que quieran revisar o modificar el programa. **No es necesaria para descargar y utilizar la aplicación.**

Requisitos: Windows y Python 3.10 o superior (Tkinter viene incluido normalmente con la instalación oficial de Python).

Desde PowerShell, dentro de la carpeta del proyecto:

```powershell
python organizador.py
```

## Compilar el ejecutable

Si quieres generar el `.exe` desde el código fuente, puedes utilizar el archivo `crear_exe.bat` incluido en el proyecto:

1. Instala Python 3.10 o superior en el equipo de desarrollo.
2. Haz doble clic en `crear_exe.bat`.
3. El proceso instalará PyInstaller si es necesario y preparará el ejecutable.
4. Al terminar, encontrarás `RyA_Organizador.exe` dentro de la carpeta `dist`.

El equipo utilizado para compilar necesita Python. **Las personas que descarguen el `.exe` desde Releases no necesitan instalar Python.**

## Archivos de la aplicación

| Qué | Dónde |
|---|---|
| Ejecutable | `RyA_Organizador.exe` |
| Registro de actividad y errores | `%LOCALAPPDATA%\RyA_Organizador\organizador.log` |

Si algo falla, el archivo de registro puede ayudar a identificar el problema.

## Privacidad

- La organización de archivos se realiza en tu propio equipo. Los archivos no se suben a ningún servidor.
- La aplicación consulta una configuración remota para obtener el texto, la imagen y el enlace del banner. Si no hay conexión o la configuración no está disponible, utiliza los valores locales.
- Si se configura una dirección para métricas, la aplicación puede enviar el identificador de la aplicación, el identificador del banner y el tipo de evento (por ejemplo, un clic). No envía nombres, rutas ni contenidos de tus archivos.

## Apoya el proyecto

R&A Organizador forma parte de las herramientas de **Ritmo & Algoritmo**. Si te resulta útil, puedes descubrir otras herramientas y apoyar el proyecto desde [j75.es/herramientas](https://j75.es/herramientas).

## Créditos

Desarrollado por **Ritmo & Algoritmo**.


## Build executable

If you prefer to generate the executable yourself, you can build it from the source code.

Requirements:
- Windows
- Python 3.10 or newer

Run `crear_exe.bat`. The script installs or updates PyInstaller and creates a Onefolder build (`--onedir`) under `dist/RyA_Organizador/`.

Keep the entire folder together, including `RyA_Organizador.exe` and `_internal/`. Do not distribute the EXE by itself. To publish a release, ZIP the complete `dist/RyA_Organizador` folder and upload it to the GitHub Release assets.
