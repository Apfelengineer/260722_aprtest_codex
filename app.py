"""Local desktop application: なんでも質問保存箱."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from data_store import CsvStore, QuestionAnswer


APP_TITLE = "なんでも質問保存箱"
CONFIG_DIR = Path.home() / ".nandemo-shitsumon"
CONFIG_PATH = CONFIG_DIR / "settings.json"


class QuestionBoxApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("940x680")
        self.minsize(720, 560)
        self.configure(bg="#f5f5f7")

        self.folder = tk.StringVar(value=self._load_folder())
        self.status = tk.StringVar(value="保存先フォルダを選択してください")
        self.count = tk.StringVar(value="0件")
        self.current_view = "input"

        self._configure_style()
        self._build_shell()
        self.show_input()
        if self.folder.get():
            self._refresh_count()

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        available = style.theme_names()
        style.theme_use("aqua" if sys.platform == "darwin" and "aqua" in available else "clam")
        style.configure("App.TFrame", background="#f5f5f7")
        style.configure("Card.TFrame", background="#ffffff")
        style.configure("Title.TLabel", background="#f5f5f7", foreground="#1d1d1f", font=("TkDefaultFont", 24, "bold"))
        style.configure("Subtitle.TLabel", background="#f5f5f7", foreground="#6e6e73", font=("TkDefaultFont", 11))
        style.configure("CardTitle.TLabel", background="#ffffff", foreground="#1d1d1f", font=("TkDefaultFont", 15, "bold"))
        style.configure("Body.TLabel", background="#ffffff", foreground="#3a3a3c", font=("TkDefaultFont", 11))
        style.configure("Muted.TLabel", background="#ffffff", foreground="#6e6e73", font=("TkDefaultFont", 10))
        style.configure("Primary.TButton", font=("TkDefaultFont", 11, "bold"), padding=(18, 10))
        style.configure("Secondary.TButton", font=("TkDefaultFont", 11), padding=(14, 9))
        style.configure("Nav.TButton", font=("TkDefaultFont", 11, "bold"), padding=(14, 8))
        style.configure("Treeview", rowheight=42, font=("TkDefaultFont", 11), background="#ffffff", fieldbackground="#ffffff", foreground="#1d1d1f")
        style.configure("Treeview.Heading", font=("TkDefaultFont", 10, "bold"), padding=(10, 8))

    def _build_shell(self) -> None:
        root = ttk.Frame(self, style="App.TFrame", padding=(36, 28, 36, 24))
        root.pack(fill="both", expand=True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(2, weight=1)

        header = ttk.Frame(root, style="App.TFrame")
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text=APP_TITLE, style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="大切な質問と答えを、あなたのPCだけに。", style="Subtitle.TLabel").grid(row=1, column=0, sticky="w", pady=(4, 0))

        nav = ttk.Frame(header, style="App.TFrame")
        nav.grid(row=0, column=1, rowspan=2, sticky="e")
        ttk.Button(nav, text="質問を追加", style="Nav.TButton", command=self.show_input).pack(side="left", padx=(0, 8))
        ttk.Button(nav, text="質問一覧", style="Nav.TButton", command=self.show_list).pack(side="left")

        location = ttk.Frame(root, style="Card.TFrame", padding=(18, 14))
        location.grid(row=1, column=0, sticky="ew", pady=(24, 16))
        location.columnconfigure(1, weight=1)
        ttk.Label(location, text="保存先", style="Body.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 14))
        ttk.Label(location, textvariable=self.folder, style="Muted.TLabel").grid(row=0, column=1, sticky="ew")
        ttk.Button(location, text="フォルダを選択…", style="Secondary.TButton", command=self.choose_folder).grid(row=0, column=2, padx=(14, 0))

        self.content = ttk.Frame(root, style="App.TFrame")
        self.content.grid(row=2, column=0, sticky="nsew")
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

        footer = ttk.Frame(root, style="App.TFrame")
        footer.grid(row=3, column=0, sticky="ew", pady=(14, 0))
        footer.columnconfigure(0, weight=1)
        ttk.Label(footer, textvariable=self.status, style="Subtitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(footer, textvariable=self.count, style="Subtitle.TLabel").grid(row=0, column=1, sticky="e")

    def _clear_content(self) -> None:
        for child in self.content.winfo_children():
            child.destroy()

    def show_input(self) -> None:
        self.current_view = "input"
        self._clear_content()
        card = ttk.Frame(self.content, style="Card.TFrame", padding=(28, 24))
        card.grid(row=0, column=0, sticky="nsew")
        card.columnconfigure(0, weight=1)
        card.rowconfigure(4, weight=1)

        ttk.Label(card, text="質問入力", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(card, text="質問と回答を入力すると、選んだフォルダの data.csv に保存されます。", style="Muted.TLabel").grid(row=1, column=0, sticky="w", pady=(5, 20))
        ttk.Label(card, text="質問", style="Body.TLabel").grid(row=2, column=0, sticky="w", pady=(0, 7))
        self.question_entry = tk.Text(card, height=3, wrap="word", font=("TkDefaultFont", 12), relief="solid", borderwidth=1, padx=12, pady=10, highlightthickness=0)
        self.question_entry.grid(row=3, column=0, sticky="ew", pady=(0, 18))
        ttk.Label(card, text="回答", style="Body.TLabel").grid(row=4, column=0, sticky="nw", pady=(0, 7))
        self.answer_entry = tk.Text(card, height=8, wrap="word", font=("TkDefaultFont", 12), relief="solid", borderwidth=1, padx=12, pady=10, highlightthickness=0)
        self.answer_entry.grid(row=5, column=0, sticky="nsew")
        ttk.Button(card, text="CSVに保存", style="Primary.TButton", command=self.save_item).grid(row=6, column=0, sticky="e", pady=(20, 0))
        self.question_entry.focus_set()

    def show_list(self) -> None:
        self.current_view = "list"
        self._clear_content()
        card = ttk.Frame(self.content, style="Card.TFrame", padding=(28, 24))
        card.grid(row=0, column=0, sticky="nsew")
        card.columnconfigure(0, weight=1)
        card.rowconfigure(2, weight=1)

        title_row = ttk.Frame(card, style="Card.TFrame")
        title_row.grid(row=0, column=0, sticky="ew")
        title_row.columnconfigure(0, weight=1)
        ttk.Label(title_row, text="質問一覧", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Button(title_row, text="再読み込み", style="Secondary.TButton", command=self.show_list).grid(row=0, column=1)
        ttk.Label(card, text="保存した質問と回答を確認できます。", style="Muted.TLabel").grid(row=1, column=0, sticky="w", pady=(5, 16))

        table_frame = ttk.Frame(card, style="Card.TFrame")
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        tree = ttk.Treeview(table_frame, columns=("question", "answer"), show="headings", selectmode="browse")
        tree.heading("question", text="質問")
        tree.heading("answer", text="回答")
        tree.column("question", width=320, minwidth=160, stretch=True)
        tree.column("answer", width=480, minwidth=220, stretch=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        if not self.folder.get():
            self.status.set("保存先フォルダを選択してください")
            return
        try:
            items = CsvStore(self.folder.get()).read_all()
            for item in items:
                tree.insert("", "end", values=(item.question, item.answer))
            self.count.set(f"{len(items)}件")
            self.status.set("一覧を読み込みました")
        except (OSError, ValueError) as error:
            messagebox.showerror("読み込みできません", str(error), parent=self)
            self.status.set("data.csv を読み込めませんでした")

    def choose_folder(self) -> None:
        selected = filedialog.askdirectory(title="data.csv の保存先を選択", initialdir=self.folder.get() or str(Path.home()), mustexist=True, parent=self)
        if not selected:
            return
        try:
            CsvStore(selected).ensure_ready()
            self.folder.set(selected)
            self._save_folder(selected)
            self.status.set("保存先を変更しました")
            self._refresh_count()
            if self.current_view == "list":
                self.show_list()
        except OSError as error:
            messagebox.showerror("フォルダを使用できません", f"このフォルダには保存できません。\n\n{error}", parent=self)

    def save_item(self) -> None:
        question = self.question_entry.get("1.0", "end-1c").strip()
        answer = self.answer_entry.get("1.0", "end-1c").strip()
        if not self.folder.get():
            self.status.set("先に保存先フォルダを選択してください")
            self.choose_folder()
            if not self.folder.get():
                return
        if not question:
            self.status.set("質問を入力してください")
            self.question_entry.focus_set()
            return
        if not answer:
            self.status.set("回答を入力してください")
            self.answer_entry.focus_set()
            return
        try:
            CsvStore(self.folder.get()).append(QuestionAnswer(question, answer))
        except OSError as error:
            messagebox.showerror("保存できません", f"data.csv に保存できませんでした。\n\n{error}", parent=self)
            return
        self.question_entry.delete("1.0", "end")
        self.answer_entry.delete("1.0", "end")
        self.question_entry.focus_set()
        self.status.set("質問と回答を保存しました")
        self._refresh_count()
        self.bell()

    def _refresh_count(self) -> None:
        try:
            self.count.set(f"{len(CsvStore(self.folder.get()).read_all())}件")
        except (OSError, ValueError):
            self.count.set("—")

    @staticmethod
    def _load_folder() -> str:
        try:
            value = json.loads(CONFIG_PATH.read_text(encoding="utf-8")).get("folder", "")
            return value if value and Path(value).is_dir() else ""
        except (OSError, ValueError, TypeError):
            return ""

    @staticmethod
    def _save_folder(folder: str) -> None:
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            CONFIG_PATH.write_text(json.dumps({"folder": folder}, ensure_ascii=False), encoding="utf-8")
        except OSError:
            pass


if __name__ == "__main__":
    app = QuestionBoxApp()
    app.mainloop()
