import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading
import socket
import time
import os
import signal

class QuickLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Runes Steelfighter - Game Launcher")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.root.configure(bg='#1a1a2e')

        self.processes = []
        self.server_ports = []
        self.next_port = 8890

        self._setup_styles()
        self._create_widgets()
        self.update_status()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        base_bg = '#1a1a2e'
        card_bg = '#16213e'
        text_fg = '#ffffff'
        font_family = 'Segoe UI'

        style_definitions = {
            'TFrame': {'background': base_bg},
            'Card.TFrame': {'background': card_bg, 'relief': 'raised', 'borderwidth': 1},
            'Title.TLabel': {'background': base_bg, 'foreground': '#00d4ff', 'font': (font_family, 22, 'bold')},
            'Subtitle.TLabel': {'background': base_bg, 'foreground': text_fg, 'font': (font_family, 11)},
            'Card.TLabel': {'background': card_bg, 'foreground': text_fg, 'font': (font_family, 10, 'bold')},
        }
        for name, conf in style_definitions.items():
            style.configure(name, **conf)

        button_styles = {
            'Action.TButton': {'background': '#0f3460', 'active': '#1e5f8b'},
            'Server.TButton': {'background': '#2d5a27', 'active': '#3d7a37'},
            'Player.TButton': {'background': '#7a4c93', 'active': '#9a6cb3'},
            'Danger.TButton': {'background': '#dc3545', 'active': '#c82333'},
        }
        for name, colors in button_styles.items():
            style.configure(name, foreground=text_fg, font=(font_family, 10, 'bold'), borderwidth=0, relief='flat', padding=(10, 8))
            style.map(name, background=[('active', colors['active']), ('pressed', colors['background'])])

    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="RUNES STEELFIGHTER", style='Title.TLabel').pack()
        ttk.Label(main_frame, text="Game Server Management System", style='Subtitle.TLabel').pack(pady=(0, 20))

        control_frame = ttk.Frame(main_frame, style='Card.TFrame', padding=15)
        control_frame.pack(fill="x", pady=10)
        
        btn_configs = [
            ("Start Load Balancer", 'Action.TButton', self.start_load_balancer),
            ("Launch Server", 'Server.TButton', self.start_server),
            ("Launch Player", 'Player.TButton', self.start_player),
            ("Terminate All", 'Danger.TButton', self.kill_all),
            ("Clear Logs", 'Action.TButton', self.clear_log),
        ]
        for i, (text, style, cmd) in enumerate(btn_configs):
            ttk.Button(control_frame, text=text, style=style, command=cmd).grid(row=i // 3, column=i % 3, padx=5, pady=5, sticky="ew")

        status_frame = ttk.Frame(main_frame, style='Card.TFrame', padding=15)
        status_frame.pack(fill="x", pady=10)
        ttk.Label(status_frame, text="System Status", style='Card.TLabel').pack(anchor="w")
        self.status_text = tk.Text(status_frame, height=4, bg='#0f1419', fg='#00d4ff', font=('JetBrains Mono', 9), relief='flat', borderwidth=0)
        self.status_text.pack(fill="x", pady=(5,0))
        
        log_frame = ttk.Frame(main_frame, style='Card.TFrame', padding=15)
        log_frame.pack(fill="both", expand=True, pady=10)
        ttk.Label(log_frame, text="Activity Logs", style='Card.TLabel').pack(anchor="w")
        self.log_text = scrolledtext.ScrolledText(log_frame, bg='#0f1419', fg= 'white', font=('JetBrains Mono', 9), relief='flat', borderwidth=0)
        self.log_text.pack(fill="both", expand=True, pady=(5,0))

        for tag, color in {'success': '#28a745', 'error': '#dc3545', 'warning': '#ffc107', 'info': '#17a2b8'}.items():
            self.log_text.tag_configure(tag, foreground=color)

    def update_status(self):
        active_procs = [name for name, proc in self.processes if proc.poll() is None]
        status = f"Active Processes: {len(active_procs)}\n"
        status += f"Server Ports: {', '.join(map(str, self.server_ports)) or 'None'}\n"
        status += f"Running Services: {', '.join(active_procs) or 'None'}"
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(1.0, status)
        self.root.after(2000, self.update_status)

    def log(self, message, tag=None):
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n", tag)
        self.log_text.see(tk.END)

    def _start_process(self, script_name, process_name, args=None):
        if not os.path.exists(script_name):
            self.log(f"{script_name} script not found", 'error')
            return
        
        command = ['python', script_name] + (args or [])
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                       creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            self.processes.append((process_name, process))
            self.log(f"{process_name} launched successfully", 'success')
            threading.Thread(target=self.monitor_process, args=(process_name, process), daemon=True).start()
        except Exception as e:
            self.log(f"Failed to start {process_name}: {e}", 'error')

    def start_load_balancer(self):
        self._start_process('load_balancer.py', 'Load Balancer')

    def start_server(self):
        port = self.next_port
        while not self.is_port_available(port):
            port += 1
        self.next_port = port + 1
        self.server_ports.append(port)
        self._start_process('server.py', f'Server:{port}', [str(port)])
    
    def start_player(self):
        self._start_process('player.py', f'Player-{len(self.processes)}')

    def monitor_process(self, name, process):
        for output in iter(process.stdout.readline, ''):
            clean_output = output.strip()
            if clean_output and 'pygame' not in clean_output:
                self.log(f"[{name}] {clean_output}", 'info')
        if process.returncode != 0 and process.returncode is not None:
             self.log(f"[{name}] Process terminated with code {process.returncode}", 'warning')

    def kill_all(self):
        killed_count = 0
        for name, process in self.processes:
            if process.poll() is None:
                try:
                    process.terminate()
                    killed_count += 1
                except: pass
        self.processes.clear()
        self.server_ports.clear()
        self.next_port = 8890
        if killed_count > 0:
            self.log(f"Terminated {killed_count} processes", 'warning')

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        self.log("Logs cleared", 'info')

    def is_port_available(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0
    
    def on_closing(self):
        self.kill_all()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuickLauncher(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()