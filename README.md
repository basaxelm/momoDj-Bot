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

## 🛠️ Historial de Correcciones Técnicas (Voice Gateway Fixes)

Esta sección documenta los errores críticos de conexión de voz resueltos en el bot para referencia y estabilidad:

### 1. Error `WebSocket closed with 4006` (Session is no longer valid)
- **Causa raíz**: Discord dio de baja la versión 4 de su Voice Gateway (`/?v=4`) y modificó el formato de sus servidores de medios (`*.discord.media:port`). Las versiones anteriores de `discord.py` (< 2.6.0) utilizaban el gateway antiguo y recortaban erróneamente los puertos con `rpartition(':')`, provocando que el servidor de voz rechazara la conexión inmediatamente.
- **Solución**: Migración a **Voice Gateway v8**, adoptado oficialmente en `discord.py` 2.6+.

### 2. Error `WebSocket closed with 4017` (`DAVE_PROTOCOL_REQUIRED`)
- **Causa raíz**: Discord implementó de forma estricta y obligatoria el protocolo **DAVE** (*Discord Audio & Video End-to-End Encryption*, basado en MLS RFC 9420) en sus canales de voz. Al intentar conectar con librerías que no anuncian `max_dave_protocol_version > 0` en el payload de `IDENTIFY`, el servidor de Discord cierra la conexión de forma abrupta con código 4017.
- **Solución**:
  - Actualización a **`discord.py[voice]==2.7.1`**, que incluye compatibilidad nativa con DAVE.
  - Integración de la biblioteca binaria **`davey`** (`davey>=0.1.0`), encargada de generar los paquetes de claves MLS y cifrar los paquetes de audio Opus al vuelo.

### 3. Incompatibilidad de Entornos MinGW/MSYS2 vs Windows CPython
- **Causa raíz**: Entornos basados en MinGW/MSYS2 (`mingw_x86_64_ucrt_gnu`) no reconocen las ruedas binarias precompiladas para Windows (`win_amd64`) de `davey`. Como consecuencia, `pip` intentaba compilar `davey` desde código fuente utilizando Rust/Maturin, fallando por requerir características experimentales (`edition2024`).
- **Solución**: Estandarización obligatoria en **CPython 3.13 oficial de Windows**, el cual instala paquetes 100% precompilados sin requerir cadenas de compilación C++/Rust locales.

### 4. Empaquetado Autónomo de `libopus-0.dll` y Limpieza de Sockets
- Se incorporó la librería **`libopus-0.dll`** directamente en la raíz del proyecto para que cualquier máquina Windows cuente con soporte Opus inmediato sin necesidad de instalar librerías adicionales en el sistema operativo.
- Se implementó limpieza forzosa de conexiones en estado zombi en `_ensure_voice_connection` y se desacopló el callback `_after_playback` de la cola mediante `fut.add_done_callback` para evitar congelamientos en el hilo de audio de Discord.

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

## 🖥️ Guía de Despliegue en Otra Máquina Windows (PC de Escritorio)

Si tenés el bot funcionando en tu notebook y querés trasladarlo a una PC de escritorio más potente para dejarlo corriendo, seguí estos pasos para realizar un despliegue limpio y óptimo.

### 1. Programas a Descargar e Instalar en la PC de Escritorio

Abrí una ventana de **PowerShell como Administrador** en tu PC de escritorio e instalá los requisitos con una sola línea mediante `winget`:

```powershell
winget install Python.Python.3.13 Gyan.FFmpeg OpenJS.NodeJS Git.Git --accept-package-agreements --accept-source-agreements
```

