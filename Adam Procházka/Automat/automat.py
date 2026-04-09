# Importy
import pygame
import random
import sys
import json
import os
from pathlib import Path
from werkzeug.security import check_password_hash

def base_dir() -> Path:
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent

        for candidate in [
            exe_dir / "_internal",
            exe_dir
        ]:
            if (candidate / "assets").exists():
                return candidate

        return exe_dir

    return Path(__file__).resolve().parent

BASE = base_dir()

def load_image(rel_path):
    return pygame.image.load(BASE / rel_path)

pygame.init()
#Rozlišení
screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
WIDTH, HEIGHT = screen.get_size()
#Název
pygame.display.set_caption("PixSpin")
#Ikona
icon = load_image("assets/images/icon.png")
SlotsBorder = load_image("assets/images/SlotsBorder.png")               # NEPLATNÝ
Bg = load_image("assets/images/Bg.png")
logo = load_image("assets/images/PixSpin.png").convert_alpha()
pygame.display.set_icon(icon)

# ========== Barvy ==========
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# ========== Definice Symbolů ==========
symbols = {
    "apple": load_image("assets/images/apple.png"),
    "banana": load_image("assets/images/banana.png"),
    "cherry": load_image("assets/images/cherry.png"),
    "grape": load_image("assets/images/grape.png"),
    "lemon": load_image("assets/images/lemon.png"),
    "orange": load_image("assets/images/orange.png"),
    "watermelon": load_image("assets/images/watermelon.png"),
    "pear": load_image("assets/images/pear.png"),
    "strawberry": load_image("assets/images/strawberry.png"),
    "pomelo": load_image("assets/images/pomelo.png"),
    "seven": load_image("assets/images/seven.png"),
    "shiny_apple": load_image("assets/images/shiny_apple.png"),
    "shiny_banana": load_image("assets/images/shiny_banana.png"),
    "shiny_cherry": load_image("assets/images/shiny_cherry.png"),
    "shiny_grape": load_image("assets/images/shiny_grape.png"),
    "shiny_lemon": load_image("assets/images/shiny_lemon.png"),
    "shiny_orange": load_image("assets/images/shiny_orange.png"),
    "shiny_watermelon": load_image("assets/images/shiny_watermelon.png"),
    "shiny_pear": load_image("assets/images/shiny_pear.png"),
    "shiny_strawberry": load_image("assets/images/shiny_strawberry.png"),
    "shiny_pomelo": load_image("assets/images/shiny_pomelo.png"),
    "golden_seven": load_image("assets/images/golden_seven.png"),
    "reroll": load_image("assets/images/reroll.png"),
    "mirror": load_image("assets/images/mirror.png"),
    "diamond": load_image("assets/images/diamond.png"),
    "bomb": load_image("assets/images/bomb.png"),
    "star": load_image("assets/images/star.png")
}

# Nepatří mezi symboly
chest_image = load_image("assets/images/chest.png").convert_alpha()
chip_icon = load_image("assets/images/chip.png")
chip_icon_small = pygame.transform.scale(chip_icon, (35, 35))
background = pygame.transform.scale(Bg, (WIDTH, HEIGHT))

mirror_img = load_image("assets/images/mirror.png").convert_alpha()
diamond_img = load_image("assets/images/diamond.png").convert_alpha()
golden_seven_img = load_image("assets/images/golden_seven.png").convert_alpha()
chest_img = load_image("assets/images/chest.png").convert_alpha()
reroll_img = load_image("assets/images/reroll.png").convert_alpha()
bomb_img = load_image("assets/images/bomb.png").convert_alpha()
star_img = load_image("assets/images/star.png").convert_alpha()
shiny_orange_img = load_image("assets/images/shiny_orange.png").convert_alpha()

# Zmenšení obrázků na rozumnou velikost (např. 64x64 px)
mirror_img = pygame.transform.scale(mirror_img, (100, 100))
diamond_img = pygame.transform.scale(diamond_img, (100, 100))
golden_seven_img = pygame.transform.scale(golden_seven_img, (100, 100))
chest_img = pygame.transform.scale(chest_img, (100, 100))
reroll_img = pygame.transform.scale(reroll_img, (100, 100))
bomb_img = pygame.transform.scale(bomb_img, (100, 100))
star_img = pygame.transform.scale(star_img, (100, 100))
shiny_orange_img = pygame.transform.scale(shiny_orange_img, (100, 100))

# ========== Hodnoty Symbolů ==========
symbol_names = list(symbols.keys())
symbol_values = {
    "strawberry": 50,
    "apple": 100,
    "banana": 200,
    "cherry": 300,
    "grape": 150,
    "pomelo": 150,
    "lemon": 250,
    "orange": 350,
    "watermelon": 400,
    "pear": 450,
    "seven": 600,
    "shiny_strawberry": 100,
    "shiny_apple": 200,
    "shiny_banana": 400,
    "shiny_cherry": 600,
    "shiny_grape": 300,
    "shiny_pomelo": 300,
    "shiny_lemon": 500,
    "shiny_orange": 700,
    "shiny_watermelon": 800,
    "shiny_pear": 900,
    "golden_seven": 3350,
    "reroll": 0,
    "mirror": 0,
    "diamond": 0,
    "bomb": 0
}

# ========== Rarita Symbolů ==========
symbol_rarity = { #čím nižší, tím vzácnejší
    "strawberry": 500,
    "apple": 490,
    "banana": 480,
    "cherry": 470,
    "grape": 460,
    "pomelo": 450,
    "lemon": 440,
    "orange": 430,
    "watermelon": 420,
    "pear": 410,
    "seven": 400,
    "shiny_strawberry": 50,
    "shiny_apple": 49,
    "shiny_banana": 48,
    "shiny_cherry": 47,
    "shiny_grape": 46,
    "shiny_pomelo": 45,
    "shiny_lemon": 44,
    "shiny_orange": 42,
    "shiny_watermelon": 40,
    "shiny_pear": 38,
    "golden_seven": 30,
    "reroll": 150,
    "mirror": 150,
    "diamond": 150,
    "bomb": 150
}

# ---------- Fonty ----------
FONT_PATH = str(BASE / "assets/fonts/VT323.ttf")

