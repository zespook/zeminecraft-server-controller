import tkinter as tk
from tkinter import messagebox
import os
import threading
import time
import subprocess
import json
import psutil
import re
from utils.config_manager import SETTINGS_PATH


class MinecraftServerController:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Server Controller")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

        self.shutdown_timer_hours = 0
        self.shutdown_timer_minutes = 0
        self.shutdown_pc = False

        # Server process
        self.server_process = None
        self.running = False
        self.server_path = ""
        self.java_path = "java"
        self.server_jar = "server.jar"
        self.xms = "1G"
        self.xmx = "2G"
        self.backup_enabled = False
        self.backup_interval = 60  # minutes
        self.max_backups = 10
        self.backup_thread = None
        self.backup_path = os.path.join(os.path.expanduser("~"), "MinecraftBackups")
        self.backup_lock = threading.Lock()

        # Setup UI
        self.create_toolbar()
        self.create_notebook()
        self.create_status_bar()

        # Data structures
        self.online_players = []
        self.whitelist = []
        self.ops = []
        self.banned_players = []
        self.banned_ips = []

        # Load data if available
        self.load_server_data()
        self.start_backup_scheduler()

    def load_server_data(self):
        try:
            if os.path.exists(SETTINGS_PATH):
                with open(SETTINGS_PATH, "r") as f:
                    settings = json.load(f)

                self.server_path = settings.get("server_path", "")
                self.java_path = settings.get("java_path", "java")
                self.server_jar = settings.get("server_jar", "server.jar")
                self.xms = settings.get("xms", "1G")
                self.xmx = settings.get("xmx", "2G")
                self.backup_path = settings.get("backup_path", "")
                self.backup_interval = settings.get("backup_interval", 60)
                self.max_backups = settings.get("max_backups", 10)
                self.shutdown_pc = settings.get("shutdown_pc", False)

                if hasattr(self, "shutdown_pc_var"):
                    self.shutdown_pc_var.set(self.shutdown_pc)

                # Update UI variables if they exist
                if hasattr(self, "server_path_var"):
                    self.server_path_var.set(self.server_path)
                    self.java_path_var.set(self.java_path)
                    self.server_jar_var.set(self.server_jar)
                    self.xms_var.set(self.xms)
                    self.xmx_var.set(self.xmx)
                    self.jvm_args_var.set(settings.get("jvm_args", ""))
                    self.refresh_interval_var.set(settings.get("refresh_interval", 5))

                if hasattr(self, "backup_path_var"):
                    self.backup_path_var.set(self.backup_path)
                    self.backup_interval_var.set(self.backup_interval)
                    self.max_backups_var.set(self.max_backups)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load settings: {str(e)}")

    def save_settings(self):
        self.server_path = self.server_path_var.get()
        self.java_path = self.java_path_var.get()
        self.server_jar = self.server_jar_var.get()
        self.xms = self.xms_var.get()
        self.xmx = self.xmx_var.get()

        # Save settings to file
        settings = {
            "server_path": self.server_path,
            "java_path": self.java_path,
            "server_jar": self.server_jar,
            "xms": self.xms,
            "xmx": self.xmx,
            "jvm_args": self.jvm_args_var.get(),
            "refresh_interval": self.refresh_interval_var.get(),
            "backup_path": self.backup_path,
            "backup_interval": self.backup_interval,
            "max_backups": self.max_backups,
            "shutdown_pc": self.shutdown_pc_var.get(),
        }

        try:
            with open(SETTINGS_PATH, "w") as f:
                json.dump(settings, f, indent=4)
            self.update_status("Settings saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

    def start_server(self):
        if self.running:
            messagebox.showinfo("Info", "Server is already running")
            return

        if not self.server_path or not os.path.exists(self.server_path):
            messagebox.showerror("Error", "Invalid server directory")
            return

        # Construct the full path to run.bat
        bat_file = os.path.join(self.server_path, "run.bat")
        if not os.path.exists(bat_file):
            messagebox.showerror("Error", f"run.bat not found in: {self.server_path}")
            return

        try:
            # Launch the batch file using subprocess
            self.server_process = subprocess.Popen(
                [bat_file],
                cwd=self.server_path,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,  # Hide the command window
            )
            self.running = True
            self.start_time = time.time()
            self.update_status("Server starting...")
            self.status_label.config(text="Starting...", foreground="orange")

            # Start threads to monitor output and update stats
            threading.Thread(target=self.monitor_output, daemon=True).start()
            threading.Thread(target=self.update_stats, daemon=True).start()

            # Clear lists for fresh update
            self.online_players = []
            self.whitelist = []
            self.ops = []
            self.banned_players = []
            self.update_online_players_display()
            self.update_whitelist_display()
            self.update_ops_display()
            self.update_banned_display()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {str(e)}")

    def stop_server(self):
        if not self.running:
            messagebox.showinfo("Info", "Server is not running")
            return

        try:
            if self.server_process.poll() is None:
                # Send save-all command before stopping
                self.server_process.stdin.write("save-all\n")
                self.server_process.stdin.flush()

                # Wait for the save to complete
                time.sleep(2)

                # Send stop command
                self.server_process.stdin.write("stop\n")
                self.server_process.stdin.flush()

                # Wait for clean exit with an additional delay
                self.server_process.wait(timeout=30)
                time.sleep(15)  # Additional 10-second delay before complete shutdown
        except subprocess.TimeoutExpired:
            self.server_process.kill()

            self.running = False
            self.online_players = []
            self.update_online_players_display()
            self.status_label.config(text="Offline", foreground="red")
            self.update_status("Server stopped")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop server: {str(e)}")

    def restart_server(self):
        if self.running:
            self.stop_server()
            # Wait 15 seconds after stopping before starting again
            self.root.after(15000, self.start_server)
        else:
            self.start_server()

    def exit_application(self):
        if self.running:
            if messagebox.askyesno(
                "Exit", "Server is still running. Stop server and exit?"
            ):
                self.stop_server()
                self.root.after(1000, self.root.destroy)
        else:
            self.root.destroy()

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
                self.uptime_label.config(
                    text=f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                )

                # Update tick rate (TPS) if available, e.g., via self.latest_tps updated in your output parser.
                if hasattr(self, "latest_tps"):
                    self.tps_label.config(text=f"{self.latest_tps:.1f}")

                time.sleep(update_interval)
            except Exception as e:
                print(f"Error updating stats: {str(e)}")
                time.sleep(update_interval)

    def send_server_command(self, command):
        if not self.running or not self.server_process:
            messagebox.showinfo("Info", "Server is not running")
            return

        try:
            # Update console to show the command
            self.update_console(f"> {command}")

            # Send command to server
            self.server_process.stdin.write(command + "\n")
            self.server_process.stdin.flush()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send command: {str(e)}")

    def start_backup_scheduler(self):
        if self.backup_thread and self.backup_thread.is_alive():
            return  # Scheduler is already running
        self.backup_thread = threading.Thread(target=self.backup_loop, daemon=True)
        self.backup_thread.start()

    def send_command(self, event=None):
        # Determine which input widget triggered the event
        if event and event.widget == self.chat_input:
            command = self.chat_input.get()
            self.chat_input.delete(0, tk.END)
            if command.startswith("/"):
                # Remove slash for server command
                self.send_server_command(command[1:])
                # Add to chat display to show command was sent
                self.update_chat(f"[COMMAND] {command}")
            else:
                # Send as say command for chat
                self.send_server_command(f"say {command}")
                # Add to chat display to show what was said
                self.update_chat(f"[SERVER] {command}")
        else:
            command = self.command_input.get()
            self.command_input.delete(0, tk.END)
            self.send_server_command(command)
            # Add to console to show command was sent
            self.update_console(f"> {command}")

    def process_server_output(self, line):
        # Update console
        self.update_console(line)

        # Look for status messages
        if "Done" in line and "For help, type" in line:
            self.status_label.config(text="Online", foreground="green")
            self.update_status("Server running")
            # Refresh player lists after server start
            self.root.after(5000, self.refresh_lists)

        # Check for player join/leave
        join_match = re.search(r"(\w+) joined the game", line)
        if join_match:
            player = join_match.group(1)
            if player not in self.online_players:
                self.online_players.append(player)
                self.update_online_players_display()
                self.update_chat(f"[SERVER] {player} joined the game")

        leave_match = re.search(r"(\w+) left the game", line)
        if leave_match:
            player = leave_match.group(1)
            if player in self.online_players:
                self.online_players.remove(player)
                self.update_online_players_display()
                self.update_chat(f"[SERVER] {player} left the game")

        # Check for chat messages (improved to catch more formats)
        chat_match = re.search(r"<(\w+)> (.*)", line)
        if chat_match:
            player, message = chat_match.groups()
            self.update_chat(f"<{player}> {message}")

        # Catch achievements and death messages
        if (
            "[Server]" in line
            or "[server]" in line
            or "achievement" in line.lower()
            or "died" in line
            or "slain" in line
            or "was killed" in line
        ):
            # This will capture most server announcements including achievements and deaths
            self.update_chat(line)

        # Check for player list response
        list_match = re.search(
            r"There are (\d+) of a max of (\d+) players online", line
        )
        if list_match:
            current, maximum = list_match.groups()
            self.update_status(f"Players: {current}/{maximum}")

            # Extract player names if available
            players_match = re.search(r"online: (.*)", line)
            if players_match:
                player_list = players_match.group(1).split(", ")
                self.online_players = [p.strip() for p in player_list]
                self.update_online_players_display()

    def monitor_output(self):
        if not self.server_process:
            return

        while self.running:
            try:
                line = self.server_process.stdout.readline()
                if not line:
                    if self.server_process.poll() is not None:
                        self.running = False
                        self.status_label.config(text="Offline", foreground="red")
                        self.update_status("Server stopped unexpectedly")
                        break
                    continue

                # Process and display the line
                self.process_server_output(line.strip())

            except Exception as e:
                self.update_status(f"Error reading server output: {str(e)}")
                break
