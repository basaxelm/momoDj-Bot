# 🎧 momoDj - Bot de Música para Discord

**momoDj** es un bot de música para Discord diseñado para ofrecer una reproducción de audio fluida, estable y de alta calidad en canales de voz. Utiliza el prefijo **`mm`** para evitar colisiones con otros bots que emplean comandos de barra diagonal (`/`) o prefijos convencionales (`!`), incorpora un motor de extracción robusto con soporte para YouTube y Spotify, gestiona colas bidireccionales con historial de reproducción, cuenta con un sistema de desconexión automática por inactividad y soporta de forma nativa el protocolo de cifrado de extremo a extremo **DAVE** de Discord.

---

## 📌 Características Principales

- **Prefijo propio (`mm`)**: Todos los comandos utilizan el prefijo `mm` (por ejemplo, `mmplay`, `mmpause`, `mmskip`, `mmprev`, `mmhelp`), garantizando compatibilidad total en servidores que ya cuentan con bots que escuchan el prefijo `/` o `!`.
- **Compatibilidad con Voice Gateway v8 y Cifrado DAVE (E2EE)**: Totalmente actualizado para cumplir con los requisitos modernos de la infraestructura de voz de Discord, soportando Voice Gateway v8 y el protocolo MLS/DAVE vía `davey`.
- **Motor de Extracción y Streaming**:
  - **YouTube**: Procesamiento de enlaces directos, listas de reproducción, transmisiones en vivo y búsquedas por texto libre mediante `yt-dlp`.
  - **Soporte de Autenticación (`cookies.txt`)**: Integración nativa de cookies de sesión en `config/cookies.txt` para autenticar peticiones como usuario registrado, evitando bloqueos por detección de bots (*"Sign in to confirm you're not a bot"*) y habilitando contenido con restricción de edad.
  - **Resolución de Metadatos de Spotify**: Extracción automática de título y artista de pistas de Spotify mediante su endpoint público oEmbed (sin necesidad de cuenta Spotify Premium ni registro previo de aplicaciones comerciales), derivando el streaming al mejor resultado equivalente en YouTube.
- **Cola Bidireccional con Historial (`MusicQueue`)**:
  - Avanzá a la siguiente pista de la cola con `mmskip`.
  - Retrocedé a canciones previamente reproducidas mediante `mmprev`, rescatándolas de la pila de historial y reencolando la pista actual.
  - Inspección del estado de la cola con `mmqueue`.
- **Panel Interactivo con Componentes de Discord (`mmnowplaying` / `mmnp`)**:
  - Envía un Embed detallado con información de la pista, duración, miniatura y usuario solicitante.
  - Incluye botones interactivos (`discord.ui.View`): `⏮️` Anterior, `⏯️` Pausar/Reanudar, `⏭️` Siguiente y `⏹️` Detener.
- **Gestión de Voz y Desconexión Autónoma por Inactividad**:
  - **Validación de canal activo**: El comando `mmplay` exige que al menos un usuario humano (no bot) se encuentre en el canal de voz antes de establecer la conexión.
  - **Temporizador de 30 segundos**: Si todos los usuarios abandonan el canal de voz mientras el bot está conectado, se inicia una cuenta regresiva de 30 segundos en segundo plano. Si un usuario se reconecta antes del vencimiento, la tarea se cancela; de lo contrario, el bot detiene la reproducción, vacía la cola y se desconecta de forma ordenada para preservar recursos.

---

## 📜 Referencia de Comandos

Todos los comandos pueden ejecutarse pegados al prefijo (ej: `mmplay`) o con un espacio (ej: `mm play`).

| Comando | Alias | Descripción |
| :--- | :--- | :--- |
| `mmplay <texto o URL>` | `mmp` | Inicia la reproducción o encola una pista a partir de un término de búsqueda o enlace de YouTube/Spotify. Si el reproductor está pausado, reanuda la reproducción. |
| `mmpause` | | Pausa la reproducción de la pista actual. |
| `mmresume` | | Reanuda la reproducción pausada. |
| `mmskip` | `mmnext`, `mms` | Salta la pista actual y reproduce la siguiente en la cola. |
| `mmprev` | `mmprevious`, `mmanterior` | Recupera y reproduce la pista anterior registrada en el historial. |
| `mmqueue` | `mmq` | Muestra la pista en curso, el historial reciente y las próximas canciones pendientes. |
| `mmnowplaying` | `mmnp` | Muestra el estado de reproducción actual junto al panel de botones interactivos. |
| `mmstop` | `mmleave`, `mmdisconnect` | Detiene la reproducción, limpia la cola y el historial, y desconecta al bot del canal de voz. |
| `mmhelp` | `mmayuda`, `mmcomandos`, `mmhelp_mm`, `mhelp` | Despliega en el canal la lista de comandos disponibles e información de uso. |

---

## 🛠️ Últimas Mejoras y Correcciones (v2.1.0)

