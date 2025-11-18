# SnakeGame.py
# Ein User-Skript, das ein komplettes Snake-Spiel startet.
# Zeigt, wie man bestehenden Code kapselt und eine Highscore-Liste
# mit Namenseingabe im Modulab-Profil speichert.

# Externe Imports
import tkinter as tk
import random

# =============================================================================
# Spiel-Logik
# =============================================================================

# Spiel-Konstanten
WIDTH = 500
HEIGHT = 500
SPEED = 150       # Etwas schneller als dein Original
SPACE_SIZE = 25   # Etwas größere Blöcke
BODY_SIZE = 2
SNAKE_COLOR = "#00FF00"
FOOD_COLOR = "#FF0000" # Rot ist besser sichtbar
BACKGROUND_COLOR = "#000000"
HIGHSCORE_KEY = "snake_highscores" # Key für die Profildaten

class Snake:
    """Definiert den Schlangenkörper (Daten)"""
    def __init__(self, canvas):
        self.canvas = canvas
        self.body_size = BODY_SIZE
        self.coordinates = []
        self.squares = []

        for i in range(0, BODY_SIZE):
            self.coordinates.append([0, 0])

        for x, y in self.coordinates:
            square = self.canvas.create_rectangle(
                x, y, x + SPACE_SIZE, y + SPACE_SIZE,
                fill=SNAKE_COLOR, tag="snake")
            self.squares.append(square)

