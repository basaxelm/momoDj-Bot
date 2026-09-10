# 🎧 momoDj - Bot de Música para Discord

**momoDj** es un bot de música para Discord pensado para que puedas tirar temas en tu servidor de forma rápida, sin trabas y con la mejor calidad de audio. Viene configurado con el prefijo **`mm`** (así no te choca con los comandos de otros bots), reproduce temas de YouTube y Spotify (resolviendo los temas al toque sin que necesites una cuenta Premium), maneja una cola bidireccional (podés saltar temas o volver al anterior si te pintó) y tiene desconexión automática si el canal queda vacío.

---

## ✨ Qué tiene de bueno momoDj

- **Prefijo propio (`mm`)**: Todos los comandos arrancan con `mm` (`mmplay`, `mmpause`, `mmskip`, `mmprev`, etc.) para evitar cualquier bardo con otros bots que usen la barra `/`.
- **Fuentes de Audio**:
  - **YouTube**: Mandale enlaces directos de videos, shorts, transmisiones en vivo o directamente el nombre del tema y el artista.
  - **Vinculación con tu cuenta de YouTube**: Soporta el uso de tu archivo `cookies.txt` en `config/cookies.txt`. Con esto te olvidás de los bloqueos anti-bot ("Sign in to confirm you're not a bot") y podés reproducir temas con restricción de edad o de tu cuenta.
  - **Spotify sin vueltas**: Si le tirás un link de una canción de Spotify, el bot rescata los metadatos (título y artista) usando el endpoint público oEmbed (no necesitás pagar Spotify Premium ni renegar con permisos de la API) y sale a buscar la mejor versión a YouTube para reproducirla de una.
- **Cola bidireccional con historial**:
  - ¿Querés pasar al tema que sigue? Tirás `mmskip`.
  - ¿Te arrepentiste y querés volver a escuchar el tema que acaba de sonar? Tirás `mmprev` y te lo rescata del historial.
  - Podés ver toda la lista ordenada con `mmqueue`.
- **Panel interactivo (`mmnowplaying` o `mmnp`)**:
  - Te muestra una tarjeta (Embed) con el tema actual, la duración, la miniatura y quién lo pidió.
  - Además te deja botones táctiles en Discord para controlar la música con un clic: `⏮️` (Anterior), `⏯️` (Pausar/Reanudar), `⏭️` (Siguiente) y `⏹️` (Detener).
- **Gestión inteligente de la llamada de voz**:
  - **Solo entra si hay gente**: Si tirás `mmplay` pero estás solo en el canal o solo hay bots, no se conecta.
  - **Auto-desconexión a los 30 segundos**: Si están escuchando música y todos se desconectan de la llamada, momoDj arranca una cuenta regresiva de 30 segundos. Si alguien vuelve a entrar en ese tiempo, la cuenta se cancela y sigue sonando. Si pasaron los 30 segundos y no quedó nadie, el bot frena la música, limpia la cola y se va solo para no gastar ancho de banda ni CPU al vicio.

---

## 📜 Lista de Comandos (`mm`)

| Comando | Atajo | ¿Qué hace? |
| :--- | :--- | :--- |
| `mmplay <tema o link>` | `mmp` | Reproduce o mete en la cola una canción por nombre o por link de YouTube o Spotify. Si estaba pausado, lo reanuda. |
| `mmpause` | | Pausa la música que esté sonando. |
| `mmresume` | | Vuelve a poner play si estaba en pausa. |
| `mmskip` | `mmnext`, `mms` | Salta a la siguiente canción de la cola. |
| `mmprev` | `mmprevious`, `mmanterior` | Vuelve a reproducir la canción anterior del historial. |
| `mmqueue` | `mmq` | Te muestra qué tema está sonando, qué sonó antes y la lista de lo que se viene. |
| `mmnowplaying` | `mmnp` | Muestra la tarjeta del tema actual con los botones interactivos. |
| `mmstop` | `mmleave`, `mmdisconnect` | Frena todo, vacía la cola y saca al bot del canal de voz. |
| `mmhelp_mm` | `mmhelp`, `mmayuda` | Tira la ayuda interactiva en el chat con todos los comandos. |

---

## 🛠️ Detalles Técnicos de la Implementación

El bot está desarrollado en **Python 3.12** utilizando una arquitectura modular limpia:

```
momoDj-Bot/
├── config/
│   ├── settings.py           # Lectura de variables de entorno (.env), rutas y carga de Opus
│   └── cookies.txt           # Tus cookies de YouTube (ignorado en git)
├── music/
│   ├── audio_source.py       # Extracción con yt-dlp, integración con Node.js y resolución de Spotify
│   ├── player.py             # Controlador de reproducción por servidor (GuildMusicPlayer)
│   ├── queue.py              # Cola bidireccional (upcoming, current, history)
│   └── song.py               # Modelo de datos de la canción y formateador de Embeds
├── cogs/
│   └── music_commands.py     # Registro de comandos mm* y componentes de interfaz gráfica (View con botones)
├── utils/
│   └── inactivity.py         # Monitor de inactividad con timer de 30s cancelable
├── .env                      # Tus tokens y credenciales privadas (ignorado en git)
├── .env.example              # Plantilla para que cualquiera pueda configurar sus variables
├── .gitignore                # Reglas estrictas de exclusión para no filtrar secretos
├── requirements.txt          # Dependencias exactas de Python
├── run_bot.bat               # Script para levantarlo con un clic en Windows
└── main.py                   # Punto de entrada del bot y conexión a Discord Gateway
```

