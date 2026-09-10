# 🎧 momoDj - Discord Music Bot

**momoDj** es un bot de música para Discord diseñado para ofrecer una experiencia fluida, intuitiva y de alta calidad. Cuenta con controles con el prefijo **`mm`** (evitando colisiones con otros bots), reproducción desde YouTube y Spotify (resolución sin requerir cuenta premium), cola de reproducción bidireccional (avanzar y retroceder), panel interactivo con botones y desconexión inteligente por inactividad.

---

## ✨ Características Principales

- **Prefijo personalizado (`mm`)**: Comandos como `mmplay`, `mmpause`, `mmskip`, `mmprev`, etc.
- **Fuentes de Audio**:
  - **YouTube**: Soporte para enlaces directos de videos, transmisiones en vivo, shorts o búsquedas por texto libre.
  - **Autenticación con Cuenta de YouTube**: Soporte nativo para archivo `cookies.txt`, permitiendo eludir bloqueos de bot y acceder a videos de tu cuenta.
  - **Spotify**: Soporte para enlaces de pistas de Spotify mediante resolución automática de metadatos (título y artista vía oEmbed público sin requerir cuenta Spotify Premium) y streaming de alta calidad.
- **Cola Bidireccional con Historial**:
  - Pasa a la siguiente pista (`mmskip`) o vuelve a la canción anterior (`mmprev`).
  - Inspecciona la lista completa con `mmqueue`.
- **Panel Interactivo (`mmnowplaying` / `mmnp`)**:
  - Embed enriquecido con información del tema, duración, carátula y quién lo pidió.
  - Botones interactivos en Discord: `⏮️` Anterior, `⏯️` Pausar/Reanudar, `⏭️` Siguiente y `⏹️` Detener.
- **Gestión Inteligente de Voz**:
  - **Activación condicionada**: Solo permite unirse y reproducir cuando hay al menos una persona activa en el canal de voz.
  - **Auto-desconexión a los 30 segundos**: Si todos los usuarios humanos abandonan la llamada, momoDj inicia una cuenta atrás de 30 segundos. Si alguien regresa antes, se cancela; si no, se desconecta automáticamente y limpia la cola.

---

## 📜 Lista de Comandos (`mm`)

| Comando | Alias | Descripción |
| :--- | :--- | :--- |
| `mmplay <canción o link>` | `mmp` | Reproduce o añade a la cola un tema/video por nombre o enlace (YouTube o Spotify). Si está pausado, lo reanuda. |
| `mmpause` | | Pausa la canción actual. |
| `mmresume` | | Reanuda la canción en pausa. |
| `mmskip` | `mmnext`, `mms` | Salta a la siguiente canción en la cola. |
| `mmprev` | `mmprevious`, `mmanterior` | Vuelve a reproducir la canción anterior del historial. |
| `mmqueue` | `mmq` | Muestra la canción en curso, el historial y las próximas canciones pendientes. |
| `mmnowplaying` | `mmnp` | Muestra el panel de reproducción actual con botones interactivos. |
| `mmstop` | `mmleave`, `mmdisconnect` | Detiene la música, limpia la cola y desconecta al bot del canal de voz. |
| `mmhelp_mm` | `mmhelp`, `mmayuda` | Muestra la ayuda interactiva de comandos en el chat. |

---

## 🚀 Guía de Instalación y Despliegue Local (Windows)

### 1. Requisitos Previos
1. **Python 3.10+**: Asegúrate de tener Python instalado.
2. **FFmpeg**: Motor de transcodificación de audio. En Windows puedes instalarlo con:
   ```powershell
   winget install Gyan.FFmpeg
   ```
3. **Node.js** *(Recomendado para resolver desafíos de YouTube con `yt-dlp`)*:
   ```powershell
   winget install OpenJS.NodeJS
   ```

### 2. Configuración de Variables de Entorno (`.env`)
Crea un archivo llamado `.env` en la raíz del proyecto (basado en `.env.example`):
```ini
# Token del bot generado en Discord Developer Portal
DISCORD_TOKEN=tu_token_aqui
COMMAND_PREFIX=mm

# Ruta del archivo de cookies de YouTube (opcional pero recomendado)
YOUTUBE_COOKIES_PATH=config/cookies.txt

# Ruta directa a FFmpeg (opcional si ya está en tu PATH)
FFMPEG_PATH=C:\Users\axelh\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe
```

### 3. Cookies de YouTube (Opcional pero recomendado)
Para vincular tu cuenta de YouTube y evitar bloqueos de bots:
1. Exporta tus cookies de `youtube.com` usando extensiones como *"Get cookies.txt LOCALLY"* en formato Netscape.
2. Guarda el archivo como `config/cookies.txt` (este archivo está protegido por `.gitignore`).

### 4. Instalación de Dependencias
Abre una terminal en la carpeta del bot:
```powershell
# Crear entorno virtual
python -m venv venv

# Instalar dependencias
pip install -r requirements.txt
```

### 5. Iniciar el Bot
Puedes iniciar el bot de dos formas:
- **Opción A (Fácil)**: Haz doble clic en el archivo `run_bot.bat`.
- **Opción B (Terminal)**:
  ```powershell
  .\venv\bin\python.exe main.py
  ```

---

## 🌐 Guía de Despliegue en Servidor / VPS (Linux / Ubuntu)

Para mantener a **momoDj** funcionando 24/7 en un servidor en la nube (ej. Oracle Cloud Free Tier, DigitalOcean, AWS EC2, VPS Ubuntu):

### 1. Instalar dependencias en el servidor
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip ffmpeg nodejs git
```

### 2. Clonar el repositorio
```bash
git clone https://github.com/basaxelm/momoDj-Bot.git
cd momoDj-Bot
```

### 3. Crear entorno virtual e instalar librerías
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Configurar el archivo `.env`
```bash
nano .env
# Pega tu DISCORD_TOKEN y guarda con CTRL+O, luego ENTER, y sal con CTRL+X
```

### 5. Configurar servicio permanente con `systemd`
Crea el archivo de servicio del sistema:
```bash
sudo nano /etc/systemd/system/momodj.service
```
Pega el siguiente contenido (ajusta la ruta según tu usuario):
```ini
[Unit]
Description=momoDj Discord Music Bot
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
Habilita y arranca el servicio:
```bash
sudo systemctl daemon-reload
sudo systemctl enable momodj
sudo systemctl start momodj
```
Para ver el estado y los logs en tiempo real:
```bash
sudo systemctl status momodj
sudo journalctl -u momodj -f
```

---

## 🛡️ Estructura del Proyecto

```
momoDj-Bot/
├── config/
│   ├── settings.py           # Carga de variables de entorno y utilidades
│   └── cookies.txt           # Cookies de YouTube (ignorado en git)
├── music/
│   ├── audio_source.py       # Extracción con yt-dlp y FFmpeg
│   ├── player.py             # Controlador de reproducción por servidor
│   ├── queue.py              # Cola bidireccional con historial
│   └── song.py               # Modelo de canción y formato de Embeds
├── cogs/
│   └── music_commands.py     # Comandos mm* y botones interactivos UI
├── utils/
│   └── inactivity.py         # Temporizador de 30s y detección de participantes
├── .env                      # Credenciales secretas (ignorado en git)
├── .env.example              # Plantilla de configuración
├── .gitignore                # Reglas de exclusión de git
├── requirements.txt          # Lista de dependencias de Python
├── run_bot.bat               # Lanzador para Windows
└── main.py                   # Punto de entrada de momoDj
```