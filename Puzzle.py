import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import os

TILE_SIZE = 100
GRID_SIZE = 5
IMAGE_FILE = next((f for f in os.listdir('.') if f.lower().endswith('.jpg') or f.lower().endswith('.jpg')), None)

class SlidingPuzzle(tk.Frame):
    def __init__(self, master, image_path):
        super().__init__(master)
        self.master = master
        self.grid()
        self.tiles = []
        self.tile_images = []
        self.empty_pos = (GRID_SIZE - 1, GRID_SIZE - 1)
        self.load_image(image_path)
        self.create_tiles()
        self.shuffle()
        self.draw()

    def load_image(self, image_path):
        img = Image.open(image_path)
        img = img.resize((TILE_SIZE * GRID_SIZE, TILE_SIZE * GRID_SIZE))
        self.tile_images = []
        for row in range(GRID_SIZE):
            row_imgs = []
            for col in range(GRID_SIZE):
                if (row, col) == (GRID_SIZE - 1, GRID_SIZE - 1):
                    row_imgs.append(None)
                else:
                    left = col * TILE_SIZE
                    upper = row * TILE_SIZE
                    right = left + TILE_SIZE
                    lower = upper + TILE_SIZE
                    tile_img = img.crop((left, upper, right, lower))
                    row_imgs.append(ImageTk.PhotoImage(tile_img))
            self.tile_images.append(row_imgs)

    def create_tiles(self):
        self.tiles = []
        n = 1
        for row in range(GRID_SIZE):
            row_tiles = []
            for col in range(GRID_SIZE):
                if (row, col) == (GRID_SIZE - 1, GRID_SIZE - 1):
                    row_tiles.append(None)
                else:
                    row_tiles.append(n)
                    n += 1
            self.tiles.append(row_tiles)

    def shuffle(self):
        # Flatten and shuffle, then reshape
        nums = [n for row in self.tiles for n in row if n is not None]
        while True:
            random.shuffle(nums)
            nums.append(None)
            tiles = [nums[i * GRID_SIZE:(i + 1) * GRID_SIZE] for i in range(GRID_SIZE)]
            if self.is_solvable(tiles):
                self.tiles = tiles
                self.empty_pos = self.find_empty()
                break
            nums.pop()

    def is_solvable(self, tiles):
        flat = [n for row in tiles for n in row if n is not None]
        inv = sum(1 for i in range(len(flat)) for j in range(i+1, len(flat)) if flat[i] > flat[j])
        empty_row = self.find_empty(tiles)[0]
        if GRID_SIZE % 2 == 1:
            return inv % 2 == 0
        else:
            return (inv + (GRID_SIZE - empty_row)) % 2 == 0

    def find_empty(self, tiles=None):
        if tiles is None:
            tiles = self.tiles
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if tiles[r][c] is None:
                    return (r, c)

    def draw(self):
        for widget in self.winfo_children():
            widget.destroy()
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                n = self.tiles[r][c]
                if n is not None:
                    img = self.tile_images[(n-1)//GRID_SIZE][(n-1)%GRID_SIZE]
                    btn = tk.Button(
                        self,
                        image=img,
                        command=lambda r=r, c=c: self.move(r, c),
                        highlightthickness=1,  # schmaler Rand
                        highlightbackground="black"
                    )
                    btn.grid(row=r, column=c, padx=0, pady=0)
                else:
                    lbl = tk.Label(self, width=TILE_SIZE//10, height=TILE_SIZE//20)
                    lbl.grid(row=r, column=c)

    def move(self, r, c):
        er, ec = self.empty_pos
        # Gleiche Zeile
        if r == er and c != ec:
            step = 1 if c < ec else -1
            for col in range(ec, c, -step):
                self.tiles[er][col] = self.tiles[er][col - step]
            self.tiles[er][c] = None
            self.empty_pos = (r, c)
            self.draw()
            if self.is_completed():
                self.show_completed()
        # Gleiche Spalte
        elif c == ec and r != er:
            step = 1 if r < er else -1
            for row in range(er, r, -step):
                self.tiles[row][ec] = self.tiles[row - step][ec]
            self.tiles[r][ec] = None
            self.empty_pos = (r, c)
            self.draw()
            if self.is_completed():
                self.show_completed()
        # Nachbarfeld wie bisher
        elif (abs(er - r) == 1 and ec == c) or (abs(ec - c) == 1 and er == r):
            self.tiles[er][ec], self.tiles[r][c] = self.tiles[r][c], self.tiles[er][ec]
            self.empty_pos = (r, c)
            self.draw()
            if self.is_completed():
                self.show_completed()

    def is_completed(self):
        n = 1
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if (r, c) == (GRID_SIZE - 1, GRID_SIZE - 1):
                    if self.tiles[r][c] is not None:
                        return False
                else:
                    if self.tiles[r][c] != n:
                        return False
                    n += 1
        return True

    def show_completed(self):
        top = tk.Toplevel(self)
        img = Image.open(IMAGE_FILE)
        img = img.resize((TILE_SIZE * GRID_SIZE, TILE_SIZE * GRID_SIZE))
        photo = ImageTk.PhotoImage(img)
        lbl = tk.Label(top, image=photo)
        lbl.image = photo
        lbl.pack()
        tk.Label(top, text="Congratulations! Puzzle completed!").pack()
        tk.Button(top, text="Close", command=top.destroy).pack()

if __name__ == "__main__":
    if not IMAGE_FILE:
        print("No JPEG file found in this directory.")
    else:
        root = tk.Tk()
        root.title("15 Puzzle")
        app = SlidingPuzzle(root, IMAGE_FILE)
        app.mainloop()