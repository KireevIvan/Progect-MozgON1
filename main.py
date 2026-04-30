
import tkinter as tk
from tkinter import messagebox, font
import json
import time
import random
from pathlib import Path
from typing import Dict, Any, Optional, List

# --- Константы ---
STATS_FILE = Path("stats.json")
SYMBOLS: List[str] = ['1', '2', '3', '4', '5', 'A', 'B', 'C', 'D', 'E']
EMOJIS: List[str] = ['😀', '🐱', '🚗', '🍎', '🌟']
REACTION_THRESHOLDS: Dict[int, float] = {1: 1.5, 2: 1.3, 3: 1.1, 4: 0.9}
MAX_LEVEL: int = 10


# --- Утилиты работы с данными ---
def load_stats() -> Dict[str, Any]:
    if not STATS_FILE.exists():
        return {}
    try:
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_stats(stats: Dict[str, Any]) -> bool:
    try:
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        messagebox.showerror("Ошибка сохранения", f"Не удалось записать данные:\n{e}")
        return False


# --- Экран: СТАРТ ---
class StartScreen(tk.Frame):
    def __init__(self, master: tk.Tk, **kwargs: Any) -> None:
        super().__init__(master, **kwargs)
        self.master_app = master
        self._build_ui()

    def _build_ui(self) -> None:
        self.configure(bg="#f0f4f8")

        tk.Label(self, text="Добро пожаловать!", font=("Segoe UI", 26, "bold"),
                 bg="#f0f4f8", fg="#2c3e50").pack(pady=(40, 20))

        self.nick_var = tk.StringVar()
        self.nick_entry = tk.Entry(self, textvariable=self.nick_var, font=("Segoe UI", 18),
                                   justify=tk.CENTER, width=15)
        self.nick_entry.pack(pady=10, ipady=8)
        self.nick_entry.bind("<Return>", lambda e: self.start_game("elderly"))

        btn_frame = tk.Frame(self, bg="#f0f4f8")
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Пожилой", font=("Segoe UI", 16), width=12, bg="#a8d8ea",
                  command=lambda: self.start_game("elderly")).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Ребёнок", font=("Segoe UI", 16), width=12, bg="#fce38a",
                  command=lambda: self.start_game("child")).pack(side=tk.LEFT, padx=10)

        self.nick_entry.focus_set()

    def start_game(self, mode: str) -> None:
        nick = self.nick_var.get().strip()
        if not nick:
            messagebox.showwarning("Внимание", "Пожалуйста, введите никнейм!")
            self.nick_entry.focus_set()
            return

        stats = load_stats()
        if nick not in stats:
            stats[nick] = {'mode': mode, 'memory_level': 1, 'reaction_level': 1, 'games_played': 0}
        elif stats[nick].get('mode') != mode:
            stats[nick]['mode'] = mode

        if not save_stats(stats):
            return

        self.master_app.switch_to_game(nick, mode, stats[nick].copy())


