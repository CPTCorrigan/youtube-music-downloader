"""
Download Manager con interfaz de consola mejorada
"""

import os
import sys
import time
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime, timedelta


class DownloadStats:
    """Estadísticas de descarga en tiempo real"""
    
    def __init__(self, total_songs: int):
        self.total_songs = total_songs
        self.downloaded = 0
        self.failed = 0
        self.skipped = 0
        self.start_time = time.time()
        self.current_song_start = None
        self.song_times = []
        
    def start_song(self):
        """Marca el inicio de descarga de una canción"""
        self.current_song_start = time.time()
    
    def finish_song(self, success: bool, skipped: bool = False):
        """Marca el fin de descarga de una canción"""
        if self.current_song_start:
            elapsed = time.time() - self.current_song_start
            self.song_times.append(elapsed)
        
        if skipped:
            self.skipped += 1
        elif success:
            self.downloaded += 1
        else:
            self.failed += 1
    
    def get_average_time(self) -> float:
        """Calcula el tiempo promedio por canción"""
        if not self.song_times:
            return 0
        return sum(self.song_times) / len(self.song_times)
    
    def get_eta(self) -> str:
        """Calcula el tiempo estimado restante"""
        remaining = self.total_songs - (self.downloaded + self.failed + self.skipped)
        if remaining <= 0 or not self.song_times:
            return "Calculando..."
        
        avg_time = self.get_average_time()
        eta_seconds = avg_time * remaining
        
        return str(timedelta(seconds=int(eta_seconds)))
    
    def get_elapsed_time(self) -> str:
        """Calcula el tiempo transcurrido"""
        elapsed = time.time() - self.start_time
        return str(timedelta(seconds=int(elapsed)))
    
    def get_download_speed(self) -> str:
        """Calcula la velocidad de descarga (canciones/min)"""
        elapsed = time.time() - self.start_time
        if elapsed < 1:
            return "..."
        
        completed = self.downloaded + self.failed + self.skipped
        songs_per_min = (completed / elapsed) * 60
        
        return f"{songs_per_min:.1f} canciones/min"
    
    def get_progress_bar(self, width: int = 40) -> str:
        """Genera una barra de progreso visual"""
        completed = self.downloaded + self.failed + self.skipped
        progress = completed / self.total_songs if self.total_songs > 0 else 0
        
        filled = int(width * progress)
        bar = '█' * filled + '░' * (width - filled)
        percentage = progress * 100
        
        return f"[{bar}] {percentage:.1f}%"


