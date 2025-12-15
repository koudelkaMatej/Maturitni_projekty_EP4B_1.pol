import tkinter as tk
import random
import time
import sqlite3
from tkinter import messagebox, simpledialog

class Minesweeper:
    def __init__(self, root):
        self.root = root
        self.root.title("Hledani min")
        self.root.attributes('-fullscreen', True)  # fullscreen
        # Escape ukonci hru
        self.root.bind('<Escape>', lambda e: self.ukonci_aplikaci())

        # Scoreboard frame
        self.scoreboard_frame = tk.Frame(self.root, bg="lightgray")
        self.scoreboard_frame.place(relx=0.01, rely=0.05, relwidth=0.22, relheight=0.9)
        self.scoreboard_label = tk.Label(self.scoreboard_frame, text="Scoreboard", font=("Arial", 30, "bold"), bg="lightgray")
        self.scoreboard_label.pack(pady=10)
        self.scoreboard_list = tk.Listbox(self.scoreboard_frame, font=("Arial", 15), width=25)
        self.scoreboard_list.pack(padx=10, pady=10, fill="both", expand=True)

        # SQLite: ulozeni vysledku
        self.conn = sqlite3.connect("score.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS vysledky (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jmeno TEXT,
                skore INTEGER,
                cas INTEGER,
                obtiznost TEXT,
                vysledek TEXT
            )
            """
        )
        self.conn.commit()

        # Hlavni menu
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(expand=True)

        tk.Label(self.menu_frame, text="Vyber obtížnost:", font=("Arial", 20)).pack(pady=20)
        tk.Button(
            self.menu_frame,
            text="Začátečník (8x8, 10 min)",
            font=("Arial", 16),
            command=lambda: self.spust_hru(8, 10),
        ).pack(pady=10)
        tk.Button(
            self.menu_frame,
            text="Střední (12x12, 20 min)",
            font=("Arial", 16),
            command=lambda: self.spust_hru(12, 20),
        ).pack(pady=10)
        tk.Button(
            self.menu_frame,
            text="Expert (16x16, 40 min)",
            font=("Arial", 16),
            command=lambda: self.spust_hru(16, 40),
        ).pack(pady=10)

        self.aktualizuj_scoreboard()

    def spust_hru(self, velikost, pocet_min):
        self.menu_frame.pack_forget()

        self.velikost = velikost
        self.pocet_min = pocet_min
        self.prvni_klik = True
        self.tlacitka = {}
        self.minova_pole = [[0 for _ in range(velikost)] for _ in range(velikost)]
        self.vlajky = [[False for _ in range(velikost)] for _ in range(velikost)]
        self.zacatek = time.time()
        self.odkryta = 0
        self.spatne_vlajky = 0

        # Statistiky uprostred horni casti
        self.info_frame = tk.Frame(self.root)
        self.info_frame.place(relx=0.5, rely=0.1, anchor="center")
        self.cas_label = tk.Label(self.info_frame, text="Cas: 0 s", font=("Arial", 16))
        self.cas_label.pack(side="left", padx=20)
        self.skore_label = tk.Label(self.info_frame, text="Skore: 0", font=("Arial", 16))
        self.skore_label.pack(side="left", padx=20)

        # Hra bezi
        self.hra_bezi = True

        # Umisteni min
        for _ in range(pocet_min):
            while True:
                x = random.randint(0, velikost - 1)
                y = random.randint(0, velikost - 1)
                if self.minova_pole[x][y] == 0:
                    self.minova_pole[x][y] = -1
                    break

        # Spocitani cisel okolo min
        for i in range(velikost):
            for j in range(velikost):
                if self.minova_pole[i][j] == -1:
                    continue
                pocet = 0
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if 0 <= i + dx < velikost and 0 <= j + dy < velikost:
                            if self.minova_pole[i + dx][j + dy] == -1:
                                pocet += 1
                self.minova_pole[i][j] = pocet

        # Herni plocha
        self.frame = tk.Frame(self.root)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        # Dynamické určení velikosti tlačítek podle velikosti okna a pole
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        # Rezerva pro horní info panel a okraje
        usable_height = int(screen_height * 0.7)
        usable_width = int(screen_width * 0.7)
        btn_size = min(usable_width // velikost, usable_height // velikost)
        btn_size = max(20, btn_size)  # minimální velikost tlačítka

        for i in range(velikost):
            self.frame.grid_rowconfigure(i, weight=1, minsize=btn_size)
            for j in range(velikost):
                self.frame.grid_columnconfigure(j, weight=1, minsize=btn_size)
                b = tk.Button(self.frame, width=btn_size // 7, height=btn_size // 20, command=lambda x=i, y=j: self.odkryj(x, y))
                b.grid(row=i, column=j, sticky="nsew", padx=1, pady=1)
                b.bind("<Button-3>", lambda _, x=i, y=j: self.prepni_vlajku(x, y))
                self.tlacitka[(i, j)] = b

        self.aktualizuj_info()

    def odkryj(self, x, y):
        if not self.hra_bezi:
            return
        b = self.tlacitka[(x, y)]
        if not b["state"] == "normal" or self.vlajky[x][y]:
            return

        # Prvni klik safe
        if getattr(self, 'prvni_klik', False):
            self.prvni_klik = False
            if self.minova_pole[x][y] == -1:
                nalezeno = False
                for i in range(self.velikost):
                    for j in range(self.velikost):
                        if self.minova_pole[i][j] != -1 and not (i == x and j == y):
                            self.minova_pole[x][y] = 0
                            self.minova_pole[i][j] = -1
                            nalezeno = True
                            break
                    if nalezeno:
                        break
                # přepočet 
                for a in range(self.velikost):
                    for b2 in range(self.velikost):
                        if self.minova_pole[a][b2] == -1:
                            continue
                        pocet = 0
                        for dx in [-1, 0, 1]:
                            for dy in [-1, 0, 1]:
                                if 0 <= a + dx < self.velikost and 0 <= b2 + dy < self.velikost:
                                    if self.minova_pole[a + dx][b2 + dy] == -1:
                                        pocet += 1
                        self.minova_pole[a][b2] = pocet

        if self.minova_pole[x][y] == -1:
            b.config(text="*", bg="red")
            self.konec_hry(vyhra=False)
        else:
            cislo = self.minova_pole[x][y]
            b.config(text=str(cislo) if cislo > 0 else "", state="disabled", relief=tk.SUNKEN)
            self.odkryta += 1
            if cislo == 0:
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if 0 <= x + dx < self.velikost and 0 <= y + dy < self.velikost:
                            self.odkryj(x + dx, y + dy)
            if self.odkryta == self.velikost * self.velikost - self.pocet_min:
                self.konec_hry(vyhra=True)

    def prepni_vlajku(self, x, y):
        b = self.tlacitka[(x, y)]
        if b["state"] == "disabled":
            return
        if not self.vlajky[x][y]:
            b.config(text="F")
            self.vlajky[x][y] = True
            if self.minova_pole[x][y] != -1:
                self.spatne_vlajky += 1
        else:
            b.config(text="")
            if self.vlajky[x][y] and self.minova_pole[x][y] != -1:
                self.spatne_vlajky -= 1
            self.vlajky[x][y] = False

    def konec_hry(self, vyhra):
        self.hra_bezi = False
        cas = int(time.time() - self.zacatek)
        skore = self.odkryta * 10 - cas - self.spatne_vlajky * 5
        skore = max(0, skore)
        vysledek = "Vyhra" if vyhra else "Prohra"
        messagebox.showinfo("Konec hry", f"{vysledek}!\nTvůj čas: {cas} s\nSkore: {skore}")
        jmeno = simpledialog.askstring("Jmeno", "Zadej své jmeno:")
        if not jmeno:
            jmeno = "Neznamy"
        self.cursor.execute(
            "INSERT INTO vysledky (jmeno, skore, cas, obtiznost, vysledek) VALUES (?, ?, ?, ?, ?)",
            (jmeno, skore, cas, f"{self.velikost}x{self.velikost}", vysledek),
        )
        self.conn.commit()
        self.aktualizuj_scoreboard()
        # Nabidni novou hru
        chce_znovu = messagebox.askyesno("Hra ukončena", "Zkusit znovu?")
        if chce_znovu:
            self.vynuluj_hraci_plochu()
            self.menu_frame.pack(expand=True)
        else:
            self.ukonci_aplikaci()

    def vynuluj_hraci_plochu(self): # Vymazání herní plochy kvůli návratu do menu
        try:
            if hasattr(self, "frame") and self.frame.winfo_exists():
                self.frame.destroy()
        except Exception:
            pass
        try:
            if hasattr(self, "info_frame") and self.info_frame.winfo_exists():
                self.info_frame.destroy()
        except Exception:
            pass

    def ukonci_aplikaci(self):
        # Bezpečné uzavření DB a okna
        try:
            if hasattr(self, "conn"):
                self.conn.commit()
                self.conn.close()
        except Exception:
            pass
        self.root.destroy()

    def aktualizuj_info(self):
        if not hasattr(self, "hra_bezi") or not self.hra_bezi:
            return
        cas = int(time.time() - self.zacatek)
        skore = self.odkryta * 10 - cas - self.spatne_vlajky * 5
        skore = max(0, skore)
        if hasattr(self, "cas_label"):
            self.cas_label.config(text=f"Cas: {cas} s")
        if hasattr(self, "skore_label"):
            self.skore_label.config(text=f"Skore: {skore}")
        if hasattr(self, "frame") and self.frame.winfo_exists():
            self.root.after(500, self.aktualizuj_info)

    def aktualizuj_scoreboard(self):
        self.scoreboard_list.delete(0, tk.END)
        self.cursor.execute("SELECT jmeno, skore, cas, obtiznost, vysledek FROM vysledky ORDER BY skore DESC, cas ASC LIMIT 10")
        vysledky = self.cursor.fetchall()
        for idx, (jmeno, skore, cas, obtiznost, vysledek) in enumerate(vysledky, 1):
            self.scoreboard_list.insert(tk.END, f"{idx}. {jmeno} | {skore}b | {cas}s | {obtiznost} | {vysledek}")

if __name__ == "__main__":
    root = tk.Tk()
    hra = Minesweeper(root)
    root.mainloop()