font = pygame.font.Font(FONT_PATH, 36)
big_font = pygame.font.Font(FONT_PATH, 48)
bigg_font = pygame.font.Font(FONT_PATH, 72)
bold_font = pygame.font.Font(FONT_PATH, 72)
desc_font = pygame.font.Font(FONT_PATH, 48)
title_font = pygame.font.Font(FONT_PATH, 96)
icon_font = pygame.font.Font(FONT_PATH, 36)
text_font = pygame.font.Font(FONT_PATH, 50)
# ========== Proměnné  ==========
slots = [                                       # URČENÍ HERNÍHO POLE 
    ["apple", "banana", "cherry"],              # 1. válec, 3 symboly
    ["lemon", "apple", "seven"],                # 2. válec
    ["cherry", "banana", "apple"]               # 3. válec
]
WIN_LINES = [
    [(0, 0), (1, 0), (2, 0)],  # horní řada
    [(0, 1), (1, 1), (2, 1)],  # prostřední řada
    [(0, 2), (1, 2), (2, 2)],  # dolní řada
    [(0, 0), (1, 1), (2, 2)],  # diagonála \
    [(0, 2), (1, 1), (2, 0)]   # diagonála /
]
winning_lines = []
SPECIAL_SYMBOLS = {"bomb", "diamond", "mirror"}
result_text = ""                                # Text pro zobrazení výsledku
total_score = 0                                 # Celkové skóre hráče
spins_left = 10                                 # Počet zbývajících spinů (zde je nelze přidávat)
spins_used = 0                                  # Počet použitých spinů
show_bonus_spin = False                         # Zda se má zobrazit animace bonusu
show_bonus_spin_amount = [1]                    # Kolik spinů se má ukázat
bonus_timer = 0                                 # Timer pro animaci bonusu
game_state = "login"                            # Stav Hry
previous_game_state = "menu"
score_multiplier = 1                            # Aktivní násobič skóre
pending_multiplier = 1                          # Násobič čekající na další kolo
bomb_penalty_next_spin = False                  # Jestli má být příští výhra záporná
chip_count = 0                                  # aktuální počet
login_username = ""
login_password = ""
login_error = ""
login_active_field = "username"
spin_input_block_until = 0

users_file = BASE / "data" / "users.json"
current_user = None
player_name = ""

flash_timer = 0                                 # Animace
shake_timer = 0
shake_offset = (0, 0)
reel_anim_timer = 0
animating = False

help_page = 0
offset_surface = pygame.Surface((WIDTH, HEIGHT))# MEGA DŮLEŽITÝ

# ========== Definice Funkcí ==========
def draw_winning_lines(surface, winning_lines, slot_start_x, slot_y, slot_size, slot_spacing):
    for line in winning_lines:
        points = []

        for col, row in line:
            x = slot_start_x + col * (slot_size + slot_spacing) + slot_size // 2 - 350
            y = slot_y + row * (slot_size + slot_spacing) + slot_size // 2 - 15
            points.append((x, y))

        if len(points) >= 2:
            # glow
            pygame.draw.lines(surface, (0, 255, 100, 50), False, points, 12)
            # hlavní čára
            pygame.draw.lines(surface, (0, 255, 100), False, points, 4)

def default_stats():
    return {
        "total_spins": 0,
        "jackpots": 0,
        "max_spins": 0,
        "lowest_score": None,
        "max_score_spin": 0,
        "current_jackpot_streak": 0,
        "max_jackpot_streak": 0
    }

stats = default_stats()

def get_current_user_highscore():
    if current_user is None:
        return None

    users = load_users()
    if current_user in users:
        return users[current_user].get("highscore", 0)
    return None

def load_users():
    if users_file.exists():
        try:
            with open(users_file, "r", encoding="utf-8") as f:
                users = json.load(f)
                if isinstance(users, dict):
                    return users
        except json.JSONDecodeError:
            print("JSON ERROR")
    else:
        print("SOUBOR NEEXISTUJE:", users_file)

    return {}