# --- Экран: ИГРА ---
class GameScreen(tk.Frame):
    def __init__(self, master: tk.Tk, **kwargs: Any) -> None:
        super().__init__(master, **kwargs)
        self.master_app = master
        self.user_nick: Optional[str] = None
        self.user_data: Optional[Dict[str, Any]] = None  # ✅ Исправлено
        self.reaction_start_time: Optional[float] = None
        self.current_game: Optional[str] = None
        self._build_ui()

    def _build_ui(self) -> None:
        self.configure(bg="#f0f4f8")

        header = tk.Frame(self, bg="#f0f4f8")
        header.pack(fill=tk.X, pady=10, padx=15)

        self.user_label = tk.Label(header, text="Игрок: ", font=("Segoe UI", 14), bg="#f0f4f8")
        self.user_label.pack(side=tk.LEFT)

        tk.Button(header, text="📊 Статистика", font=("Segoe UI", 12),
                  command=self.show_stats).pack(side=tk.RIGHT, padx=5)
        tk.Button(header, text="⬅ Назад", font=("Segoe UI", 12),
                  command=self.master_app.switch_to_start).pack(side=tk.RIGHT, padx=5)

        mode_frame = tk.Frame(self, bg="#f0f4f8")
        mode_frame.pack(pady=15)

        tk.Button(mode_frame, text="🧠 Тренировка памяти", font=("Segoe UI", 16), width=20, bg="#e8f5e9",
                  command=self.start_memory_game).pack(side=tk.LEFT, padx=10)
        tk.Button(mode_frame, text="⚡ Тренировка реакции", font=("Segoe UI", 16), width=20, bg="#fff3e0",
                  command=self.start_reaction_game).pack(side=tk.LEFT, padx=10)

        self.game_area = tk.Frame(self, bg="#ffffff", bd=2, relief=tk.GROOVE)
        self.game_area.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

    def init_session(self, nick: str, mode: str, data: Dict[str, Any]) -> None:
        self.user_nick = nick
        self.user_data = data
        self.user_label.config(text=f"Игрок: {nick}")
        self.clear_game_area()

    def clear_game_area(self) -> None:
        for w in self.game_area.winfo_children():
            w.destroy()

    def show_stats(self) -> None:
        if not self.user_data:  # ✅ Исправлено
            return
        mode_text = "👴 Пожилой" if self.user_data['mode'] == 'elderly' else "👶 Ребёнок"
        lvl = self.user_data['reaction_level']
        threshold = REACTION_THRESHOLDS.get(lvl)
        thr_text = f"{threshold:.2f}" if threshold is not None else "?"

        msg = (f"Статистика: {self.user_nick}\n\n"
               f"Режим: {mode_text}\n"
               f"🧠 Память: уровень {self.user_data['memory_level']}\n"
               f"⚡ Реакция: уровень {lvl} (цель < {thr_text}с)\n"
               f"🎮 Игр сыграно: {self.user_data.get('games_played', 0)}")
        messagebox.showinfo("Статистика", msg)

    # --- ПАМЯТЬ ---
    def start_memory_game(self) -> None:
        self.current_game = 'memory'
        self.master_app.cancel_jobs()
        self.clear_game_area()

        if not self.user_data:  # ✅ Исправлено
            return
        lvl = self.user_data['memory_level']
        symbols = SYMBOLS if self.user_data['mode'] == 'elderly' else EMOJIS
        length = min(lvl, len(symbols))
        sequence = random.sample(symbols, length)

        tk.Label(self.game_area, text=" ".join(sequence), font=("Segoe UI", 48),
                 bg="#ffffff", fg="#2c3e50").pack(expand=True)

        self.master_app.schedule(2000, lambda: self.show_memory_input(sequence))

    def show_memory_input(self, sequence: List[str]) -> None:
        self.clear_game_area()
        tk.Label(self.game_area, text="Введите последовательность через пробел:",
                 font=("Segoe UI", 16), bg="#ffffff").pack(pady=10)

        entry = tk.Entry(self.game_area, font=("Segoe UI", 20), justify=tk.CENTER, width=15)
        entry.pack(pady=5, ipady=5)
        entry.focus_set()

        def check():
            self.check_memory_answer(sequence, entry.get().strip())

        entry.bind("<Return>", lambda e: check())
        tk.Button(self.game_area, text="✅ Проверить", font=("Segoe UI", 16),
                  command=check).pack(pady=10)

    def check_memory_answer(self, correct: List[str], answer: str) -> None:
        correct_str = " ".join(correct)
        if not self.user_data:  # ✅ Исправлено
            return

        if answer == correct_str:
            new_lvl = min(self.user_data['memory_level'] + 1, MAX_LEVEL)
            self.user_data['memory_level'] = new_lvl
            self.user_data['games_played'] = self.user_data.get('games_played', 0) + 1
            msg = f"✅ Верно!\nУровень памяти: {new_lvl}/{MAX_LEVEL}"
            messagebox.showinfo("Результат", msg)
            self.master_app.schedule(300, self.start_memory_game)
        else:
            self.user_data['games_played'] = self.user_data.get('games_played', 0) + 1
            msg = f"❌ Неверно!\nПравильный ответ:\n{correct_str}"
            messagebox.showwarning("Результат", msg)
            self.master_app.schedule(1500, self.start_memory_game)

    # --- РЕАКЦИЯ ---
    def start_reaction_game(self) -> None:
        self.current_game = 'reaction'
        self.master_app.cancel_jobs()
        self.clear_game_area()
        self.reaction_start_time = None

        self.master_app.schedule(random.randint(2000, 5000), self.show_reaction_button)

    def show_reaction_button(self) -> None:
        if self.current_game != 'reaction':
            return
        self.clear_game_area()

        btn = tk.Button(self.game_area, text="🔴 ЖМИ!", font=("Segoe UI", 36), bg="#ff6b6b", fg="white",
                        activebackground="#ff5252", activeforeground="white", padx=20, pady=20)
        btn.pack(expand=True)

        self.reaction_start_time = time.time()
        btn.config(command=self.finish_reaction)
        btn.focus_set()

    def finish_reaction(self) -> None:
        if self.reaction_start_time is None or not self.user_data:  # ✅ Исправлено
            return

        reaction_time = time.time() - self.reaction_start_time
        self.reaction_start_time = None

        level = self.user_data['reaction_level']
        threshold = REACTION_THRESHOLDS.get(level, 0.7)
        self.user_data['games_played'] = self.user_data.get('games_played', 0) + 1

        if reaction_time <= threshold:
            new_lvl = min(level + 1, MAX_LEVEL)
            self.user_data['reaction_level'] = new_lvl
            msg = f"⚡ Отлично!\nВремя: {reaction_time:.2f}с < {threshold:.2f}с\nУровень: {new_lvl}/{MAX_LEVEL}"
            messagebox.showinfo("Результат", msg)
            self.master_app.schedule(500, self.start_reaction_game)
        else:
            msg = f"⏱ Медленно!\nВремя: {reaction_time:.2f}с\nЦель: < {threshold:.2f}с\nПопробуй ещё!"
            messagebox.showinfo("Результат", msg)
            self.master_app.schedule(1000, self.start_reaction_game)