class ConsoleUI:
    """Interfaz de consola mejorada"""
    
    # Colores ANSI
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    
    @staticmethod
    def clear():
        """Limpia la consola"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def print_header(text: str):
        """Imprime un encabezado destacado"""
        line = "=" * 60
        print(f"\n{ConsoleUI.CYAN}{ConsoleUI.BOLD}{line}{ConsoleUI.RESET}")
        print(f"{ConsoleUI.CYAN}{ConsoleUI.BOLD}{text.center(60)}{ConsoleUI.RESET}")
        print(f"{ConsoleUI.CYAN}{ConsoleUI.BOLD}{line}{ConsoleUI.RESET}\n")
    
    @staticmethod
    def print_success(text: str):
        """Imprime texto de éxito"""
        print(f"{ConsoleUI.GREEN}✅ {text}{ConsoleUI.RESET}")
    
    @staticmethod
    def print_error(text: str):
        """Imprime texto de error"""
        print(f"{ConsoleUI.RED}❌ {text}{ConsoleUI.RESET}")
    
    @staticmethod
    def print_warning(text: str):
        """Imprime texto de advertencia"""
        print(f"{ConsoleUI.YELLOW}⚠️  {text}{ConsoleUI.RESET}")
    
    @staticmethod
    def print_info(text: str):
        """Imprime texto informativo"""
        print(f"{ConsoleUI.BLUE}ℹ️  {text}{ConsoleUI.RESET}")
    
    @staticmethod
    def print_stats(stats: DownloadStats, download_speed: str = "..."):
        """Imprime estadísticas en tiempo real"""
        print(f"\n{ConsoleUI.BOLD}📊 ESTADÍSTICAS EN TIEMPO REAL{ConsoleUI.RESET}")
        print(f"{'─' * 60}")
        print(f"🎵 Total:          {stats.total_songs} canciones")
        print(f"✅ Descargadas:    {stats.downloaded}")
        print(f"⏭️  Ya existían:    {stats.skipped}")
        print(f"❌ Fallidas:       {stats.failed}")
        print(f"⏱️  Tiempo:         {stats.get_elapsed_time()}")
        print(f"⏳ ETA:            {stats.get_eta()}")
        print(f"🚀 Velocidad:      {stats.get_download_speed()}")
        print(f"📶 Descarga:       {download_speed}")
        print(f"\n{stats.get_progress_bar()}\n")
    
    @staticmethod
    def print_menu(options: List[str]) -> int:
        """Muestra un menú y retorna la opción seleccionada"""
        print(f"\n{ConsoleUI.BOLD}📋 OPCIONES:{ConsoleUI.RESET}\n")
        
        for i, option in enumerate(options, 1):
            print(f"  {ConsoleUI.CYAN}{i}.{ConsoleUI.RESET} {option}")
        
        print()
        
        while True:
            try:
                choice = int(input(f"{ConsoleUI.BOLD}👉 Selecciona una opción: {ConsoleUI.RESET}"))
                if 1 <= choice <= len(options):
                    return choice
                else:
                    ConsoleUI.print_error(f"Por favor selecciona un número entre 1 y {len(options)}")
            except ValueError:
                ConsoleUI.print_error("Por favor ingresa un número válido")
    
    @staticmethod
    def confirm(message: str) -> bool:
        """Solicita confirmación del usuario"""
        response = input(f"{ConsoleUI.YELLOW}❓ {message} (s/n): {ConsoleUI.RESET}").lower()
        return response in ['s', 'si', 'sí', 'y', 'yes']
    
    @staticmethod
    def input_text(prompt: str) -> str:
        """Solicita entrada de texto"""
        return input(f"{ConsoleUI.CYAN}📝 {prompt}: {ConsoleUI.RESET}").strip()
    
    @staticmethod
    def print_song_status(index: int, total: int, artist: str, song: str, status: str, success: bool):
        """Imprime el estado de una canción"""
        icon = "✅" if success else "❌"
        color = ConsoleUI.GREEN if success else ConsoleUI.RED
        
        print(f"\n{ConsoleUI.BOLD}[{index}/{total}]{ConsoleUI.RESET} {artist} - {song}")
        print(f"  {color}{icon} {status}{ConsoleUI.RESET}")


def create_main_menu():
    """Crea el menú principal de la aplicación"""
    ui = ConsoleUI()
    
    ui.clear()
    ui.print_header("🎵 YOUTUBE MUSIC DOWNLOADER")
    
    print(f"{ConsoleUI.MAGENTA}{'─' * 60}{ConsoleUI.RESET}")
    print(f"{ConsoleUI.MAGENTA}   Descarga música de YouTube con integración de Spotify{ConsoleUI.RESET}")
    print(f"{ConsoleUI.MAGENTA}{'─' * 60}{ConsoleUI.RESET}\n")
    
    options = [
        "🎵 Descargar desde lista manual",
        "📀 Descargar playlist de Spotify (por URL)",
        "👤 Ver mis playlists de Spotify y descargar",
        "🔄 Actualizar playlists descargadas (sincronizar)",
        "📋 Descargar múltiples playlists de Spotify",
        "⛔ Ver/Gestionar lista negra",
        "⚙️  Configurar delays de seguridad",
        "📁 Ver carpeta de descargas",
        "❌ Salir"
    ]
    
    return ui.print_menu(options)


def show_delay_config():
    """Muestra y permite configurar los delays"""
    ui = ConsoleUI()
    
    ui.clear()
    ui.print_header("⚙️ CONFIGURACIÓN DE DELAYS")
    
    print(f"{ConsoleUI.BOLD}Presets recomendados:{ConsoleUI.RESET}\n")
    print(f"  {ConsoleUI.CYAN}1.{ConsoleUI.RESET} Rápido      (10-30 canciones)   → 0.5-2.0s")
    print(f"  {ConsoleUI.CYAN}2.{ConsoleUI.RESET} Normal      (30-100 canciones)  → 1.0-3.0s")
    print(f"  {ConsoleUI.CYAN}3.{ConsoleUI.RESET} Seguro      (100-200 canciones) → 1.5-4.0s {ConsoleUI.GREEN}[Recomendado]{ConsoleUI.RESET}")
    print(f"  {ConsoleUI.CYAN}4.{ConsoleUI.RESET} Muy seguro  (200+ canciones)    → 2.0-5.0s")
    print(f"  {ConsoleUI.CYAN}5.{ConsoleUI.RESET} Personalizado")
    print(f"  {ConsoleUI.CYAN}6.{ConsoleUI.RESET} Volver al menú principal\n")
    
    choice = input(f"{ConsoleUI.BOLD}👉 Selecciona: {ConsoleUI.RESET}")
    
    presets = {
        '1': (0.5, 2.0, 10),
        '2': (1.0, 3.0, 15),
        '3': (1.5, 4.0, 20),
        '4': (2.0, 5.0, 25)
    }
    
    if choice in presets:
        return presets[choice]
    elif choice == '5':
        try:
            min_d = float(ui.input_text("Delay mínimo (segundos)"))
            max_d = float(ui.input_text("Delay máximo (segundos)"))
            pause = int(ui.input_text("Pausa larga cada X canciones"))
            return (min_d, max_d, pause)
        except ValueError:
            ui.print_error("Valores inválidos, usando configuración por defecto")
            return (1.5, 4.0, 20)
    else:
        return None


# Ejemplo de uso
if __name__ == "__main__":
    ui = ConsoleUI()
    
    # Simular estadísticas
    stats = DownloadStats(total_songs=50)
    
    for i in range(50):
        stats.start_song()
        time.sleep(0.1)  # Simular descarga
        stats.finish_song(success=True)
        
        if i % 10 == 0:
            ui.clear()
            ui.print_header("🎵 DESCARGANDO MÚSICA")
            ui.print_stats(stats)
    
    ui.print_success("¡Descarga completada!")