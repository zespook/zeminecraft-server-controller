import tkinter as tk
import sys
import os
import subprocess
import controller as MinecraftServerController


if __name__ == "__main__":
    # Improved pythonw.exe detection
    if sys.executable.lower().endswith("pythonw.exe"):
        root = tk.Tk()
        app = MinecraftServerController(root)
        root.protocol("WM_DELETE_WINDOW", app.exit_application)
        root.mainloop()
    else:
        try:
            pythonw = sys.executable.replace("python.exe", "pythonw.exe")
            if not os.path.exists(pythonw):
                pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")

            subprocess.Popen(
                [pythonw, __file__], creationflags=subprocess.CREATE_NO_WINDOW
            )
        except Exception as e:
            print(f"Error relaunching: {str(e)}")
            input("Press Enter to exit...")
