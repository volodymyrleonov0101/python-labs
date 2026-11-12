import os
import pickle

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEVELS_DIR = os.path.join(BASE_DIR, "levels")
INDEX_FILE = os.path.join(LEVELS_DIR, "index.txt")
RECORDS_FILE = os.path.join(BASE_DIR, "records.txt")
SAVE_FILE = os.path.join(BASE_DIR, "savegame.pkl")


ELEMENTS = {
    "#": {"name": "стена", "icon": "⬛", "passable": False, "points": 0,
          "blocked": "Там стена!"},
    ".": {"name": "пусто", "icon": "⬜", "passable": True, "points": 0},
    "K": {"name": "ключ", "icon": "🔑", "passable": True, "points": 10},
    "D": {"name": "дверь", "icon": "🔒", "passable": False, "points": 0,
          "blocked": "Дверь закрыта 🔒 — нужен ключ"},
    "E": {"name": "выход", "icon": "🏁", "passable": True, "points": 50,
          "needs_all_keys": True,
          "blocked": "Выход закрыт! Собери все ключи."},
}
PLAYER_ICON = "😎"
EFFECT_ICON = "✨"


DIRECTIONS = {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}


ICONS = {sym: props["icon"] for sym, props in ELEMENTS.items()}


def load_level_list():
    with open(INDEX_FILE, encoding="utf-8") as f:
        names = [line.strip() for line in f if line.strip()]
    return [os.path.join(LEVELS_DIR, name) for name in names]


def load_level(path):
    with open(path, encoding="utf-8") as f:
        rows = [line.rstrip("\n") for line in f if line.strip()]
    field = [list(row) for row in rows]
    start = next((x, y) for y, row in enumerate(field)
                 for x, ch in enumerate(row) if ch == "@")
    x, y = start
    field[y][x] = "."
    return field, start


def new_state(path, **extra):
    field, pos = load_level(path)
    state = {
        "level_path": path,
        "level_name": os.path.basename(path),
        "field": field,
        "pos": pos,
        "doors": [(x, y) for y, row in enumerate(field)
                  for x, ch in enumerate(row) if ch == "D"],
        "total_keys": sum(row.count("K") for row in field),
        "keys": 0,
        "steps": 0,
        "score": 0,
        "visited": {pos},
        "collected": set(),
        "effect": None,
        "message": "Собери все ключи и дойди до 🏁. Ходи: W A S D + Enter "
                   "(p — сохранить, l — загрузить, q — выход)",
    }
    state.update(extra)
    return state


def save_record(player, level_name, steps, score):
    line = ";".join([level_name, player, str(steps), str(score)])
    with open(RECORDS_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_records():
    records = []
    if not os.path.exists(RECORDS_FILE):
        return records
    with open(RECORDS_FILE, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(";")
            if len(parts) < 4:
                continue
            level, name, *numbers = parts
            steps, score = map(int, numbers[:2])
            records.append((level, name, steps, score))
    return records


def best_records():
    best = {}
    for level, name, steps, _score in load_records():
        if level not in best or steps < best[level][1]:
            best[level] = (name, steps)
    return best


def save_game(state):
    with open(SAVE_FILE, "wb") as f:
        pickle.dump(state, f)


def load_game():
    if not os.path.exists(SAVE_FILE):
        return None
    with open(SAVE_FILE, "rb") as f:
        return pickle.load(f)


def draw(state):
    os.system("cls" if os.name == "nt" else "clear")
    for y, row in enumerate(state["field"]):
        line = []
        for x, ch in enumerate(row):
            if (x, y) == state["pos"]:
                line.append(PLAYER_ICON)
            elif (x, y) == state["effect"]:
                line.append(EFFECT_ICON)
            else:
                line.append(ICONS[ch])
        print("".join(line))
    print()
    print(info_line(state["level_name"],
                    f"Ключи: {state['keys']}/{state['total_keys']}",
                    f"Шаги: {state['steps']}",
                    f"Клеток посещено: {len(state['visited'])}",
                    f"Очки: {state['score']}"))
    print(state["message"])


def info_line(*parts, sep=" | "):
    return sep.join(parts)


def move(state, key):
    field = state["field"]
    dx, dy = DIRECTIONS[key]
    x, y = state["pos"]
    nx, ny = x + dx, y + dy
    if not (0 <= ny < len(field) and 0 <= nx < len(field[ny])):
        state["message"] = "Там стена!"
        return False

    cell = field[ny][nx]
    props = ELEMENTS[cell]

    if not props["passable"]:
        state["message"] = props["blocked"]
        return False
    if props.get("needs_all_keys") and state["keys"] < state["total_keys"]:
        state["message"] = props["blocked"]
        return False

    state["pos"] = (nx, ny)
    state["steps"] += 1
    state["visited"].add((nx, ny))
    state["score"] += props["points"]
    state["message"] = ""

    if cell == "K":
        field[ny][nx] = "."
        state["collected"].add((nx, ny))
        state["keys"] += 1
        state["message"] = "Ты взял ключ 🔑"
        if state["doors"]:
            dx_, dy_ = state["doors"].pop()
            field[dy_][dx_] = "."
            state["effect"] = (dx_, dy_)
            state["message"] += " — где-то открылась дверь ✨"
    return cell == "E"


def play_level(state, player):
    while True:
        draw(state)
        cmd = input("> ").strip().lower()

        if cmd == "q":
            return "quit"
        if cmd == "p":
            save_game(state)
            state["message"] = "Игра сохранена 💾"
            continue
        if cmd == "l":
            loaded = load_game()
            if loaded is None:
                state["message"] = "Сохранения нет."
            else:
                state.clear()
                state.update(loaded)
                state["message"] = "Игра загружена 📂"
            continue
        if cmd not in DIRECTIONS:
            state["message"] = "Используй W A S D (p, l, q — команды)"
            continue

        state["effect"] = None
        if move(state, cmd):
            draw(state)
            print(f"\n🎉 Уровень {state['level_name']} пройден! "
                  f"Шагов: {state['steps']}, очков: {state['score']}")
            save_record(player, state["level_name"],
                        state["steps"], state["score"])
            name, steps = best_records()[state["level_name"]]
            print(f"🏆 Рекорд уровня: {name} — {steps} шагов")
            input("Enter — дальше...")
            return "win"


def main():
    player = input("Имя игрока: ").strip().title() or "Игрок"
    levels = load_level_list()
    index = 0
    total_score = 0

    while index < len(levels):
        state = new_state(levels[index], index=index)
        result = play_level(state, player)
        if result == "quit":
            break
        total_score += state["score"]
        index = state["index"] + 1
    else:
        print(f"\n🏁 Все уровни пройдены! Общий счёт: {total_score}")
        return
    print("Игра завершена.")


if __name__ == "__main__":
    main()
