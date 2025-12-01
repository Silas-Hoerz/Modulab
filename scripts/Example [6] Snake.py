# SnakeGame.py
# Ein High-End Snake-Spiel für Modulab.
# Robust, performant und visuell aufgewertet.

import tkinter as tk
from tkinter import font as tkfont
import random

# =============================================================================
# KONFIGURATION & STYLING
# =============================================================================

class Config:
    # Dimensionen
    WIDTH = 600
    HEIGHT = 600
    GRID_SIZE = 25
    
    # Gameplay
    INITIAL_SPEED = 150  # Start-Geschwindigkeit in ms
    MIN_SPEED = 60       # Maximale Geschwindigkeit (kleiner ist schneller)
    SPEED_DECREMENT = 2  # Pro gefressenem Apfel wird es X ms schneller
    
    # Farben (Modernes Dark Theme)
    COL_BG = "#212121"           # Dunkles Anthrazit
    COL_GRID_ODD = "#262626"     # Leicht helleres Schachbrettmuster (optional)
    COL_SNAKE_HEAD = "#00E676"   # Helles Neon-Grün
    COL_SNAKE_BODY = "#2E7D32"   # Dunkleres Grün
    COL_FOOD = "#FF5252"         # Helles Rot/Pink
    COL_TEXT = "#ECEFF1"         # Fast Weiß
    COL_ACCENT = "#FFD740"       # Gold für Highscores
    COL_OVERLAY = "#000000"      # Für Abdunklung bei Pause

    HIGHSCORE_KEY = "snake_highscores_v2"

# =============================================================================
# SPIEL-LOGIK KLASSEN
# =============================================================================

class GameState:
    """Verwaltet den Zustand des Spiels, um Spaghetti-Code zu vermeiden."""
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3

