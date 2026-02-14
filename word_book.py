import customtkinter as ctk
import requests
import os
import subprocess
from tkinter import messagebox

# ⭐ 获取当前脚本所在目录（核心修复）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_NAME = os.path.join(BASE_DIR, "words.txt")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ========= Git 同步 =========
def git_pull():
    try:
        subprocess.run(["git", "pull"], check=True, cwd=BASE_DIR)
    except:
        pass


def git_push():
    try:
        subprocess.run(["git", "add", "."], check=True, cwd=BASE_DIR)
        subprocess.run(["git", "commit", "-m", "auto sync"], check=True, cwd=BASE_DIR)
        subprocess.run(["git", "push"], check=True, cwd=BASE_DIR)
        messagebox.showinfo("同步成功", "已同步到云端 ☁️")
    except Exception as e:
        messagebox.showerror("失败", str(e))


# ========= 文件 =========
def load_words():
    words = {}

    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or "|" not in line:
                    continue
                eng, ch = line.split("|", 1)
                words[eng] = ch

    return words


def save_words(words):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        for eng, ch in words.items():
            f.write(f"{eng}|{ch}\n")


# ========= 翻译 =========
def translate(word):
    try:
        url = "https://api.mymemory.translated.net/get"
        params = {"q": word, "langpair": "en|zh"}
        r = requests.get(url, params=params, timeout=5)
        return r.json()["responseData"]["translatedText"]
    except:
        return "翻译失败"


# ========= GUI =========
class WordBook(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("📘 Word Book (Cloud)")
        self.geometry("520x620")

        git_pull()  # 启动自动同步

        self.words = load_words()
        self.show_chinese = True

        self.entry = ctk.CTkEntry(self, height=40, font=("Arial", 16))
        self.entry.pack(pady=15, padx=20, fill="x")
        self.entry.bind("<Return>", lambda e: self.add_word())

        frame = ctk.CTkFrame(self)
        frame.pack(pady=10)

        ctk.CTkButton(frame, text="添加", command=self.add_word).pack(side="left", padx=5)
        ctk.CTkButton(frame, text="隐藏中文", command=self.toggle).pack(side="left", padx=5)
        ctk.CTkButton(frame, text="同步云端", command=git_push).pack(side="left", padx=5)

        self.listbox = ctk.CTkTextbox(self, font=("Consolas", 16))
        self.listbox.pack(fill="both", expand=True, padx=20, pady=15)

        self.refresh()

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


if __name__ == "__main__":
    app = WordBook()
    app.mainloop()