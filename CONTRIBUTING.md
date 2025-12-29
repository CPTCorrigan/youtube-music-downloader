# Contribuir a YouTube Music Downloader

¡Gracias por tu interés en contribuir! 🎉

## 🚀 Cómo contribuir

### 1. Reportar bugs

Si encuentras un bug, abre un [Issue](https://github.com/TU_USUARIO/youtube-music-downloader/issues) con:

- **Descripción clara** del problema
- **Pasos para reproducir** el bug
- **Comportamiento esperado** vs **comportamiento actual**
- **Sistema operativo** y **versión de Python**
- **Logs de error** (si aplica)

**Ejemplo:**
```markdown
## Descripción
Las canciones con caracteres especiales fallan al descargarse.

## Pasos para reproducir
1. Ejecutar `python youtube_downloader.py`
2. Intentar descargar "Møтive - Ñoño"
3. Error: "Invalid filename"

## Sistema
- OS: Windows 11
- Python: 3.10.5
- yt-dlp: 2024.1.1
```

### 2. Sugerir nuevas características

Abre un [Issue](https://github.com/TU_USUARIO/youtube-music-downloader/issues) con la etiqueta `enhancement`:

- **Descripción** de la característica
- **Caso de uso** (¿por qué es útil?)
- **Propuesta de implementación** (opcional)

### 3. Contribuir código

#### Fork y clone

```bash
# Fork el repositorio en GitHub
# Luego clona tu fork
git clone https://github.com/TU_USUARIO/youtube-music-downloader.git
cd youtube-music-downloader
```

#### Crear rama

```bash
# Crear rama para tu feature
git checkout -b feature/nombre-descriptivo

# O para un bugfix
git checkout -b fix/descripcion-bug
```

#### Hacer cambios

1. Escribe código limpio y documentado
2. Sigue el estilo de código existente
3. Agrega comentarios donde sea necesario
4. Prueba tus cambios

#### Commit

```bash
# Agregar archivos
git add .

# Commit con mensaje descriptivo
git commit -m "feat: agregar soporte para playlists

- Función para leer playlists de archivos .txt
- Validación de formato
- Tests incluidos"
```

**Formato de commits:**
- `feat:` Nueva característica
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `style:` Formato, punto y coma, etc
- `refactor:` Refactorización de código
- `test:` Agregar tests
- `chore:` Mantenimiento

#### Push y Pull Request

```bash
# Push a tu fork
git push origin feature/nombre-descriptivo
```

Luego abre un Pull Request en GitHub con:
- **Título claro**
- **Descripción** de los cambios
- **Screenshots** (si aplica)
- Referencias a **Issues relacionados**

## 📝 Estilo de código

### Python

- Sigue [PEP 8](https://pep8.org/)
- Usa 4 espacios para indentación
- Máximo 100 caracteres por línea
- Docstrings para funciones y clases

**Ejemplo:**
```python
def download_song(self, artist: str, song: str) -> Tuple[bool, str]:
    """
    Descarga una canción específica
    
    Args:
        artist: Nombre del artista
        song: Título de la canción
        
    Returns:
        Tupla (éxito, mensaje)
    """
    # Tu código aquí
    pass
```

### Nombres

- **Variables/funciones:** `snake_case`
- **Clases:** `PascalCase`
- **Constantes:** `UPPER_CASE`

## ✅ Checklist antes del Pull Request

- [ ] El código funciona correctamente
- [ ] Agregaste/actualizaste documentación
- [ ] El código sigue el estilo del proyecto
- [ ] No hay archivos innecesarios (música, cache, etc.)
- [ ] Los commits tienen mensajes descriptivos
- [ ] Actualizaste el CHANGELOG.md si es necesario

## 🙏 Código de conducta

- Sé respetuoso con otros contribuidores
- Acepta críticas constructivas
- Enfócate en lo mejor para el proyecto
- Ayuda a otros cuando sea posible

## ❓ ¿Necesitas ayuda?

No dudes en preguntar en los [Issues](https://github.com/TU_USUARIO/youtube-music-downloader/issues) o abrir un [Discussion](https://github.com/TU_USUARIO/youtube-music-downloader/discussions).

¡Gracias por contribuir! 🎵