class SnakeGame:
    def __init__(self, root, api):
        self.root = root
        self.api = api
        
        # API Manager Shortcuts
        self.log = api.log_mgr
        self.profile = api.profile_mgr

        # Fenster Setup
        self.root.title("Modulab Snake")
        self.root.resizable(False, False)
        self.root.configure(bg=Config.COL_BG)

        # UI Schriftarten initialisieren
        self.font_big = tkfont.Font(family="Helvetica", size=30, weight="bold")
        self.font_med = tkfont.Font(family="Helvetica", size=14, weight="bold")
        self.font_small = tkfont.Font(family="Consolas", size=10)

        # Variablen
        self.state = GameState.MENU
        self.score = 0
        self.high_score = 0
        self.direction = 'down'
        self.next_direction = 'down' # Puffer für schnelle Eingaben
        self.speed = Config.INITIAL_SPEED
        self.snake_coords = []
        self.food_coords = None
        self.player_name = self.profile.get_current_profile_name() or "Spieler"

        # Highscore laden
        self.load_local_highscore()

        # Canvas erstellen
        self.create_ui()
        
        # Input Binding
        self.bind_keys()
        
        # Fenster zentrieren
        self.center_window()

        # Startbildschirm zeigen
        self.show_menu()

    def create_ui(self):
        """Erstellt das Canvas und die Info-Leiste."""
        # Top Header für Score
        self.header_frame = tk.Frame(self.root, bg=Config.COL_BG, pady=5)
        self.header_frame.pack(fill='x')
        
        self.lbl_score = tk.Label(self.header_frame, text="SCORE: 0", 
                                  font=self.font_med, bg=Config.COL_BG, fg=Config.COL_TEXT)
        self.lbl_score.pack(side='left', padx=20)

        self.lbl_highscore = tk.Label(self.header_frame, text=f"BEST: {self.high_score}", 
                                      font=self.font_med, bg=Config.COL_BG, fg=Config.COL_ACCENT)
        self.lbl_highscore.pack(side='right', padx=20)

        # Haupt-Spielfeld
        self.canvas = tk.Canvas(self.root, bg=Config.COL_BG, 
                                height=Config.HEIGHT, width=Config.WIDTH, 
                                highlightthickness=0)
        self.canvas.pack(padx=10, pady=(0, 10))

    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.root.geometry(f'+{int(x)}+{int(y)}')

    def bind_keys(self):
        """Robuste Tastensteuerung."""
        # Bewegung
        self.root.bind('<Left>', lambda e: self.change_dir('left'))
        self.root.bind('<Right>', lambda e: self.change_dir('right'))
        self.root.bind('<Up>', lambda e: self.change_dir('up'))
        self.root.bind('<Down>', lambda e: self.change_dir('down'))
        # Alternativ WASD
        self.root.bind('a', lambda e: self.change_dir('left'))
        self.root.bind('d', lambda e: self.change_dir('right'))
        self.root.bind('w', lambda e: self.change_dir('up'))
        self.root.bind('s', lambda e: self.change_dir('down'))
        
        # Spielsteuerung
        self.root.bind('<space>', self.handle_space)
        self.root.bind('<Escape>', self.handle_escape)
        self.root.bind('p', self.toggle_pause)

    # =========================================================================
    # LOGIK & STATE MANAGEMENT
    # =========================================================================

    def start_game(self):
        """Initialisiert eine neue Runde."""
        self.log.info("[Snake] Neue Runde gestartet.")
        self.state = GameState.PLAYING
        self.canvas.delete("all")
        
        # Reset Stats
        self.score = 0
        self.speed = Config.INITIAL_SPEED
        self.update_score_ui()
        
        # Schlange mittig starten
        start_x = Config.WIDTH // 2
        start_y = Config.HEIGHT // 2
        self.snake_coords = [
            [start_x, start_y],
            [start_x, start_y - Config.GRID_SIZE],
            [start_x, start_y - 2*Config.GRID_SIZE]
        ]
        self.direction = 'down'
        self.next_direction = 'down'
        
        self.spawn_food()
        self.draw_game_objects()
        self.game_loop()

    def game_loop(self):
        """Die Hauptschleife des Spiels (Heartbeat)."""
        # 1. Sicherheitschecks
        if self.state != GameState.PLAYING:
            return
        if self.api._is_stopped:
            self.root.destroy()
            return
        while self.api._is_paused:
            # Wenn Modulab pausiert ist, warten wir hier
            self.root.update()

        # 2. Logik berechnen
        self.direction = self.next_direction # Eingabe anwenden
        x, y = self.snake_coords[0]

        if self.direction == "up": y -= Config.GRID_SIZE
        elif self.direction == "down": y += Config.GRID_SIZE
        elif self.direction == "left": x -= Config.GRID_SIZE
        elif self.direction == "right": x += Config.GRID_SIZE

        # Kollision Wand
        if x < 0 or x >= Config.WIDTH or y < 0 or y >= Config.HEIGHT:
            self.trigger_game_over()
            return

        # Kollision Selbst
        new_head = [x, y]
        if new_head in self.snake_coords:
            self.trigger_game_over()
            return

        # Bewegung ausführen
        self.snake_coords.insert(0, new_head)

        # Essen prüfen
        if self.food_coords and x == self.food_coords[0] and y == self.food_coords[1]:
            self.score += 1
            # Geschwindigkeit erhöhen (Limit beachten)
            self.speed = max(Config.MIN_SPEED, Config.INITIAL_SPEED - (self.score * Config.SPEED_DECREMENT))
            self.update_score_ui()
            self.spawn_food()
        else:
            # Schwanz entfernen (nur wenn nichts gegessen wurde)
            self.snake_coords.pop()

        # 3. Zeichnen
        self.draw_game_objects()

        # 4. Nächster Tick
        self.root.after(self.speed, self.game_loop)

    def draw_game_objects(self):
        """Zeichnet Schlange und Futter neu."""
        self.canvas.delete("all")
        
        # Futter zeichnen (als Kreis für edlen Look)
        fx, fy = self.food_coords
        self.canvas.create_oval(fx+2, fy+2, fx+Config.GRID_SIZE-2, fy+Config.GRID_SIZE-2, 
                                fill=Config.COL_FOOD, outline="")

        # Schlange zeichnen
        for i, (sx, sy) in enumerate(self.snake_coords):
            color = Config.COL_SNAKE_HEAD if i == 0 else Config.COL_SNAKE_BODY
            # Etwas kleiner als Grid für "Kachel-Look"
            self.canvas.create_rectangle(sx+1, sy+1, sx+Config.GRID_SIZE-1, sy+Config.GRID_SIZE-1,
                                         fill=color, outline="")

    def spawn_food(self):
        """Plaziert Futter an freier Stelle."""
        while True:
            x = random.randint(0, (Config.WIDTH // Config.GRID_SIZE) - 1) * Config.GRID_SIZE
            y = random.randint(0, (Config.HEIGHT // Config.GRID_SIZE) - 1) * Config.GRID_SIZE
            if [x, y] not in self.snake_coords:
                self.food_coords = [x, y]
                break

    def change_dir(self, new_dir):
        """Puffert die Richtungsänderung um Fehler bei schnellem Drücken zu vermeiden."""
        opposites = {'left': 'right', 'right': 'left', 'up': 'down', 'down': 'up'}
        if new_dir != opposites.get(self.direction):
            self.next_direction = new_dir

    # =========================================================================
    # UI STATES & OVERLAYS
    # =========================================================================

    def show_menu(self):
        self.state = GameState.MENU
        self.canvas.delete("all")
        self.draw_overlay_bg()
        
        cx, cy = Config.WIDTH // 2, Config.HEIGHT // 2
        
        self.canvas.create_text(cx, cy - 60, text="SNAKE PRO", 
                                font=self.font_big, fill=Config.COL_SNAKE_HEAD)
        
        self.canvas.create_text(cx, cy, text="Drücke [LEERTASTE] zum Starten", 
                                font=self.font_med, fill=Config.COL_TEXT)
        
        self.canvas.create_text(cx, cy + 40, text="Steuerung: Pfeiltasten oder WASD\nPause: P", 
                                font=self.font_small, fill="#888888", justify="center")

        # Top 5 Liste im Menü anzeigen
        self.draw_leaderboard(cy + 100)

    def trigger_game_over(self):
        self.state = GameState.GAME_OVER
        self.log.info(f"[Snake] Game Over. Score: {self.score}")
        self.save_highscore()
        self.show_game_over_screen()

    def show_game_over_screen(self):
        self.draw_overlay_bg(alpha_simulated=True) # Halbtransparent simulieren
        cx, cy = Config.WIDTH // 2, Config.HEIGHT // 2
        
        self.canvas.create_text(cx, cy - 50, text="GAME OVER", 
                                font=self.font_big, fill=Config.COL_FOOD)
        
        self.canvas.create_text(cx, cy, text=f"Dein Score: {self.score}", 
                                font=self.font_med, fill=Config.COL_TEXT)
        
        self.canvas.create_text(cx, cy + 50, text="[LEERTASTE] für Neustart\n[ESC] zum Beenden", 
                                font=self.font_small, fill=Config.COL_TEXT, justify="center")

    def toggle_pause(self, event=None):
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
            self.draw_overlay_bg(alpha_simulated=True)
            self.canvas.create_text(Config.WIDTH//2, Config.HEIGHT//2, text="PAUSE", 
                                    font=self.font_big, fill=Config.COL_ACCENT)
        elif self.state == GameState.PAUSED:
            self.state = GameState.PLAYING
            self.draw_game_objects() # UI wiederherstellen
            self.game_loop()

    def draw_overlay_bg(self, alpha_simulated=False):
        """Zeichnet einen dunklen Hintergrund über das Spielfeld."""
        # Tkinter hat keine echte Transparenz auf Canvas, wir nutzen ein Stipple-Muster
        stipple = "gray50" if alpha_simulated else ""
        self.canvas.create_rectangle(0, 0, Config.WIDTH, Config.HEIGHT, 
                                     fill=Config.COL_OVERLAY, stipple=stipple)

    def draw_leaderboard(self, start_y):
        try:
            highscores = self.profile.read(Config.HIGHSCORE_KEY) or []
            if not highscores: return
            
            self.canvas.create_text(Config.WIDTH // 2, start_y, text="--- TOP 5 ---",
                                    font=self.font_small, fill=Config.COL_ACCENT)
            
            for i, entry in enumerate(highscores[:5]):
                txt = f"{i+1}. {entry.get('name', '?')} ... {entry.get('score', 0)}"
                self.canvas.create_text(Config.WIDTH // 2, start_y + 20 + (i*18), 
                                        text=txt, font=self.font_small, fill=Config.COL_TEXT)
        except Exception:
            pass # Fehler im Leaderboard sollen das Menü nicht zerstören

    # =========================================================================
    # DATEN & EVENTS
    # =========================================================================

    def update_score_ui(self):
        self.lbl_score.config(text=f"SCORE: {self.score}")
        if self.score > self.high_score:
            self.lbl_highscore.config(text=f"BEST: {self.score}")

    def handle_space(self, event):
        if self.state == GameState.MENU or self.state == GameState.GAME_OVER:
            self.start_game()
        elif self.state == GameState.PAUSED:
            self.toggle_pause()

    def handle_escape(self, event):
        if self.state == GameState.PLAYING:
            self.toggle_pause()
        else:
            self.root.destroy()

    def load_local_highscore(self):
        """Lädt den besten Score, um ihn im UI anzuzeigen."""
        try:
            data = self.profile.read(Config.HIGHSCORE_KEY) or []
            if data:
                # Suche den höchsten Score in der Liste
                self.high_score = max(item['score'] for item in data)
        except Exception as e:
            self.log.error(f"[Snake] Fehler beim Laden der Highscores: {e}")

    def save_highscore(self):
        """Speichert den aktuellen Score sicher ab."""
        try:
            current_list = self.profile.read(Config.HIGHSCORE_KEY) or []
            new_entry = {"name": self.player_name, "score": self.score}
            current_list.append(new_entry)
            
            # Sortieren und Beschneiden
            current_list.sort(key=lambda x: x.get('score', 0), reverse=True)
            current_list = current_list[:10] # Top 10 behalten
            
            self.profile.write(Config.HIGHSCORE_KEY, current_list)
            self.log.info("[Snake] Highscore gespeichert.")
            
            # Update lokaler Highscore für Anzeige
            if self.score > self.high_score:
                self.high_score = self.score
                
        except Exception as e:
            self.log.error(f"[Snake] CRITICAL: Konnte Highscore nicht speichern: {e}")


# =============================================================================
# EINSTIEGSPUNKT
# =============================================================================

def run_experiment(api):
    """Startet das Spiel im Kontext von Modulab."""
    
    # 1. Profil-Check
    if not api.profile_mgr.get_current_profile_name():
        # Fallback: Versuche es trotzdem, aber warne
        api.log_mgr.warning("[Snake] Warnung: Kein Profil geladen. Highscores werden eventuell nicht korrekt zugeordnet.")

    api.log_mgr.info("Starte Snake Engine...")

    try:
        root = tk.Tk()
        # Setze das Fenster in den Fokus, damit Tastatureingaben sofort gehen
        root.focus_force() 
        
        game = SnakeGame(root, api)
        
        # Blockiert den Worker-Thread, bis das Fenster geschlossen wird.
        # Das ist das gewünschte Verhalten für ein User-Skript in Modulab.
        root.mainloop()

        api.log_mgr.info("[Snake] Beendet.")
        
    except Exception as e:
        api.log_mgr.error(f"[Snake] Absturz: {e}", exc_info=True)