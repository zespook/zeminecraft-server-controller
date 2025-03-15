import tkinter as tk
from tkinter import ttk, scrolledtext


def create_console_tab(self, parent):
    # Console output
    console_frame = ttk.Frame(parent)
    console_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    self.console_output = scrolledtext.ScrolledText(console_frame, state=tk.DISABLED)
    self.console_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Command input
    command_frame = ttk.Frame(parent)
    command_frame.pack(fill=tk.X, padx=5, pady=5)

    ttk.Label(command_frame, text="Command:").pack(side=tk.LEFT, padx=5)

    self.command_input = ttk.Entry(command_frame)
    self.command_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    self.command_input.bind("<Return>", self.send_command)

    send_button = ttk.Button(command_frame, text="Send", command=self.send_command)
    send_button.pack(side=tk.RIGHT, padx=5)


def update_console(self, text):
    self.console_output.config(state=tk.NORMAL)
    self.console_output.insert(tk.END, text + "\n")
    self.console_output.see(tk.END)
    self.console_output.config(state=tk.DISABLED)
