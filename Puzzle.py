# Benötigte Module importieren
import tkinter as tk          # GUI-Bibliothek für die grafische Benutzeroberfläche
import os                     # Für Dateisystemoperationen (zum Finden der Bilddatei)
import random                 # Für das zufällige Mischen der Kacheln
from tkinter import messagebox # Für Benachrichtigungsfenster
from PIL import Image, ImageTk # Für Bildverarbeitung und -anzeige

# Konstanten für das Spiellayout
TILE_SIZE = 100               # Größe jeder Kachel in Pixeln
GRID_SIZE = 5                 # Spielfeldgröße (5x5 ergibt ein 24-Puzzle)
# Suche nach der ersten JPG-Datei im aktuellen Verzeichnis mit bestimmten Namen
IMAGE_FILE = next((f for f in os.listdir('.') if f.lower().endswith('puzzle_image.jpg') or f.lower().endswith('image.jpg')), None)

class SlidingPuzzle(tk.Frame):
    """
    Hauptklasse für das Schiebepuzzle-Spiel.
    Erbt von tk.Frame und implementiert die gesamte Spiellogik.
    """
    def __init__(self, master, image_path):
        """
        Konstruktor - initialisiert das Puzzle.
        
        Args:
            master: Das übergeordnete tkinter-Fenster
            image_path: Pfad zur Bilddatei für das Puzzle
        """
        super().__init__(master)
        self.master = master
        self.grid()                            # Frame im Hauptfenster platzieren
        self.tiles = []                        # 2D-Liste zur Speicherung der Kachelnummern
        self.tile_images = []                  # 2D-Liste zur Speicherung der Kachelbilder
        self.empty_pos = (GRID_SIZE - 1, GRID_SIZE - 1)  # Position der leeren Kachel (unten rechts)
        self.load_image(image_path)            # Bild laden und in Kacheln aufteilen
        self.create_tiles()                    # Kachel-Nummern initialisieren
        self.shuffle()                         # Kacheln zufällig mischen
        self.draw()                            # Puzzle auf dem Bildschirm anzeigen

        # Referenzfenster-Variable initialisieren
        self.reference_window = None
        self.image_path = image_path

        # Button zum Anzeigen/Ausblenden der Vorlage
        self.ref_button = tk.Button(self.master, text="Vorlage ein-/ausblenden", 
                                 command=self.toggle_reference_image)
        self.ref_button.grid(row=GRID_SIZE+1, column=0, columnspan=GRID_SIZE, pady=10)

    def load_image(self, image_path):
        """
        Lädt das ausgewählte Bild und teilt es in einzelne Kacheln auf.
        
        Args:
            image_path: Pfad zum Bild, das als Puzzle verwendet werden soll
        """
        img = Image.open(image_path)
        img = img.resize((TILE_SIZE * GRID_SIZE, TILE_SIZE * GRID_SIZE))  # Bild an Puzzle-Größe anpassen
        self.tile_images = []
        for row in range(GRID_SIZE):
            row_images = []
            for col in range(GRID_SIZE):
                # Für jede Position im Raster einen Bildausschnitt erstellen
                if (row, col) == (GRID_SIZE - 1, GRID_SIZE - 1):  # Leere Position
                    row_images.append(None)
                else:
                    # Bildausschnitt berechnen und extrahieren
                    left = col * TILE_SIZE
                    upper = row * TILE_SIZE
                    right = left + TILE_SIZE
                    lower = upper + TILE_SIZE
                    # Teilbild ausschneiden und in tkinter-Format konvertieren
                    tile_image = img.crop((left, upper, right, lower))
                    photo_image = ImageTk.PhotoImage(tile_image)
                    row_images.append(photo_image)
            self.tile_images.append(row_images)

    def create_tiles(self):
        """
        Erstellt die numerische Darstellung der Kacheln in ihrer Ausgangsposition.
        Die Kacheln sind anfangs in aufsteigender Reihenfolge angeordnet (1-24).
        """
        self.tiles = []
        n = 1  # Startwert für Kachelnummerierung
        for row in range(GRID_SIZE):
            tile_row = []
            for col in range(GRID_SIZE):
                if (row, col) == (GRID_SIZE - 1, GRID_SIZE - 1):  # Leere Position
                    tile_row.append(None)
                else:
                    tile_row.append(n)  # Nummerierte Kachel hinzufügen
                    n += 1
            self.tiles.append(tile_row)

    def shuffle(self):
        """
        Mischt die Kacheln zufällig.
        Stellt sicher, dass das gemischte Puzzle auch lösbar ist.
        """
        # Alle Kachelnummern (außer der leeren) in eine Liste extrahieren
        nums = [n for row in self.tiles for n in row if n is not None]
        while True:
            random.shuffle(nums)  # Kacheln zufällig mischen
            
            # Gemischte Zahlen zurück in 2D-Array formatieren
            shuffled_tiles = []
            i = 0
            for row in range(GRID_SIZE):
                tile_row = []
                for col in range(GRID_SIZE):
                    if (row, col) == (GRID_SIZE - 1, GRID_SIZE - 1):  # Leere Position
                        tile_row.append(None)
                    else:
                        tile_row.append(nums[i])
                        i += 1
                shuffled_tiles.append(tile_row)
            
            # Prüfen, ob das gemischte Puzzle lösbar ist
            if self.is_solvable(shuffled_tiles):
                self.tiles = shuffled_tiles
                self.empty_pos = self.find_empty()  # Position der leeren Kachel aktualisieren
                break

    def is_solvable(self, tiles):
        """
        Überprüft, ob ein Puzzle-Zustand lösbar ist.
        
        In einem Schiebepuzzle ist die Lösbarkeit durch die Anzahl der Inversionen 
        und die Position des leeren Feldes bestimmt.
        
        Args:
            tiles: 2D-Liste mit der aktuellen Kachelanordnung
            
        Returns:
            bool: True wenn das Puzzle lösbar ist, sonst False
        """
        # Flache Liste aller Zahlen erstellen (ohne None)
        flat = [n for row in tiles for n in row if n is not None]
        
        # Anzahl der Inversionen berechnen
        # Eine Inversion ist ein Paar (i,j) mit i<j und flat[i]>flat[j]
        inv = sum(1 for i in range(len(flat)) for j in range(i+1, len(flat)) if flat[i] > flat[j])
        
        # Position der leeren Kachel finden
        empty_row = self.find_empty(tiles)[0]
        
        # Lösbarkeitsregel anwenden:
        if GRID_SIZE % 2 == 1:  # Bei ungerader Gittergröße
            # Bei ungerader Gittergröße muss die Anzahl der Inversionen gerade sein
            return inv % 2 == 0
        else:  # Bei gerader Gittergröße
            # Bei gerader Gittergröße muss die Summe aus Inversionen und Zeilenindex 
            # der leeren Kachel (von unten gezählt) gerade sein
            return (inv + (GRID_SIZE - empty_row)) % 2 == 0

    def find_empty(self, tiles=None):
        """
        Findet die Position der leeren Kachel.
        
        Args:
            tiles: Optional eine benutzerdefinierte Kachelanordnung
                  (verwendet self.tiles, wenn nicht angegeben)
                  
        Returns:
            tuple: Position (row, col) der leeren Kachel
        """
        if tiles is None:
            tiles = self.tiles
            
        # Durchsuche das Raster nach der leeren Kachel (None)
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if tiles[r][c] is None:
                    return (r, c)
        
        # Sollte nie erreicht werden, da immer eine leere Kachel vorhanden sein sollte
        raise ValueError("Keine leere Kachel gefunden!")

    def draw(self):
        """
        Zeichnet das aktuelle Puzzle auf dem Bildschirm.
        Erstellt für jede Kachel einen Button mit dem entsprechenden Bildausschnitt.
        """
        # Alle vorhandenen Widgets entfernen
        for widget in self.winfo_children():
            widget.destroy()
            
        # Kacheln als Buttons neu erstellen
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                n = self.tiles[r][c]
                if n is not None:  # Normale Kachel
                    # Berechne den Original-Index des Bildes für diese Kachel
                    img_row = (n-1) // GRID_SIZE
                    img_col = (n-1) % GRID_SIZE
                    img = self.tile_images[img_row][img_col]
                    
                    # Button mit Bild erstellen
                    btn = tk.Button(
                        self,
                        image=img,
                        command=lambda r=r, c=c: self.move(r, c),  # Klickhandler mit Position
                        highlightthickness=0,  # Kein Abstand zwischen Kacheln
                        borderwidth=0,         # Kein Border
                        padx=0, pady=0         # Kein Padding
                    )
                    btn.grid(row=r, column=c, padx=0, pady=0)
                else:  # Leere Kachel
                    lbl = tk.Label(self, width=TILE_SIZE//10, height=TILE_SIZE//20, 
                                  background='#ddd', borderwidth=0)
                    lbl.grid(row=r, column=c, padx=0, pady=0)

    def move(self, r, c):
        """
        Verarbeitet einen Klick auf eine Kachel und bewegt sie entsprechend.
        
        Besonderheit: Erlaubt das Verschieben ganzer Reihen oder Spalten, 
        wenn das leere Feld in derselben Reihe/Spalte ist.
        
        Args:
            r: Zeilenindex der angeklickten Kachel
            c: Spaltenindex der angeklickten Kachel
        """
        er, ec = self.empty_pos  # Position der leeren Kachel
        
        # Wenn in gleicher Zeile wie leere Kachel
        if r == er and c != ec:
            step = 1 if c < ec else -1  # Richtung bestimmen
            # Alle Kacheln zwischen Klickposition und leerem Feld verschieben
            for col in range(ec, c, -step):
                self.tiles[r][col] = self.tiles[r][col - step]
            self.tiles[r][c] = None  # Klickposition wird zum leeren Feld
            self.empty_pos = (r, c)
            self.draw()  # Neu zeichnen
            
            # Prüfen, ob Puzzle gelöst wurde
            if self.is_completed():
                self.show_completed()
                
        # Wenn in gleicher Spalte wie leere Kachel
        elif c == ec and r != er:
            step = 1 if r < er else -1  # Richtung bestimmen
            # Alle Kacheln zwischen Klickposition und leerem Feld verschieben
            for row in range(er, r, -step):
                self.tiles[row][c] = self.tiles[row - step][c]
            self.tiles[r][c] = None  # Klickposition wird zum leeren Feld
            self.empty_pos = (r, c)
            self.draw()  # Neu zeichnen
            
            # Prüfen, ob Puzzle gelöst wurde
            if self.is_completed():
                self.show_completed()

    def is_completed(self):
        """
        Überprüft, ob das Puzzle gelöst ist (alle Kacheln in der richtigen Reihenfolge).
        
        Returns:
            bool: True wenn das Puzzle gelöst ist, sonst False
        """
        n = 1  # Erwarteter Startwert
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if (r, c) == (GRID_SIZE - 1, GRID_SIZE - 1):  # Leeres Feld sollte unten rechts sein
                    if self.tiles[r][c] is not None:
                        return False
                else:
                    # Jedes andere Feld sollte die fortlaufende Nummer haben
                    if self.tiles[r][c] != n:
                        return False
                    n += 1
        return True

    def show_completed(self):
        """
        Zeigt einen Glückwunsch-Dialog mit dem vollständigen Bild an,
        wenn das Puzzle erfolgreich gelöst wurde.
        """
        # Neues Fenster für die Glückwunschnachricht erstellen
        top = tk.Toplevel(self)
        top.title("Puzzle gelöst!")
        
        # Vollständiges Bild anzeigen
        img = Image.open(IMAGE_FILE)
        img = img.resize((TILE_SIZE * GRID_SIZE, TILE_SIZE * GRID_SIZE))
        photo = ImageTk.PhotoImage(img)
        lbl = tk.Label(top, image=photo)
        lbl.image = photo  # Referenz behalten, um Garbage Collection zu verhindern
        lbl.pack(padx=10, pady=10)
        
        # Glückwunschtext und Schließen-Button
        tk.Label(top, text="Glückwunsch! Du hast das Puzzle gelöst!", 
                font=("Arial", 14)).pack(pady=10)
        tk.Button(top, text="Schließen", command=top.destroy).pack(pady=10)

    # Alternativ zur automatischen Anzeige: Button zum Ein-/Ausblenden der Vorlage
    def toggle_reference_image(self):
        """
        Zeigt die Vorlage an oder blendet sie aus, wenn sie bereits angezeigt wird.
        """
        if self.reference_window and self.reference_window.winfo_exists():
            self.reference_window.destroy()
            self.reference_window = None
        else:
            self.show_reference_image(self.image_path)

    def show_reference_image(self, image_path):
        """
        Öffnet ein separates Fenster mit dem kompletten Originalbild als Vorlage.
        """
        self.reference_window = tk.Toplevel(self.master)
        self.reference_window.title("Puzzle-Vorlage")
        
        img = Image.open(image_path)
        img = img.resize((TILE_SIZE * GRID_SIZE, TILE_SIZE * GRID_SIZE))
        photo = ImageTk.PhotoImage(img)
        lbl = tk.Label(self.reference_window, image=photo)
        lbl.image = photo  # Referenz behalten, um Garbage Collection zu verhindern
        lbl.pack(padx=10, pady=10)

# Hauptprogramm
if __name__ == "__main__":
    if not IMAGE_FILE:
        # Wenn keine Bilddatei gefunden wurde
        print("Keine JPEG-Datei im aktuellen Verzeichnis gefunden.")
        messagebox.showerror("Fehler", "Keine JPEG-Datei gefunden. Bitte lege eine Bilddatei im Programmverzeichnis ab.")
    else:
        # Tkinter-Anwendung starten
        root = tk.Tk()
        root.title("Sliding Puzzle")
        app = SlidingPuzzle(root, IMAGE_FILE)
        root.mainloop()  # Ereignisschleife starten