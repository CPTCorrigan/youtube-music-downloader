# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto sigue [Versionado Semántico](https://semver.org/lang/es/).

## [2.0.0] - 2024-12-29 (En desarrollo)

### Agregado
- 🎵 Integración completa con Spotify API
- 📀 Descarga automática de playlists completas
- 📋 Soporte para múltiples playlists simultáneas
- 🎨 Interfaz de consola con colores ANSI
- 📊 Medidor de velocidad en tiempo real (canciones/min)
- ⏱️ Cálculo de ETA (tiempo estimado restante)
- 📈 Barra de progreso visual
- ⚙️ Menú interactivo de configuración
- 🎯 Presets de delays (Rápido, Normal, Seguro, Muy Seguro)
- 📁 Botón para abrir carpeta de descargas
- 🔄 Sistema de eliminación automática de duplicados

### Mejorado
- ✨ Sistema de delays ahora incluye micro-variaciones
- 🎨 Mejor formato de salida con estadísticas en vivo
- 📊 Tracking de canciones ya existentes vs nuevas
- ⏸️ Pausas largas más inteligentes cada N canciones

### Archivos nuevos
- `spotify_integration.py` - Módulo de conexión con Spotify
- `download_manager.py` - Gestor de interfaz y estadísticas
- `main_app.py` - Aplicación principal con menú
- `CHANGELOG.md` - Este archivo

### Dependencias nuevas
- `spotipy>=2.23.0` - Cliente de Spotify API
- `python-dotenv>=1.0.0` - Gestión de variables de entorno

---

## [1.0.0] - 2024-12-28

### Agregado
- 🎵 Descarga de audio desde YouTube usando yt-dlp
- 🔍 Búsqueda inteligente con filtros (evita remixes, covers, live)
- ⏱️ Sistema de delays variables para simular comportamiento humano
- 🏷️ Agregado automático de metadatos ID3 (título, artista)
- 🖼️ Descarga de carátulas desde iTunes API
- 📁 Organización automática por carpetas de artista
- ✅ Prevención de duplicados
- 🎚️ Conversión a MP3 320kbps
- 📊 Barra de progreso con tqdm
- 🛡️ Manejo robusto de errores

### Características técnicas
- Delays variables: 70% normal, 20% rápido, 10% lento
- Validación de duración (30s - 10min)
- Limpieza de nombres de archivo
- Carpetas temporales auto-limpiadas
- Pausas largas configurables

### Archivos
- `youtube_downloader.py` - Módulo principal
- `requirements.txt` - Dependencias
- `README.md` - Documentación
- `.gitignore` - Archivos ignorados

### Dependencias
- `yt-dlp>=2024.0.0` - Descarga de YouTube
- `mutagen>=1.47.0` - Metadatos de audio
- `requests>=2.31.0` - Peticiones HTTP
- `tqdm>=4.66.0` - Barras de progreso

---

## Formato de versiones

Este proyecto usa [Versionado Semántico](https://semver.org/):

- **MAJOR.MINOR.PATCH** (ej: 2.1.3)
- **MAJOR**: Cambios incompatibles con versiones anteriores
- **MINOR**: Nueva funcionalidad compatible con versiones anteriores
- **PATCH**: Correcciones de bugs compatibles

### Ejemplos:
- `1.0.0` → `1.0.1`: Bug fix
- `1.0.1` → `1.1.0`: Nueva característica
- `1.1.0` → `2.0.0`: Cambio importante (rompe compatibilidad)

---

## Leyenda de emojis

- 🎵 Nueva funcionalidad principal
- 📀 Integración externa
- 🎨 Interfaz/UI
- ⚙️ Configuración
- 🔧 Herramientas
- 🐛 Corrección de bug
- ⚡ Mejora de rendimiento
- 📝 Documentación
- 🔒 Seguridad
- ♻️ Refactorización
- 🗑️ Eliminación de código/funcionalidad