def save_users(users):
    users_file.parent.mkdir(parents=True, exist_ok=True)
    with open(users_file, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def ensure_user_data(users, username):
    if username not in users:
        return False

    if "highscore" not in users[username]:
        users[username]["highscore"] = 0

    if "stats" not in users[username] or not isinstance(users[username]["stats"], dict):
        users[username]["stats"] = default_stats()
    else:
        defaults = default_stats()
        for key, value in defaults.items():
            if key not in users[username]["stats"]:
                users[username]["stats"][key] = value

    return True

def login_user(username, password):
    global current_user, player_name, stats

    users = load_users()
    if username in users and check_password_hash(users[username]["password_hash"], password):
        ensure_user_data(users, username)
        save_users(users)

        current_user = username
        player_name = username
        stats = users[username]["stats"]
        return True
    return False

def get_leaderboard_rows():
    users = load_users()
    rows = []

    for username, data in users.items():
        score = data.get("highscore", 0)
        rows.append({"name": username, "score": score})

    rows.sort(key=lambda x: x["score"], reverse=True)
    return rows[:10]

def get_rows(slots):
    return [[slots[col][row] for col in range(3)] for row in range(3)]

def get_diagonals(slots):
    return [
        [slots[0][0], slots[1][1], slots[2][2]],
        [slots[0][2], slots[1][1], slots[2][0]]
    ]

def get_row_coords():
    return [
        [(0, 0), (1, 0), (2, 0)],
        [(0, 1), (1, 1), (2, 1)],
        [(0, 2), (1, 2), (2, 2)]
    ]

def get_diagonal_coords():
    return [
        [(0, 0), (1, 1), (2, 2)],
        [(0, 2), (1, 1), (2, 0)]
    ]

def spin():
    weighted_symbols = []
    for symbol, rarity in symbol_rarity.items():
        weighted_symbols.extend([symbol] * rarity)

    # Základní random 3x3 grid
    slots = [
        [random.choice(weighted_symbols) for _ in range(3)],
        [random.choice(weighted_symbols) for _ in range(3)],
        [random.choice(weighted_symbols) for _ in range(3)]
    ]

    # Šance na počet cíleně vytvořených výherních linek
    roll = random.random()

    if roll < 0.03:          # 3 %
        win_count = 3
    elif roll < 0.15:        # 12 %
        win_count = 2
    elif roll < 0.45:        # 30 %
        win_count = 1
    else:                    # 55 %
        win_count = 0

    if win_count > 0:
        chosen_lines = random.sample(WIN_LINES, k=win_count)

        for line in chosen_lines:
            base = random.choice(weighted_symbols)
            for col, row in line:
                slots[col][row] = base

    return slots

# ============================== Nejdůležitější Definice na kalkulaci skóre ==============================

def calculate_score(slots):
    global result_text, spins_left, show_bonus_spin, bonus_timer, flash_timer, shake_timer, stats, score_multiplier
    global pending_multiplier, bomb_penalty_next_spin, winning_lines

    rows = get_rows(slots)
    diagonals = get_diagonals(slots)

    row_coords = get_row_coords()
    diagonal_coords = get_diagonal_coords()

    all_lines = rows + diagonals
    all_coords = row_coords + diagonal_coords

    winning_lines.clear()

    # ---------- BOMB ----------
    # bomba se počítá jen na horizontálách
    for line, coords in zip(rows, row_coords):
        if line.count("bomb") == 3:
            winning_lines.append(coords)
            bomb_penalty_next_spin = True
            result_text = "3x bomb | Další skóre záporné!"
            return 0

        if line.count("bomb") == 2:
            winning_lines.append(coords)
            result_text = "2x bomb | NIC"
            return 0

    # ========== Multipliery, Zápory a Proměnné ==========
    total_value = 0
    bonus_spins = 0
    messages = []
    jackpot_count_total = 0
    had_jackpot = False

    # Použije pending_multiplier jako násobič, pak se resetuje
    score_multiplier = pending_multiplier
    pending_multiplier = 1

    # Pokud je aktivní bomba, invertuje skóre
    invert_score = bomb_penalty_next_spin
    bomb_penalty_next_spin = False

    # ---------- REROLL ----------
    # reroll se počítá jen na horizontálách
    for line, coords in zip(rows, row_coords):
        if line.count("reroll") == 3:
            bonus_spins += 3
            messages.append("3x reroll | +3 zatočení")

        elif line.count("reroll") == 2:
            bonus_spins += 2
            messages.append("2x reroll | +2 zatočení")

    # ---------- MIRROR ----------
    # mirror funguje jen na horizontálách
    for line, coords in zip(rows, row_coords):
        mirror_count = line.count("mirror")
        non_mirrors = [s for s in line if s != "mirror"]

        if mirror_count == 3:
            messages.append("3x mirror | NIC")

        elif mirror_count == 2 and len(non_mirrors) == 1:
            symbol = non_mirrors[0]
            if symbol in symbol_values and symbol not in SPECIAL_SYMBOLS:
                winning_lines.append(coords)

                value = symbol_values[symbol] * 3 * score_multiplier
                if invert_score:
                    value = -value
                    messages.append(f"2x mirror + {symbol.upper()} | ZTRÁTA {value}")
                else:
                    messages.append(f"2x mirror + {symbol} | +{value}")
                    bonus_spins += 1

                total_value += value
                flash_timer = pygame.time.get_ticks()
                shake_timer = pygame.time.get_ticks()
                had_jackpot = True
                jackpot_count_total += 1

        elif mirror_count == 1 and len(non_mirrors) == 2:
            if non_mirrors[0] == non_mirrors[1]:
                symbol = non_mirrors[0]
                if symbol in symbol_values and symbol not in SPECIAL_SYMBOLS:
                    winning_lines.append(coords)

                value = symbol_values[symbol] * 3 * score_multiplier

                if invert_score:
                    value = -value
                    messages.append(f"mirror + 2x {symbol.upper()} | ZTRÁTA {value}")
                else:
                    messages.append(f"mirror + 2x {symbol} | +{value}")
                    bonus_spins += 1

                total_value += value
                flash_timer = pygame.time.get_ticks()
                shake_timer = pygame.time.get_ticks()
                had_jackpot = True
                jackpot_count_total += 1
            else:
                sym1, sym2 = non_mirrors
                if sym1 in SPECIAL_SYMBOLS or sym2 in SPECIAL_SYMBOLS:
                    continue
                
                higher = sym1 if symbol_values[sym1] >= symbol_values[sym2] else sym2

                winning_lines.append(coords)

                value = symbol_values[higher] * 2 * score_multiplier

                if invert_score:
                    value = -value
                    messages.append(f"mirror + {higher.upper()} | ZTRÁTA {value}")
                else:
                    messages.append(f"mirror + {higher} | +{value}")

                total_value += value

    # ---------- DIAMOND ----------
    # diamond funguje jen na horizontálách
    best_diamond_multiplier = 0
    diamond_messages = []

    for line, coords in zip(rows, row_coords):
        diamond_count = line.count("diamond")

        if diamond_count >= 2:
            best_diamond_multiplier = max(best_diamond_multiplier, min(diamond_count, 3))
            diamond_messages.append(f"{diamond_count}x diamant | Násobič x{min(diamond_count, 3)} příště")

        elif diamond_count == 1:
            diamond_messages.append("1x diamant | NIC")

    # ========== JACKPOT ==========
    for line, coords in zip(all_lines, all_coords):
        filtered_line = [s for s in line if s != "diamond"]

        if len(filtered_line) == 3 and filtered_line.count(filtered_line[0]) == 3:
            symbol = filtered_line[0]
            if symbol in symbol_values and symbol not in SPECIAL_SYMBOLS:
                winning_lines.append(coords)
                base_value = symbol_values[symbol] * 3
                value = base_value * 5 * score_multiplier

                if invert_score:
                    value = -value
                    messages.append(f"3× {symbol.upper()} | ZTRÁTA {value}")
                else:
                    messages.append(f"3× {symbol} | JACKPOT! +{value}")
                    bonus_spins += 1

                flash_timer = pygame.time.get_ticks()
                shake_timer = pygame.time.get_ticks()

                total_value += value
                jackpot_count_total += 1
                had_jackpot = True

    # ========== 2 Stejné Symboly ==========
    if total_value == 0:
        for line, coords in zip(all_lines, all_coords):
            filtered_line = [s for s in line if s != "diamond"]

            if len(filtered_line) == 2 and filtered_line[0] == filtered_line[1]:
                symbol = filtered_line[0]

                if symbol in symbol_values and symbol not in SPECIAL_SYMBOLS:
                    value = symbol_values[symbol] * 2 * score_multiplier

                    if invert_score:
                        value = -value
                        result_text = f"2× {symbol.upper()} | ZTRÁTA {value}"
                    else:
                        result_text = f"2× {symbol} | +{value}"

                    winning_lines.append(coords)
                    total_value += value
                    break
        
    # ========== Finální Vyhodnocení ==========
    if bonus_spins > 0:
        spins_left += bonus_spins
        show_bonus_spin = True
        bonus_timer = pygame.time.get_ticks()
        show_bonus_spin_amount[0] = bonus_spins

    if had_jackpot:
        stats["jackpots"] += jackpot_count_total
        stats["current_jackpot_streak"] += 1

        if stats["current_jackpot_streak"] > stats["max_jackpot_streak"]:
            stats["max_jackpot_streak"] = stats["current_jackpot_streak"]
    else:
        stats["current_jackpot_streak"] = 0

    if total_value > stats["max_score_spin"]:
        stats["max_score_spin"] = total_value

    if messages:
        result_text = " | ".join(messages)
    elif total_value == 0:
        result_text = "NIC"

    if best_diamond_multiplier > 0:
        pending_multiplier = best_diamond_multiplier

    messages.extend(diamond_messages)

    return total_value
# ============================== Konec definice kalkulace skóre ==============================

# ========== Button Designs ==========
# ---------- Button Design (velké - hrát, leaderboard, zpět) ----------
def draw_button(text, x, y, width, height, callback, surface=screen):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    rect = pygame.Rect(x, y, width, height)

    if rect.collidepoint(mouse):
        color = DARK_GRAY
        if click[0] == 1:
            if callback:  # ✅ VOLÁME callback JEN pokud existuje
                callback()
    else:
        color = GRAY

    pygame.draw.rect(surface, color, (x, y, width, height), border_radius=8)
    pygame.draw.rect(surface, WHITE, (x, y, width, height), 2, border_radius=8)

    font = pygame.font.Font(str(BASE / "assets/fonts/VT323.ttf"), 64)
    text_render = font.render(text, True, WHITE)
    surface.blit(text_render, (x + width // 2 - text_render.get_width() // 2,
                               y + height // 2 - text_render.get_height() // 2))
    
    return rect

# ---------- Button Design (malé - credits, stats) ----------
def draw_icon_button(x, y, width, height, callback, surface=None, label="", action=None):
    if surface is None:
        surface = screen  # fallback

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, width, height)

    # Hover efekt: změní barvu pozadí
    color = GRAY if rect.collidepoint(mouse) else DARK_GRAY

    # Vykreslí pozadí + okraj
    pygame.draw.rect(surface, color, rect, border_radius=5)
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=5)

    # Vykreslí text (ikonu)
    if label:
        label_text = icon_font.render(label, True, WHITE)
        surface.blit(label_text, (
            x + (width - label_text.get_width()) // 2,
            y + (height - label_text.get_height()) // 2
        ))

    # Reakce na kliknutí
    if rect.collidepoint(mouse) and click[0] == 1:
        pygame.time.delay(200)
        if callback:
            callback()
        if action:
            action()

# ========== Nastavení začátku hry ==========
def reset_game_values():
    global total_score, spins_left, result_text, spins_used
    global score_multiplier, pending_multiplier, bomb_penalty_next_spin, chip_count

    total_score = 0
    spins_left = 10
    spins_used = 0
    result_text = ""
    score_multiplier = 1
    pending_multiplier = 1
    bomb_penalty_next_spin = False
    chip_count = 0

def try_login():
    global game_state, login_error

    if login_user(login_username.strip(), login_password):
        login_error = ""
        reset_game_values()
        game_state = "menu"
    else:
        login_error = "Nesprávné jméno nebo heslo"

def logout_user():
    global current_user, player_name, stats
    global login_username, login_password, login_error, login_active_field, game_state

    current_user = None
    player_name = ""
    stats = default_stats()

    login_username = ""
    login_password = ""
    login_error = ""
    login_active_field = "username"

    game_state = "login"

def start_game():
    global game_state
    reset_game_values()
    game_state = "game"

def restart_game():
    global game_state
    game_state = "menu"

def quit_game():
    pygame.quit()
    sys.exit()

def show_leaderboard():
    global game_state
    game_state = "leaderboard"

def show_stats():
    global game_state
    game_state = "stats"

def show_credits():
    global game_state
    game_state = "credits"

def show_help():
    global game_state
    game_state = "help"

def show_help_ingame():
    global game_state, previous_game_state, spin_input_block_until
    previous_game_state = game_state
    game_state = "helpInGame"

def return_from_help_ingame():
    global game_state, spin_input_block_until
    game_state = previous_game_state
    spin_input_block_until = pygame.time.get_ticks() + 200          #Blokace LMB na 200ms při kliknutí na zpět

def change_help_page(direction):
    global help_page
    max_page = (len(help_lines) - 1) // lines_per_page
    help_page = max(0, min(help_page + direction, max_page))

    

# ---------- Bonus (Bedny) ----------
def start_bonus_phase():
    global game_state, bonus_chests, bonus_selected, bonus_multiplier
    game_state = "bonus"
    multipliers = [1]*3 + [2]*2 + [3]                       # Počet jednotlivých multiplierů (v [] je multiplier a bez závorky je kolikrát tam je)
    random.shuffle(multipliers)
    bonus_chests = [{"x": 110 + (i % 3) * 130, "y": 100 + (i // 3) * 120, "value": multipliers[i], "revealed": False} for i in range(6)]
    bonus_selected = False
    bonus_multiplier = 1

running = True
input_active = False
clock = pygame.time.Clock()

# ============================== Loop Hry ==============================
while running:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ==== Login State ====
        elif game_state == "login":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    if login_active_field == "username":
                        login_active_field = "password"
                    else:
                        login_active_field = "username"

                elif event.key == pygame.K_RETURN:
                    try_login()

                elif event.key == pygame.K_BACKSPACE:
                    if login_active_field == "username":
                        login_username = login_username[:-1]
                    else:
                        login_password = login_password[:-1]

                else:
                    if event.unicode.isprintable():
                        if login_active_field == "username" and len(login_username) < 20:
                            login_username += event.unicode
                        elif login_active_field == "password" and len(login_password) < 30:
                            login_password += event.unicode

# ==== SPIN State (lze točit myškou i spacem ) ====
        elif game_state == "game":
            if pygame.time.get_ticks () < spin_input_block_until:
                continue
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Levé tlačítko
                mx, my = pygame.mouse.get_pos()

                if help_button_rect.collidepoint((mx,my)):
                    show_help_ingame()
                    continue

                if not animating and spins_left > 0:
                    winning_lines.clear()
                    animating = True
                    reel_anim_timer = pygame.time.get_ticks()

                # pokud chceš případně filtrovat klik mimo tlačítka, patří to sem
#                  if (not exchange_button_rect.collidepoint((mx, my)) and
#                  not upgrade_button_rect.collidepoint((mx, my))):
#                  # Klik mimo tlačítka = spusť spin

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not animating and spins_left > 0:
                    winning_lines.clear()
                    animating = True
                    reel_anim_timer = pygame.time.get_ticks()

#            if event.type == pygame.MOUSEBUTTONDOWN:
#                if exchange_button_rect.collidepoint(pygame.mouse.get_pos()):
#                    if total_score >= 100:
#                        total_score -= 100
#                        chip_count += 1
#                elif upgrade_button_rect.collidepoint((mx, my)):
#                    game_state = "upgrades"

#        elif game_state == "upgrades":
#            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
#                mx, my = pygame.mouse.get_pos()
#                # Klik na "Zpět"
#                if back_button_rect.collidepoint((mx, my)):
#                    game_state = "game"  # Návrat do hry
#                # Klik na upgrade
#                if upgrade1_rect.collidepoint((mx, my)):
#                    if chip_count >= 5:
#                        chip_count -= 5
#                    # Zde aktivuj vylepšení, např. score_multiplier += 1
#                    print("Upgrade koupen!")
#                else:
#                    print("Nemáš dost chipů.")

        # ==== SHOW RESULT State (lze pokračovat myškou i spacem) ====
        elif game_state == "show_result":
            if (event.type == pygame.MOUSEBUTTONDOWN or
                (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)):
                start_bonus_phase()

        # ==== BONUS State ====
        elif game_state == "bonus":
            if event.type == pygame.MOUSEBUTTONDOWN and not bonus_selected:
                mx, my = pygame.mouse.get_pos()
                for chest in bonus_chests:
                    rect = pygame.Rect(chest["x"], chest["y"], 80, 80)
                    if rect.collidepoint(mx, my):
                        chest["revealed"] = True
                        bonus_multiplier = chest["value"]
                        bonus_selected = True
                        total_score *= bonus_multiplier             # Celkové skóre se násobí multiplierem z bedny

                        # Spustíme časovač pro postup do výsledků
                        pygame.time.set_timer(pygame.USEREVENT + 1, 1500) # Poslední číslo je prodleva v ms

        if event.type == pygame.USEREVENT + 1:
        # ==== Uložení statistik a highscore ke konkrétnímu uživateli ====
            if current_user is not None:
                users = load_users()

                if ensure_user_data(users, current_user):
                    user_stats = users[current_user]["stats"]

                    # runtime staty přeneseme nejdřív
                    user_stats["jackpots"] = stats["jackpots"]
                    user_stats["current_jackpot_streak"] = stats["current_jackpot_streak"]
                    user_stats["max_jackpot_streak"] = stats["max_jackpot_streak"]
                    user_stats["max_score_spin"] = stats["max_score_spin"]

                    # per-game staty dopočítáme tady
                    user_stats["total_spins"] += spins_used
                    user_stats["max_spins"] = max(user_stats["max_spins"], spins_used)

                    if user_stats["lowest_score"] is None or total_score < user_stats["lowest_score"]:
                        user_stats["lowest_score"] = total_score

                    users[current_user]["highscore"] = max(
                        users[current_user].get("highscore", 0),
                        total_score
                    )

                    save_users(users)
                    stats = user_stats

            game_state = "end"
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # vypneme časovač (idk co to je?)

    screen.fill(BLACK)
    offset_surface.fill(BLACK)

    if animating:
        now = pygame.time.get_ticks()
        if now - reel_anim_timer < 1000:
            slots = [
                [random.choice(symbol_names) for _ in range(3)],
                [random.choice(symbol_names) for _ in range(3)],
                [random.choice(symbol_names) for _ in range(3)]
            ]   
        else:
            slots = spin()
            gained = calculate_score(slots)                
            total_score += gained
            spins_left -= 1
            spins_used += 1
            if spins_left == 0:                             # pokud spinů zbývá 0 tak to skončí
                game_state = "show_result"
            animating = False

    # ==== Animace u jackpotu ====
    if flash_timer and pygame.time.get_ticks() - flash_timer < 150:
        offset_surface.fill(WHITE)
    elif shake_timer and pygame.time.get_ticks() - shake_timer < 300:
        offset_x = random.randint(-5, 5)
        offset_y = random.randint(-5, 5)
        shake_offset = (offset_x, offset_y)
    else:
        shake_offset = (0, 0)

    offset_surface.fill(BLACK)

    # ==== Menu Design ====
    if game_state == "menu":
        logo_width = 600
        logo_height = int(logo.get_height() * (logo_width / logo.get_width()))
        logo_scaled = pygame.transform.scale(logo, (logo_width, logo_height))

        center_y = HEIGHT // 2 - 300
        logo_x = WIDTH // 2 - logo_scaled.get_width() // 2
        logo_y = center_y

        logo_center_x = logo_x + logo_scaled.get_width() // 2
        logo_center_y = logo_y + logo_scaled.get_height() // 2 - 10

        # logo a UI
        offset_surface.blit(logo_scaled, (logo_x, logo_y))

        if current_user:
            user_text = font.render(f"Přihlášen jako: {current_user}", True, WHITE)
            offset_surface.blit(user_text, (20, HEIGHT - 40))

        draw_button("Hrát", WIDTH // 2 - 250, 500, 500, 65, start_game, surface=offset_surface)            # Hrát Button
        draw_button("Leaderboard", WIDTH // 2 - 250, 570, 500, 65, show_leaderboard, surface=offset_surface)     # Leaderboard Button
        draw_button("Konec", WIDTH // 2 - 250, 640, 500, 65, quit_game, surface=offset_surface)                  # Quit Button
        draw_icon_button(WIDTH - 60, 10, 60, 60, show_stats, label="S", surface=offset_surface)                  # Stats Button
        draw_icon_button(WIDTH - 130, 10, 60, 60, show_credits, label="C", surface=offset_surface)                # Credits Button
        draw_icon_button(WIDTH - 200, 10, 60, 60, show_help, label="H", surface=offset_surface)                  # Help Button
        draw_icon_button(20, HEIGHT - 105, 180, 50, logout_user, label="Odhlásit" ,surface=offset_surface)

        screen.blit(offset_surface, (0, 0))

    # ==== Login Design ====

    elif game_state == "login":
        title = title_font.render("PŘIHLÁŠENÍ", True, YELLOW)
        offset_surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))

        info = big_font.render("Přihlas se účtem z webu", True, WHITE)
        offset_surface.blit(info, (WIDTH // 2 - info.get_width() // 2, 220))

        username_cursor = "|" if login_active_field == "username" and pygame.time.get_ticks() % 1000 < 500 else ""
        password_cursor = "|" if login_active_field == "password" and pygame.time.get_ticks() % 1000 < 500 else ""

        username_display = login_username + username_cursor if login_active_field == "username" else login_username
        hidden_password = "*" * len(login_password)
        password_display = hidden_password + password_cursor if login_active_field == "password" else hidden_password

        username_text = big_font.render(f"Jméno: {username_display}", True, WHITE)
        password_text = big_font.render(f"Heslo: {password_display}", True, WHITE)

        offset_surface.blit(username_text, (WIDTH // 2 - username_text.get_width() // 2, 340))
        offset_surface.blit(password_text, (WIDTH // 2 - password_text.get_width() // 2, 420))

        help_text = font.render("TAB = přepnutí pole, ENTER = přihlášení", True, WHITE)
        offset_surface.blit(help_text, (WIDTH // 2 - help_text.get_width() // 2, 500))

        if login_error:
            error_text = font.render(login_error, True, RED)
            offset_surface.blit(error_text, (WIDTH // 2 - error_text.get_width() // 2, 550))

        draw_button("Přihlásit", WIDTH // 2 - 250, 610, 500, 65, try_login, surface=offset_surface)
        draw_button("Konec", WIDTH // 2 - 250, 680, 500, 65, quit_game, surface=offset_surface)   

    # ==== Spin Design ====
    elif game_state in ("game", "show_result"):
        slot_size = 280
        slot_spacing = 50
        n = len(slots)

        total_slot_width = 3 * slot_size + 2 * slot_spacing
        total_slot_height = 3 * slot_size + 2 * slot_spacing

        inset_x = (SlotsBorder.get_width() - total_slot_width) // 2
        inset_y = (SlotsBorder.get_height() - total_slot_height) // 2

        # umístění rámečku = vystředit podle obrázku rámečku
        border_x = WIDTH // 2 - SlotsBorder.get_width() // 2
        border_y = HEIGHT // 2 - SlotsBorder.get_height() // 2

        # Background u spinů včetně rámečku
        offset_surface.blit(background, (0, 0))

#        offset_surface.blit(SlotsBorder, (border_x, border_y))

        inset_x = (SlotsBorder.get_width() - total_slot_width) // 2         # NEPLATNÝ
        inset_y = (SlotsBorder.get_height() - slot_size) // 2

        slot_start_x = border_x + inset_x
        slot_y = border_y + inset_y - 330   

        # Velikost tlačítek
        button_width = 380
        button_height = 70
        button_margin = 10  # mezera mezi tlačítky

        # Umístění pravý dolní roh
        button_x = WIDTH - button_width - 20  # 20 px odsazení od pravého okraje
        button_y = HEIGHT - (button_height * 2 + button_margin) - 20  # 20 px od spodního okraje
        
#        # Uložíme Rect pro klikání
#        exchange_button_rect = draw_button("Vyměnit (100 za 1 chip)", button_x, button_y, button_width, button_height, None, surface=offset_surface)
#        upgrade_button_rect = draw_button("Upgrady", button_x, button_y + button_height + button_margin, button_width, button_height, None, surface=offset_surface)

#        draw_button("Vyměnit (100 za 1 chip) ", button_x, button_y, button_width, button_height, None, surface=offset_surface)
#        draw_button("Upgrady", button_x, button_y + button_height + button_margin, button_width, button_height, None, surface=offset_surface)

        # Čáry co propojují u výhry
        draw_winning_lines(offset_surface, winning_lines, slot_start_x, slot_y, slot_size, slot_spacing)
        # Vykreslení slotů 3x3
        for col in range(3):
            for row in range(3):
                x = slot_start_x + col * (slot_size + slot_spacing) - 365
                y = slot_y + row * (slot_size + slot_spacing) - 18

                sym_name = slots[col][row]
                img = pygame.transform.scale(symbols[sym_name], (slot_size, slot_size))
                offset_surface.blit(img, (x, y))

        # === Chip count design ===
#        display_x = WIDTH - 80
#        display_y = HEIGHT - 215

        # === Text s počtem chipů ===
#        text = big_font.render(str(chip_count), True, (255, 255, 255))

        # === Vykreslit text ===
#        offset_surface.blit(text, (display_x, display_y))

        # === Vykreslit ikonu chipu vedle textu ===
#        img_x = display_x + text.get_width() + 5
#        img_y = display_y + (text.get_height() - chip_icon_small.get_height()) // 2
#        offset_surface.blit(chip_icon_small, (img_x, img_y))

        # === Text: Výsledek === (výš nad sloty)
        text = bigg_font.render(result_text, True, WHITE)
        offset_surface.blit(text, (WIDTH // 2 - text.get_width() // 2, slot_y - 255))

        # === Skóre (větší a blíž ke slotům) ===
        score_text = big_font.render("Skóre: " + str(total_score), True, YELLOW)
        offset_surface.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2 + 550, slot_y + slot_size + 90))

        # === Zbývající zatočení (pod skórem) ===
        spins_color = RED if spins_left <= 3 else WHITE
        spins_text = big_font.render("Zbývající zatočení: " + str(spins_left), True, spins_color)
        offset_surface.blit(spins_text, (WIDTH // 2 - spins_text.get_width() // 2 + 550, slot_y + slot_size + 140))

        # === Bonus spin (bliknutí +X) ===
        if show_bonus_spin:
            now = pygame.time.get_ticks()
            if now - bonus_timer < 1000:
                bonus_text = big_font.render(f"+{show_bonus_spin_amount[0]}", True, GREEN)
                offset_surface.blit(bonus_text, (
                    WIDTH // 2 + spins_text.get_width() // 2 + 555,
                    slot_y + slot_size + 140
                ))
            else:
                show_bonus_spin = False
                show_bonus_spin_amount[0] = 1

        # === Když dojdou spiny ===
        if game_state == "show_result":
            prompt = big_font.render("Klikni pro bonus", True, WHITE)
            offset_surface.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2 + 550, slot_y + slot_size + 190))

        # === Help Button ===
        draw_icon_button(WIDTH - 130, 10, 120, 60, show_help_ingame, label="Help", surface=offset_surface)
        help_button_rect = pygame.Rect(WIDTH - 130, 10, 120, 60)

    # ==== Upgrades Design ====
    elif game_state == "upgrades":
        # Pozadí
        offset_surface.fill((30, 30, 30))

        # Nadpis
        title = title_font.render("Upgrady", True, WHITE)
        offset_surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        # Ukázka upgrade tlačítka
        upgrade1_rect = pygame.Rect(WIDTH // 2 - 150, 150, 300, 80)
        pygame.draw.rect(offset_surface, GRAY, upgrade1_rect, border_radius=8)
        pygame.draw.rect(offset_surface, WHITE, upgrade1_rect, 2, border_radius=8)
        upgrade_text = font.render("Lepší výhry (5 chipů)", True, WHITE)
        offset_surface.blit(upgrade_text, (
            upgrade1_rect.centerx - upgrade_text.get_width() // 2,
            upgrade1_rect.centery - upgrade_text.get_height() // 2))

        # Tlačítko zpět
        back_button_rect = pygame.Rect(20, HEIGHT - 90, 200, 60)
        pygame.draw.rect(offset_surface, GRAY, back_button_rect, border_radius=8)
        pygame.draw.rect(offset_surface, WHITE, back_button_rect, 2, border_radius=8)
        back_text = font.render("Zpět", True, WHITE)
        offset_surface.blit(back_text,(
            back_button_rect.centerx - back_text.get_width() // 2,
            back_button_rect.centery - back_text.get_height() // 2))
    
    # ==== Bonus Design ====
    elif game_state == "bonus":
        title_text = title_font.render("Vyber si bednu", True, YELLOW)
        offset_surface.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 300))
        chest_size = 120  # zvětšené truhly pro fullscreen
        spacing = 60
        total_width = len(bonus_chests) * chest_size + (len(bonus_chests) - 1) * spacing
        start_x = WIDTH // 2 - total_width // 2
        chest_y = HEIGHT // 2 - chest_size // 2

        for i, chest in enumerate(bonus_chests):
            chest["x"] = start_x + i * (chest_size + spacing)
            chest["y"] = chest_y
            offset_surface.blit(pygame.transform.scale(chest_image, (chest_size, chest_size)), (chest["x"], chest["y"]))
            if chest["revealed"]:
                val = font.render(f"{chest['value']}x", True, GREEN)
                text_x = chest["x"] + chest_size // 2 - val.get_width() // 2
                text_y = chest["y"] + chest_size + 10
                offset_surface.blit(val, (text_x, text_y))

    # ==== End Design ====
    elif game_state == "end":
        end_text = title_font.render("KONEC HRY", True, YELLOW)
        final_score = big_font.render(f"Celkové skóre: {total_score}", True, WHITE)
        total_spins = big_font.render(f"Celkový počet zatočení: {spins_used}", True, WHITE)

        y_start = HEIGHT // 2 - 100
        spacing = 50

        offset_surface.blit(end_text, (WIDTH // 2 - end_text.get_width() // 2, y_start))
        offset_surface.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, y_start + spacing + 80))
        offset_surface.blit(total_spins, (WIDTH // 2 - total_spins.get_width() // 2, y_start + spacing * 2 +80))

        button_width = 320
        button_height = 70
        draw_button(
            "Zpět do menu",
            WIDTH // 2 - button_width // 2,
            y_start + spacing * 3 + 324,
            button_width,
            button_height,
            restart_game,
            surface=offset_surface
        )

    # ==== Leaderboard Design ====
    elif game_state == "leaderboard":
        title = title_font.render("LEADERBOARD", True, YELLOW)  # Stejný font jako u stats
        offset_surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        line_spacing = 50
        start_y = 250

        # Vytvoř leaderboard z users.json
        leaderboard_rows = get_leaderboard_rows()

        lines = []
        for i in range(10):
            if i < len(leaderboard_rows):
                entry = leaderboard_rows[i]
                lines.append((f"{i+1}. {entry['name']}", f"{entry['score']}"))
            else:
                lines.append((f"{i+1}. ---", "---"))

        # Render textů
        rendered_labels = [text_font.render(label, True, WHITE) for label, _ in lines]
        rendered_values = [text_font.render(value, True, WHITE) for _, value in lines]

        # Vypočítej zarovnání
        max_label_width = max(lbl.get_width() for lbl in rendered_labels) if rendered_labels else 0
        max_value_width = max(val.get_width() for val in rendered_values) if rendered_values else 0

        label_value_gap = 100
        total_width = max_label_width + label_value_gap + max_value_width
        start_x = WIDTH // 2 - total_width // 2

        for i, (label, value) in enumerate(lines):
                y = start_y + i * line_spacing
                label_surf = text_font.render(label, True, WHITE)
                value_surf = text_font.render(value, True, WHITE)
                label_x = start_x
                value_x = start_x + max_label_width + label_value_gap + (max_value_width - value_surf.get_width())
                offset_surface.blit(label_surf, (label_x, y))
                offset_surface.blit(value_surf, (value_x, y))

        draw_button("Zpět", WIDTH // 2 - 500 // 2, 380 + len(lines) * line_spacing + 40,
                    500, 65, restart_game, surface=offset_surface)


    # ==== Stats Design ====
    elif game_state == "stats":
        title = title_font.render("STATISTIKY", True, YELLOW)                                         # Nadpis
        offset_surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        highscore = get_current_user_highscore()
        line_spacing = 60

        lines = [
            ("Celkový počet zatočení:", f"{stats['total_spins']}"),
            ("Nejvíce zatočení v jedné hře:", f"{stats['max_spins']}"),
            ("Počet jackpotů:", f"{stats['jackpots']}"),
            ("Nejvíc jackpotů v kuse:", f"{stats['max_jackpot_streak']}"),
            ("Největší skóre z jednoho zatočení:", f"{stats['max_score_spin']}"),
            ("Nejnižší osobní skóre:", f"{stats['lowest_score'] if stats['lowest_score'] is not None else 'Žádné'}"),
            ("Nejvyšší osobní skóre:", f"{highscore}")
        ]

        # Render textů
        rendered_labels = [text_font.render(label, True, WHITE) for label, _ in lines]
        rendered_values = [text_font.render(value, True, WHITE) for _, value in lines]

        # Vypočítej největší šířku pro zarovnání
        max_label_width = max(lbl.get_width() for lbl in rendered_labels)
        max_value_width = max(val.get_width() for val in rendered_values)

        label_value_gap = 100
        total_width = max_label_width + label_value_gap + max_value_width

        start_x = WIDTH // 2 - total_width // 2
        start_y = 260  # nebo 270 či 280 – podle potřeby

        for i, (lbl_surf, val_surf) in enumerate(zip(rendered_labels, rendered_values)):
            y = start_y + i * line_spacing
            label_x = start_x
            value_x = start_x + max_label_width + label_value_gap + (max_value_width - val_surf.get_width())
            offset_surface.blit(lbl_surf, (label_x, y))
            offset_surface.blit(val_surf, (value_x, y))


        draw_button("Zpět", WIDTH //2 - 500 // 2, 520 + len(lines) * line_spacing + 40,
                    500, 65, restart_game, surface=offset_surface)

    # ==== Credits Design ====
    elif game_state == "credits":
        title = title_font.render("CREDITS", True, YELLOW)
        offset_surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        credits_lines = [
        "AUTOR",
        "Adam Procházka",
        "",
        "TESTEŘI",
        "Vojtěch Procházka",
        "Lukáš Čarada",
        "William Nobilis",
        "Helena Procházková",
        "Další spolužáci",
        "",
        "Vytvořeno 12.5.2025"
        ]

        line_spacing = 45
        total_height = len(credits_lines) * line_spacing
        start_y = HEIGHT // 2 - total_height // 2 - 80

        for i, line in enumerate(credits_lines):
            txt = desc_font.render(line, True, WHITE)
            offset_surface.blit(txt, (WIDTH // 2 - txt.get_width() // 2, start_y + i * line_spacing))

        draw_button("Zpět", WIDTH // 2 - 230, start_y + total_height + 207, 480, 70, restart_game, surface=offset_surface)

    # ==== Help Design ====
    elif game_state == "help":
        title = title_font.render("NÁPOVĚDA", True, YELLOW)
        offset_surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        help_lines = [
        ("Diamond", "Násobí skóre dalšího kola"),
        ("Golden Seven", "Největší skóre ze hry (za jeden 3350)"),
        ("Chests", "Možnost znásobit své skóre"),
        ("Mirror", "Může nahradit většinu symbolů"),
        ("Reroll", "Vrací zpět několik zatočení"),
        ("Bomb", "V dalším kole se skóre odečítá"),
        ("Star", "PLACEHOLDER"),
        ("Shiny Symboly", "Dávají 2x víc skóre než normální")
        ]

        symbol_images = {
        "Diamond": diamond_img,
        "Golden Seven": golden_seven_img,
        "Chests": chest_img,
        "Mirror": mirror_img,
        "Reroll": reroll_img,
        "Bomb": bomb_img,
        "Star": star_img,
        "Shiny Symboly": shiny_orange_img
        }

        lines_per_page = 4
        line_spacing = 140  # ⬅️ Zvětšený vertikální prostor mezi položkami
        total_pages = (len(help_lines) + lines_per_page - 1) // lines_per_page
        start_line = help_page * lines_per_page
        end_line = start_line + lines_per_page

        clip_rect = pygame.Rect(80, 120, WIDTH - 160, lines_per_page * line_spacing + 80)
        help_surface = pygame.Surface((clip_rect.width, clip_rect.height), pygame.SRCALPHA)
        help_surface.fill((0, 0, 0, 0))

        # Horní a dolní mezera (červená a modrá čára)
        top_y = 15
        bottom_y = 650
        total_space = bottom_y - top_y

        # Počet mezer = počet položek + 1 (mezera i nahoře a dole)
        num_items = lines_per_page
        spacing = total_space // (num_items + 1)  # tedy 440 // 5 = 88 px

        for i, (title_line, desc_line) in enumerate(help_lines[start_line:end_line]):
            y_base = top_y + (i + 1) * spacing  # (i + 1), protože chceme mezeru i nahoře

             # Texty
            title_txt = bold_font.render(title_line, True, WHITE)
            desc_txt = desc_font.render(desc_line, True, WHITE)

            # Šířka obou textů
            max_text_width = max(title_txt.get_width(), desc_txt.get_width())
            text_x = clip_rect.width // 2 - max_text_width // 2  # zarovnání na střed v rámci clip_rect

            text_x = 470
            help_surface.blit(title_txt, (text_x, y_base))
            help_surface.blit(desc_txt, (text_x, y_base + 60))

            # Ikona zarovnaná doprava
            if title_line in symbol_images:
                img = symbol_images[title_line]
                img_x = 1200
                img_y = y_base + 10
                help_surface.blit(img, (img_x, img_y))

        offset_surface.blit(help_surface, (clip_rect.x, clip_rect.y))

        # ===== Tlačítka dole =====
        button_y = clip_rect.y + clip_rect.height + 155
        button_width = 480
        button_height = 70

        def previous_page():
            global help_page
            if help_page > 0:
                help_page -= 1

        def next_page():
            global help_page
            if (help_page + 1) * lines_per_page < len(help_lines):
                help_page += 1

        # Tlačítko Zpět na střed
        draw_button("Zpět", WIDTH // 2 - button_width // 2, button_y, button_width, button_height, restart_game, surface=offset_surface)

        # Šipky těsně vedle tlačítka
        arrow_margin = 40
        draw_button("<", WIDTH // 2 - button_width // 2 - arrow_margin - 50, button_y, 80, button_height, previous_page, surface=offset_surface)
        draw_button(">", WIDTH // 2 + button_width // 2 + arrow_margin - 30, button_y, 80, button_height, next_page, surface=offset_surface)

        # Číslo stránky
        page_text = font.render(f"Strana {help_page + 1} / {total_pages}", True, WHITE)
        offset_surface.blit(page_text, (WIDTH // 2 - page_text.get_width() // 2, button_y - 40))

    # ==== Help In Game Design ====
    elif game_state == "helpInGame":
        title = title_font.render("NÁPOVĚDA IN GAME", True, YELLOW)
        offset_surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))


        help_lines = [
        ("Diamond", "Násobí skóre dalšího kola"),
        ("Golden Seven", "Největší skóre ze hry (za jeden 3350)"),
        ("Chests", "Možnost znásobit své skóre"),
        ("Mirror", "Může nahradit většinu symbolů"),
        ("Reroll", "Vrací zpět několik zatočení"),
        ("Bomb", "V dalším kole se skóre odečítá"),
        ("Star", "PLACEHOLDER"),
        ("Shiny Symboly", "Dávají 2x víc skóre než normální")
        ]

        symbol_images = {
        "Diamond": diamond_img,
        "Golden Seven": golden_seven_img,
        "Chests": chest_img,
        "Mirror": mirror_img,
        "Reroll": reroll_img,
        "Bomb": bomb_img,
        "Star": star_img,
        "Shiny Symboly": shiny_orange_img
        }

        lines_per_page = 4
        line_spacing = 140  # ⬅️ Zvětšený vertikální prostor mezi položkami
        total_pages = (len(help_lines) + lines_per_page - 1) // lines_per_page
        start_line = help_page * lines_per_page
        end_line = start_line + lines_per_page

        clip_rect = pygame.Rect(80, 120, WIDTH - 160, lines_per_page * line_spacing + 80)
        help_surface = pygame.Surface((clip_rect.width, clip_rect.height), pygame.SRCALPHA)
        help_surface.fill((0, 0, 0, 0))

        # Horní a dolní mezera (červená a modrá čára)
        top_y = 15
        bottom_y = 650
        total_space = bottom_y - top_y

        # Počet mezer = počet položek + 1 (mezera i nahoře a dole)
        num_items = lines_per_page
        spacing = total_space // (num_items + 1)  # tedy 440 // 5 = 88 px

        for i, (title_line, desc_line) in enumerate(help_lines[start_line:end_line]):
            y_base = top_y + (i + 1) * spacing  # (i + 1), protože chceme mezeru i nahoře

             # Texty
            title_txt = bold_font.render(title_line, True, WHITE)
            desc_txt = desc_font.render(desc_line, True, WHITE)

            # Šířka obou textů
            max_text_width = max(title_txt.get_width(), desc_txt.get_width())
            text_x = clip_rect.width // 2 - max_text_width // 2  # zarovnání na střed v rámci clip_rect

            text_x = 470
            help_surface.blit(title_txt, (text_x, y_base))
            help_surface.blit(desc_txt, (text_x, y_base + 60))

            # Ikona zarovnaná doprava
            if title_line in symbol_images:
                img = symbol_images[title_line]
                img_x = 1200
                img_y = y_base + 10
                help_surface.blit(img, (img_x, img_y))

        offset_surface.blit(help_surface, (clip_rect.x, clip_rect.y))

        # ===== Tlačítka dole =====
        button_y = clip_rect.y + clip_rect.height + 155
        button_width = 480
        button_height = 70

        def previous_page():
            global help_page
            if help_page > 0:
                help_page -= 1

        def next_page():
            global help_page
            if (help_page + 1) * lines_per_page < len(help_lines):
                help_page += 1

        # Tlačítko Zpět na střed
        draw_button("Zpět", WIDTH // 2 - button_width // 2, button_y, button_width, button_height, return_from_help_ingame, surface=offset_surface)

        # Šipky těsně vedle tlačítka
        arrow_margin = 40
        draw_button("<", WIDTH // 2 - button_width // 2 - arrow_margin - 50, button_y, 80, button_height, previous_page, surface=offset_surface)
        draw_button(">", WIDTH // 2 + button_width // 2 + arrow_margin - 30, button_y, 80, button_height, next_page, surface=offset_surface)

        # Číslo stránky
        page_text = font.render(f"Strana {help_page + 1} / {total_pages}", True, WHITE)
        offset_surface.blit(page_text, (WIDTH // 2 - page_text.get_width() // 2, button_y - 40))

    screen.blit(offset_surface, shake_offset)

    # ==== Jackpot effect ====
    if flash_timer and pygame.time.get_ticks() - flash_timer < 200:                                 # Jak dlouho to bude v ms (asi?)
        flash_overlay = pygame.Surface((WIDTH, HEIGHT))
        flash_overlay.set_alpha(80)                                                                 # Průhlednost
        flash_overlay.fill(WHITE)                                                                   # Barva flashe
        screen.blit(flash_overlay, (0, 0))

    pygame.display.flip()

pygame.quit()
sys.exit()