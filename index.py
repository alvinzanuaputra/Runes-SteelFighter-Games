import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading
import socket
import time
import os

class QuickLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Runes Steelfighter - Game Launcher")
        self.root.state('zoomed')
        self.root.resizable(True, True)
        self.root.configure(bg='#1a1a2e')
        self.processes = []
        self.server_ports = []
        self.next_port = 8890
        self.redis_started = False
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
            'Database.TButton': {'background': '#6c757d', 'active': '#5a6268'},
            'Redis.TButton': {'background': '#e74c3c', 'active': '#c0392b'},
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
            ("Start Redis Server", 'Redis.TButton', self.start_redis_server),
            ("Start Redis Client", 'Action.TButton', self.start_redis_client),
            ("Start Load Balancer", 'Action.TButton', self.start_load_balancer),
            ("Launch Server (8890)", 'Server.TButton', lambda: self.start_server(8890)),
            ("Launch Server (8891)", 'Server.TButton', lambda: self.start_server(8891)),
            ("Launch Client", 'Player.TButton', self.start_client),
            ("Launch Client #2", 'Player.TButton', self.start_client),
            ("Terminate All", 'Danger.TButton', self.kill_all),
            ("Clear Logs", 'Action.TButton', self.clear_log),
        ]
        
        for i, (text, style, cmd) in enumerate(btn_configs):
            row = i // 3
            col = i % 3
            ttk.Button(control_frame, text=text, style=style, command=cmd).grid(
                row=row, column=col, padx=5, pady=5, sticky="ew"
            )
        
        for col in range(3):
            control_frame.grid_columnconfigure(col, weight=1)

        status_frame = ttk.Frame(main_frame, style='Card.TFrame', padding=15)
        status_frame.pack(fill="x", pady=10)
        ttk.Label(status_frame, text="System Status", style='Card.TLabel').pack(anchor="w")
        self.status_text = tk.Text(status_frame, height=6, bg='#0f1419', fg='#00d4ff', font=('JetBrains Mono', 10), relief='flat', borderwidth=0, wrap=tk.WORD)
        self.status_text.pack(fill="x", pady=(5,0))
        
        log_frame = ttk.Frame(main_frame, style='Card.TFrame', padding=15)
        log_frame.pack(fill="both", expand=True, pady=10)
        ttk.Label(log_frame, text="Activity Logs", style='Card.TLabel').pack(anchor="w")
        self.log_text = scrolledtext.ScrolledText(log_frame, bg='#0f1419', fg='white', 
                                                 font=('JetBrains Mono', 10), relief='flat', 
                                                 borderwidth=0, wrap=tk.WORD)
        self.log_text.pack(fill="both", expand=True, pady=(5,0))
        
        for tag, color in {'success': '#28a745', 'error': '#dc3545', 'warning': '#ffc107', 'info': '#17a2b8'}.items():
            self.log_text.tag_configure(tag, foreground=color)

    def update_status(self):
        active_procs = [name for name, proc in self.processes if proc.poll() is None]
        status = f"Active Processes: {len(active_procs)}\n"
        status += f"Server Ports: {', '.join(map(str, self.server_ports)) or 'None'}\n"
        status += f"Redis Server: {'Running' if self.redis_started else 'Stopped'}\n"
        status += f"Running Services: {', '.join(active_procs) or 'None'}"
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(1.0, status)
        self.root.after(2000, self.update_status)

    def log(self, message, tag=None):
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n", tag)
        self.log_text.see(tk.END)

    def _start_process(self, script_name, process_name, args=None, show_errors=True):
        if not os.path.exists(script_name):
            self.log(f"❌ {script_name} script not found", 'error')
            return None
        command = ['python', script_name] + (args or [])
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                       creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            self.processes.append((process_name, process))
            self.log(f"🚀 {process_name} launched successfully", 'success')
            threading.Thread(target=self.monitor_process, args=(process_name, process, show_errors), daemon=True).start()
            return process
        except Exception as e:
            self.log(f"❌ Failed to start {process_name}: {e}", 'error')
            return None

    def check_database(self):
        self.log("🔍 Memeriksa koneksi database...", 'info')
        process = self._start_process('database/database.py', 'Database Check', 
                                      args=['check'], show_errors=False)
        
        if process:
            process.wait()
            
            stdout_data = process.stdout.read()
            if '✅ Koneksi ke database berhasil' in stdout_data:
                self.log("✅ Koneksi database berhasil", 'success')
            else:
                self.log("❌ Koneksi database gagal", 'error')

    def start_redis_server(self):
        if self.redis_started:
            self.log("⚠️ Redis server is already running", 'warning')
            return
        
        self.log("🔧 Starting Redis server...", 'info')
        try:
            process = subprocess.Popen(['redis-server'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                     creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            self.processes.append(('Redis Server', process))
            self.redis_started = True
            self.log("✅ Redis server started in background", 'success')
            threading.Thread(target=self.monitor_process, args=('Redis Server', process, False), daemon=True).start()
        except Exception as e:
            self.log(f"❌ Failed to start Redis server: {e}", 'error')

    def start_redis_client(self):
        if not self.redis_started:
            self.log("⚠️ Please start Redis server first", 'warning')
            return
        self.log("🔌 Starting Redis client...", 'info')
        self._start_process('redis_client.py', 'Redis Client', show_errors=True)

    def start_load_balancer(self):
        self.log("⚖️ Starting load balancer...", 'info')
        self._start_process('load_balancer.py', 'Load Balancer', show_errors=True)

    def start_server(self, port=None):
        if port is None:
            port = self.next_port
            while not self.is_port_available(port):
                port += 1
            self.next_port = port + 1
        
        if port in self.server_ports:
            self.log(f"⚠️ Server on port {port} is already running", 'warning')
            return
            
        if not self.is_port_available(port):
            self.log(f"❌ Port {port} is not available", 'error')
            return
        
        self.log(f"🌐 Starting server on port {port}...", 'info')    
        self.server_ports.append(port)
        self._start_process('server_thread_http.py', f'Server:{port}', [str(port)], show_errors=True)

    def start_client(self):
        client_number = len([name for name, _ in self.processes if 'Client' in name]) + 1
        self.log(f"👤 Starting client #{client_number}...", 'info')
        self._start_process('client2.py', f'Client-{client_number}', show_errors=True)

    def monitor_process(self, name, process, show_errors=True):
        try:
            stdout_lines = []
            stderr_lines = []
            has_success_message = False
            
            for output in iter(process.stdout.readline, ''):
                clean_output = output.strip()
                if clean_output and 'pygame' not in clean_output.lower():
                    stdout_lines.append(clean_output)
                    if ('✅' in clean_output or 'berhasil' in clean_output.lower() or 
                        'success' in clean_output.lower() or 'connected' in clean_output.lower()):
                        has_success_message = True
                        self.log(f"✅ [{name}] {clean_output}", 'success')
                    elif ('❌' in clean_output or 'error' in clean_output.lower() or 
                          'failed' in clean_output.lower() or 'gagal' in clean_output.lower()):
                        self.log(f"❌ [{name}] {clean_output}", 'error')
                    elif ('⚠️' in clean_output or 'warning' in clean_output.lower() or 
                          'peringatan' in clean_output.lower()):
                        self.log(f"⚠️ [{name}] {clean_output}", 'warning')
                    elif not any(x in clean_output.lower() for x in ['sqlalchemy', 'info sqlalchemy', '[raw sql]', 'generated in', 'begin (implicit)', 'rollback']):
                        self.log(f"📝 [{name}] {clean_output}", 'info')
            
            process.wait()
            stderr_output = process.stderr.read()
            
            if stderr_output.strip():
                stderr_lines = stderr_output.strip().split('\n')
                for error_line in stderr_lines:
                    if error_line.strip() and show_errors:
                        if not any(x in error_line.lower() for x in ['info', 'debug', 'warning']):
                            self.log(f"🚨 [{name}] ERROR: {error_line}", 'error')
            
            if name == 'Database Check':
                if has_success_message or (process.returncode == 0):
                    self.log(f"✅ [{name}] Database connection verified successfully", 'success')
                elif process.returncode != 0:
                    self.log(f"❌ [{name}] Database connection failed (exit code: {process.returncode})", 'error')
                    if show_errors and stderr_lines:
                        self.log(f"💡 [{name}] Check database server status and credentials", 'info')
            elif name.startswith('Server:'):
                if process.returncode != 0:
                    self.log(f"❌ [{name}] Server failed to start (exit code: {process.returncode})", 'error')
                    if show_errors:
                        self.log(f"💡 [{name}] Check if port is available and dependencies are installed", 'info')
                else:
                    self.log(f"✅ [{name}] Server started successfully", 'success')
            elif name.startswith('Client'):
                if process.returncode != 0:
                    self.log(f"❌ [{name}] Client failed to start (exit code: {process.returncode})", 'error')
                else:
                    self.log(f"✅ [{name}] Client completed successfully", 'success')
            else:
                if process.returncode != 0:
                    self.log(f"⚠️ [{name}] Process exited with code {process.returncode}", 'warning')
                    if show_errors and stderr_lines and not has_success_message:
                        self.log(f"💡 [{name}] Check error messages above for details", 'info')
                else:
                    self.log(f"✅ [{name}] Process completed successfully", 'success')
                
            if name == 'Redis Server':
                self.redis_started = False
                
        except Exception as e:
            self.log(f"❌ Error monitoring {name}: {e}", 'error')

    def kill_all(self):
        killed_count = 0
        self.log("🛑 Terminating all processes...", 'warning')
        
        for name, process in self.processes:
            if process.poll() is None:
                try:
                    process.terminate()
                    killed_count += 1
                    self.log(f"🔪 Terminated {name}", 'warning')
                except Exception as e:
                    self.log(f"❌ Error terminating {name}: {e}", 'error')
        
        self.processes.clear()
        self.server_ports.clear()
        self.next_port = 8890
        self.redis_started = False
        
        if killed_count > 0:
            self.log(f"✅ Successfully terminated {killed_count} processes", 'info')
        else:
            self.log("ℹ️ No active processes to terminate", 'info')

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        self.log("Logs cleared", 'info')

    def is_port_available(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0
    
    def on_closing(self):
        self.kill_all()
        self.root.destroy()
    
    def toggle_fullscreen(self, event=None):
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)

if __name__ == "__main__":
    root = tk.Tk()
    app = QuickLauncher(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.bind('<F11>', app.toggle_fullscreen)
    root.bind('<Escape>', lambda e: root.attributes('-fullscreen', False))
    root.mainloop()