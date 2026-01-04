# 🎵 YouTube Music Downloader

> Descarga audio de YouTube con búsqueda inteligente, metadatos automáticos y delays de seguridad

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Stable-success.svg)](https://github.com/TU_USUARIO/youtube-music-downloader)

---

## ✨ Características

- 🔍 **Búsqueda inteligente** - Encuentra automáticamente la mejor versión en YouTube
- 🎚️ **Alta calidad** - Descarga en MP3 320kbps
- 🏷️ **Metadatos automáticos** - Agrega título, artista y carátula del álbum
- 📁 **Organización** - Crea carpetas por artista automáticamente
- ✅ **Prevención de duplicados** - No descarga canciones que ya tienes
- 🛡️ **Sistema de seguridad** - Delays variables para evitar bloqueos
- 🚫 **Filtros inteligentes** - Evita remixes, covers, versiones live

---

## 📋 Requisitos previos

### 1. Python 3.10 o superior

Verifica tu versión:
```bash
python --version
```

Si no lo tienes, descárgalo de [python.org](https://www.python.org/downloads/)

### 2. FFmpeg (OBLIGATORIO)

**Windows:**
```powershell
# Opción 1: Con winget
winget install Gyan.FFmpeg

# Opción 2: Con Chocolatey
choco install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

**Verificar instalación:**
```bash
ffmpeg -version
```

---

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/youtube-music-downloader.git
cd youtube-music-downloader
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 💻 Uso

### Uso básico

```bash
python youtube_downloader.py
```

El script incluye ejemplos de canciones. Modifica el archivo para usar tu propia lista:

```python
# Al final de youtube_downloader.py
example_songs = [
    ("Artista 1", "Canción 1"),
    ("Artista 2", "Canción 2"),
    ("Artista 3", "Canción 3")
]

results = download_songs_from_list(example_songs, output_dir="music")
```

### Uso programático

```python
from youtube_downloader import download_songs_from_list

# Lista de canciones
songs = [
    ("Daft Punk", "Get Lucky"),
    ("The Weeknd", "Blinding Lights"),
    ("Billie Eilish", "Bad Guy")
]

# Descargar
results = download_songs_from_list(
    songs, 
    output_dir="music",
    min_delay=1.0,      # Delay mínimo entre descargas
    max_delay=3.0,      # Delay máximo entre descargas
    pause_every=10      # Pausa larga cada 10 canciones
)

# Ver resultados
for song, info in results.items():
    if info['success']:
        print(f"✅ {song}: {info['message']}")
    else:
        print(f"❌ {song}: {info['message']}")
```

---

## ⚙️ Configuración

### Ajustar delays de seguridad

Para evitar ser bloqueado por YouTube, el bot usa delays variables:

```python
# Delays cortos (10-30 canciones)
download_songs_from_list(songs, min_delay=0.5, max_delay=2.0)

# Delays normales (30-100 canciones) - RECOMENDADO
download_songs_from_list(songs, min_delay=1.0, max_delay=3.0)

# Delays largos (100+ canciones)
download_songs_from_list(songs, min_delay=1.5, max_delay=4.0)
```

### Cambiar calidad de audio

Edita `youtube_downloader.py`:

```python
self.ydl_opts = {
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',  # 128, 192, 256, 320
    }],
}
```

### Cambiar formato de salida

```python
'preferredcodec': 'm4a',  # mp3, m4a, opus, vorbis
```

---

## 📁 Estructura de salida

```
music/
├── Daft Punk/
│   ├── Daft Punk - Get Lucky.mp3
│   └── Daft Punk - One More Time.mp3
├── The Weeknd/
│   ├── The Weeknd - Blinding Lights.mp3
│   └── The Weeknd - Starboy.mp3
└── Billie Eilish/
    └── Billie Eilish - Bad Guy.mp3
```

**Cada archivo incluye:**
- 🎵 Título de la canción
- 👤 Nombre del artista  
- 🖼️ Carátula del álbum (cuando está disponible)
- 🎚️ Calidad de 320 kbps

---

## 🛡️ Sistema de seguridad

### Delays variables

El bot simula comportamiento humano con delays variables:

- **70%** del tiempo: delay normal (1.0-3.0s)
- **20%** del tiempo: más rápido (0.5-1.0s)  
- **10%** del tiempo: más lento (3.0-6.0s)

### Pausas inteligentes

Cada 10-20 canciones, el bot hace una pausa larga de 30-60 segundos, simulando descansos humanos.

### Filtros de búsqueda

Evita automáticamente:
- ❌ Remixes
- ❌ Covers
- ❌ Versiones live/concert
- ❌ Speedup/slowed versions
- ❌ Videos muy cortos (<30s) o muy largos (>10min)

---

## 🐛 Solución de problemas

### Error: "ffmpeg not found"

**Causa:** FFmpeg no está instalado o no está en el PATH.

**Solución:**
```bash
# Instalar FFmpeg (ver sección de requisitos)
winget install Gyan.FFmpeg

# Reiniciar la terminal
```

### Error: "No se encontró la canción"

**Causa:** El nombre es muy específico o la canción es muy nueva/rara.

**Soluciones:**
- Simplifica el nombre (ej: "Get Lucky" en lugar de "Get Lucky (Radio Edit)")
- Verifica que esté en YouTube
- Intenta con el nombre en inglés si es una canción internacional

### Descargas lentas

**Causa:** YouTube está limitando tu IP.

**Solución:**
```python
# Aumenta los delays
download_songs_from_list(songs, min_delay=2.0, max_delay=5.0)
```

### Muchas canciones fallan (>20%)

**Causas comunes:**
- Internet lento o inestable
- YouTube bloqueando temporalmente tu IP
- Nombres de canciones incorrectos

**Solución:**
- Espera 10-15 minutos antes de reintentar
- Usa delays más largos
- Verifica los nombres de las canciones

---

## 📊 Rendimiento esperado

| Cantidad | Tiempo estimado | Configuración |
|----------|-----------------|---------------|
| 10 canciones | 2-5 min | Delays cortos |
| 50 canciones | 10-20 min | Delays normales |
| 100 canciones | 25-40 min | Delays largos |
| 200 canciones | 60-90 min | Delays muy largos |

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/NuevaCaracteristica`)
3. Commit tus cambios (`git commit -m 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Abre un Pull Request

---

## 📝 Changelog

Ver [CHANGELOG.md](CHANGELOG.md) para el historial completo de cambios.

### [1.0.0] - 2024-12-29

#### Agregado
- Descarga de audio desde YouTube con yt-dlp
- Sistema de delays variables para seguridad
- Metadatos y carátulas automáticas
- Organización por carpetas de artista
- Prevención de duplicados
- Filtros inteligentes de búsqueda

---

## ⚠️ Disclaimer

Este proyecto es solo para **uso educativo y personal**. 

- ✅ **Permitido:** Descargar música que ya posees como respaldo
- ❌ **No permitido:** Redistribución, piratería o uso comercial

**Respeta los derechos de autor.** Considera suscribirte a servicios de streaming para apoyar a los artistas.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 🙏 Agradecimientos

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Librería de descarga de YouTube
- [mutagen](https://github.com/quodlibet/mutagen) - Manejo de metadatos de audio
- [iTunes API](https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/) - Carátulas de álbumes

---

## 📧 Contacto

¿Preguntas o sugerencias? Abre un [Issue](https://github.com/TU_USUARIO/youtube-music-downloader/issues)

---

<p align="center">
  Hecho con ❤️ por <a href="https://github.com/TU_USUARIO">Tu Nombre</a>
</p>

<p align="center">
  ⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub
</p>