### Tecnologías clave:
- **`discord.py[voice]`**: Conexión con el Gateway de Discord y manejo de clientes de voz mediante sockets UDP cifrados.
- **`yt-dlp` + Node.js runtime**: Extracción de streams de audio directo desde YouTube. Utiliza el runtime de Node y componentes remotos para saltear los desafíos JavaScript que implementó YouTube recientemente.
- **`FFmpeg`**: Transcodificación en tiempo real del flujo de audio a PCM/Opus con flags de reconexión automática (`-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5`) para que la transmisión no se corte nunca.
- **`PyNaCl` + `libopus`**: Manejo de cifrado y empaquetado de paquetes de audio para Discord.

---

## 💻 Cómo Levantarlo en tu Máquina (Windows)

### 1. Requisitos previos
- **Python 3.10 o superior**.
- **FFmpeg**: Si no lo tenés, abrís una PowerShell y tirás:
  ```powershell
  winget install Gyan.FFmpeg
  ```
- **Node.js**: Necesario para que `yt-dlp` no tenga problemas con las firmas de YouTube:
  ```powershell
  winget install OpenJS.NodeJS
  ```

### 2. Clonar y preparar el proyecto
Abrí una terminal en la carpeta donde quieras trabajar:
```powershell
git clone https://github.com/basaxelm/momoDj-Bot.git
cd momoDj-Bot
```

### 3. Crear el entorno virtual e instalar paquetes
```powershell
# Armás el entorno virtual
python -m venv venv

# Instalás las librerías necesarias
.\venv\bin\pip.exe install -r requirements.txt
```

### 4. Configurar el archivo `.env`
Creá un archivo llamado `.env` en la raíz de la carpeta (podés guiarte con `.env.example`):
```ini
# Token del bot sacado del Discord Developer Portal
DISCORD_TOKEN=tu_token_de_discord_aca
COMMAND_PREFIX=mm

# Ruta a las cookies de YouTube (opcional pero muy recomendado)
YOUTUBE_COOKIES_PATH=config/cookies.txt

# Ruta directa a FFmpeg (opcional si ya está en tu PATH)
FFMPEG_PATH=C:\Users\axelh\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe
```

### 5. Configurar tus cookies de YouTube (Opcional pero recomendado)
1. Instalate en tu navegador la extensión **"Get cookies.txt LOCALLY"**.
2. Entrá a YouTube con tu cuenta iniciada.
3. Apretá la extensión y descargá el archivo en formato Netscape.
4. Guardalo como `config/cookies.txt` (quedate tranquilo que está en el `.gitignore`, nunca se va a subir a GitHub).

### 6. Poner a correr el bot
Tenés dos opciones fáciles:
- **La más rápida**: Le hacés doble clic al archivo `run_bot.bat` y listo.
- **Por terminal**:
  ```powershell
  .\venv\bin\python.exe main.py
  ```

---

## ☁️ Guía de Deploy 24/7 en un Servidor (VPS Ubuntu / Debian)

Si querés que el bot quede prendido todo el día sin depender de tener tu computadora prendida, lo ideal es meterlo en un servidor Linux (por ejemplo en Oracle Cloud Free Tier, DigitalOcean o AWS):

### 1. Instalar las dependencias en el servidor
Conectate por SSH a tu servidor y mandale:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip ffmpeg nodejs git
```

### 2. Bajar el repositorio
```bash
git clone https://github.com/basaxelm/momoDj-Bot.git
cd momoDj-Bot
```

### 3. Crear el entorno virtual y meter las librerías
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Crear el archivo `.env`
```bash
nano .env
```
Pegás tu token de Discord:
```ini
DISCORD_TOKEN=tu_token_de_discord_aca
COMMAND_PREFIX=mm
```
*(Para guardar en nano apretás `Ctrl + O`, después le das `Enter` y salís con `Ctrl + X`).*

*(Si querés usar tus cookies de YouTube en el servidor, podés copiar tu `cookies.txt` a la carpeta `config/cookies.txt`).*

### 5. Armar el servicio con `systemd` (para que levante solo siempre)
Para que si el servidor se reinicia o el bot se cae por cualquier motivo, vuelva a levantarse solo al toque:

Creá el archivo de servicio:
```bash
sudo nano /etc/systemd/system/momodj.service
```

Pegale esto (cambiá `ubuntu` por tu nombre de usuario en el servidor si es diferente):
```ini
[Unit]
Description=momoDj - Bot de Musica para Discord
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

Ahora recargás systemd, habilitás el servicio y lo arrancás:
```bash
sudo systemctl daemon-reload
sudo systemctl enable momodj
sudo systemctl start momodj
```

### 6. Ver cómo viene marchando el bot
Para chequear el estado:
```bash
sudo systemctl status momodj
```

Para ver los logs en vivo (y ver qué canciones va reproduciendo):
```bash
sudo journalctl -u momodj -f
```

¡Y listo! Ya tenés a **momoDj** sonando 24/7 en tu servidor de Discord.