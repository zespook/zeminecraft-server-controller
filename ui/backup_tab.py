import datetime
import glob
import os
import time
import tkinter as tk
from tkinter import ttk
import threading
import zipfile

def create_backup_tab(self, parent):
    backup_frame = ttk.LabelFrame(parent, text="Server Backup")
    backup_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Backup directory
    ttk.Label(backup_frame, text="Backup Directory:").grid(
        row=0, column=0, sticky="w", padx=10, pady=5
    )
    self.backup_path_var = tk.StringVar(value=self.backup_path)
    ttk.Entry(backup_frame, textvariable=self.backup_path_var, width=50).grid(
        row=0, column=1, padx=10, pady=5
    )
    ttk.Button(backup_frame, text="Browse...", command=self.browse_backup_path).grid(
        row=0, column=2, padx=10, pady=5
    )

    # Backup interval (in minutes)
    ttk.Label(backup_frame, text="Backup Interval (min):").grid(
        row=1, column=0, sticky="w", padx=10, pady=5
    )
    self.backup_interval_var = tk.IntVar(value=self.backup_interval)
    ttk.Spinbox(
        backup_frame, from_=1, to=1440, textvariable=self.backup_interval_var, width=5
    ).grid(row=1, column=1, sticky="w", padx=10, pady=5)

    # Maximum number of backups
    ttk.Label(backup_frame, text="Max Backups:").grid(
        row=2, column=0, sticky="w", padx=10, pady=5
    )
    self.max_backups_var = tk.IntVar(value=self.max_backups)
    ttk.Spinbox(
        backup_frame, from_=1, to=100, textvariable=self.max_backups_var, width=5
    ).grid(row=2, column=1, sticky="w", padx=10, pady=5)

    # Action buttons
    ttk.Button(backup_frame, text="Manual Backup", command=self.manual_backup).grid(
        row=3, column=1, pady=10
    )
    ttk.Button(
        backup_frame, text="Apply Settings", command=self.apply_backup_settings
    ).grid(row=3, column=2, pady=10)


def apply_backup_settings(self):
    self.backup_enabled = True
    self.backup_path = self.backup_path_var.get()
    self.backup_interval = self.backup_interval_var.get()
    self.max_backups = self.max_backups_var.get()
    self.save_settings()  # Ensure these settings are persisted
    self.start_backup_scheduler()


def browse_backup_path(self):
    from tkinter import filedialog

    path = filedialog.askdirectory(title="Select Backup Directory")
    if path:
        self.backup_path_var.set(path)


def manual_backup(self):
    threading.Thread(target=self.create_backup, daemon=True).start()


def backup_loop(self):
    while self.running and self.backup_enabled:
        time.sleep(self.backup_interval * 60)  # Convert minutes to seconds
        self.create_backup()


def create_backup(self):
    try:
        if not os.path.exists(self.backup_path):
            os.makedirs(self.backup_path)
        # If the server is running, trigger a save to ensure the latest data is stored.
        with self.backup_lock:
            if self.running:
                self.send_server_command("save-all")
                time.sleep(5)  # Allow time for the server to complete saving

            # Ensure the backup directory exists.
            backup_dir = self.backup_path
            os.makedirs(backup_dir, exist_ok=True)

            # Generate a timestamped filename for the backup.
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup_file = os.path.join(backup_dir, f"backup-{timestamp}.zip")

            # Create the zip file, archiving all files from the server directory.
            with zipfile.ZipFile(backup_file, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.server_path):
                    for file in files:
                        # Skip backup of server JARs, existing backups, and log files.
                        if not file.endswith((".zip", ".log")):
                            full_path = os.path.join(root, file)
                            # Use relative paths for archive structure.
                            relative_path = os.path.relpath(full_path, self.server_path)
                            zipf.write(full_path, relative_path)

            # Cleanup: Remove older backups beyond the max backups limit.
            backups = sorted(
                glob.glob(os.path.join(backup_dir, "backup-*.zip")),
                key=os.path.getctime,
                reverse=True,
            )
            for old_backup in backups[self.max_backups :]:
                os.remove(old_backup)

        self.update_console(f"Backup created: {backup_file}")
    except Exception as e:
        self.update_status(f"Backup directory error: {str(e)}")
