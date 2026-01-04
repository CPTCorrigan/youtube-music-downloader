"""
Spotify Integration Module
Obtiene canciones de playlists de Spotify para descargar
"""

import os
from typing import List, Tuple, Optional
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv


class SpotifyPlaylistExtractor:
    """Extrae canciones de playlists de Spotify"""
    
    def __init__(self):
        """Inicializa la conexión con Spotify"""
        load_dotenv()
        
        # Configurar autenticación
        self.scope = "playlist-read-private playlist-read-collaborative"
        
        try:
            auth_manager = SpotifyOAuth(
                client_id=os.getenv('SPOTIPY_CLIENT_ID'),
                client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
                redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI'),
                scope=self.scope,
                open_browser=True,
                cache_path=".cache"
            )
            
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            
            # Obtener ID del usuario
            try:
                self.user_id = self.sp.current_user()['id']
            except:
                # Método alternativo
                playlists = self.sp.current_user_playlists(limit=1)
                if playlists and playlists['items']:
                    self.user_id = playlists['items'][0]['owner']['id']
                else:
                    self.user_id = "unknown"
                    
            print(f"✅ Conectado a Spotify como: {self.user_id}")
            
        except Exception as e:
            print(f"❌ Error al conectar con Spotify: {e}")
            raise
    
    def _extract_playlist_id(self, playlist_input: str) -> str:
        """Extrae el ID de la playlist desde URL o ID directo"""
        if 'spotify.com/playlist/' in playlist_input:
            playlist_id = playlist_input.split('playlist/')[-1].split('?')[0]
        else:
            playlist_id = playlist_input
        
        return playlist_id
    
    def get_playlist_info(self, playlist_input: str) -> dict:
        """
        Obtiene información básica de la playlist
        
        Args:
            playlist_input: URL o ID de la playlist
            
        Returns:
            Diccionario con información de la playlist
        """
        playlist_id = self._extract_playlist_id(playlist_input)
        
        try:
            playlist = self.sp.playlist(playlist_id)
            return {
                'id': playlist['id'],
                'name': playlist['name'],
                'owner': playlist['owner']['display_name'],
                'total_tracks': playlist['tracks']['total'],
                'description': playlist.get('description', ''),
                'public': playlist['public']
            }
        except Exception as e:
            print(f"❌ Error obteniendo información de playlist: {e}")
            return None
    
    def get_all_tracks(self, playlist_input: str) -> List[Tuple[str, str, str]]:
        """
        Obtiene todas las canciones de una playlist
        
        Args:
            playlist_input: URL o ID de la playlist
            
        Returns:
            Lista de tuplas (track_id, artista, canción)
        """
        playlist_id = self._extract_playlist_id(playlist_input)
        
        songs = []
        
        try:
            results = self.sp.playlist_tracks(playlist_id)
            
            while results:
                for item in results['items']:
                    if not item['track']:
                        continue
                    
                    track = item['track']
                    
                    if not track['artists'] or not track['id']:
                        continue
                    
                    track_id = track['id']
                    artist = track['artists'][0]['name']
                    song_name = track['name']
                    
                    # Limpiar el nombre de la canción (quitar "(feat. ...)")
                    song_name = song_name.split(' (feat.')[0]
                    song_name = song_name.split(' [')[0]
                    
                    songs.append((track_id, artist, song_name))
                
                # Paginación
                if results['next']:
                    results = self.sp.next(results)
                else:
                    break
            
            return songs
            
        except Exception as e:
            print(f"❌ Error obteniendo canciones: {e}")
            return []
    
    def get_user_playlists(self) -> List[dict]:
        """
        Obtiene todas las playlists del usuario
        
        Returns:
            Lista de diccionarios con info de playlists
        """
        playlists = []
        
        try:
            results = self.sp.current_user_playlists(limit=50)
            
            while results:
                for playlist in results['items']:
                    playlists.append({
                        'id': playlist['id'],
                        'name': playlist['name'],
                        'owner': playlist['owner']['display_name'],
                        'total_tracks': playlist['tracks']['total'],
                        'public': playlist['public']
                    })
                
                if results['next']:
                    results = self.sp.next(results)
                else:
                    break
            
            return playlists
            
        except Exception as e:
            print(f"❌ Error obteniendo playlists del usuario: {e}")
            return []
    
    def get_multiple_playlists(self, playlist_inputs: List[str]) -> List[Tuple[str, str, str]]:
        """
        Obtiene canciones de múltiples playlists
        
        Args:
            playlist_inputs: Lista de URLs o IDs de playlists
            
        Returns:
            Lista de tuplas (track_id, artista, canción) sin duplicados
        """
        all_songs = []
        seen = set()
        
        for playlist_input in playlist_inputs:
            print(f"\n📀 Obteniendo playlist...")
            
            info = self.get_playlist_info(playlist_input)
            if info:
                print(f"   Nombre: {info['name']}")
                print(f"   Canciones: {info['total_tracks']}")
            
            songs = self.get_all_tracks(playlist_input)
            
            # Filtrar duplicados
            for track_id, artist, song in songs:
                if track_id not in seen:
                    seen.add(track_id)
                    all_songs.append((track_id, artist, song))
        
        return all_songs


def get_songs_from_spotify_playlist(playlist_url: str) -> List[Tuple[str, str, str]]:
    """
    Función de conveniencia para obtener canciones de Spotify
    
    Args:
        playlist_url: URL o ID de la playlist de Spotify
        
    Returns:
        Lista de tuplas (track_id, artista, canción)
    
    Ejemplo:
        songs = get_songs_from_spotify_playlist("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
    """
    extractor = SpotifyPlaylistExtractor()
    
    info = extractor.get_playlist_info(playlist_url)
    if not info:
        return []
    
    print(f"\n📀 Playlist: {info['name']}")
    print(f"👤 Por: {info['owner']}")
    print(f"🎵 Total: {info['total_tracks']} canciones\n")
    
    songs = extractor.get_all_tracks(playlist_url)
    
    print(f"✅ {len(songs)} canciones obtenidas")
    
    return songs


# Ejemplo de uso
if __name__ == "__main__":
    # Obtener canciones de una playlist
    playlist_url = input("🎯 Ingresa la URL de la playlist de Spotify: ").strip()
    
    songs = get_songs_from_spotify_playlist(playlist_url)
    
    if songs:
        print(f"\n📋 Primeras 5 canciones:")
        for i, (artist, song) in enumerate(songs[:5], 1):
            print(f"  {i}. {artist} - {song}")
        
        print(f"\n... y {len(songs) - 5} más" if len(songs) > 5 else "")