class Food:
    """Definiert das Futter (Daten)"""
    def __init__(self, canvas):
        self.canvas = canvas
        x = random.randint(0, (WIDTH // SPACE_SIZE) - 1) * SPACE_SIZE
        y = random.randint(0, (HEIGHT // SPACE_SIZE) - 1) * SPACE_SIZE
        self.coordinates = [x, y]
        self.canvas.create_oval(
            x, y, x + SPACE_SIZE, y + SPACE_SIZE,
            fill=FOOD_COLOR, tag="food")

class SnakeGame:
    """
    Kapselt die gesamte Spiellogik, UI und Highscore-Verwaltung.
    """
    def __init__(self, root, api):
        self.root = root
        self.api = api
        
        # Direkter Zugriff auf die Manager
        self.log_mgr = api.log_mgr
        self.profile_mgr = api.profile_mgr
        
        self.score = 0
        self.direction = 'down'
        self.is_game_over = False

        self.root.title("Modulab Snake")
        self.root.resizable(False, False)

        # UI für das Spiel erstellen
        self.setup_game_ui()
        
        # Spiellogik-Objekte erstellen
        self.snake = Snake(self.canvas)
        self.food = Food(self.canvas)
        
        # Tastatur-Bindings
        self.bind_keys()
        
        # Fenster zentrieren
        self.center_window()
        
        # Spiel-Loop starten
        self.log_mgr.info("[SnakeGame] Spiel gestartet!")
        self.next_turn()

    def setup_game_ui(self):
        """Erstellt die Widgets für das laufende Spiel."""
        self.score_label = tk.Label(self.root, text=f"Score: {self.score}",
                                    font=('consolas', 20))
        self.score_label.pack()

        self.canvas = tk.Canvas(self.root, bg=BACKGROUND_COLOR,
                                height=HEIGHT, width=WIDTH)
        self.canvas.pack()

    def bind_keys(self):
        """Bindet die Pfeiltasten an die Richtungsänderung."""
        self.root.bind('<Left>', lambda event: self.change_direction('left'))
        self.root.bind('<Right>', lambda event: self.change_direction('right'))
        self.root.bind('<Up>', lambda event: self.change_direction('up'))
        self.root.bind('<Down>', lambda event: self.change_direction('down'))

    def center_window(self):
        """Zentriert das Tkinter-Fenster auf dem Bildschirm."""
        self.root.update() # Wichtig, damit winfo_width/height korrekte Werte liefert
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def next_turn(self):
        """Die Haupt-Spielschleife."""
        if self.is_game_over:
            return
        while self.api._is_paused:
            if self.api._is_stopped:
                self.root.destroy()
        if self.api._is_stopped:
            self.root.destroy()

        x, y = self.snake.coordinates[0]

        if self.direction == "up":
            y -= SPACE_SIZE
        elif self.direction == "down":
            y += SPACE_SIZE
        elif self.direction == "left":
            x -= SPACE_SIZE
        elif self.direction == "right":
            x += SPACE_SIZE

        self.snake.coordinates.insert(0, (x, y))
        square = self.canvas.create_rectangle(
            x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=SNAKE_COLOR)
        self.snake.squares.insert(0, square)

        # Futter-Kollision
        if x == self.food.coordinates[0] and y == self.food.coordinates[1]:
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            self.canvas.delete("food")
            self.food = Food(self.canvas)
        else:
            # Letztes Teil entfernen
            del self.snake.coordinates[-1]
            self.canvas.delete(self.snake.squares[-1])
            del self.snake.squares[-1]

        # Kollisionsprüfung
        if self.check_collisions():
            self.game_over()
        else:
            # Nächsten Zug planen
            self.root.after(SPEED, self.next_turn)

    def change_direction(self, new_direction):
        """Ändert die Richtung der Schlange, ohne Umdrehen zu erlauben."""
        if new_direction == 'left' and self.direction != 'right':
            self.direction = new_direction
        elif new_direction == 'right' and self.direction != 'left':
            self.direction = new_direction
        elif new_direction == 'up' and self.direction != 'down':
            self.direction = new_direction
        elif new_direction == 'down' and self.direction != 'up':
            self.direction = new_direction

    def check_collisions(self):
        """Prüft auf Kollisionen mit Wand oder sich selbst."""
        x, y = self.snake.coordinates[0]

        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            return True  # Wand-Kollision

        for body_part in self.snake.coordinates[1:]:
            if x == body_part[0] and y == body_part[1]:
                return True  # Selbst-Kollision

        return False

    def game_over(self):
        """Beendet das Spiel und zeigt den Highscore-Bildschirm."""
        self.is_game_over = True
        self.log_mgr.info(f"[SnakeGame] Game Over! Finaler Score: {self.score}")
        
        # Spiel-Widgets entfernen
        self.canvas.destroy()
        self.score_label.destroy()
        
        # Highscore-UI aufbauen
        self.setup_highscore_ui()

    def setup_highscore_ui(self):
        """Erstellt die UI zur Eingabe des Namens und Anzeige der Rangliste."""
        self.root.title("Game Over - Highscore eintragen")
        
        # Frame für die Eingabe
        entry_frame = tk.Frame(self.root)
        entry_frame.pack(pady=10)

        tk.Label(entry_frame, text=f"Game Over! Dein Score: {self.score}",
                 font=('consolas', 16)).pack()
        
        tk.Label(entry_frame, text="Trage deinen Namen ein:",
                 font=('consolas', 12)).pack(pady=(10, 0))
        
        self.name_entry = tk.Entry(entry_frame, font=('consolas', 12))
        
        # Profilnamen als Standard-Namen vorschlagen
        default_name = self.profile_mgr.get_current_profile_name() or "Spieler"
        self.name_entry.insert(0, default_name)
        self.name_entry.pack(pady=5)
        
        tk.Button(entry_frame, text="Speichern & Beenden",
                  font=('consolas', 12), command=self.save_and_exit).pack(pady=10)

        # Frame für die Rangliste
        list_frame = tk.Frame(self.root)
        list_frame.pack(pady=10, fill="both", expand=True)
        
        tk.Label(list_frame, text="--- Rangliste ---",
                 font=('consolas', 14, 'bold')).pack()

        # Lade existierende Highscores aus dem Profil
        try:
            highscores = self.profile_mgr.read(HIGHSCORE_KEY) or []
            
            if not highscores:
                tk.Label(list_frame, text="Noch keine Highscores!",
                         font=('consolas', 10)).pack()
            
            # Zeige die Top 10
            for i, entry in enumerate(highscores[:10]):
                rank = i + 1
                name = entry.get('name', '???')
                score = entry.get('score', 0)
                tk.Label(list_frame, text=f"{rank}. {name} - {score}",
                         font=('consolas', 10)).pack()
                         
        except Exception as e:
            self.log_mgr.error(f"[SnakeGame] Fehler beim Lesen der Highscores: {e}")
            tk.Label(list_frame, text="Fehler beim Laden der Rangliste.",
                     font=('consolas', 10)).pack()

    def save_and_exit(self):
        """Speichert den neuen Score und schließt das Fenster."""
        player_name = self.name_entry.get()
        if not player_name:
            player_name = "Anonym" # Fallback
            
        self.log_mgr.info(f"[SnakeGame] Speichere Highscore für {player_name}...")
        
        try:
            # 1. Lade die aktuelle Liste
            highscores = self.profile_mgr.read(HIGHSCORE_KEY) or []
            
            # 2. Füge den neuen Score hinzu
            new_entry = {"name": player_name, "score": self.score}
            highscores.append(new_entry)
            
            # 3. Sortiere die Liste (höchster Score zuerst)
            highscores.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            # 4. Behalte nur die Top 10
            highscores = highscores[:10]
            
            # 5. Schreibe die Liste zurück ins Profil
            self.profile_mgr.write(HIGHSCORE_KEY, highscores)
            
            self.log_mgr.info("[SnakeGame] Highscore erfolgreich gespeichert.")
            
        except Exception as e:
            self.log_mgr.error(f"[SnakeGame] Fehler beim Speichern des Highscores: {e}")

        # 6. Fenster schließen
        self.root.destroy()


# =============================================================================
# EXPERIMENT-EINSTIEGSPUNKT
# =============================================================================

def run_experiment(api):
    """
    Diese Funktion wird vom ExperimentManager aufgerufen.
    'api' ist das Objekt mit den Managern.
    """
    
    # Prüfen, ob überhaupt ein Profil geladen ist
    if not api.profile_mgr.get_current_profile_name():
        api.log_mgr.error("[SnakeGame] Spiel kann nicht gestartet werden: "
                          "Bitte zuerst ein Profil in Modulab laden.")
        # Optional: Ein Tkinter-Error-Popup anzeigen
        root_err = tk.Tk()
        root_err.withdraw() # Verstecke das Hauptfenster
        tk.messagebox.showerror("Fehler", "Kein Modulab-Profil geladen!\n"
                                "Highscore kann nicht gespeichert werden.")
        root_err.destroy()
        return

    # Loggen über den LogManager der Haupt-App
    api.log_mgr.info("Starte das 'Snake'-Minispiel!")
    
    # Ein Tkinter-Fenster erstellen.
    # WICHTIG: Tkinter läuft in seiner eigenen 'mainloop' im Worker-Thread.
    # Dies blockiert den Worker-Thread, bis das Fenster geschlossen wird,
    # aber nicht die Haupt-PySide6-UI.
    try:
        root = tk.Tk()
        game = SnakeGame(root, api)
        root.mainloop() # Diese Funktion blockiert, bis das Fenster geschlossen wird
        
        api.log_mgr.info("[SnakeGame] Fenster geschlossen.")
        
    except Exception as e:
        api.log_mgr.error(f"[SnakeGame] Fehler beim Ausführen des Minispiels: {e}", exc_info=True)