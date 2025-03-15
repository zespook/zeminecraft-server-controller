import tkinter as tk
from tkinter import ttk, messagebox
import os
import json


def create_players_tab(self, parent):
    # Left frame for player lists
    left_frame = ttk.Frame(parent)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Online players
    online_frame = ttk.LabelFrame(left_frame, text="Online Players")
    online_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    online_scroll = ttk.Scrollbar(online_frame)
    online_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    self.online_listbox = tk.Listbox(online_frame, yscrollcommand=online_scroll.set)
    self.online_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    online_scroll.config(command=self.online_listbox.yview)

    # Operator players
    op_frame = ttk.LabelFrame(left_frame, text="Server Operators")
    op_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    op_scroll = ttk.Scrollbar(op_frame)
    op_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    self.op_listbox = tk.Listbox(op_frame, yscrollcommand=op_scroll.set)
    self.op_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    op_scroll.config(command=self.op_listbox.yview)

    # Right frame for player actions
    right_frame = ttk.Frame(parent)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Whitelist
    whitelist_frame = ttk.LabelFrame(right_frame, text="Whitelist")
    whitelist_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    whitelist_scroll = ttk.Scrollbar(whitelist_frame)
    whitelist_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    self.whitelist_listbox = tk.Listbox(
        whitelist_frame, yscrollcommand=whitelist_scroll.set
    )
    self.whitelist_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    whitelist_scroll.config(command=self.whitelist_listbox.yview)

    # Banned players
    banned_frame = ttk.LabelFrame(right_frame, text="Banned Players")
    banned_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    banned_scroll = ttk.Scrollbar(banned_frame)
    banned_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    self.banned_listbox = tk.Listbox(banned_frame, yscrollcommand=banned_scroll.set)
    self.banned_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    banned_scroll.config(command=self.banned_listbox.yview)

    # Actions frame
    actions_frame = ttk.LabelFrame(parent, text="Player Actions")
    actions_frame.pack(fill=tk.X, padx=5, pady=5)

    # Player name input
    ttk.Label(actions_frame, text="Player Name:").grid(row=0, column=0, padx=5, pady=5)
    self.player_name = ttk.Entry(actions_frame, width=20)
    self.player_name.grid(row=0, column=1, padx=5, pady=5)

    # Button frame
    button_frame = ttk.Frame(actions_frame)
    button_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    # Action buttons
    ttk.Button(button_frame, text="Ban Player", command=self.ban_player).grid(
        row=0, column=0, padx=5, pady=5
    )
    ttk.Button(button_frame, text="Unban Player", command=self.unban_player).grid(
        row=0, column=1, padx=5, pady=5
    )
    ttk.Button(
        button_frame, text="Add to Whitelist", command=self.add_to_whitelist
    ).grid(row=0, column=2, padx=5, pady=5)
    ttk.Button(
        button_frame, text="Remove from Whitelist", command=self.remove_from_whitelist
    ).grid(row=0, column=3, padx=5, pady=5)
    ttk.Button(button_frame, text="Make Operator", command=self.make_operator).grid(
        row=1, column=0, padx=5, pady=5
    )
    ttk.Button(button_frame, text="Remove Operator", command=self.remove_operator).grid(
        row=1, column=1, padx=5, pady=5
    )
    ttk.Button(button_frame, text="Kick Player", command=self.kick_player).grid(
        row=1, column=2, padx=5, pady=5
    )
    ttk.Button(button_frame, text="Refresh Lists", command=self.refresh_lists).grid(
        row=1, column=3, padx=5, pady=5
    )


def refresh_lists(self):
    if self.running:
        self.send_server_command("list")
        # Force reload of server files
        self.root.after(500, self.load_server_files)
    else:
        self.load_server_files()


def ban_player(self):
    player = self.player_name.get()
    if not player:
        messagebox.showinfo("Info", "Please enter a player name")
        return

    if self.running:
        self.send_server_command(f"ban {player}")
        self.player_name.delete(0, tk.END)
        self.root.after(1000, self.refresh_lists)  # Refresh after 1 second
    else:
        messagebox.showinfo("Info", "Server is not running")


def unban_player(self):
    player = self.player_name.get()
    if not player:
        # Check if any player is selected in the banned list
        if hasattr(self, "banned_listbox") and self.banned_listbox.curselection():
            index = self.banned_listbox.curselection()[0]
            player = self.banned_listbox.get(index)
        else:
            messagebox.showinfo(
                "Info", "Please enter a player name or select from the banned list"
            )
            return

    if self.running:
        self.send_server_command(f"pardon {player}")
        self.player_name.delete(0, tk.END)
        self.root.after(1000, self.refresh_lists)
    else:
        messagebox.showinfo("Info", "Server is not running")


