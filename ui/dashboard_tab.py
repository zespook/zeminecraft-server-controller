import tkinter as tk
from tkinter import ttk, scrolledtext
import time
import psutil
import datetime


def create_dashboard_tab(self, parent):
    # Split into two frames: stats and chat
    top_frame = ttk.Frame(parent)
    top_frame.pack(fill=tk.BOTH, expand=True)

    # Left side - Server stats
    stats_frame = ttk.LabelFrame(top_frame, text="Server Statistics")
    stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    # CPU usage
    ttk.Label(stats_frame, text="CPU Usage:").grid(
        row=0, column=0, sticky="w", padx=10, pady=5
    )
    self.cpu_usage = ttk.Label(stats_frame, text="0%")
    self.cpu_usage.grid(row=0, column=1, sticky="w", padx=10, pady=5)

    # Memory usage
    ttk.Label(stats_frame, text="Memory Usage:").grid(
        row=1, column=0, sticky="w", padx=10, pady=5
    )
    self.memory_usage = ttk.Label(stats_frame, text="0 MB")
    self.memory_usage.grid(row=1, column=1, sticky="w", padx=10, pady=5)

    # Uptime
    ttk.Label(stats_frame, text="Uptime:").grid(
        row=2, column=0, sticky="w", padx=10, pady=5
    )
    self.uptime_label = ttk.Label(stats_frame, text="00:00:00")
    self.uptime_label.grid(row=2, column=1, sticky="w", padx=10, pady=5)

    # TPS (Ticks Per Second)
    ttk.Label(stats_frame, text="TPS:").grid(
        row=3, column=0, sticky="w", padx=10, pady=5
    )
    self.tps_label = ttk.Label(stats_frame, text="20.0")
    self.tps_label.grid(row=3, column=1, sticky="w", padx=10, pady=5)

    # Server status
    ttk.Label(stats_frame, text="Status:").grid(
        row=4, column=0, sticky="w", padx=10, pady=5
    )
    self.status_label = ttk.Label(stats_frame, text="Offline", foreground="red")
    self.status_label.grid(row=4, column=1, sticky="w", padx=10, pady=5)

    # Right side - Online players
    players_frame = ttk.LabelFrame(top_frame, text="Online Players")
    players_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Players listbox with scrollbar
    scrollbar = ttk.Scrollbar(players_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    self.players_listbox = tk.Listbox(
        players_frame, yscrollcommand=scrollbar.set, height=10
    )
    self.players_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    scrollbar.config(command=self.players_listbox.yview)

    # Bottom frame for chat
    chat_frame = ttk.LabelFrame(parent, text="Server Chat")
    chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Chat display
    self.chat_display = scrolledtext.ScrolledText(
        chat_frame, state=tk.DISABLED, height=10
    )
    self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Chat input
    input_frame = ttk.Frame(chat_frame)
    input_frame.pack(fill=tk.X, padx=5, pady=5)

    self.chat_input = ttk.Entry(input_frame)
    self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
    self.chat_input.bind("<Return>", self.send_command)

    send_button = ttk.Button(input_frame, text="Send", command=self.send_command)
    send_button.pack(side=tk.RIGHT, padx=5)


def update_stats(self):
    """Update server statistics by monitoring the actual Minecraft server process."""
    update_interval = 1  # in seconds
    while self.running:
        try:
            server_proc = self.get_server_process()
            if server_proc is None:
                # If the server process isn’t found, skip updating this cycle.
                time.sleep(update_interval)
                continue

            # CPU usage
            cpu_percent = server_proc.cpu_percent(interval=0.1)
            normalized_cpu = cpu_percent / psutil.cpu_count()
            self.cpu_usage.config(text=f"{normalized_cpu:.1f}%")

            # Memory usage
            memory_info = server_proc.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            self.memory_usage.config(text=f"{memory_mb:.1f} MB")

            # Uptime (based on when you started the server, not the Python app)
            uptime = time.time() - self.start_time
            hours, remainder = divmod(int(uptime), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.uptime_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")

            # Update tick rate (TPS) if available, e.g., via self.latest_tps updated in your output parser.
            if hasattr(self, "latest_tps"):
                self.tps_label.config(text=f"{self.latest_tps:.1f}")

            time.sleep(update_interval)
        except Exception as e:
            print(f"Error updating stats: {str(e)}")
            time.sleep(update_interval)


def get_server_process(self):
    """Find the Minecraft server process by checking for java.exe running Minecraft server."""
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            # Check if it's a java process
            if proc.info.get("name") == "java.exe":
                cmdline = proc.info.get("cmdline", [])
                # Look for common Minecraft server indicators in the command line
                cmdline_str = " ".join(cmdline).lower()
                if cmdline and any(
                    indicator in cmdline_str
                    for indicator in [
                        "minecraft_server",
                        "spigot",
                        "paper",
                        "forge",
                        "-jar server.jar",
                    ]
                ):
                    return proc  # Return the Minecraft server java process
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None


def update_online_players_display(self):
    if hasattr(self, "online_listbox") and hasattr(self, "players_listbox"):
        self.online_listbox.delete(0, tk.END)
        self.players_listbox.delete(0, tk.END)
        for player in self.online_players:
            self.online_listbox.insert(tk.END, player)
            self.players_listbox.insert(tk.END, player)


def update_chat(self, text):
    # Ensure we don't duplicate console lines in chat
    if not text.startswith(">") and "[CONSOLE]" not in text:
        timestamp = datetime.now().strftime("[%H:%M:%S] ")
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, timestamp + text + "\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
