1. main.py
```python
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
```
2. load_balancer.py
```python
import socket
import threading
import pickle

servers = [
    # Round robin load balancing with 10 servers
    {"host": "localhost", "port": 8890, "clients": 0},
    {"host": "localhost", "port": 8891, "clients": 0},
    {"host": "localhost", "port": 8892, "clients": 0},
    {"host": "localhost", "port": 8893, "clients": 0},
    {"host": "localhost", "port": 8894, "clients": 0},
    {"host": "localhost", "port": 8895, "clients": 0},
    {"host": "localhost", "port": 8896, "clients": 0},
    {"host": "localhost", "port": 8897, "clients": 0},
    {"host": "localhost", "port": 8898, "clients": 0},
    {"host": "localhost", "port": 8899, "clients": 0}
]
lock = threading.Lock()
def forward(src, dst, server_ref):
    try:
        while True:
            data = src.recv(4096)
            if not data:
                break
            dst.sendall(data)
    except:
        pass
    finally:
        src.close()
        dst.close()
        with lock:
            server_ref["clients"] -= 1

def handle_client(client_socket):
    global servers
    with lock:
        selected_server = None
        for server in servers:
            if server["clients"] < 2:
                selected_server = server
                server["clients"] += 1
                break
        if not selected_server:
            client_socket.send(b"FULL")
            client_socket.close()
            return
    try:
        backend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend.connect((selected_server["host"], selected_server["port"]))
    except:
        client_socket.send(b"ERROR CONNECTING TO SERVER")
        client_socket.close()
        return
    threading.Thread(target=forward, args=(client_socket, backend, selected_server)).start()
    threading.Thread(target=forward, args=(backend, client_socket, selected_server)).start()

def main():
    balancer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    balancer.bind(("0.0.0.0", 8888))
    balancer.listen(10)
    print("[LOAD BALANCER] Listening on port 8888...")
    while True:
        client_sock, addr = balancer.accept()
        print(f"[LOAD BALANCER] Client connected from {addr}")
        threading.Thread(target=handle_client, args=(client_sock,)).start()

if __name__ == "__main__":
    main()
```
3. server.py
```python
import socket
import threading
import pickle
import sys

players = [{}, {}] 
lock = threading.Lock()

def handle_client(conn, player_id):
    players[player_id] = {
        "x": 100 if player_id == 0 else 700,
        "y": 300,
        "health": 100,
        "action": 0,
        "flip": False,
        "attack_type": 0
    }
    conn.send(pickle.dumps({"player": player_id}))
    while True:
        try:
            data = pickle.loads(conn.recv(4096))
            with lock:
                for key in data:
                    if key != "health":
                        players[player_id][key] = data[key]
                
                enemy_id = 1 - player_id

                if players[enemy_id]:
                    att_x = players[player_id].get("x", 0)
                    att_y = players[player_id].get("y", 0)
                    target_x = players[enemy_id].get("x", 0)
                    target_y = players[enemy_id].get("y", 0)

                    if players[player_id].get("attack_type", 0) in [1, 2]:
                        if abs(att_x - target_x) < 150 and abs(att_y - target_y) < 100:
                            players[enemy_id]["health"] = max(0, players[enemy_id].get("health", 100) - 10)
                        players[player_id]["attack_type"] = 0

                reply = {
                    "self": players[player_id],
                    "enemy": players[enemy_id] if players[enemy_id] else {}
                }
                conn.sendall(pickle.dumps(reply))
        except:
            break
    conn.close()

def main():
    PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8889
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", PORT))
    server.listen(2)
    print(f"[SERVER] Running on port {PORT}...")
    player_id = 0
    while player_id < 2:
        conn, addr = server.accept()
        print(f"[SERVER] Player {player_id} connected from {addr}")
        thread = threading.Thread(target=handle_client, args=(conn, player_id))
        thread.start()
        player_id += 1

if __name__ == "__main__":
    main()
```
4. player.py
```python
import pygame
from pygame import mixer
from fighter import Fighter, RemoteFighter
import socket
import pickle

class GameClient:
    def __init__(self):
        self._init_pygame()
        self._init_display()
        self._init_game_constants()
        self._init_assets()
        self._init_fonts()
        self._init_network()
        self._init_fighters()
        self.enemy_connected = False
        self.run = True
        
    def _init_pygame(self):
        mixer.init()
        pygame.init()
        self.info = pygame.display.Info()
        self.clock = pygame.time.Clock()
        
    def _init_display(self):
        self.WINDOW_WIDTH = 1000
        self.WINDOW_HEIGHT = 600
        self.FULLSCREEN_WIDTH = self.info.current_w
        self.FULLSCREEN_HEIGHT = self.info.current_h
        self.is_fullscreen = False
        self.SCREEN_WIDTH = self.WINDOW_WIDTH
        self.SCREEN_HEIGHT = self.WINDOW_HEIGHT
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Runes & Steel Fighter")
        
    def _init_game_constants(self):
        self.FPS = 60
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.intro_count = 3
        self.last_count_update = pygame.time.get_ticks()
        self.score = [0, 0]
        self.round_over = False
        self.game_over = False
        self.game_result = None
        self.result_sound_played = False
        self.game_over_delay_time = None
        self.ROUND_OVER_COOLDOWN = 2000
        self.GAME_OVER_DELAY = 1500
        self.WARRIOR_SIZE = 162
        self.WARRIOR_SCALE = 4
        self.WARRIOR_OFFSET = [72, 56]
        self.WARRIOR_DATA = [self.WARRIOR_SIZE, self.WARRIOR_SCALE, self.WARRIOR_OFFSET]
        self.WIZARD_SIZE = 250
        self.WIZARD_SCALE = 3
        self.WIZARD_OFFSET = [112, 107]
        self.WIZARD_DATA = [self.WIZARD_SIZE, self.WIZARD_SCALE, self.WIZARD_OFFSET]
        self.WARRIOR_ANIMATION_STEPS = [10, 8, 1, 7, 7, 3, 7]
        self.WIZARD_ANIMATION_STEPS = [8, 8, 1, 8, 8, 3, 7]
        self.ATTACK_COOLDOWN = 500 
        self.last_attack_time = 0
        
    def _init_assets(self):
        pygame.mixer.music.load("assets/audio/music.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1, 0.0, 5000)
        
        self.sword_fx = pygame.mixer.Sound("assets/audio/sword.wav")
        self.sword_fx.set_volume(0.5)
        self.magic_fx = pygame.mixer.Sound("assets/audio/magic.wav")
        self.magic_fx.set_volume(0.75)
        self.warrior_graunt_fx = pygame.mixer.Sound("assets/audio/warior-graunt.wav")
        self.warrior_graunt_fx.set_volume(0.7)
        self.wizard_graunt_fx = pygame.mixer.Sound("assets/audio/wizard-graunt.wav")
        self.wizard_graunt_fx.set_volume(0.7)
        self.victory_fx = pygame.mixer.Sound("assets/audio/victory.wav")
        self.victory_fx.set_volume(0.8)
        self.defeat_fx = pygame.mixer.Sound("assets/audio/defeat.wav")
        self.defeat_fx.set_volume(0.8)
        
        self.bg_image = pygame.image.load("assets/images/background/background.jpg").convert_alpha()
        self.warrior_sheet = pygame.image.load("assets/images/warrior/Sprites/warrior.png").convert_alpha()
        self.wizard_sheet = pygame.image.load("assets/images/wizard/Sprites/wizard.png").convert_alpha()
        
    def _init_fonts(self):
        """Initialize fonts"""
        self.count_font = pygame.font.Font("assets/fonts/turok.ttf", 80)
        self.score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)
        self.result_font = pygame.font.Font("assets/fonts/turok.ttf", 60)
        self.message_font = pygame.font.Font("assets/fonts/turok.ttf", 40)
        
    def _init_network(self):
        """Initialize network connection"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(("localhost", 8888))
        player_data = pickle.loads(self.sock.recv(1024))
        self.player_num = player_data["player"]
        print(f"Connected as Player {self.player_num}")
        if self.player_num == 0:
            self.local_label = "P1-Warrior: "
            self.enemy_label = "P2-Wizard: "
        else:
            self.local_label = "P2-Wizard: "
            self.enemy_label = "P1-Warrior: "
            
    def _init_fighters(self):
        self._calculate_fighter_positions()
        if self.player_num == 0:
            self.local_fighter = Fighter(
                1, self.fighter_1_x, self.ground_y, False, 
                self.WARRIOR_DATA, self.warrior_sheet, 
                self.WARRIOR_ANIMATION_STEPS, self.sword_fx, self.warrior_graunt_fx
            )
            self.remote_fighter = RemoteFighter(
                {}, self.wizard_sheet, self.WIZARD_SCALE, self.WIZARD_OFFSET
            )
            self.remote_animation = self.remote_fighter.load_images(
                self.wizard_sheet, self.WIZARD_ANIMATION_STEPS
            )
        else:
            self.local_fighter = Fighter(
                2, self.fighter_2_x, self.ground_y, True, 
                self.WIZARD_DATA, self.wizard_sheet, 
                self.WIZARD_ANIMATION_STEPS, self.magic_fx, self.wizard_graunt_fx
            )
            self.remote_fighter = RemoteFighter(
                {}, self.warrior_sheet, self.WARRIOR_SCALE, self.WARRIOR_OFFSET
            )
            self.remote_animation = self.remote_fighter.load_images(
                self.warrior_sheet, self.WARRIOR_ANIMATION_STEPS
            )
            
    def _calculate_fighter_positions(self):
        self.fighter_1_x = int(self.SCREEN_WIDTH * 0.2)
        self.fighter_2_x = int(self.SCREEN_WIDTH * 0.7)
        self.ground_y = int(self.SCREEN_HEIGHT * 0.7)
        
    def draw_text(self, text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        self.screen.blit(img, (x, y))
        
    def draw_bg(self):
        scaled_bg = pygame.transform.scale(self.bg_image, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.screen.blit(scaled_bg, (0, 0))
        
    def draw_health_bar(self, health, x, y, width=400):
        ratio = health / 100
        pygame.draw.rect(self.screen, self.WHITE, (x - 2, y - 2, width + 4, 34))
        pygame.draw.rect(self.screen, self.RED, (x, y, width, 30))
        pygame.draw.rect(self.screen, self.YELLOW, (x, y, width * ratio, 30))
        
    def handle_screen_resize(self, new_width, new_height):
        self.SCREEN_WIDTH = new_width
        self.SCREEN_HEIGHT = new_height
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE)
        self._calculate_fighter_positions()
        if self.player_num == 0:
            self.local_fighter.rect.x = self.fighter_1_x
        else:
            self.local_fighter.rect.x = self.fighter_2_x
        self.local_fighter.rect.y = self.ground_y
        
    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.handle_screen_resize(self.FULLSCREEN_WIDTH, self.FULLSCREEN_HEIGHT)
        else:
            self.handle_screen_resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
            
    def handle_events(self):
        events = pygame.event.get()
        current_time = pygame.time.get_ticks()
        for event in events:
            if event.type == pygame.QUIT:
                self.run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.run = False
            elif event.type == pygame.VIDEORESIZE:
                if not self.is_fullscreen:
                    self.handle_screen_resize(event.w, event.h)
            elif event.type == pygame.VIDEOEXPOSE:
                pygame.display.flip()
        return events
    
    def handle_network(self):
        send_data = {
            "x": self.local_fighter.rect.x,
            "y": self.local_fighter.rect.y,
            "health": self.local_fighter.health,
            "action": self.local_fighter.action,
            "flip": self.local_fighter.flip,
            "attack_type": self.local_fighter.attack_type
        }
        try:
            self.sock.send(pickle.dumps(send_data))
            received = self.sock.recv(4096)
            if received:
                all_data = pickle.loads(received)
                self.local_fighter.health = all_data["self"]["health"]
                self.local_fighter.rect.x = all_data["self"]["x"]
                self.local_fighter.rect.y = all_data["self"]["y"]
                self.local_fighter.flip = all_data["self"]["flip"]
                self.local_fighter.action = all_data["self"]["action"]
                if all_data["enemy"] and "x" in all_data["enemy"]:
                    self.enemy_connected = True
                    self.remote_fighter.update_data(all_data["enemy"])
                else:
                    self.enemy_connected = False
        except:
            pass
            
    def handle_round_logic(self):
        if not self.round_over:
            if not self.local_fighter.alive:
                self.score[1 - self.player_num] += 1
                self.round_over = True
                self.round_over_time = pygame.time.get_ticks()
                self.game_result = 'lose'
                self.game_over_delay_time = pygame.time.get_ticks()
            elif self.remote_fighter.health <= 0:
                self.score[self.player_num] += 1
                self.round_over = True
                self.round_over_time = pygame.time.get_ticks()
                self.game_result = 'win'
                self.game_over_delay_time = pygame.time.get_ticks()
        if self.game_over_delay_time and not self.game_over:
            if pygame.time.get_ticks() - self.game_over_delay_time >= self.GAME_OVER_DELAY:
                self.game_over = True
    
    def draw_game_result(self):
        if not self.game_over:
            return
        if not self.result_sound_played:
            if self.game_result == 'win':
                self.victory_fx.play()
            elif self.game_result == 'lose':
                self.defeat_fx.play()
            self.result_sound_played = True
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        if self.game_result == 'win':
            victory_text = "VICTORY"
            message_text = "You Win!"
            text_color = self.GREEN
        else:
            victory_text = "DEFEAT"
            message_text = "You Lose!"
            text_color = self.RED
        victory_surface = self.result_font.render(victory_text, True, text_color)
        victory_x = (self.SCREEN_WIDTH - victory_surface.get_width()) // 2
        victory_y = self.SCREEN_HEIGHT // 3
        self.screen.blit(victory_surface, (victory_x, victory_y))
        message_surface = self.message_font.render(message_text, True, text_color)
        message_x = (self.SCREEN_WIDTH - message_surface.get_width()) // 2
        message_y = victory_y + 80
        self.screen.blit(message_surface, (message_x, message_y))
        quit_button_width = 150
        quit_button_height = 50
        quit_button_x = (self.SCREEN_WIDTH - quit_button_width) // 2
        quit_button_y = message_y + 100
        button_color = (255, 255, 255)
        hover_color = (230, 230, 230)
        click_color = (200, 200, 200)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_button = pygame.mouse.get_pressed()
        mouse_over_button = (
            quit_button_x < mouse_x < quit_button_x + quit_button_width and
            quit_button_y < mouse_y < quit_button_y + quit_button_height
        )
        
        # Tentukan warna tombol berdasarkan status
        if mouse_over_button and mouse_button[0]:  # Klik kiri
            current_color = click_color
        elif mouse_over_button:
            current_color = hover_color
        else:
            current_color = button_color
        
        # Gambar tombol
        pygame.draw.rect(self.screen, current_color, (quit_button_x, quit_button_y, quit_button_width, quit_button_height))
        quit_text = self.result_font.render("QUIT", True, (0, 0, 0))  # Teks hitam
        text_x = quit_button_x + (quit_button_width - quit_text.get_width()) // 2
        text_y = quit_button_y + (quit_button_height - quit_text.get_height()) // 2
        self.screen.blit(quit_text, (text_x, text_y))
        return (quit_button_x, quit_button_y, quit_button_width, quit_button_height)

    def draw_ui(self):
        """Draw user interface elements"""
        health_bar_width = int(self.SCREEN_WIDTH * 0.4)
        margin = int(self.SCREEN_WIDTH * 0.02)
        if self.player_num == 0:
            local_health_x = margin
            enemy_health_x = self.SCREEN_WIDTH - health_bar_width - margin
        else:
            local_health_x = self.SCREEN_WIDTH - health_bar_width - margin
            enemy_health_x = margin
        self.draw_health_bar(self.local_fighter.health, local_health_x, 20, health_bar_width)
        self.draw_text(
            self.local_label + str(self.score[self.player_num]), 
            self.score_font, self.RED, local_health_x, 60
        )
        if self.enemy_connected:
            self.draw_health_bar(
                self.remote_fighter.health, 
                enemy_health_x, 20, 
                health_bar_width
            )
            self.draw_text(
                self.enemy_label + str(self.score[1 - self.player_num]), 
                self.score_font, self.RED,
                enemy_health_x, 60
            )
            
    def update_fighters(self):
        if not self.game_over:
            self.local_fighter.update()
            if self.enemy_connected:
                self.remote_fighter.update(self.remote_animation)
            
    def draw_fighters(self):
        self.local_fighter.draw(self.screen)
        if self.enemy_connected:
            self.remote_fighter.draw(self.screen, self.remote_animation)
            
    def check_game_over(self):
        pass
            
    def draw_quit_button(self):
        button_width = 100
        button_height = 50
        button_x = self.SCREEN_WIDTH - button_width - 20
        button_y = 20 
        button_color = (200, 50, 50) 
        hover_color = (255, 100, 100)
        text_color = self.WHITE
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_over_button = (
            button_x < mouse_x < button_x + button_width and
            button_y < mouse_y < button_y + button_height
        )
        current_color = hover_color if mouse_over_button else button_color
        pygame.draw.rect(self.screen, current_color, (button_x, button_y, button_width, button_height))
        quit_text = self.message_font.render("Quit", True, text_color)
        text_x = button_x + (button_width - quit_text.get_width()) // 2
        text_y = button_y + (button_height - quit_text.get_height()) // 2
        self.screen.blit(quit_text, (text_x, text_y))
        return (button_x, button_y, button_width, button_height)

    def handle_quit_button(self, events, quit_button_rect):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        button_x, button_y, button_width, button_height = quit_button_rect

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if (button_x < mouse_x < button_x + button_width and
                        button_y < mouse_y < button_y + button_height):
                        self.run = False
                        break

    def run_game(self):
        quit_button_rect = None
        while self.run:
            self.clock.tick(self.FPS)
            events = self.handle_events()
            self.draw_bg()
            self.draw_ui()
            if not self.game_over:
                self.handle_countdown()
            if self.intro_count <= 0 and not self.round_over and not self.game_over:
                self.local_fighter.move(
                    self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 
                    self.screen, self.remote_fighter, 
                    self.round_over, events
                )
            self.update_fighters()
            if not self.game_over:
                self.handle_network()
            self.draw_fighters()
            self.handle_round_logic()
            if self.game_over:
                quit_button_rect = self.draw_game_result()
                if quit_button_rect:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    button_x, button_y, button_width, button_height = quit_button_rect

                    for event in events:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:
                                if (button_x < mouse_x < button_x + button_width and
                                    button_y < mouse_y < button_y + button_height):
                                    self.run = False
                                    break
            self.check_game_over()
            pygame.display.update()
            
    def cleanup(self):
        if hasattr(self, 'sock'):
            self.sock.close()
        pygame.quit()

    def handle_countdown(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_count_update >= 1000:
            self.last_count_update = current_time
            self.intro_count -= 1

def main():
    game = None
    try:
        game = GameClient()
        game.run_game()
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        if game:
            game.cleanup()

if __name__ == "__main__":
    main()
```
5. fighter.py
```python
import pygame
import sys

class Fighter:
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound, graunt_sound=None):
        self.player = player
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.flip = flip
        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        self.action = 0
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 80, 180))
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.max_attack_cooldown = 50 
        self.last_attack_time = 0 
        self.attack_sound = sound
        self.graunt_sound = graunt_sound
        self.hit = False
        self.health = 100
        self.alive = True

    def load_images(self, sprite_sheet, animation_steps):
        animation_list = []
        for y, animation in enumerate(animation_steps):
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size)
                temp_img_list.append(pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale)))
            animation_list.append(temp_img_list)
        return animation_list

    def move(self, screen_width, screen_height, surface, target, round_over, events):
        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0
        key = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()
        if not self.attacking and self.alive and not round_over:
            dx, self.running = self._handle_movement(key, SPEED)
            dy = self._handle_jumping(key, dy)
            if current_time - self.last_attack_time > self.max_attack_cooldown:
                self._handle_attacks(events, target)
        self.vel_y += GRAVITY
        dy += self.vel_y
        dx = self._constrain_horizontal_movement(screen_width, dx)
        dy = self._constrain_vertical_movement(screen_height, dy)
        self._update_facing_direction(target)
        self.rect.x += dx
        self.rect.y += dy

    def _handle_movement(self, key, SPEED):
        dx = 0
        running = False
        if self.player == 1:
            if key[pygame.K_a]:
                dx = -SPEED
                running = True
            if key[pygame.K_d]:
                dx = SPEED
                running = True
        elif self.player == 2:
            if key[pygame.K_LEFT]:
                dx = -SPEED
                running = True
            if key[pygame.K_RIGHT]:
                dx = SPEED
                running = True
        return dx, running

    def _handle_jumping(self, key, dy):
        if self.player == 1 and key[pygame.K_w] and not self.jump:
            self.vel_y = -30
            self.jump = True
        elif self.player == 2 and key[pygame.K_UP] and not self.jump:
            self.vel_y = -30
            self.jump = True
        return dy

    def _handle_attacks(self, events, target):
        for event in events:
            if event.type == pygame.KEYDOWN:
                current_time = pygame.time.get_ticks()
                if current_time - self.last_attack_time > self.max_attack_cooldown:
                    if self.player == 1:
                        if event.key == pygame.K_k:
                            self.attack_type = 1
                            self.attack(target)
                            self.last_attack_time = current_time
                        elif event.key == pygame.K_l:
                            self.attack_type = 2
                            self.attack(target)
                            self.last_attack_time = current_time
                    elif self.player == 2:
                        if event.key == pygame.K_z:
                            self.attack_type = 1
                            self.attack(target)
                            self.last_attack_time = current_time
                        elif event.key == pygame.K_x:
                            self.attack_type = 2
                            self.attack(target)
                            self.last_attack_time = current_time

    def _constrain_horizontal_movement(self, screen_width, dx):
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        return dx

    def _constrain_vertical_movement(self, screen_height, dy):
        if self.rect.bottom + dy > screen_height - 110:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 110 - self.rect.bottom
        return dy

    def _update_facing_direction(self, target):
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

    def update(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(6)
        elif self.hit:
            self.update_action(5)
        elif self.attacking:
            if self.attack_type == 1:
                self.update_action(3)
            elif self.attack_type == 2:
                self.update_action(4)
        elif self.jump:
            self.update_action(2)
        elif self.running:
            self.update_action(1)
        else:
            self.update_action(0)

        animation_cooldown = 50
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        if self.frame_index >= len(self.animation_list[self.action]):
            if not self.alive:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_cooldown = 20
                if self.action == 5:
                    self.hit = False
                    self.attacking = False
                    self.attack_cooldown = 20

    def attack(self, target):
        self.attacking = True
        self.attack_sound.play()
        if self.graunt_sound:
            self.graunt_sound.play()
        attacking_rect = pygame.Rect(
            self.rect.centerx - (2 * self.rect.width * self.flip),
            self.rect.y, 2 * self.rect.width, self.rect.height)
        
        if attacking_rect.colliderect(target.rect):
            target.hit = True
            if self.attack_type == 1: 
                damage = 10
            elif self.attack_type == 2: 
                damage = 20
            else:
                damage = 0
            target.health = max(0, target.health - damage)

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale),
                           self.rect.y - (self.offset[1] * self.image_scale)))

class RemoteFighter:
    def __init__(self, data, sprite_sheet, image_scale, offset):
        self.image_scale = image_scale
        self.offset = offset
        self.action = 0
        self.frame_index = 0
        self.sprite_sheet = sprite_sheet
        self.image = None
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect(data.get("x", 0), data.get("y", 0), 80, 180)
        self.health = data.get("health", 100)
        self.flip = data.get("flip", False)

    def update_data(self, data):
        self.rect.x = data.get("x", self.rect.x)
        self.rect.y = data.get("y", self.rect.y)
        self.health = data.get("health", self.health)
        self.action = data.get("action", self.action)
        self.flip = data.get("flip", self.flip)

    def load_images(self, sprite_sheet, animation_steps):
        animation_list = []
        size = sprite_sheet.get_height() // len(animation_steps)
        for y, animation in enumerate(animation_steps):
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(x * size, y * size, size, size)
                temp_img_list.append(pygame.transform.scale(temp_img, (size * self.image_scale, size * self.image_scale)))
            animation_list.append(temp_img_list)
        return animation_list
    
    def update(self, animation_list):
        animation_cooldown = 50
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index = (self.frame_index + 1) % len(animation_list[self.action])
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface, animation_list):
        img = animation_list[self.action][self.frame_index % len(animation_list[self.action])]
        img = pygame.transform.flip(img, self.flip, False)
        surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale),
                           self.rect.y - (self.offset[1] * self.image_scale)))

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Fighter Game")
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
```