def add_to_whitelist(self):
    player = self.player_name.get()
    if not player:
        messagebox.showinfo("Info", "Please enter a player name")
        return

    if self.running:
        self.send_server_command(f"whitelist add {player}")
        self.player_name.delete(0, tk.END)
        self.root.after(1000, self.refresh_lists)
    else:
        messagebox.showinfo("Info", "Server is not running")


def remove_from_whitelist(self):
    player = self.player_name.get()
    if not player:
        # Check if any player is selected in the whitelist
        if hasattr(self, "whitelist_listbox") and self.whitelist_listbox.curselection():
            index = self.whitelist_listbox.curselection()[0]
            player = self.whitelist_listbox.get(index)
        else:
            messagebox.showinfo(
                "Info", "Please enter a player name or select from the whitelist"
            )
            return

    if self.running:
        self.send_server_command(f"whitelist remove {player}")
        self.player_name.delete(0, tk.END)
        self.root.after(1000, self.refresh_lists)
    else:
        messagebox.showinfo("Info", "Server is not running")


def make_operator(self):
    player = self.player_name.get()
    if not player:
        # Check if any player is selected in the online list
        if hasattr(self, "online_listbox") and self.online_listbox.curselection():
            index = self.online_listbox.curselection()[0]
            player = self.online_listbox.get(index)
        else:
            messagebox.showinfo(
                "Info", "Please enter a player name or select from the online list"
            )
            return

    if self.running:
        self.send_server_command(f"op {player}")
        self.player_name.delete(0, tk.END)
        self.root.after(1000, self.refresh_lists)
    else:
        messagebox.showinfo("Info", "Server is not running")


def remove_operator(self):
    player = self.player_name.get()
    if not player:
        # Check if any player is selected in the ops list
        if hasattr(self, "op_listbox") and self.op_listbox.curselection():
            index = self.op_listbox.curselection()[0]
            player = self.op_listbox.get(index)
        else:
            messagebox.showinfo(
                "Info", "Please enter a player name or select from the operators list"
            )
            return

    if self.running:
        self.send_server_command(f"deop {player}")
        self.player_name.delete(0, tk.END)
        self.root.after(1000, self.refresh_lists)
    else:
        messagebox.showinfo("Info", "Server is not running")


def kick_player(self):
    player = self.player_name.get()
    if not player:
        # Check if any player is selected in the online list
        if hasattr(self, "online_listbox") and self.online_listbox.curselection():
            index = self.online_listbox.curselection()[0]
            player = self.online_listbox.get(index)
        else:
            messagebox.showinfo(
                "Info", "Please enter a player name or select from the online list"
            )
            return

    if self.running:
        self.send_server_command(f"kick {player}")
        self.player_name.delete(0, tk.END)
    else:
        messagebox.showinfo("Info", "Server is not running")


def update_whitelist_display(self):
    if hasattr(self, "whitelist_listbox"):
        self.whitelist_listbox.delete(0, tk.END)
        for player in self.whitelist:
            self.whitelist_listbox.insert(tk.END, player)


def update_ops_display(self):
    if hasattr(self, "op_listbox"):
        self.op_listbox.delete(0, tk.END)
        for player in self.ops:
            self.op_listbox.insert(tk.END, player)


def update_banned_display(self):
    if hasattr(self, "banned_listbox"):
        self.banned_listbox.delete(0, tk.END)
        for player in self.banned_players:
            self.banned_listbox.insert(tk.END, player)


def load_server_files(self):
    try:
        # Load whitelist
        whitelist_path = os.path.join(self.server_path, "whitelist.json")
        if os.path.exists(whitelist_path):
            with open(whitelist_path, "r") as f:
                whitelist_data = json.load(f)
                self.whitelist = []
                for player in whitelist_data:
                    if isinstance(player, dict) and "name" in player:
                        self.whitelist.append(player["name"])
            self.update_whitelist_display()

        # Load ops
        ops_path = os.path.join(self.server_path, "ops.json")
        if os.path.exists(ops_path):
            with open(ops_path, "r") as f:
                ops_data = json.load(f)
                self.ops = []
                for player in ops_data:
                    if isinstance(player, dict) and "name" in player:
                        self.ops.append(player["name"])
            self.update_ops_display()

        # Load banned players
        banned_players_path = os.path.join(self.server_path, "banned-players.json")
        if os.path.exists(banned_players_path):
            with open(banned_players_path, "r") as f:
                banned_data = json.load(f)
                self.banned_players = []
                for player in banned_data:
                    if isinstance(player, dict) and "name" in player:
                        self.banned_players.append(player["name"])
            self.update_banned_display()
    except Exception as e:
        self.update_status(f"Failed to load server files: {str(e)}")
        print(f"Error loading server files: {str(e)}")  # For debugging
