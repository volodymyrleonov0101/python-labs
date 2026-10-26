import os

# '#' стена, '.' пусто, 'K' ключ, 'D' дверь, 'E' выход, '@' игрок
MAZE = [
    "##########",
    "#@.#....K#",
    "#..#.#.#.#",
    "#.K#.#D###",
    "#..D.#...#",
    "####.#.#.#",
    "#K...#.#E#",
    "##########",
]

SYMBOLS = {
    "#": "⬛", ".": "▫️", "K": "🗝️", "D": "🔒",
    "E": "🏁", "@": "😎", "*": "✨",
}

grid = [list(row) for row in MAZE]

for r, row in enumerate(grid):
    for c, ch in enumerate(row):
        if ch == "@":
            pr, pc = r, c
            grid[r][c] = "."

doors = [(r, c) for r, row in enumerate(grid) for c, ch in enumerate(row) if ch == "D"]
total_keys = sum(row.count("K") for row in grid)
keys = 0
effect = None
message = "Собери все ключи и дойди до 🏁. Ходи: W A S D + Enter"


def draw():
    os.system("cls" if os.name == "nt" else "clear")
    for r, row in enumerate(grid):
        line = ""
        for c, ch in enumerate(row):
            if (r, c) == (pr, pc):
                line += SYMBOLS["@"]
            elif (r, c) == effect:
                line += SYMBOLS["*"]
            else:
                line += SYMBOLS[ch]
        print(line)
    print(f"\nКлючи: {keys}/{total_keys}")
    print(message)


moves = {"w": (-1, 0), "s": (1, 0), "a": (0, -1), "d": (0, 1)}

while True:
    draw()
    cmd = input("> ").lower().strip()
    if cmd == "q":
        break
    if cmd not in moves:
        message = "Используй W A S D (q — выход)"
        continue

    effect = None
    nr, nc = pr + moves[cmd][0], pc + moves[cmd][1]
    cell = grid[nr][nc]

    if cell == "#":
        message = "Там стена!"
    elif cell == "D":
        message = "Дверь закрыта 🔒 — нужен ключ"
    elif cell == "E" and keys < total_keys:
        message = "Выход закрыт! Собери все ключи."
    else:
        pr, pc = nr, nc
        message = ""
        if cell == "K":
            grid[pr][pc] = "."
            keys += 1
            message = "Ты взял ключ 🗝️"
            if doors:  
                dr, dc = doors.pop()
                grid[dr][dc] = "."
                effect = (dr, dc)
                message += " — где-то открылась дверь ✨"
        elif cell == "E":
            draw()
            print("\n🎉 Ты вышел из лабиринта! Победа!")
            break
