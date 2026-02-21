import customtkinter as ctk
import requests
import os
import subprocess
import sys
from tkinter import messagebox

# =========================
# 路径
# =========================
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FILE_NAME = os.path.join(BASE_DIR, "words.txt")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# =========================
# Git 同步
# =========================
def git_pull():
    try:
        subprocess.run(["git", "pull"], cwd=BASE_DIR)
    except:
        pass


def git_push():
    try:
        subprocess.run(["git", "add", "."], cwd=BASE_DIR)
        subprocess.run(["git", "commit", "-m", "auto sync"], cwd=BASE_DIR)
        subprocess.run(["git", "push"], cwd=BASE_DIR)
        messagebox.showinfo("成功", "已同步到云端 ☁️")
    except Exception as e:
        messagebox.showerror("失败", str(e))


# =========================
# 翻译
# =========================
def translate(word):
    try:
        url = "https://api.mymemory.translated.net/get"
        params = {"q": word, "langpair": "en|zh"}
        r = requests.get(url, params=params, timeout=5)
        return r.json()["responseData"]["translatedText"]
    except:
        return "翻译失败"


# =========================
# 主程序
# =========================
class WordBook(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("📘 Word Book")
        self.geometry("520x620")

        git_pull()

        self.hide_meaning = False
        self.original_content = ""

        self.entry = ctk.CTkEntry(self, height=40, font=("Arial", 16))
        self.entry.pack(pady=15, padx=20, fill="x")
        self.entry.bind("<Return>", lambda e: self.add_word())

        frame = ctk.CTkFrame(self)
        frame.pack(pady=10)

        ctk.CTkButton(frame, text="添加单词", command=self.add_word).pack(side="left", padx=5)
        ctk.CTkButton(frame, text="隐藏/显示释义", command=self.toggle_meaning).pack(side="left", padx=5)
        ctk.CTkButton(frame, text="同步云端", command=git_push).pack(side="left", padx=5)

        self.textbox = ctk.CTkTextbox(self, font=("Consolas", 16))
        self.textbox.pack(fill="both", expand=True, padx=20, pady=15)

        self.load_file()

        # Ctrl + S 只保存本地
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-S>", lambda e: self.save_file())

    # =========================
    # 加载文件
    # =========================
    def load_file(self):
        if os.path.exists(FILE_NAME):
            with open(FILE_NAME, "r", encoding="utf-8") as f:
                self.original_content = f.read()
        else:
            self.original_content = ""

        self.display_content()

    # =========================
    # 显示内容
    # =========================
    def display_content(self):
        self.textbox.delete("1.0", "end")

        if not self.hide_meaning:
            self.textbox.insert("1.0", self.original_content)
        else:
            lines = self.original_content.splitlines()
            for line in lines:
                if line.strip():
                    word = line.split()[0]
                    self.textbox.insert("end", word + "\n")

    # =========================
    # 添加单词（防止拼接）
    # =========================
    def add_word(self):
        word = self.entry.get().strip().lower()
        if not word:
            return

        for line in self.original_content.splitlines():
            if line.startswith(word + " "):
                messagebox.showinfo("提示", "单词已存在")
                self.entry.delete(0, "end")
                return

        meaning = translate(word)

        # 🔥 防止上一行没有换行
        if self.original_content and not self.original_content.endswith("\n"):
            self.original_content += "\n"

        new_line = f"{word:<15} {meaning}\n"
        self.original_content += new_line

        self.display_content()
        self.entry.delete(0, "end")

    # =========================
    # 保存文件（修复 strip 吃掉换行）
    # =========================
    def save_file(self):
        if not self.hide_meaning:
            content = self.textbox.get("1.0", "end")

            # 不使用 strip()
            lines = content.splitlines()
            fixed_content = "\n".join(lines) + "\n"

            self.original_content = fixed_content

        with open(FILE_NAME, "w", encoding="utf-8") as f:
            f.write(self.original_content)

        messagebox.showinfo("已保存", "已保存到本地 (Ctrl+S)")

    # =========================
    # 隐藏 / 显示释义
    # =========================
    def toggle_meaning(self):
        self.hide_meaning = not self.hide_meaning
        self.display_content()


if __name__ == "__main__":
    app = WordBook()
    app.mainloop()