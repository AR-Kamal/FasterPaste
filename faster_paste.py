import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time

try:
    import keyboard
except ImportError:
    print("Missing dependency: keyboard")
    print("Run: pip install keyboard")
    exit(1)

try:
    import pyperclip
except ImportError:
    print("Missing dependency: pyperclip")
    print("Run: pip install pyperclip")
    exit(1)


class FasterPaste:
    def __init__(self):
        self.records = []
        self.current_index = 0
        self.is_loaded = False
        self.setup_ui()
        self.register_hotkey()

    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title("FasterPaste")
        self.root.attributes("-topmost", True)
        self.root.geometry("420x560")
        self.root.minsize(350, 480)
        self.root.configure(bg="#f5f5f5")

        style = ttk.Style()
        style.theme_use("clam")
        # Remove borders from all labels
        style.configure("TLabel", relief="flat", borderwidth=0, background="#f5f5f5")
        style.configure("TFrame", background="#f5f5f5")
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))

        main = ttk.Frame(self.root, padding=15)
        main.pack(fill=tk.BOTH, expand=True)

        # Header
        tk.Label(main, text="FasterPaste", font=("Segoe UI", 18, "bold"),
                 bg="#f5f5f5", bd=0).pack(pady=(0, 2))
        tk.Label(main, text="Paste nombor kad one by one", font=("Segoe UI", 9),
                 fg="#666", bg="#f5f5f5", bd=0).pack(pady=(0, 12))

        # Input area
        tk.Label(main, text="Paste your list below (one per line):", font=("Segoe UI", 10),
                 bg="#f5f5f5", bd=0).pack(anchor="w")
        self.text_area = scrolledtext.ScrolledText(main, height=7, font=("Consolas", 10), wrap=tk.NONE)
        self.text_area.pack(fill=tk.BOTH, expand=True, pady=(4, 6))

        # Load / Reset buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=(0, 8))
        self.load_btn = ttk.Button(btn_frame, text="Load Records", command=self.load_records, style="Accent.TButton")
        self.load_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))
        self.reset_btn = ttk.Button(btn_frame, text="Reset", command=self.reset, state="disabled", width=10)
        self.reset_btn.pack(side=tk.LEFT)

        # Separator
        ttk.Separator(main).pack(fill=tk.X, pady=4)

        # Current record
        tk.Label(main, text="Current Record:", font=("Segoe UI", 10),
                 bg="#f5f5f5", bd=0).pack(anchor="w", pady=(4, 0))
        self.current_var = tk.StringVar(value="-")
        self.current_label = tk.Label(main, textvariable=self.current_var,
                                      font=("Consolas", 16, "bold"), fg="#0066cc", bg="#f5f5f5", bd=0)
        self.current_label.pack(pady=(4, 6))

        # Progress
        self.progress_var = tk.StringVar(value="0 / 0")
        tk.Label(main, textvariable=self.progress_var, font=("Segoe UI", 10),
                 bg="#f5f5f5", bd=0).pack()
        self.progress_bar = ttk.Progressbar(main, mode="determinate", length=300)
        self.progress_bar.pack(fill=tk.X, pady=(4, 8))

        # Navigation
        nav = ttk.Frame(main)
        nav.pack(fill=tk.X, pady=(0, 8))
        self.prev_btn = ttk.Button(nav, text="\u25c4 Prev", command=self.prev_record, state="disabled")
        self.prev_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 3))
        self.paste_btn = ttk.Button(nav, text="Paste & Next", command=self.paste_with_delay, state="disabled", style="Accent.TButton")
        self.paste_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=3)
        self.next_btn = ttk.Button(nav, text="Next \u25ba", command=self.next_record, state="disabled")
        self.next_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(3, 0))

        # Hotkey info box
        hk_frame = tk.Frame(main, bg="#e8f4e8", bd=1, relief="solid", padx=10, pady=6)
        hk_frame.pack(fill=tk.X, pady=(0, 6))
        tk.Label(hk_frame, text="Hotkey:  F2  = paste current & go next", font=("Segoe UI", 9, "bold"),
                 bg="#e8f4e8", fg="#2d6a2d").pack()
        tk.Label(hk_frame, text="Focus your target field, then press F2", font=("Segoe UI", 8),
                 bg="#e8f4e8", fg="#555").pack()

        # Status bar
        self.status_var = tk.StringVar(value="Ready \u2014 paste your list and click Load")
        tk.Label(main, textvariable=self.status_var, font=("Segoe UI", 8),
                 fg="#999", bg="#f5f5f5", bd=0).pack(pady=(4, 0))

    def register_hotkey(self):
        try:
            keyboard.add_hotkey("F2", self.on_hotkey_paste, suppress=True)
        except Exception as e:
            self.status_var.set(f"Hotkey error: {e}")

    def load_records(self):
        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("No Data", "Please paste your list first.")
            return

        self.records = [line.strip() for line in text.split("\n") if line.strip()]
        if not self.records:
            messagebox.showwarning("No Data", "No valid records found.")
            return

        self.current_index = 0
        self.is_loaded = True
        self.text_area.configure(state="disabled")
        self.load_btn.configure(state="disabled")
        self.reset_btn.configure(state="normal")
        self.paste_btn.configure(state="normal")
        self.update_display()
        self.highlight_current_line()
        self.status_var.set(f"Loaded {len(self.records)} records. Press F2 to paste!")

    def reset(self):
        self.records = []
        self.current_index = 0
        self.is_loaded = False
        self.text_area.configure(state="normal")
        self.text_area.delete("1.0", tk.END)
        self.load_btn.configure(state="normal")
        self.reset_btn.configure(state="disabled")
        self.paste_btn.configure(state="disabled")
        self.prev_btn.configure(state="disabled")
        self.next_btn.configure(state="disabled")
        self.current_var.set("-")
        self.progress_var.set("0 / 0")
        self.progress_bar["value"] = 0
        self.status_var.set("Ready \u2014 paste your list and click Load")

    def update_display(self):
        if not self.records:
            return

        total = len(self.records)
        if self.current_index < total:
            self.current_var.set(self.records[self.current_index])
            self.current_label.configure(fg="#0066cc")
            self.progress_var.set(f"{self.current_index + 1} / {total}")
            self.progress_bar["value"] = ((self.current_index + 1) / total) * 100
            self.paste_btn.configure(state="normal")
        else:
            self.current_var.set("All Done!")
            self.current_label.configure(fg="#28a745")
            self.progress_var.set(f"{total} / {total}")
            self.progress_bar["value"] = 100
            self.paste_btn.configure(state="disabled")
            self.status_var.set("All records have been pasted!")

        # Update nav buttons
        self.prev_btn.configure(state="normal" if self.current_index > 0 else "disabled")
        self.next_btn.configure(state="normal" if self.current_index < total - 1 else "disabled")

        self.highlight_current_line()

    def highlight_current_line(self):
        self.text_area.tag_remove("highlight", "1.0", tk.END)
        self.text_area.tag_remove("done", "1.0", tk.END)

        # Highlight completed lines in grey
        for i in range(self.current_index):
            line_start = f"{i + 1}.0"
            line_end = f"{i + 1}.end"
            self.text_area.tag_add("done", line_start, line_end)

        # Highlight current line
        if self.current_index < len(self.records):
            line_num = self.current_index + 1
            self.text_area.tag_add("highlight", f"{line_num}.0", f"{line_num}.end")
            self.text_area.see(f"{line_num}.0")

        self.text_area.tag_configure("highlight", background="#cce5ff", foreground="#003d80")
        self.text_area.tag_configure("done", foreground="#aaa")

    def flash_feedback(self):
        """Brief visual flash to confirm paste happened."""
        self.current_label.configure(fg="#28a745")
        self.root.after(300, lambda: self.current_label.configure(
            fg="#0066cc" if self.current_index < len(self.records) else "#28a745"))

    def on_hotkey_paste(self):
        """Called from keyboard thread when F2 is pressed."""
        if not self.is_loaded or not self.records or self.current_index >= len(self.records):
            return

        value = self.records[self.current_index]
        pyperclip.copy(value)
        time.sleep(0.05)
        keyboard.send("ctrl+v")

        self.current_index += 1
        self.root.after(0, self.update_display)
        self.root.after(0, self.flash_feedback)

    def paste_with_delay(self):
        """Button click: gives user 2 seconds to focus target field, then pastes."""
        if not self.records or self.current_index >= len(self.records):
            return

        self.status_var.set("Pasting in 2s... click on target field NOW!")
        self.paste_btn.configure(state="disabled")
        self.root.update()

        def delayed():
            time.sleep(2)
            value = self.records[self.current_index]
            pyperclip.copy(value)
            time.sleep(0.05)
            keyboard.send("ctrl+v")
            self.current_index += 1
            self.root.after(0, self.update_display)
            self.root.after(0, self.flash_feedback)
            self.root.after(0, lambda: self.status_var.set("Pasted! Press F2 for next."))

        threading.Thread(target=delayed, daemon=True).start()

    def prev_record(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()

    def next_record(self):
        if self.current_index < len(self.records) - 1:
            self.current_index += 1
            self.update_display()

    def run(self):
        try:
            self.root.mainloop()
        finally:
            keyboard.unhook_all()


if __name__ == "__main__":
    app = FasterPaste()
    app.run()
