import customtkinter as ctk
import requests
import json
import os
import subprocess
from tkinter import messagebox

FILE_NAME = "words.json"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# =============================
# Git 云同步
# =============================
def git_pull():
    try:
        subprocess.run("git pull", shell=True)
    except:
        pass


def git_push():
    try:
        subprocess.run("git add .", shell=True)
        subprocess.run('git commit -m "update words"', shell=True)
        subprocess.run("git push", shell=True)
    except:
        pass


# =============================
# 本地数据
# =============================
def load_words():
    git_pull()  # ⭐ 启动自动拉取

    if not os.path.exists(FILE_NAME):
        return {}

    with open(FILE_NAME, "r", encoding="utf-8") as f:
        return json.load(f)


def save_words(words):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)

    git_push()  # ⭐ 保存自动上传


# =============================
# 翻译
# =============================
def translate(word):
    try:
        url = "https://api.mymemory.translated.net/get"
        params = {"q": word, "langpair": "en|zh"}
        r = requests.get(url, params=params, timeout=5)
        return r.json()["responseData"]["translatedText"]
    except:
        return "翻译失败"


# =============================
# GUI
# =============================
class WordBook(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("☁ Cloud Word Book")
        self.geometry("520x650")

        self.words = load_words()
        self.show_chinese = True

        self.build_ui()
        self.refresh()

    def build_ui(self):

        self.entry = ctk.CTkEntry(self, height=40, font=("Arial", 16))
        self.entry.pack(pady=15, padx=20, fill="x")
        self.entry.bind("<Return>", lambda e: self.add_word())

        frame = ctk.CTkFrame(self)
        frame.pack(pady=10)

        ctk.CTkButton(frame, text="添加", command=self.add_word).pack(side="left", padx=5)
        ctk.CTkButton(frame, text="隐藏中文", command=self.toggle).pack(side="left", padx=5)
        ctk.CTkButton(frame, text="刷新", command=self.refresh).pack(side="left", padx=5)

        self.listbox = ctk.CTkTextbox(self, font=("Consolas", 16))
        self.listbox.pack(fill="both", expand=True, padx=20, pady=15)

    # =============================
    # 功能
    # =============================
    def add_word(self):
        eng = self.entry.get().strip().lower()
        if not eng:
            return

        if eng not in self.words:
            ch = translate(eng)
            self.words[eng] = ch
            save_words(self.words)

        self.entry.delete(0, "end")
        self.refresh()

    def refresh(self):
        self.listbox.delete("1.0", "end")

        for eng, ch in sorted(self.words.items()):
            if self.show_chinese:
                self.listbox.insert("end", f"{eng:<15} {ch}\n")
            else:
                self.listbox.insert("end", f"{eng}\n")

    def toggle(self):
        self.show_chinese = not self.show_chinese
        self.refresh()


# =============================
if __name__ == "__main__":
    app = WordBook()
    app.mainloop()