- **Soporte completo para Voice Gateway v8 y Cifrado DAVE (E2EE)**: Actualización a `discord.py 2.7.1` con la librería `davey` para resolver los errores de conexión de voz `4006` y `4017` introducidos por los nuevos requisitos de Discord.
- **Estandarización en CPython 3.13 de Windows**: Garantiza la instalación directa de ruedas binarias precompiladas de 64 bits sin necesidad de compilar paquetes locales.
- **Empaquetado autónomo de `libopus-0.dll`**: Provee soporte inmediato para codificación Opus en Windows sin requerir librerías externas.
- **Nuevo comando `mmhelp`**: Menú de ayuda interactivo para consultar la lista de comandos disponibles (`mmhelp` o `mm help`).
- **Mayor robustez en reproducción**: Limpieza preventiva de conexiones de voz zombi y progreso asíncrono no bloqueante en la cola.

> 📖 Para el análisis técnico exhaustivo de cada corrección y diagnóstico de errores de voz, consultá el [CHANGELOG.md](CHANGELOG.md).

---

## 🏗️ Arquitectura del Proyecto

```
momoDj-Bot/
├── config/
│   ├── settings.py           # Configuración centralizada, variables de entorno y carga de Opus
│   └── cookies.txt           # Cookies de sesión de YouTube (excluido de git)
├── music/
│   ├── audio_source.py       # Extracción asíncrona vía yt-dlp, integración con Node.js y resolución de Spotify
│   ├── player.py             # Controlador de reproducción por servidor (GuildMusicPlayer)
│   ├── queue.py              # Estructura de datos para la cola bidireccional (MusicQueue)
│   └── song.py               # Modelo de datos Song y generador de Embeds
├── cogs/
│   └── music_commands.py     # Registro de comandos con prefijo mm y vistas interactivas con botones (View)
├── utils/
│   └── inactivity.py         # Monitor de eventos de voz y temporizador de 30 segundos cancelable
├── libopus-0.dll             # Binario nativo Opus autónomo para Windows (x64)
├── .env                      # Variables de entorno y token privado (excluido de git)
├── .env.example              # Plantilla documentada de variables requeridas
├── .gitignore                # Reglas de exclusión para evitar filtración de credenciales
├── requirements.txt          # Dependencias de Python fijadas (discord.py 2.7.1 + davey)
├── run_bot.bat               # Script de inicio rápido para Windows
└── main.py                   # Inicialización del bot, cogs y eventos globales
```

---

## 🚀 Guía de Instalación y Despliegue

Esta sección explica paso a paso cómo poner en funcionamiento el bot, ya sea de forma local en tu computadora personal (Windows) o en un servidor en la nube (Linux VPS) para mantenerlo activo 24/7.

---

### 💻 Opción 1: Instalación Local en Windows (Tu Computadora)

Esta opción es ideal para ejecutar el bot directamente en tu PC cada vez que quieras escuchar música con amigos.

#### 1. Requisitos Previos e Instalación Rápida
Podés instalar todos los programas necesarios ejecutando una sola línea en **PowerShell como Administrador** con `winget`:

```powershell
winget install Python.Python.3.13 Gyan.FFmpeg OpenJS.NodeJS Git.Git --accept-package-agreements --accept-source-agreements
```

