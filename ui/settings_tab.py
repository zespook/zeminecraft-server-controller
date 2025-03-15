import tkinter as tk
from tkinter import ttk, messagebox
import os
import threading
import time
import platform


def create_settings_tab(self, parent):
    # Server settings
    settings_frame = ttk.LabelFrame(parent, text="Server Settings")
    settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Add Shutdown Timer section
    shutdown_frame = ttk.LabelFrame(settings_frame, text="Shutdown Timer (Temporary)")
    shutdown_frame.grid(row=8, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

    # Hours input
    ttk.Label(shutdown_frame, text="Hours:").grid(row=0, column=0, padx=5, pady=5)
    self.shutdown_hours_var = tk.StringVar()
    ttk.Spinbox(
        shutdown_frame, from_=0, to=24, textvariable=self.shutdown_hours_var, width=5
    ).grid(row=0, column=1, padx=5, pady=5)

    # Minutes input
    ttk.Label(shutdown_frame, text="Minutes:").grid(row=0, column=2, padx=5, pady=5)
    self.shutdown_minutes_var = tk.StringVar()
    ttk.Spinbox(
        shutdown_frame, from_=0, to=59, textvariable=self.shutdown_minutes_var, width=5
    ).grid(row=0, column=3, padx=5, pady=5)

    # Shutdown PC checkbox
    self.shutdown_pc_var = tk.BooleanVar()
    ttk.Checkbutton(
        shutdown_frame, text="Shutdown PC after stopping", variable=self.shutdown_pc_var
    ).grid(row=0, column=4, padx=5, pady=5)

    # Start timer button
    ttk.Button(
        shutdown_frame, text="Start Timer", command=self.set_shutdown_timer
    ).grid(row=0, column=5, padx=10, pady=5)

    # Server path
    ttk.Label(settings_frame, text="Server Directory:").grid(
        row=0, column=0, sticky="w", padx=10, pady=5
    )
    self.server_path_var = tk.StringVar(value=self.server_path)
    ttk.Entry(settings_frame, textvariable=self.server_path_var, width=50).grid(
        row=0, column=1, padx=10, pady=5
    )
    ttk.Button(settings_frame, text="Browse...", command=self.browse_server_path).grid(
        row=0, column=2, padx=10, pady=5
    )

    # Java path
    ttk.Label(settings_frame, text="Java Path:").grid(
        row=1, column=0, sticky="w", padx=10, pady=5
    )
    self.java_path_var = tk.StringVar(value=self.java_path)
    ttk.Entry(settings_frame, textvariable=self.java_path_var, width=50).grid(
        row=1, column=1, padx=10, pady=5
    )
    ttk.Button(settings_frame, text="Browse...", command=self.browse_java_path).grid(
        row=1, column=2, padx=10, pady=5
    )

    # Server JAR
    ttk.Label(settings_frame, text="Server JAR File:").grid(
        row=2, column=0, sticky="w", padx=10, pady=5
    )
    self.server_jar_var = tk.StringVar(value=self.server_jar)
    ttk.Entry(settings_frame, textvariable=self.server_jar_var, width=50).grid(
        row=2, column=1, padx=10, pady=5
    )
    ttk.Button(settings_frame, text="Browse...", command=self.browse_server_jar).grid(
        row=2, column=2, padx=10, pady=5
    )

    # Memory settings
    ttk.Label(settings_frame, text="Minimum Memory:").grid(
        row=3, column=0, sticky="w", padx=10, pady=5
    )
    self.xms_var = tk.StringVar(value=self.xms)
    ttk.Combobox(
        settings_frame,
        textvariable=self.xms_var,
        values=["512M", "1G", "2G", "4G", "6G", "8G"],
    ).grid(row=3, column=1, sticky="w", padx=10, pady=5)

    ttk.Label(settings_frame, text="Maximum Memory:").grid(
        row=4, column=0, sticky="w", padx=10, pady=5
    )
    self.xmx_var = tk.StringVar(value=self.xmx)
    ttk.Combobox(
        settings_frame,
        textvariable=self.xmx_var,
        values=["1G", "2G", "4G", "6G", "8G", "10G", "12G", "16G"],
    ).grid(row=4, column=1, sticky="w", padx=10, pady=5)

    # Additional JVM arguments
    ttk.Label(settings_frame, text="Additional JVM Args:").grid(
        row=5, column=0, sticky="w", padx=10, pady=5
    )
    self.jvm_args_var = tk.StringVar()
    ttk.Entry(settings_frame, textvariable=self.jvm_args_var, width=50).grid(
        row=5, column=1, padx=10, pady=5
    )

    # GUI settings
    ttk.Label(settings_frame, text="Auto-refresh Interval (seconds):").grid(
        row=6, column=0, sticky="w", padx=10, pady=5
    )
    self.refresh_interval_var = tk.IntVar(value=5)
    ttk.Spinbox(
        settings_frame, from_=1, to=60, textvariable=self.refresh_interval_var, width=5
    ).grid(row=6, column=1, sticky="w", padx=10, pady=5)

    # Save button
    ttk.Button(settings_frame, text="Save Settings", command=self.save_settings).grid(
        row=7, column=1, pady=20
    )


def browse_server_path(self):
    from tkinter import filedialog

    path = filedialog.askdirectory(title="Select Minecraft Server Directory")
    if path:
        self.server_path_var.set(path)


def browse_java_path(self):
    from tkinter import filedialog

    path = filedialog.askopenfilename(
        title="Select Java Executable",
        filetypes=[("Executable", "*.exe"), ("All Files", "*.*")],
    )
    if path:
        self.java_path_var.set(path)


def browse_server_jar(self):
    from tkinter import filedialog

    path = filedialog.askopenfilename(
        title="Select Server Executable",
        filetypes=[("Executable Files", "*.*"), ("All Files", "*.*")],
    )
    if path:
        self.server_jar_var.set(os.path.basename(path))


def set_shutdown_timer(self):
    try:
        hours = int(self.shutdown_hours_var.get() or 0)
        minutes = int(self.shutdown_minutes_var.get() or 0)
        total_seconds = (hours * 3600) + (minutes * 60)

        if total_seconds <= 0:
            raise ValueError("Timer must be at least 1 minute")

        if hours < 0 or minutes < 0:
            raise ValueError("Negative values not allowed")

    except ValueError as e:
        messagebox.showerror("Error", f"Invalid time: {str(e)}")
        return

    shutdown_pc = self.shutdown_pc_var.get()
    threading.Thread(
        target=self._shutdown_countdown, args=(total_seconds, shutdown_pc), daemon=True
    ).start()
    self.update_status(
        f"Server will shutdown in {hours}h {minutes}m {'+ PC shutdown' if shutdown_pc else ''}"
    )


def _shutdown_countdown(self, total_seconds, shutdown_pc):
    start_time = time.time()

    # Update status with remaining time
    while (time.time() - start_time) < total_seconds and self.running:
        remaining = total_seconds - (time.time() - start_time)
        hours, rem = divmod(remaining, 3600)
        minutes, seconds = divmod(rem, 60)
        self.root.after(
            0,
            self.update_status,
            f"Shutting down in: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}",
        )
        time.sleep(1)

    if not self.running:
        return  # Server already stopped

    # Stop server from main thread
    self.root.after(0, self.stop_server)

    # Wait for server to stop
    time.sleep(30)

    # Shutdown PC if requested
    if shutdown_pc:
        try:
            if platform.system() == "Windows":
                os.system("shutdown /s /t 0")
            elif platform.system() == "Linux":
                os.system("shutdown now")
            elif platform.system() == "Darwin":
                os.system("shutdown -h now")
        except Exception as e:
            self.update_status(f"Failed to shutdown PC: {str(e)}")
