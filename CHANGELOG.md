# 📝 Changelog - momoDj

Todos los cambios notables, mejoras arquitectónicas y correcciones de errores en **momoDj** están documentados en este archivo.

---

## [2.1.0] - 2026-09-10

### 🚀 Novedades y Comandos
- **Comando de ayuda `mmhelp`**:
  - Implementación del comando interactivo `mmhelp` (con alias `mmayuda`, `mmcomandos`, `mhelp`, `help_mm`).
  - Soporte de invocación tanto con prefijo contiguo (`mmhelp`) como con espacio (`mm help`).
  - Actualización del manejador global de errores para guiar a los usuarios hacia `mmhelp`.

### 🛡️ Correcciones de Conexión de Voz (Voice Gateway & Cifrado DAVE)

#### 1. Corrección de desconexión inmediata `WebSocket closed with 4006`
- **Diagnóstico**: Discord dio de baja definitivamente la versión 4 de su Voice Gateway (`/?v=4`) y migró sus servidores de medios a la estructura `*.discord.media:port`. Las versiones anteriores de `discord.py` (< 2.6.0) utilizaban el protocolo v4 y recortaban erróneamente los puertos con `rpartition(':')`, causando un rechazo inmediato por parte de Discord (*"Session is no longer valid"*).
- **Solución**: Migración de la biblioteca a Voice Gateway v8, que procesa adecuadamente los endpoints de medios y mantiene la integridad del socket de voz.

#### 2. Soporte obligatorio del protocolo DAVE (Error `WebSocket closed with 4017`)
- **Diagnóstico**: Discord implementó e impuso de forma obligatoria el protocolo **DAVE** (*Discord Audio & Video End-to-End Encryption*, basado en IETF MLS RFC 9420) en todos sus canales de voz estándar. Aquellos clientes que no anunciaban `max_dave_protocol_version > 0` durante el handshake de `IDENTIFY` eran desconectados inmediatamente con el código de cierre `4017` (`DAVE_PROTOCOL_REQUIRED`).
- **Solución**:
  - Actualización de dependencias a **`discord.py[voice]==2.7.1`**.
  - Integración nativa de la librería binaria **`davey`** (`davey>=0.1.0`), la cual gestiona los paquetes de claves MLS, negocia las transiciones de época criptográficas y cifra los paquetes de audio Opus al vuelo.

#### 3. Estandarización en CPython 3.13 oficial de Windows
- **Diagnóstico**: Entornos virtuales basados en MinGW/MSYS2 (`mingw_x86_64_ucrt_gnu`) no reconocen las ruedas binarias precompiladas para Windows (`win_amd64`) de `davey`. Como resultado, `pip` intentaba compilar `davey` y `maturin` desde código fuente utilizando Rust, fallando por requerir características del compilador no estabilizadas (`edition2024`).
- **Solución**: Se estandarizó el uso de **Python 3.13 oficial de Windows** (`py -3.13 -m venv venv`), permitiendo la instalación inmediata de paquetes precompilados de 64 bits sin necesidad de herramientas de compilación locales.

#### 4. Empaquetado local de `libopus-0.dll` y limpieza de sockets
- **Empaquetado autónomo**: Se incorporó el binario `libopus-0.dll` (x64) en la raíz del proyecto y se adaptó `config/settings.py` para priorizar la carga local. Esto elimina la dependencia de tener herramientas como MSYS2 instaladas en el sistema operativo del host.
- **Limpieza de sesiones zombi**: Se incorporó en `_ensure_voice_connection` la detección y desconexión forzosa de clientes de voz huérfanos antes de abrir una nueva sesión.
- **Progreso asíncrono no bloqueante**: En `GuildMusicPlayer._after_playback`, se desacopló el avance de la cola utilizando `fut.add_done_callback` en lugar del método bloqueante `fut.result()`, evitando congelamientos en el hilo de audio de Discord al pasar a la siguiente pista.

---

## [2.0.0] - Versión Inicial Estable
- Arquitectura desacoplada en cogs (`MusicCommands`) y controlador orientado a objetos (`GuildMusicPlayer`).
- Cola bidireccional (`MusicQueue`) con comandos `mmskip` y `mmprev` (historial de reproducción).
- Integración de `yt-dlp` con soporte para listas de reproducción, búsquedas por texto y cookies de sesión (`config/cookies.txt`).
- Extracción de metadatos de Spotify mediante oEmbed público y derivación automática a YouTube.
- Panel interactivo de botones Discord UI (`discord.ui.View`) en `mmnowplaying`.
- Monitor de inactividad (`InactivityMonitor`) con temporizador de desconexión automática a los 30 segundos en canales vacíos.