# --- Главное приложение ---
class BrainTrainerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("🧠⚡ Тренировка мозга")
        self.geometry("550x700")
        self.resizable(False, False)
        self.configure(bg="#f0f4f8")

        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=12)
        self.option_add("*Font", default_font)

        self.start_screen = StartScreen(self)
        self.game_screen = GameScreen(self)
        self.start_screen.pack(fill=tk.BOTH, expand=True)
        self.game_screen.pack(fill=tk.BOTH, expand=True)
        self.game_screen.pack_forget()

        self._pending_jobs: List[int] = []

    def switch_to_game(self, nick: str, mode: str, data: Dict[str, Any]) -> None:
        self.cancel_jobs()
        self.start_screen.pack_forget()
        self.game_screen.pack(fill=tk.BOTH, expand=True)
        self.game_screen.init_session(nick, mode, data)

    def switch_to_start(self) -> None:
        self.cancel_jobs()
        # Сохраняем прогресс при выходе
        if self.game_screen.user_nick and self.game_screen.user_data:  # ✅ Исправлено
            stats = load_stats()
            if self.game_screen.user_nick in stats:
                stats[self.game_screen.user_nick].update(self.game_screen.user_data)
                save_stats(stats)

        self.game_screen.pack_forget()
        self.start_screen.pack(fill=tk.BOTH, expand=True)
        self.start_screen.nick_var.set("")
        self.start_screen.nick_entry.focus_set()

    def schedule(self, ms: int, callback: Any) -> int:
        job = self.after(ms, callback)
        self._pending_jobs.append(job)
        return job

    def cancel_jobs(self) -> None:
        for job in self._pending_jobs:
            self.after_cancel(job)
        self._pending_jobs.clear()


# Запуск приложения
app = BrainTrainerApp()
app.mainloop()
