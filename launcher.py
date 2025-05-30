import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

APP_LIST_FILE = 'app_list.json'

# 初期データ（カテゴリ別）
initial_apps = {
    "業務": [
        {"name": "サンプルアプリ1", "path": "C:/myapps/sample1.exe", "icon": "icons/sample1.ico"},
    ],
    "ツール": [
        {"name": "サンプルアプリ2", "path": "C:/myapps/sample2.exe", "icon": "icons/sample2.ico"},
    ]
}

def load_app_list():
    if os.path.exists(APP_LIST_FILE):
        with open(APP_LIST_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        with open(APP_LIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(initial_apps, f, ensure_ascii=False, indent=4)
        return initial_apps

def save_app_list(apps):
    with open(APP_LIST_FILE, 'w', encoding='utf-8') as f:
        json.dump(apps, f, ensure_ascii=False, indent=4)

def launch_app(path):
    try:
        if os.path.exists(path):
            os.startfile(path)
        else:
            messagebox.showerror("エラー", "指定されたパスが存在しません。")
    except Exception as e:
        messagebox.showerror("エラー", f"アプリの起動に失敗しました:\n{e}")

def get_clipboard_text():
    try:
        text = root.clipboard_get().strip()
        return text
    except tk.TclError:
        return ""

def launch_from_clipboard():
    path = get_clipboard_text()
    if os.path.exists(path):
        launch_app(path)
    else:
        messagebox.showerror("エラー", "クリップボードのパスが存在しません、または正しくありません。")

def add_app():
    category = simpledialog.askstring("カテゴリ選択", "カテゴリ名を入力してください（例：業務、ツール）")
    if not category:
        return
    name = simpledialog.askstring("アプリ名", "アプリの名前を入力してください")
    if not name:
        return
    path = simpledialog.askstring("パス", "アプリのフルパスを入力してください")
    if not path or not os.path.exists(path):
        messagebox.showerror("エラー", "正しいパスを入力してください。")
        return
    icon = simpledialog.askstring("アイコン", "アイコンのパスを入力してください（省略可）")
    if not icon:
        icon = "icons/default.ico"

    if category not in apps:
        apps[category] = []
    apps[category].append({"name": name, "path": path, "icon": icon})
    save_app_list(apps)
    refresh_tree()

def add_app_from_clipboard():
    category = simpledialog.askstring("カテゴリ選択", "カテゴリ名を入力してください（例：業務、ツール）")
    if not category:
        return
    name = simpledialog.askstring("アプリ名", "アプリの名前を入力してください")
    if not name:
        return
    path = get_clipboard_text()
    if not path or not os.path.exists(path):
        messagebox.showerror("エラー", "クリップボードのパスが正しくありません。")
        return
    icon = simpledialog.askstring("アイコン", "アイコンのパスを入力してください（省略可）")
    if not icon:
        icon = "icons/default.ico"

    if category not in apps:
        apps[category] = []
    apps[category].append({"name": name, "path": path, "icon": icon})
    save_app_list(apps)
    refresh_tree()

def delete_app():
    selected = tree.selection()
    if not selected:
        return
    item_id = selected[0]
    parent_id = tree.parent(item_id)
    if not parent_id:
        messagebox.showinfo("情報", "カテゴリは削除できません。アプリを選択してください。")
        return
    category = tree.item(parent_id, 'text')
    name = tree.item(item_id, 'text')

    apps[category] = [a for a in apps[category] if a["name"] != name]
    if not apps[category]:
        del apps[category]
    save_app_list(apps)
    refresh_tree()

def refresh_tree():
    tree.delete(*tree.get_children())
    for category, app_list in apps.items():
        cat_id = tree.insert('', 'end', text=category, open=True)
        for app in app_list:
            tree.insert(cat_id, 'end', text=app['name'], values=(app['path'],), tags=(category,))

def on_double_click(event):
    selected = tree.selection()
    if not selected:
        return
    item_id = selected[0]
    parent_id = tree.parent(item_id)
    if parent_id:
        path = tree.item(item_id, 'values')[0]
        launch_app(path)

# GUI構築
root = tk.Tk()
root.title("業務アプリ起動ランチャー")
root.geometry("600x400")

apps = load_app_list()

tree = ttk.Treeview(root, columns=("path",), show="tree headings")
tree.heading("path", text="アプリパス")
tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
tree.bind("<Double-1>", on_double_click)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="アプリ追加", command=add_app, width=15).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="クリップボードから追加", command=add_app_from_clipboard, width=20).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="選択アプリ削除", command=delete_app, width=15).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="クリップボードから起動", command=launch_from_clipboard, width=20).pack(side=tk.LEFT, padx=5)

refresh_tree()
root.mainloop()