O si preferís descargarlos manualmente desde sus sitios oficiales:
1. **Python 3.13** ([python.org/downloads](https://www.python.org/downloads/)):
   - ⚠️ **CRUCIAL**: En la primera pantalla del instalador, marcá la casilla **"Add python.exe to PATH"**.
2. **FFmpeg** ([gyan.dev/ffmpeg](https://www.gyan.dev/ffmpeg/builds/)):
   - Motor de audio. Asegurate de que la carpeta `bin` de FFmpeg esté agregada a tu PATH o configurada en tu `.env`.
3. **Node.js** ([nodejs.org](https://nodejs.org/)):
   - Versión LTS. Necesario para que `yt-dlp` procese las firmas y tokens dinámicos de YouTube.
4. **Git** ([git-scm.com](https://git-scm.com/)):
   - Para clonar el código y mantenerlo actualizado.

> ℹ️ **Librería Opus**: El archivo nativo `libopus-0.dll` ya viene incluido en la raíz de este proyecto, por lo que no es necesario instalar paquetes adicionales de audio en Windows.

---

#### 2. Descarga y Creación del Entorno Virtual

Abrí una terminal de PowerShell en la carpeta donde desees ubicar el bot (por ejemplo, `C:\projects`):

```powershell
# 1. Clonar el repositorio
git clone https://github.com/basaxelm/momoDj-Bot.git
cd momoDj-Bot

# 2. Crear el entorno virtual con Python 3.13 oficial
py -3.13 -m venv venv

# 3. Actualizar pip e instalar las dependencias
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

> [!IMPORTANT]
> **Aviso sobre el entorno virtual (`venv/`)**:
> NUNCA muevas ni copies la carpeta `venv/` entre diferentes computadoras. Los entornos virtuales contienen rutas absolutas y enlaces simbólicos específicos del sistema donde fueron creados. Creá siempre el entorno desde cero en cada máquina siguiendo los comandos de arriba.

---

#### 3. Configuración de Credenciales (`.env` y `cookies.txt`)

1. **Crear archivo `.env`**:
   Creá un archivo llamado `.env` en la raíz del proyecto (podés copiar `.env.example` como referencia):
   ```ini
   DISCORD_TOKEN=tu_token_de_discord_aqui
   COMMAND_PREFIX=mm
   ```
2. **Cookies de YouTube (`config/cookies.txt`)** *(Opcional pero recomendado)*:
   Para evitar bloqueos de IP o restricciones de edad por parte de YouTube:
   - Utilizá una extensión de navegador como **Get cookies.txt LOCALLY**.
   - Iniciá sesión en YouTube y exportá las cookies en formato Netscape.
   - Guardá el archivo como `config/cookies.txt`.

---

#### 4. Puesta en Marcha

Podés iniciar el bot inmediatamente mediante cualquiera de estas opciones:
- **Doble clic**: Ejecutá el archivo **`run_bot.bat`**.
- **Desde la consola**:
  ```powershell
  .\run_bot.bat
  ```

---

#### 5. Opciones Avanzadas de Ejecución Continua en Windows

Si querés que el bot funcione de manera ininterrumpida sin tener una ventana de terminal abierta en tu barra de tareas:

- **Opción A (Recomendada): Como Servicio de Windows con NSSM** 🌟  
  El bot arrancará automáticamente al encender la PC (incluso sin haber iniciado sesión en Windows) y se autoreiniciará si ocurre algún error inesperado:
  ```powershell
  # 1. Instalar NSSM
  winget install NSSM.NSSM

  # 2. Configurar el servicio (ajustá la ruta según tu instalación)
  nssm install momoDj "C:\projects\momoDj-Bot\venv\Scripts\python.exe" "C:\projects\momoDj-Bot\main.py"
  nssm set momoDj AppDirectory "C:\projects\momoDj-Bot"
  nssm set momoDj Start SERVICE_AUTO_START

  # 3. Iniciar el servicio
  nssm start momoDj
  ```
  *(Podés detenerlo o desinstalarlo en cualquier momento con `nssm stop momoDj` o `nssm remove momoDj confirm`).*

- **Opción B: Inicio Silencioso con el Programador de Tareas (Task Scheduler)**  
  Si no deseás instalar programas adicionales:
  1. Presioná `Win + R`, escribí `taskschd.msc` y presioná Enter.
  2. Seleccioná **Crear tarea básica** y llamala `momoDj Discord Bot`.
  3. Desencadenador: **Al iniciar sesión**.
  4. Acción: **Iniciar un programa**.
     - **Programa o script**: `C:\projects\momoDj-Bot\venv\Scripts\pythonw.exe` *(el ejecutable `pythonw.exe` corre en segundo plano sin ventana gráfica)*.
     - **Argumentos**: `main.py`
     - **Iniciar en**: `C:\projects\momoDj-Bot`
  5. Guardá los cambios. El bot se iniciará automáticamente cada vez que inicies sesión.

---

### ☁️ Opción 2: Despliegue en Servidor (VPS Linux / Ubuntu 24/7)

Si contás con un servidor en la nube (como Ubuntu o Debian) y preferís que el bot funcione las 24 horas del día sin depender de tener tu computadora encendida:

#### 1. Instalación de Dependencias del Sistema
Conectate por SSH a tu servidor y ejecutá:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip ffmpeg nodejs git
```

#### 2. Clonado y Configuración del Entorno Virtual
```bash
git clone https://github.com/basaxelm/momoDj-Bot.git
cd momoDj-Bot
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. Configuración del Archivo `.env`
```bash
nano .env
```
Ingresá tus credenciales:
```ini
DISCORD_TOKEN=tu_token_de_discord_aqui
COMMAND_PREFIX=mm
```
*(Guardá con `Ctrl + O`, presioná `Enter` y salí con `Ctrl + X`).*

#### 4. Configuración como Servicio del Sistema (`systemd`)
Para que el bot inicie automáticamente con el servidor y se reinicie ante caídas:
```bash
sudo nano /etc/systemd/system/momodj.service
```

Ingresá la siguiente plantilla (reemplazá `ubuntu` por tu usuario y ajustá la ruta si difiere):
```ini
[Unit]
Description=momoDj - Bot de Música para Discord
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/momoDj-Bot
ExecStart=/home/ubuntu/momoDj-Bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Habilitá y arrancá el servicio:
```bash
sudo systemctl daemon-reload
sudo systemctl enable momodj
sudo systemctl start momodj
```

#### 5. Monitoreo y Verificación
- **Verificar estado del servicio**:
  ```bash
  sudo systemctl status momodj
  ```
- **Monitorear logs en tiempo real**:
  ```bash
  sudo journalctl -u momodj -f
  ```