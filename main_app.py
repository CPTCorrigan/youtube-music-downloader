"""
YouTube Music Downloader - Aplicación Principal
Integra Spotify, descarga de YouTube y interfaz de usuario
"""

import os
import sys
import time
from pathlib import Path
from typing import List, Tuple

from youtube_downloader import YouTubeAudioDownloader
from spotify_integration import SpotifyPlaylistExtractor, get_songs_from_spotify_playlist
from download_manager import ConsoleUI, DownloadStats, create_main_menu, show_delay_config


class MusicDownloaderApp:
    """Aplicación principal de descarga de música"""
    
    def __init__(self):
        self.ui = ConsoleUI()
        self.output_dir = "music"
        self.delay_config = (1.5, 4.0, 20)  # (min_delay, max_delay, pause_every)
        
    def run(self):
        """Ejecuta la aplicación"""
        while True:
            choice = create_main_menu()
            
            if choice == 1:
                self.download_manual_list()
            elif choice == 2:
                self.download_spotify_playlist()
            elif choice == 3:
                self.browse_user_playlists()
            elif choice == 4:
                self.update_playlists()
            elif choice == 5:
                self.download_multiple_playlists()
            elif choice == 6:
                self.manage_blacklist()
            elif choice == 7:
                self.configure_delays()
            elif choice == 8:
                self.open_downloads_folder()
            elif choice == 9:
                self.ui.print_info("¡Hasta luego! 👋")
                sys.exit(0)
    
    def configure_delays(self):
        """Configura los delays de descarga"""
        config = show_delay_config()
        if config:
            self.delay_config = config
            self.ui.clear()
            self.ui.print_header("⚙️ CONFIGURACIÓN GUARDADA")
            self.ui.print_success(f"Min: {config[0]}s | Max: {config[1]}s | Pausa cada: {config[2]}")
            input("\nPresiona Enter para continuar...")
    
    def download_manual_list(self):
        """Descarga canciones desde lista manual"""
        self.ui.clear()
        self.ui.print_header("🎵 DESCARGA MANUAL")
        
        songs = []
        
        self.ui.print_info("Ingresa las canciones una por una (deja vacío para terminar)\n")
        
        while True:
            artist = self.ui.input_text(f"Artista #{len(songs) + 1} (o Enter para terminar)")
            if not artist:
                break
            
            song = self.ui.input_text(f"Canción")
            if not song:
                break
            
            songs.append((artist, song))
            self.ui.print_success(f"Agregada: {artist} - {song}")
        
        if not songs:
            self.ui.print_warning("No se agregaron canciones")
            input("\nPresiona Enter para continuar...")
            return
        
        self.ui.print_info(f"\n📊 Total: {len(songs)} canciones")
        
        if self.ui.confirm(f"¿Descargar estas {len(songs)} canciones?"):
            self._download_with_progress(songs)
        
        input("\nPresiona Enter para continuar...")
    
    def download_spotify_playlist(self):
        """Descarga una playlist de Spotify"""
        self.ui.clear()
        self.ui.print_header("📀 DESCARGA DESDE SPOTIFY")
        
        try:
            # Conectar con Spotify
            self.ui.print_info("Conectando con Spotify...")
            extractor = SpotifyPlaylistExtractor()
            
            # Solicitar URL
            playlist_url = self.ui.input_text("URL de la playlist de Spotify")
            
            if not playlist_url:
                self.ui.print_warning("URL vacía")
                input("\nPresiona Enter para continuar...")
                return
            
            # Obtener información
            self.ui.print_info("Obteniendo información de la playlist...")
            info = extractor.get_playlist_info(playlist_url)
            
            if not info:
                self.ui.print_error("No se pudo obtener la playlist")
                input("\nPresiona Enter para continuar...")
                return
            
            # Mostrar información
            print(f"\n{self.ui.BOLD}📀 Playlist:{self.ui.RESET} {info['name']}")
            print(f"{self.ui.BOLD}👤 Creador:{self.ui.RESET} {info['owner']}")
            print(f"{self.ui.BOLD}🎵 Canciones:{self.ui.RESET} {info['total_tracks']}")
            
            if not self.ui.confirm(f"\n¿Descargar {info['total_tracks']} canciones?"):
                return
            
            # Obtener canciones
            self.ui.print_info("Obteniendo lista de canciones...")
            songs = extractor.get_all_tracks(playlist_url)
            
            if not songs:
                self.ui.print_error("No se encontraron canciones")
                input("\nPresiona Enter para continuar...")
                return
            
            self.ui.print_success(f"✅ {len(songs)} canciones obtenidas")
            
            # Verificar si ya se descargó antes
            playlist_id = extractor._extract_playlist_id(playlist_url)
            downloader_temp = YouTubeAudioDownloader(
                output_dir=self.output_dir,
                min_delay=self.delay_config[0],
                max_delay=self.delay_config[1]
            )
            
            if playlist_id in downloader_temp.download_history:
                self.ui.print_warning("⚠️  Esta playlist ya fue descargada antes")
                print(f"\n{self.ui.CYAN}💡 Sugerencia:{self.ui.RESET} Usa la opción 4 'Actualizar playlists' para descargar solo canciones nuevas")
                
                if not self.ui.confirm("\n¿Continuar de todos modos y procesar toda la playlist?"):
                    return
            
            # Advertencia si son muchas canciones
            if len(songs) > 100:
                self.ui.print_warning(f"Esta playlist tiene {len(songs)} canciones")
                
                min_d, max_d, pause = self.delay_config
                estimated_time = (len(songs) * (min_d + max_d) / 2) / 60
                
                print(f"\n⏱️  Tiempo estimado: ~{estimated_time:.0f} minutos")
                print(f"⚙️  Delays configurados: {min_d}-{max_d}s (pausa cada {pause})")
                
                if not self.ui.confirm("\n¿Continuar con la descarga?"):
                    return
            
            # Descargar
            self._download_with_progress(songs)
            
        except Exception as e:
            self.ui.print_error(f"Error: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def browse_user_playlists(self):
        """Muestra las playlists del usuario y permite seleccionar"""
        self.ui.clear()
        self.ui.print_header("👤 MIS PLAYLISTS DE SPOTIFY")
        
        try:
            self.ui.print_info("Obteniendo tus playlists...")
            extractor = SpotifyPlaylistExtractor()
            playlists = extractor.get_user_playlists()
            
            if not playlists:
                self.ui.print_error("No se encontraron playlists")
                input("\nPresiona Enter para continuar...")
                return
            
            # Mostrar playlists
            print(f"\n{self.ui.BOLD}📋 TUS PLAYLISTS:{self.ui.RESET}\n")
            for i, playlist in enumerate(playlists, 1):
                print(f"  {self.ui.CYAN}{i}.{self.ui.RESET} {playlist['name']}")
                print(f"     👤 {playlist['owner']} | 🎵 {playlist['total_tracks']} canciones")
            
            print(f"\n  {self.ui.CYAN}0.{self.ui.RESET} Volver al menú principal\n")
            
            # Seleccionar playlist
            try:
                choice = int(input(f"{self.ui.BOLD}👉 Selecciona una playlist (número): {self.ui.RESET}"))
                
                if choice == 0:
                    return
                
                if 1 <= choice <= len(playlists):
                    selected = playlists[choice - 1]
                    playlist_id = selected['id']
                    
                    print(f"\n{self.ui.BOLD}📀 Seleccionada:{self.ui.RESET} {selected['name']}")
                    print(f"{self.ui.BOLD}🎵 Canciones:{self.ui.RESET} {selected['total_tracks']}")
                    
                    if self.ui.confirm(f"\n¿Descargar esta playlist?"):
                        # Obtener canciones
                        self.ui.print_info("Obteniendo canciones...")
                        songs_with_ids = extractor.get_all_tracks(playlist_id)
                        
                        if songs_with_ids:
                            self.ui.print_success(f"✅ {len(songs_with_ids)} canciones obtenidas")
                            self._download_with_progress(songs_with_ids, playlist_id)
                else:
                    self.ui.print_error("Opción inválida")
                    
            except ValueError:
                self.ui.print_error("Por favor ingresa un número")
        
        except Exception as e:
            self.ui.print_error(f"Error: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def update_playlists(self):
        """Actualiza playlists ya descargadas con canciones nuevas"""
        self.ui.clear()
        self.ui.print_header("🔄 ACTUALIZAR PLAYLISTS")
        
        try:
            downloader = YouTubeAudioDownloader(
                output_dir=self.output_dir,
                min_delay=self.delay_config[0],
                max_delay=self.delay_config[1]
            )
            
            history = downloader.download_history
            
            if not history:
                self.ui.print_warning("No hay playlists en el historial")
                self.ui.print_info("Primero descarga una playlist para poder sincronizarla")
                input("\nPresiona Enter para continuar...")
                return
            
            # Mostrar playlists en historial
            print(f"\n{self.ui.BOLD}📋 PLAYLISTS DESCARGADAS:{self.ui.RESET}\n")
            playlist_ids = list(history.keys())
            
            extractor = SpotifyPlaylistExtractor()
            
            valid_playlists = []
            for i, playlist_id in enumerate(playlist_ids, 1):
                info = extractor.get_playlist_info(playlist_id)
                if info:
                    valid_playlists.append((playlist_id, info))
                    last_update = history[playlist_id]['last_update'][:10]  # Solo fecha
                    print(f"  {self.ui.CYAN}{i}.{self.ui.RESET} {info['name']}")
                    print(f"     🎵 {info['total_tracks']} canciones | 📅 Última actualización: {last_update}")
            
            if not valid_playlists:
                self.ui.print_error("No se pudieron cargar las playlists")
                input("\nPresiona Enter para continuar...")
                return
            
            print(f"\n  {self.ui.CYAN}0.{self.ui.RESET} Actualizar TODAS\n")
            print(f"  {self.ui.CYAN}X.{self.ui.RESET} Volver al menú principal\n")
            
            choice = input(f"{self.ui.BOLD}👉 Selecciona (número o X): {self.ui.RESET}").strip()
            
            if choice.upper() == 'X':
                return
            
            try:
                choice_int = int(choice)
                
                if choice_int == 0:
                    # Actualizar todas
                    for playlist_id, info in valid_playlists:
                        print(f"\n🔄 Actualizando: {info['name']}")
                        self._update_single_playlist(playlist_id, extractor, downloader)
                
                elif 1 <= choice_int <= len(valid_playlists):
                    # Actualizar una
                    playlist_id, info = valid_playlists[choice_int - 1]
                    print(f"\n🔄 Actualizando: {info['name']}")
                    self._update_single_playlist(playlist_id, extractor, downloader)
                else:
                    self.ui.print_error("Opción inválida")
                    
            except ValueError:
                self.ui.print_error("Opción inválida")
        
        except Exception as e:
            self.ui.print_error(f"Error: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def _update_single_playlist(self, playlist_id: str, extractor, downloader):
        """Actualiza una playlist individual"""
        # Obtener canciones actuales de Spotify
        current_tracks = extractor.get_all_tracks(playlist_id)
        
        if not current_tracks:
            self.ui.print_error("No se pudieron obtener las canciones de la playlist")
            return
        
        # MÉTODO 1: Verificar historial (si existe)
        new_tracks_by_history = []
        if playlist_id in downloader.download_history:
            new_tracks_by_history = downloader._get_new_tracks(playlist_id, current_tracks)
            
            if not new_tracks_by_history:
                self.ui.print_info("✅ La playlist ya está actualizada (no hay canciones nuevas según historial)")
                
                # MÉTODO 2: Verificar archivos en disco
                if self.ui.confirm("¿Verificar también archivos en disco por si acaso?"):
                    new_tracks_by_history = self._check_existing_files(current_tracks, downloader)
                else:
                    return
            else:
                self.ui.print_success(f"🆕 {len(new_tracks_by_history)} canciones nuevas encontradas (según historial)")
        else:
            # No hay historial, verificar archivos en disco
            self.ui.print_warning("No hay historial de esta playlist")
            self.ui.print_info("Verificando qué canciones ya están descargadas...")
            new_tracks_by_history = self._check_existing_files(current_tracks, downloader)
        
        if not new_tracks_by_history:
            self.ui.print_success("✅ Todas las canciones ya están descargadas")
            return
        
        self.ui.print_success(f"🆕 {len(new_tracks_by_history)} canciones nuevas para descargar")
        
        if self.ui.confirm(f"¿Descargar {len(new_tracks_by_history)} canciones nuevas?"):
            self._download_with_progress(new_tracks_by_history, playlist_id, update_mode=True)
    
    def _check_existing_files(self, tracks: List[Tuple], downloader) -> List[Tuple]:
        """
        Verifica qué canciones ya existen en disco
        
        Args:
            tracks: Lista de tuplas (track_id, artist, song)
            downloader: Instancia del descargador
            
        Returns:
            Lista de canciones que NO existen en disco
        """
        new_tracks = []
        
        for track_data in tracks:
            if len(track_data) == 3:
                track_id, artist, song = track_data
            else:
                track_id = None
                artist, song = track_data
            
            # Construir path esperado
            artist_normalized = downloader._normalize_artist(artist)
            artist_dir = downloader.output_dir / artist_normalized
            filename = downloader._sanitize_filename(f"{artist} - {song}.mp3")
            file_path = artist_dir / filename
            
            # Si NO existe, agregarlo a la lista de nuevas
            if not file_path.exists():
                if len(track_data) == 3:
                    new_tracks.append((track_id, artist, song))
                else:
                    new_tracks.append((artist, song))
        
        return new_tracks
    
    def manage_blacklist(self):
        """Gestiona la lista negra de canciones"""
        self.ui.clear()
        self.ui.print_header("⛔ LISTA NEGRA")
        
        try:
            downloader = YouTubeAudioDownloader(
                output_dir=self.output_dir,
                min_delay=self.delay_config[0],
                max_delay=self.delay_config[1]
            )
            
            blacklist = downloader.blacklist
            
            if not blacklist:
                self.ui.print_info("La lista negra está vacía")
                input("\nPresiona Enter para continuar...")
                return
            
            # Separar por estado
            blacklisted = {k: v for k, v in blacklist.items() if v.get('blacklisted', False)}
            pending = {k: v for k, v in blacklist.items() if not v.get('blacklisted', False)}
            
            # Mostrar estadísticas
            print(f"\n{self.ui.BOLD}📊 ESTADÍSTICAS:{self.ui.RESET}")
            print(f"  ⛔ En lista negra (3+ intentos): {len(blacklisted)}")
            print(f"  ⚠️  Con intentos fallidos (1-2): {len(pending)}")
            
            # Mostrar canciones en lista negra
            if blacklisted:
                print(f"\n{self.ui.BOLD}⛔ CANCIONES BLOQUEADAS:{self.ui.RESET}\n")
                for i, (key, data) in enumerate(blacklisted.items(), 1):
                    print(f"  {i}. {data['artist']} - {data['song']}")
                    print(f"     Intentos: {data['attempts']} | Último error: {data['last_error']}")
            
            # Opciones
            print(f"\n{self.ui.BOLD}OPCIONES:{self.ui.RESET}")
            print(f"  {self.ui.CYAN}1.{self.ui.RESET} Limpiar lista negra completa")
            print(f"  {self.ui.CYAN}2.{self.ui.RESET} Resetear intentos (dar segunda oportunidad)")
            print(f"  {self.ui.CYAN}3.{self.ui.RESET} Volver\n")
            
            choice = input(f"{self.ui.BOLD}👉 Selecciona: {self.ui.RESET}")
            
            if choice == '1':
                if self.ui.confirm("¿Limpiar TODA la lista negra?"):
                    downloader.blacklist = {}
                    downloader._save_blacklist()
                    self.ui.print_success("✅ Lista negra limpiada")
            
            elif choice == '2':
                # Resetear intentos
                for key in blacklist:
                    downloader.blacklist[key]['attempts'] = 0
                    downloader.blacklist[key]['blacklisted'] = False
                downloader._save_blacklist()
                self.ui.print_success("✅ Intentos reseteados, las canciones se volverán a intentar")
        
        except Exception as e:
            self.ui.print_error(f"Error: {e}")
        
        input("\nPresiona Enter para continuar...")
        """Descarga múltiples playlists de Spotify"""
        self.ui.clear()
        self.ui.print_header("📋 DESCARGAS MÚLTIPLES")
        
        try:
            extractor = SpotifyPlaylistExtractor()
            
            playlists = []
            
            self.ui.print_info("Ingresa las URLs de las playlists (deja vacío para terminar)\n")
            
            while True:
                url = self.ui.input_text(f"Playlist #{len(playlists) + 1} (o Enter para terminar)")
                if not url:
                    break
                
                # Validar playlist
                info = extractor.get_playlist_info(url)
                if info:
                    playlists.append(url)
                    self.ui.print_success(f"Agregada: {info['name']} ({info['total_tracks']} canciones)")
                else:
                    self.ui.print_error("URL inválida, intenta de nuevo")
            
            if not playlists:
                self.ui.print_warning("No se agregaron playlists")
                input("\nPresiona Enter para continuar...")
                return
            
            # Obtener todas las canciones
            self.ui.print_info(f"\nObteniendo canciones de {len(playlists)} playlists...")
            all_songs = extractor.get_multiple_playlists(playlists)
            
            self.ui.print_success(f"✅ {len(all_songs)} canciones únicas encontradas")
            
            if self.ui.confirm(f"\n¿Descargar {len(all_songs)} canciones?"):
                self._download_with_progress(all_songs)
        
        except Exception as e:
            self.ui.print_error(f"Error: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def _download_with_progress(self, songs: List[Tuple], playlist_id: str = None, update_mode: bool = False):
        """
        Descarga canciones con barra de progreso y estadísticas
        
        Args:
            songs: Lista de tuplas (track_id, artista, canción)
            playlist_id: ID de la playlist (para tracking)
            update_mode: Si es True, solo descarga canciones nuevas
        """
        self.ui.clear()
        header = "🔄 ACTUALIZANDO PLAYLIST" if update_mode else "⬇️ DESCARGANDO MÚSICA"
        self.ui.print_header(header)
        
        # Crear estadísticas
        stats = DownloadStats(len(songs))
        
        # Crear descargador
        min_delay, max_delay, pause_every = self.delay_config
        downloader = YouTubeAudioDownloader(
            output_dir=self.output_dir,
            min_delay=min_delay,
            max_delay=max_delay
        )
        
        # Mostrar configuración
        print(f"{self.ui.BOLD}📊 CONFIGURACIÓN:{self.ui.RESET}")
        print(f"  📁 Carpeta: {self.output_dir}/")
        print(f"  ⏱️  Delays: {min_delay}-{max_delay}s")
        print(f"  ☕ Pausa cada: {pause_every} canciones")
        if update_mode:
            print(f"  🔄 Modo: Actualización (solo canciones nuevas)")
        print()
        
        # Extraer track_ids para el historial
        track_ids = [song[0] if len(song) >= 3 else None for song in songs]
        
        # Descargar con estadísticas en tiempo real
        actual_downloads = 0  # Contador de descargas reales (no skips)
        
        for i, song_data in enumerate(songs, 1):
            # Parsear datos de la canción
            if len(song_data) == 3:
                track_id, artist, song = song_data
            else:
                track_id = None
                artist, song = song_data
            
            # Actualizar estadísticas
            stats.start_song()
            
            # Mostrar progreso
            print(f"\n{self.ui.BOLD}[{i}/{len(songs)}]{self.ui.RESET} {artist} - {song}")
            
            # Descargar
            success, message = downloader.download_song(artist, song, track_id)
            
            # Actualizar estadísticas
            skipped = (message == "Ya existe")
            stats.finish_song(success, skipped)
            
            # Mostrar resultado
            if success:
                if skipped:
                    self.ui.print_warning(f"Ya existe")
                else:
                    self.ui.print_success(message)
                    actual_downloads += 1  # Solo contar descargas reales
            else:
                self.ui.print_error(message)
            
            # Mostrar estadísticas cada 5 canciones o al final
            if i % 5 == 0 or i == len(songs):
                download_speed = downloader.get_download_speed()
                self.ui.print_stats(stats, download_speed)
            
            # Pausa larga SOLO después de descargas reales (no skips)
            if actual_downloads > 0 and actual_downloads % pause_every == 0 and i < len(songs):
                import random
                pause_time = random.uniform(30, 60)
                print(f"\n{self.ui.YELLOW}☕ Pausa de descanso: {pause_time:.1f}s (después de {actual_downloads} descargas reales){self.ui.RESET}")
                time.sleep(pause_time)
                actual_downloads = 0  # Resetear contador para la próxima pausa
        
        # Actualizar historial si es una playlist de Spotify
        if playlist_id and track_ids:
            downloader._update_download_history(playlist_id, [tid for tid in track_ids if tid])
        
        # Resumen final
        self.ui.clear()
        self.ui.print_header("✨ DESCARGA COMPLETADA")
        download_speed = downloader.get_download_speed()
        self.ui.print_stats(stats, download_speed)
        
        print(f"\n{self.ui.BOLD}📁 Ubicación:{self.ui.RESET} {Path(self.output_dir).absolute()}")
        
        # Resultados
        if stats.downloaded > 0:
            self.ui.print_success(f"{stats.downloaded} canciones descargadas")
        if stats.skipped > 0:
            self.ui.print_info(f"{stats.skipped} canciones ya existían")
        if stats.failed > 0:
            self.ui.print_error(f"{stats.failed} canciones fallaron")
        
        # Mostrar canciones fallidas
        if downloader.download_stats['failed_songs']:
            print(f"\n{self.ui.BOLD}❌ CANCIONES FALLIDAS:{self.ui.RESET}\n")
            for i, failed in enumerate(downloader.download_stats['failed_songs'], 1):
                print(f"  {i}. {failed['artist']} - {failed['song']}")
                print(f"     💬 Motivo: {failed['reason']}")
            
            # Sugerencia
            print(f"\n{self.ui.YELLOW}💡 Tip: Las canciones con 3+ intentos fallidos se agregan automáticamente")
            print(f"   a la lista negra para no seguir intentando descargarlas.{self.ui.RESET}")
            print(f"\n{self.ui.CYAN}   Puedes gestionar la lista negra desde el menú principal (opción 6){self.ui.RESET}")
    
    def open_downloads_folder(self):
        """Abre la carpeta de descargas"""
        path = Path(self.output_dir).absolute()
        
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            self.ui.print_warning("Carpeta creada (aún no hay descargas)")
        
        self.ui.print_info(f"📁 Carpeta: {path}")
        
        try:
            if os.name == 'nt':  # Windows
                os.startfile(path)
            elif sys.platform == 'darwin':  # macOS
                os.system(f'open "{path}"')
            else:  # Linux
                os.system(f'xdg-open "{path}"')
            
            self.ui.print_success("Carpeta abierta")
        except Exception as e:
            self.ui.print_error(f"No se pudo abrir: {e}")
        
        input("\nPresiona Enter para continuar...")


def main():
    """Punto de entrada de la aplicación"""
    try:
        app = MusicDownloaderApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Aplicación cerrada por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()