Si preferís instalarlos manualmente desde sus páginas oficiales:
1. **Python 3.13** ([python.org/downloads](https://www.python.org/downloads/)):
   - ⚠️ **MUY IMPORTANTE**: En la primera pantalla del instalador, marcá la casilla **"Add python.exe to PATH"**.
2. **FFmpeg** ([gyan.dev/ffmpeg](https://www.gyan.dev/ffmpeg/builds/)):
   - Descargá la versión *release essentials*, descomprimila y asegurate de que la carpeta `bin` esté en tus variables de entorno PATH, o configurala en el `.env`.
3. **Node.js** ([nodejs.org](https://nodejs.org/)):
   - Versión LTS recomendada. Necesario para que `yt-dlp` procese los tokens dinámicos de YouTube.
4. **Git** ([git-scm.com](https://git-scm.com/)):
   - Para clonar y actualizar el repositorio cómodamente.

---

### 2. Clonado y Configuración del Proyecto

En tu PC de escritorio, abrí PowerShell en la carpeta donde quieras ubicar el bot (por ejemplo `C:\projects`):

```powershell
# 1. Clonar el repositorio
git clone https://github.com/basaxelm/momoDj-Bot.git
cd momoDj-Bot

# 2. Crear el entorno virtual con Python 3.13 oficial
py -3.13 -m venv venv

# 3. Actualizar pip e instalar dependencias con soporte DAVE
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

> [!WARNING]
> **¿Qué NO copiar de la notebook a la PC?**
> **NUNCA copies la carpeta `venv/`** directamente entre máquinas. Los entornos virtuales contienen rutas absolutas y punteros a los binarios de la máquina de origen. Creá siempre el entorno virtual desde cero en la máquina de destino siguiendo los comandos anteriores.

---

### 3. Configuración de Credenciales (`.env` y `cookies.txt`)

Copiá los siguientes archivos desde tu notebook hacia la carpeta del bot en tu PC de escritorio:

1. **`.env`**:
   Crealo en la raíz del proyecto con tu token de Discord:
   ```ini
   DISCORD_TOKEN=tu_token_de_discord_aqui
   COMMAND_PREFIX=mm
   ```
2. **`config/cookies.txt`** *(Opcional pero muy recomendado)*:
   Copiá tu archivo `cookies.txt` a la carpeta `config/` para mantener el acceso autenticado a YouTube y evitar restricciones de IP o captchas.

---

### 4. Puesta en Marcha

Podés iniciar el bot inmediatamente con:
- Doble clic sobre el archivo **`run_bot.bat`**.
- O desde PowerShell:
  ```powershell
  .\run_bot.bat
  ```

---

### 5. Formas Más Óptimas de Ejecución en PC de Escritorio

En una PC de escritorio no siempre querés tener una ventana negra de consola abierta en tu barra de tareas todo el tiempo. Existen dos métodos profesionales para optimizar la ejecución:

#### Opción A: Ejecutar como Servicio de Windows con NSSM (Recomendado 🌟)
Con **NSSM** (*Non-Sucking Service Manager*), el bot se convierte en un servicio real de Windows: arranca silenciosamente en segundo plano cuando encendés la PC (incluso sin iniciar sesión) y se reinicia solo si ocurre algún error inesperado.

1. Instalá NSSM mediante winget:
   ```powershell
   winget install NSSM.NSSM
   ```
2. Creá el servicio:
   ```powershell
   nssm install momoDj "C:\projects\momoDj-Bot\venv\Scripts\python.exe" "C:\projects\momoDj-Bot\main.py"
   nssm set momoDj AppDirectory "C:\projects\momoDj-Bot"
   nssm set momoDj Start SERVICE_AUTO_START
   ```
3. Iniciá el servicio:
   ```powershell
   nssm start momoDj
   ```
*(Podés detenerlo o desinstalarlo en cualquier momento con `nssm stop momoDj` o `nssm remove momoDj confirm`).*

#### Opción B: Inicio Automático con el Programador de Tareas (Sin consola)
Si preferís no instalar programas extra:
1. Presioná `Win + R`, escribí `taskschd.msc` y presioná Enter.
2. Hacé clic en **Crear tarea básica**.
3. Nombre: `momoDj Discord Bot`.
4. Desencadenador: **Al iniciar sesión**.
5. Acción: **Iniciar un programa**.
   - **Programa o script**: `C:\projects\momoDj-Bot\venv\Scripts\pythonw.exe` *(la 'w' ejecuta en segundo plano sin ventana)*.
   - **Argumentos**: `main.py`
   - **Iniciar en**: `C:\projects\momoDj-Bot`
6. Finalizá la configuración. El bot arrancará automáticamente cada vez que inicies sesión en tu PC.

---

## ☁️ Despliegue en Servidor (VPS Linux / Ubuntu)

Para mantener el servicio activo 24/7 en un servidor en la nube:

### 1. Instalación de Dependencias del Sistema
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

### 4. Servicio del Sistema (`systemd`)
Creá la unidad de servicio:
```bash
sudo nano /etc/systemd/system/momodj.service
```

Configuración sugerida:
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

Monitoreo de logs en vivo:
```bash
sudo journalctl -u momodj -f
```