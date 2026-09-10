# 🎧 momoDj - Bot de Música para Discord

**momoDj** es un bot de música para Discord diseñado para ofrecer una reproducción de audio fluida, estable y de alta calidad en canales de voz. Utiliza el prefijo **`mm`** para evitar colisiones con otros bots que emplean comandos de barra diagonal (`/`), incorpora un motor de extracción robusto con soporte para YouTube y Spotify, gestiona colas bidireccionales con historial de reproducción y cuenta con un sistema de desconexión automática basado en la presencia de usuarios en el canal.

---

## 📌 Características Principales

- **Prefijo propio (`mm`)**: Todos los comandos utilizan el prefijo `mm` (por ejemplo, `mmplay`, `mmpause`, `mmskip`, `mmprev`), garantizando compatibilidad total en servidores que ya cuentan con bots que escuchan el prefijo `/` o `!`.
- **Motor de Extracción y Streaming**:
  - **YouTube**: Procesamiento de enlaces directos, listas de reproducción, transmisiones en vivo y búsquedas por texto libre mediante `yt-dlp`.
  - **Soporte de Autenticación (`cookies.txt`)**: Integración nativa de cookies de sesión en `config/cookies.txt` para autenticar peticiones como usuario registrado, evitando bloqueos por detección de bots (*"Sign in to confirm you're not a bot"*) y habilitando contenido restringido.
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
| `mmhelp_mm` | `mmhelp`, `mmayuda` | Despliega en el canal la guía interactiva con la lista de comandos disponibles. |

---

## 🏗️ Arquitectura del Proyecto

El bot está implementado en **Python 3.12** bajo un diseño desacoplado y orientado a objetos:

```
momoDj-Bot/
├── config/
│   ├── settings.py           # Gestión centralizada de configuración, entorno (.env) y carga de libopus
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
├── .env                      # Variables de entorno y token privado (excluido de git)
├── .env.example              # Plantilla documentada de variables requeridas
├── .gitignore                # Reglas de exclusión para evitar filtración de credenciales
├── requirements.txt          # Dependencias de Python fijadas
├── run_bot.bat               # Script de inicio rápido para entornos Windows
└── main.py                   # Inicialización del cliente de Discord, cogs y eventos globales
```

### Componentes Técnicos Clave:
- **`discord.py[voice]`**: Manejo de la conexión Gateway y del protocolo de voz en tiempo real sobre UDP.
- **`yt-dlp` + Node.js runtime**: Permite resolver desafíos de código JavaScript generados dinámicamente por YouTube (n-sig y signature challenges).
- **`FFmpeg`**: Transcodificación en vivo hacia formato PCM con parámetros de reconexión automática (`-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5`) para prevenir cortes por fluctuaciones de red.
- **`PyNaCl` + `libopus`**: Cifrado simétrico de paquetes de audio y codificación Opus requerida por la API de voz de Discord.

---

## 💻 Instalación y Ejecución Local (Windows)

### 1. Requisitos Previos
- **Python 3.10 o superior** (disponible en el PATH).
- **FFmpeg**: Motor de procesamiento de audio. Podés instalarlo mediante Windows Package Manager:
  ```powershell
  winget install Gyan.FFmpeg
  ```
- **Node.js**: Requerido por `yt-dlp` para resolver desafíos criptográficos de YouTube:
  ```powershell
  winget install OpenJS.NodeJS
  ```

### 2. Clonado y Preparación del Entorno
Abrí una consola de PowerShell y cloná el repositorio:
```powershell
git clone https://github.com/basaxelm/momoDj-Bot.git
cd momoDj-Bot
```

Creá el entorno virtual e instalá las dependencias requeridas:
```powershell
python -m venv venv
.\venv\bin\pip.exe install -r requirements.txt
```

### 3. Configuración de Variables de Entorno (`.env`)
Creá el archivo `.env` en la raíz del proyecto basándote en la plantilla `.env.example`:
```ini
# Token del bot generado en Discord Developer Portal
DISCORD_TOKEN=tu_token_de_discord_aqui
COMMAND_PREFIX=mm

# Ruta del archivo de cookies de YouTube (opcional pero recomendado)
YOUTUBE_COOKIES_PATH=config/cookies.txt

# Ruta directa al ejecutable de FFmpeg (opcional si ya está en tu PATH)
FFMPEG_PATH=C:\Users\axelh\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe
```

### 4. Configuración de Cookies de YouTube (Opcional pero recomendado)
Para vincular tu cuenta de YouTube y garantizar acceso sin restricciones de bot:
1. Instalá una extensión como **Get cookies.txt LOCALLY** en tu navegador.
2. Ingresá a `youtube.com` con tu sesión iniciada.
3. Exportá las cookies en formato Netscape.
4. Guardá el archivo en `config/cookies.txt` (este archivo se encuentra protegido por `.gitignore`).

### 5. Inicio del Bot
Podés ejecutar el bot mediante cualquiera de las siguientes opciones:
- **Ejecución directa**: Hacé doble clic en el archivo `run_bot.bat`.
- **Desde la terminal**:
  ```powershell
  .\venv\bin\python.exe main.py
  ```

---

## ☁️ Guía de Despliegue en Servidor (VPS Linux / Ubuntu)

Para mantener el servicio activo 24/7 en un servidor en la nube:

### 1. Instalación de Dependencias del Sistema
Conectate a tu servidor mediante SSH y actualizá los paquetes:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip ffmpeg nodejs git
```

### 2. Clonado y Configuración del Entorno Virtual
```bash
git clone https://github.com/basaxelm/momoDj-Bot.git
cd momoDj-Bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Archivo de Configuración
Creá el archivo `.env`:
```bash
nano .env
```
Ingresá tu token:
```ini
DISCORD_TOKEN=tu_token_de_discord_aqui
COMMAND_PREFIX=mm
```
*(Guardá con `Ctrl + O`, presioná `Enter` y salí con `Ctrl + X`).*

### 4. Configuración como Servicio del Sistema (`systemd`)
Para garantizar que el bot se ejecute en segundo plano y se reinicie automáticamente ante fallos o reinicios del servidor, creá una unidad de `systemd`:
```bash
sudo nano /etc/systemd/system/momodj.service
```

Ingresá la siguiente configuración (ajustá el campo `User` y las rutas si tu usuario difiere de `ubuntu`):
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

### 5. Monitoreo y Verificación
- **Estado del servicio**:
  ```bash
  sudo systemctl status momodj
  ```
- **Lectura de logs en tiempo real**:
  ```bash
  sudo journalctl -u momodj -f
  ```