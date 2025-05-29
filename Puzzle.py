# Erforderliche Module importieren
import tkinter as tk          # GUI-Framework
from tkinter import messagebox # Für Dialogfenster
from PIL import Image, ImageTk # Für Bildverarbeitung
import random                 # Für Zufallszahlen beim Mischen
import os                     # Für Dateisystemzugriff

# Globale Konstanten
TILE_SIZE = 100               # Größe jeder Kachel in Pixeln
GRID_SIZE = 5                 # Anzahl der Kacheln pro Zeile/Spalte (5x5 = 24-Puzzle + 1 leeres Feld)
# Sucht nach der ersten JPEG-Datei im aktuellen Verzeichnis
IMAGE_FILE = next((f for f in os.listdir('.') if f.lower().endswith('.jpg') or f.lower().endswith('.jpg')), None)

class SlidingPuzzle(tk.Frame):
    """
    Hauptklasse für das Schiebepuzzle-Spiel.
    Erbt von tk.Frame und implementiert die Spiellogik.
    """
    def __init__(self, master, image_path):
        """
        Initialisiert das Puzzle mit dem übergebenen Bild.
        
        Args:
            master: Das übergeordnete tkinter-Fenster
            image_path: Pfad zum Bild, das für das Puzzle verwendet wird
        """
        super().__init__(master)
        self.master = master
        self.grid()                            # Platziert den Frame im übergeordneten Fenster
        self.tiles = []                        # 2D-Liste zur Speicherung der Kachelnummern
        self.tile_images = []                  # 2D-Liste zur Speicherung der Kachelbilder
        self.empty_pos = (GRID_SIZE - 1, GRID_SIZE - 1)  # Position des leeren Felds (standardmäßig unten rechts)
        self.load_image(image_path)            # Lädt und verarbeitet das Bild
        self.create_tiles()                    # Initialisiert die Kachelnummern
        self.shuffle()                         # Mischt die Kacheln
        self.draw()                            # Zeichnet das Puzzle auf dem Bildschirm

    def load_image(self, image_path):
        """
        Lädt das Bild und teilt es in einzelne Kacheln auf.
        
        Args:
            image_path: Pfad zum zu ladenden Bild
        """
        img = Image.open(image_path)
        img = img.resize((TILE_SIZE * GRID_SIZE, TILE_SIZE * GRID_SIZE))  # Skaliert das Bild auf die Puzzle-Größe
        self.tile_images = []
        for row in range(GRID_SIZE):
            row_imgs = []
            for col in range(GRID_SIZE):
                if (row, col) == (GRID_SIZE - 1, GRID_SIZE - 1):
                    row_imgs.append(None)  # Leeres Feld hat kein Bild
                else:
                    # Schneidet einen Abschnitt aus dem Gesamtbild aus
                    left = col * TILE_SIZE
                    upper = row * TILE_SIZE
                    right = left + TILE_SIZE
                    lower = upper + TILE_SIZE
                    tile_img = img.crop((left, upper, right, lower))
                    # Konvertiert Bild in tkinter-kompatibles Format
                    row_imgs.append(ImageTk.PhotoImage(tile_img))
            self.tile_images.append(row_imgs)

    def create_tiles(self):
        """
        Erstellt die initiale Anordnung der Kacheln (1 bis n in aufsteigender Reihenfolge).
        """
        self.tiles = []
        n = 1  # Startwert für die Kachelnummerierung
        for row in range(GRID_SIZE):
            row_tiles = []
            for col in range(GRID_SIZE):
                if (row, col) == (GRID_SIZE - 1, GRID_SIZE - 1):
                    row_tiles.append(None)  # Leeres Feld
                else:
                    row_tiles.append(n)  # Nummerierte Kachel
                    n += 1
            self.tiles.append(row_tiles)

    def shuffle(self):
        """
        Mischt die Kacheln zufällig und stellt sicher, dass das Puzzle lösbar ist.
        """
        # Flacht die 2D-Liste in eine 1D-Liste ab (ohne das leere Feld)
        nums = [n for row in self.tiles for n in row if n is not None]
        while True:
            random.shuffle(nums)  # Mischt die Zahlen
            nums.append(None)     # Fügt das leere Feld hinzu
            # Konvertiert zurück in eine 2D-Liste
            tiles = [nums[i * GRID_SIZE:(i + 1) * GRID_SIZE] for i in range(GRID_SIZE)]
            # Überprüft, ob das gemischte Puzzle lösbar ist
            if self.is_solvable(tiles):
                self.tiles = tiles
                self.empty_pos = self.find_empty()  # Aktualisiert die Position des leeren Felds
                break
            nums.pop()  # Entfernt das leere Feld für den nächsten Versuch

    def is_solvable(self, tiles):
        """
        Überprüft, ob ein gegebenes Puzzle lösbar ist.
        Verwendet den Inversions-Zählalgorithmus.
        
        Args:
            tiles: 2D-Liste mit der Puzzle-Anordnung
            
        Returns:
            bool: True, wenn das Puzzle lösbar ist, sonst False
        """
        flat = [n for row in tiles for n in row if n is not None]
        # Zählt die Anzahl der Inversionen (wenn eine höhere Zahl vor einer niedrigeren steht)
        inv = sum(1 for i in range(len(flat)) for j in range(i+1, len(flat)) if flat[i] > flat[j])
        empty_row = self.find_empty(tiles)[0]
        
        # Prüft Lösbarkeit nach verschiedenen Regeln je nach Gittergröße
        if GRID_SIZE % 2 == 1:
            # Für ungerade Gittergrößen: Die Anzahl der Inversionen muss gerade sein
            return inv % 2 == 0
        else:
            # Für gerade Gittergrößen: Die Summe aus Inversionen und Zeilenposition des leeren Felds
            # (von unten gezählt) muss gerade sein
            return (inv + (GRID_SIZE - empty_row)) % 2 == 0

    def find_empty(self, tiles=None):
        """
        Findet die Position des leeren Felds im Puzzle.
        
        Args:
            tiles: Optional eine 2D-Liste mit einer Puzzle-Anordnung
                  (verwendet self.tiles, wenn nicht angegeben)
                  
        Returns:
            tuple: (Zeile, Spalte) des leeren Felds
        """
        if tiles is None:
            tiles = self.tiles
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if tiles[r][c] is None:
                    return (r, c)

    def draw(self):
        """
        Zeichnet das Puzzle auf dem Bildschirm.
        Erstellt für jede Kachel einen Button mit dem entsprechenden Bild.
        """
        # Löscht alle vorherigen Widgets
        for widget in self.winfo_children():
            widget.destroy()
            
        # Erstellt neue Buttons für jede Kachel
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                n = self.tiles[r][c]
                if n is not None:
                    # Berechnet den Index des Bildes basierend auf der Kachelnummer
                    img = self.tile_images[(n-1)//GRID_SIZE][(n-1)%GRID_SIZE]
                    btn = tk.Button(
                        self,
                        image=img,
                        command=lambda r=r, c=c: self.move(r, c),  # Kachelbewegung bei Klick
                        highlightthickness=1,  # schmaler Rand
                        highlightbackground="black"
                    )
                    btn.grid(row=r, column=c, padx=0, pady=0)
                else:
                    # Leeres Feld
                    lbl = tk.Label(self, width=TILE_SIZE//10, height=TILE_SIZE//20)
                    lbl.grid(row=r, column=c)

    def move(self, r, c):
        """
        Bewegt eine Kachel oder eine Reihe/Spalte von Kacheln, wenn auf sie geklickt wird.
        
        Args:
            r: Zeilenindex der angeklickten Kachel
            c: Spaltenindex der angeklickten Kachel
        """
        er, ec = self.empty_pos
        # Wenn Kachel in gleicher Zeile wie leeres Feld ist
        if r == er and c != ec:
            step = 1 if c < ec else -1
            # Verschiebt alle Kacheln zwischen der angeklickten und dem leeren Feld
            for col in range(ec, c, -step):
                self.tiles[er][col] = self.tiles[er][col - step]
            self.tiles[er][c] = None
            self.empty_pos = (r, c)
            self.draw()  # Aktualisiert die Anzeige
            if self.is_completed():
                self.show_completed()
        # Wenn Kachel in gleicher Spalte wie leeres Feld ist
        elif c == ec and r != er:
            step = 1 if r < er else -1
            # Verschiebt alle Kacheln zwischen der angeklickten und dem leeren Feld
            for row in range(er, r, -step):
                self.tiles[row][ec] = self.tiles[row - step][ec]
            self.tiles[r][ec] = None
            self.empty_pos = (r, c)
            self.draw()  # Aktualisiert die Anzeige
            if self.is_completed():
                self.show_completed()
        # Wenn Kachel direkt neben leerem Feld ist (klassische Bewegung)
        elif (abs(er - r) == 1 and ec == c) or (abs(ec - c) == 1 and er == r):
            self.tiles[er][ec], self.tiles[r][c] = self.tiles[r][c], self.tiles[er][ec]
            self.empty_pos = (r, c)
            self.draw()  # Aktualisiert die Anzeige
            if self.is_completed():
                self.show_completed()

    def is_completed(self):
        """
        Überprüft, ob das Puzzle gelöst ist (alle Kacheln in der richtigen Reihenfolge).
        
        Returns:
            bool: True, wenn das Puzzle gelöst ist, sonst False
        """
        n = 1
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if (r, c) == (GRID_SIZE - 1, GRID_SIZE - 1):
                    # Das leere Feld sollte unten rechts sein
                    if self.tiles[r][c] is not None:
                        return False
                else:
                    # Jede andere Position sollte die fortlaufende Nummer haben
                    if self.tiles[r][c] != n:
                        return False
                    n += 1
        return True

    def show_completed(self):
        """
        Zeigt ein Popup-Fenster mit dem vollständigen Bild und einer Glückwunsch-Nachricht an,
        wenn das Puzzle gelöst wurde.
        """
        top = tk.Toplevel(self)  # Erstellt ein neues Popup-Fenster
        img = Image.open(IMAGE_FILE)
        img = img.resize((TILE_SIZE * GRID_SIZE, TILE_SIZE * GRID_SIZE))
        photo = ImageTk.PhotoImage(img)
        lbl = tk.Label(top, image=photo)
        lbl.image = photo  # Verhindert, dass das Bild vom Garbage Collector entfernt wird
        lbl.pack()
        tk.Label(top, text="Congratulations! Puzzle completed!").pack()
        tk.Button(top, text="Close", command=top.destroy).pack()

# Hauptprogramm
if __name__ == "__main__":
    if not IMAGE_FILE:
        print("No JPEG file found in this directory.")
    else:
        root = tk.Tk()           # Erstellt das Hauptfenster
        root.title("15 Puzzle")  # Setzt den Fenstertitel
        app = SlidingPuzzle(root, IMAGE_FILE)  # Erstellt die Anwendung
        app.mainloop()           # Startet die Ereignisschleife