"""
YouTube Audio Downloader
Módulo para descargar audio de YouTube a partir de nombres de canciones
"""

import os
import re
import time
import random
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import yt_dlp
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, APIC
from mutagen.mp4 import MP4, MP4Cover
import requests
from tqdm import tqdm


class YouTubeAudioDownloader:
    """Descargador de audio desde YouTube con detección inteligente"""
    
    def __init__(self, output_dir: str = "music", min_delay: float = 0.5, max_delay: float = 3.0):
        """
        Inicializa el descargador
        
        Args:
            output_dir: Directorio base donde se guardarán las canciones
            min_delay: Tiempo mínimo de espera entre descargas (segundos)
            max_delay: Tiempo máximo de espera entre descargas (segundos)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Configuración de delays variables para simular comportamiento humano
        self.min_delay = min_delay
        self.max_delay = max_delay
        
        # Archivos de datos
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.blacklist_file = self.data_dir / "blacklist.json"
        self.download_history_file = self.data_dir / "download_history.json"
        
        # Cargar listas
        self.blacklist = self._load_blacklist()
        self.download_history = self._load_download_history()
        
        # Estadísticas de descarga
        self.download_stats = {
            'bytes_downloaded': 0,
            'start_time': None,
            'failed_songs': []
        }
        
        # Palabras clave a evitar en los resultados
        self.blacklist = [
            'remix', 'mix', 'mashup', 'cover', 'karaoke',
            'instrumental', 'acoustic', 'live', 'concert',
            'reaction', 'tutorial', 'how to', 'speedup',
            'speed up', 'slowed', 'reverb', '8d audio',
            'nightcore', 'bass boosted', 'extended', 'hour'
        ]
        
        # Configuración de yt-dlp con hook para velocidad
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'outtmpl': '%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'geo_bypass': True,
            'age_limit': None,
            'progress_hooks': [self._download_progress_hook],
        }
    
    def _download_progress_hook(self, d):
        """Hook para capturar estadísticas de descarga"""
        if d['status'] == 'downloading':
            if 'downloaded_bytes' in d:
                self.download_stats['bytes_downloaded'] = d['downloaded_bytes']
    
    def _load_blacklist(self) -> Dict:
        """Carga la lista negra de canciones fallidas"""
        if self.blacklist_file.exists():
            try:
                with open(self.blacklist_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_blacklist(self):
        """Guarda la lista negra"""
        with open(self.blacklist_file, 'w', encoding='utf-8') as f:
            json.dump(self.blacklist, f, indent=2, ensure_ascii=False)
    
    def _load_download_history(self) -> Dict:
        """Carga el historial de descargas por playlist"""
        if self.download_history_file.exists():
            try:
                with open(self.download_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_download_history(self):
        """Guarda el historial de descargas"""
        with open(self.download_history_file, 'w', encoding='utf-8') as f:
            json.dump(self.download_history, f, indent=2, ensure_ascii=False)
    
    def _add_to_blacklist(self, artist: str, song: str, reason: str):
        """Agrega una canción a la lista negra después de 3 intentos"""
        key = f"{artist} - {song}"
        
        if key not in self.blacklist:
            self.blacklist[key] = {
                'artist': artist,
                'song': song,
                'attempts': 1,
                'last_error': reason,
                'last_attempt': datetime.now().isoformat()
            }
        else:
            self.blacklist[key]['attempts'] += 1
            self.blacklist[key]['last_error'] = reason
            self.blacklist[key]['last_attempt'] = datetime.now().isoformat()
        
        # Si llega a 3 intentos, marcar como bloqueada
        if self.blacklist[key]['attempts'] >= 3:
            self.blacklist[key]['blacklisted'] = True
            print(f"  ⛔ Canción agregada a lista negra después de 3 intentos fallidos")
        
        self._save_blacklist()
    
    def _is_blacklisted(self, artist: str, song: str) -> bool:
        """Verifica si una canción está en la lista negra"""
        key = f"{artist} - {song}"
        return key in self.blacklist and self.blacklist[key].get('blacklisted', False)
    
    def _update_download_history(self, playlist_id: str, track_ids: List[str]):
        """Actualiza el historial de una playlist"""
        self.download_history[playlist_id] = {
            'track_ids': track_ids,
            'last_update': datetime.now().isoformat(),
            'total_tracks': len(track_ids)
        }
        self._save_download_history()
    
    def _get_new_tracks(self, playlist_id: str, current_tracks: List[Tuple[str, str, str]]) -> List[Tuple[str, str, str]]:
        """Obtiene solo las canciones nuevas de una playlist"""
        if playlist_id not in self.download_history:
            # Primera vez, todas son nuevas
            return current_tracks
        
        old_track_ids = set(self.download_history[playlist_id]['track_ids'])
        new_tracks = [
            (track_id, artist, song) 
            for track_id, artist, song in current_tracks 
            if track_id not in old_track_ids
        ]
        
        return new_tracks
    
    def get_download_speed(self) -> str:
        """Calcula la velocidad de descarga"""
        if self.download_stats['start_time'] and self.download_stats['bytes_downloaded'] > 0:
            elapsed = time.time() - self.download_stats['start_time']
            if elapsed > 0:
                speed_mbps = (self.download_stats['bytes_downloaded'] / 1024 / 1024) / elapsed
                return f"{speed_mbps:.2f} MB/s"
        return "Calculando..."
    
    def _human_delay(self):
        """
        Espera un tiempo aleatorio para simular comportamiento humano
        
        Incluye variaciones naturales:
        - 70% del tiempo: delay normal (min_delay a max_delay)
        - 20% del tiempo: delay corto (para simular rapidez ocasional)
        - 10% del tiempo: delay largo (para simular distracciones)
        """
        rand = random.random()
        
        if rand < 0.70:
            # Comportamiento normal
            delay = random.uniform(self.min_delay, self.max_delay)
        elif rand < 0.90:
            # Ocasionalmente más rápido
            delay = random.uniform(self.min_delay * 0.5, self.min_delay)
        else:
            # Ocasionalmente más lento (como si el usuario se distrajera)
            delay = random.uniform(self.max_delay, self.max_delay * 2)
        
        # Agregar micro-variaciones (como clics humanos no perfectos)
        delay += random.uniform(-0.1, 0.1)
        delay = max(0.3, delay)  # Mínimo absoluto de 0.3s
        
        time.sleep(delay)
        
    def _sanitize_filename(self, filename: str) -> str:
        """
        Limpia el nombre de archivo de caracteres inválidos
        
        Args:
            filename: Nombre original del archivo
            
        Returns:
            Nombre limpio y seguro para el sistema de archivos
        """
        # Reemplazar caracteres no permitidos
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        
        # Limitar longitud
        return filename[:200].strip()
    
    def _normalize_artist(self, artist: str) -> str:
        """
        Normaliza el nombre del artista para el nombre de carpeta
        
        Args:
            artist: Nombre del artista
            
        Returns:
            Nombre normalizado
        """
        # Limpiar caracteres especiales
        normalized = re.sub(r'[^\w\s-]', '', artist)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return self._sanitize_filename(normalized)
    
    def _is_valid_result(self, title: str, duration: int) -> bool:
        """
        Valida si un resultado de búsqueda es apropiado
        
        Args:
            title: Título del video
            duration: Duración en segundos
            
        Returns:
            True si el resultado es válido
        """
        title_lower = title.lower()
        
        # Verificar palabras en lista negra
        for word in self.blacklist:
            if word in title_lower:
                return False
        
        # Verificar duración razonable (30 segundos a 10 minutos)
        if duration < 30 or duration > 600:
            return False
        
        return True
    
    def _search_youtube(self, query: str, max_results: int = 5) -> Optional[Dict]:
        """
        Busca en YouTube y selecciona el mejor resultado
        
        Args:
            query: Texto de búsqueda
            max_results: Número máximo de resultados a considerar
            
        Returns:
            Información del mejor video encontrado o None
        """
        search_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'force_generic_extractor': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(search_opts) as ydl:
                # Buscar en YouTube
                results = ydl.extract_info(
                    f"ytsearch{max_results}:{query}",
                    download=False
                )
                
                if not results or 'entries' not in results:
                    return None
                
                # Filtrar y seleccionar el mejor resultado
                for entry in results['entries']:
                    if not entry:
                        continue
                    
                    title = entry.get('title', '')
                    duration = entry.get('duration', 0)
                    
                    # Validar resultado
                    if self._is_valid_result(title, duration):
                        return {
                            'id': entry['id'],
                            'title': title,
                            'url': entry['url'],
                            'duration': duration,
                            'channel': entry.get('channel', ''),
                        }
                
                # Si no hay resultados válidos, usar el primero
                if results['entries']:
                    entry = results['entries'][0]
                    return {
                        'id': entry['id'],
                        'title': entry.get('title', ''),
                        'url': entry['url'],
                        'duration': entry.get('duration', 0),
                        'channel': entry.get('channel', ''),
                    }
                
        except Exception as e:
            print(f"  ⚠️  Error en búsqueda: {e}")
            return None
        
        return None
    
    def _download_audio(self, video_info: Dict, output_path: Path) -> bool:
        """
        Descarga el audio de un video de YouTube
        
        Args:
            video_info: Información del video
            output_path: Ruta donde guardar el archivo
            
        Returns:
            True si la descarga fue exitosa
        """
        temp_output = output_path.parent / "temp_download"
        temp_output.mkdir(exist_ok=True)
        
        opts = self.ydl_opts.copy()
        opts['outtmpl'] = str(temp_output / '%(title)s.%(ext)s')
        
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([f"https://www.youtube.com/watch?v={video_info['id']}"])
            
            # Buscar el archivo descargado
            downloaded_files = list(temp_output.glob("*.mp3"))
            
            if downloaded_files:
                # Mover al destino final
                downloaded_files[0].rename(output_path)
                
                # Limpiar carpeta temporal
                for f in temp_output.iterdir():
                    f.unlink()
                temp_output.rmdir()
                
                return True
            
        except Exception as e:
            print(f"  ❌ Error descargando: {e}")
            
            # Limpiar archivos temporales
            if temp_output.exists():
                for f in temp_output.iterdir():
                    try:
                        f.unlink()
                    except:
                        pass
                try:
                    temp_output.rmdir()
                except:
                    pass
        
        return False
    
    def _get_album_art(self, artist: str, song: str) -> Optional[bytes]:
        """
        Intenta obtener la carátula del álbum desde iTunes API
        
        Args:
            artist: Nombre del artista
            song: Nombre de la canción
            
        Returns:
            Bytes de la imagen o None
        """
        try:
            # Buscar en iTunes API
            query = f"{artist} {song}".replace(' ', '+')
            url = f"https://itunes.apple.com/search?term={query}&entity=song&limit=1"
            
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if data['resultCount'] > 0:
                artwork_url = data['results'][0]['artworkUrl100']
                # Obtener versión de alta resolución
                artwork_url = artwork_url.replace('100x100', '600x600')
                
                img_response = requests.get(artwork_url, timeout=5)
                if img_response.status_code == 200:
                    return img_response.content
        
        except Exception:
            pass
        
        return None
    
    def _add_metadata(self, file_path: Path, artist: str, song: str):
        """
        Agrega metadatos ID3 al archivo de audio
        
        Args:
            file_path: Ruta del archivo de audio
            artist: Nombre del artista
            song: Título de la canción
        """
        try:
            if file_path.suffix.lower() == '.mp3':
                # MP3 con ID3
                audio = MP3(file_path, ID3=ID3)
                
                # Agregar o crear tags
                try:
                    audio.add_tags()
                except:
                    pass
                
                # Título y artista
                audio.tags.add(TIT2(encoding=3, text=song))
                audio.tags.add(TPE1(encoding=3, text=artist))
                
                # Intentar agregar carátula
                artwork = self._get_album_art(artist, song)
                if artwork:
                    audio.tags.add(
                        APIC(
                            encoding=3,
                            mime='image/jpeg',
                            type=3,
                            desc='Cover',
                            data=artwork
                        )
                    )
                
                audio.save()
                
            elif file_path.suffix.lower() == '.m4a':
                # M4A/MP4
                audio = MP4(file_path)
                audio['\xa9nam'] = song
                audio['\xa9ART'] = artist
                
                # Intentar agregar carátula
                artwork = self._get_album_art(artist, song)
                if artwork:
                    audio['covr'] = [MP4Cover(artwork, imageformat=MP4Cover.FORMAT_JPEG)]
                
                audio.save()
        
        except Exception as e:
            print(f"  ⚠️  No se pudieron agregar metadatos: {e}")
    
    def download_song(self, artist: str, song: str, track_id: str = None) -> Tuple[bool, str]:
        """
        Descarga una canción específica
        
        Args:
            artist: Nombre del artista
            song: Título de la canción
            track_id: ID de Spotify (opcional, para tracking)
            
        Returns:
            Tupla (éxito, mensaje)
        """
        # Verificar lista negra
        if self._is_blacklisted(artist, song):
            return False, "En lista negra (3+ intentos fallidos)"
        
        # Crear carpeta del artista
        artist_normalized = self._normalize_artist(artist)
        artist_dir = self.output_dir / artist_normalized
        artist_dir.mkdir(exist_ok=True)
        
        # Nombre del archivo
        filename = self._sanitize_filename(f"{artist} - {song}.mp3")
        output_path = artist_dir / filename
        
        # Verificar si ya existe
        if output_path.exists():
            return True, "Ya existe"
        
        # Buscar en YouTube
        query = f"{artist} - {song} audio oficial"
        print(f"  🔍 Buscando: {artist} - {song}")
        
        video_info = self._search_youtube(query)
        
        if not video_info:
            reason = "No encontrado en YouTube"
            self._add_to_blacklist(artist, song, reason)
            self.download_stats['failed_songs'].append({
                'artist': artist,
                'song': song,
                'reason': reason
            })
            return False, reason
        
        print(f"  📹 Encontrado: {video_info['title'][:60]}...")
        
        # Descargar audio
        print(f"  ⬇️  Descargando...")
        self.download_stats['start_time'] = time.time()
        self.download_stats['bytes_downloaded'] = 0
        
        success = self._download_audio(video_info, output_path)
        
        if not success:
            reason = "Error en descarga (archivo corrupto o bloqueado)"
            self._add_to_blacklist(artist, song, reason)
            self.download_stats['failed_songs'].append({
                'artist': artist,
                'song': song,
                'reason': reason
            })
            return False, reason
        
        # Agregar metadatos
        print(f"  🏷️  Agregando metadatos...")
        self._add_metadata(output_path, artist, song)
        
        # Espera variable para simular comportamiento humano
        self._human_delay()
        
        return True, "Descargado exitosamente"
    
    def download_batch(self, songs: List[Tuple[str, str]], pause_every: int = 10, long_pause: Tuple[float, float] = (30, 60)) -> Dict[str, Dict]:
        """
        Descarga un lote de canciones con pausas inteligentes
        
        Args:
            songs: Lista de tuplas (artista, canción)
            pause_every: Cada cuántas canciones hacer una pausa larga
            long_pause: Rango de tiempo para la pausa larga (min, max) en segundos
            
        Returns:
            Diccionario con resultados de cada descarga
        """
        results = {}
        
        print("=" * 60)
        print("🎵 YOUTUBE AUDIO DOWNLOADER")
        print("=" * 60)
        print(f"📊 Total de canciones: {len(songs)}")
        print(f"⏱️  Delays variables: {self.min_delay}-{self.max_delay}s")
        print(f"☕ Pausa larga cada {pause_every} canciones\n")
        
        for i, (artist, song) in enumerate(songs, 1):
            print(f"[{i}/{len(songs)}] {artist} - {song}")
            
            success, message = self.download_song(artist, song)
            
            results[f"{artist} - {song}"] = {
                'success': success,
                'message': message,
                'artist': artist,
                'song': song
            }
            
            status = "✅" if success else "❌"
            print(f"  {status} {message}\n")
            
            # Pausa larga cada X canciones (simula descansos humanos)
            if i % pause_every == 0 and i < len(songs):
                pause_time = random.uniform(long_pause[0], long_pause[1])
                print(f"☕ Pausa de descanso: {pause_time:.1f}s (cada {pause_every} canciones)")
                time.sleep(pause_time)
                print()
        
        # Resumen final
        successful = sum(1 for r in results.values() if r['success'])
        failed = sum(1 for r in results.values() if not r['success'] and r['message'] != "Ya existe")
        
        print("=" * 60)
        print("✨ DESCARGA COMPLETADA")
        print("=" * 60)
        print(f"✅ Exitosas: {successful}/{len(songs)}")
        print(f"❌ Fallidas: {len(songs) - successful}/{len(songs)}")
        print(f"📁 Ubicación: {self.output_dir.absolute()}")
        
        # Mostrar canciones fallidas
        if self.download_stats['failed_songs']:
            print(f"\n{'=' * 60}")
            print("❌ CANCIONES FALLIDAS")
            print(f"{'=' * 60}")
            for i, failed_song in enumerate(self.download_stats['failed_songs'], 1):
                print(f"\n{i}. {failed_song['artist']} - {failed_song['song']}")
                print(f"   Motivo: {failed_song['reason']}")
        
        print()
        
        return results


def download_songs_from_list(songs: List[Tuple[str, str]], output_dir: str = "music", 
                            min_delay: float = 0.5, max_delay: float = 3.0,
                            pause_every: int = 10) -> Dict:
    """
    Función de conveniencia para descargar canciones con comportamiento humano
    
    Args:
        songs: Lista de tuplas (artista, canción)
        output_dir: Directorio de salida
        min_delay: Tiempo mínimo entre descargas (segundos)
        max_delay: Tiempo máximo entre descargas (segundos)
        pause_every: Hacer pausa larga cada X canciones
        
    Returns:
        Diccionario con resultados
    
    Ejemplo:
        songs = [
            ("Daft Punk", "Get Lucky"),
            ("The Weeknd", "Blinding Lights"),
            ("Billie Eilish", "Bad Guy")
        ]
        
        # Delays cortos (para pocas canciones)
        results = download_songs_from_list(songs, min_delay=0.5, max_delay=2.0)
        
        # Delays más largos (para muchas canciones)
        results = download_songs_from_list(songs, min_delay=1.0, max_delay=4.0, pause_every=15)
    """
    downloader = YouTubeAudioDownloader(output_dir, min_delay, max_delay)
    return downloader.download_batch(songs, pause_every=pause_every)


# Ejemplo de uso
if __name__ == "__main__":
    # Lista de ejemplo
    example_songs = [
        ("Daft Punk", "Get Lucky"),
        ("The Weeknd", "Blinding Lights"),
        ("Billie Eilish", "Bad Guy"),
        ("Arctic Monkeys", "Do I Wanna Know"),
        ("Tame Impala", "The Less I Know The Better")
    ]
    
    # Descargar
    results = download_songs_from_list(example_songs, output_dir="downloads")
    
    # Mostrar resultados detallados
    print("\n📋 Resultados detallados:")
    for song, info in results.items():
        status = "✅" if info['success'] else "❌"
        print(f"{status} {song}: {info['message']}")