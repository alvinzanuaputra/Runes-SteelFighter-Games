import pygame
import json
import socket
import threading

class HomePage:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 40)
        self.battle_button_rect = pygame.Rect(200, 500, 200, 50)
        self.logout_button = pygame.Rect(200, 560, 200, 50)
        self.logout_message = None
        self.finding_match = False
        self.match_start_time = None
        self.timeout_limit = 5 * 60 * 1000 
        self.is_fullscreen = False
        self.hero_frame_index = 0
        self.hero_animation_timer = 0
        self.hero_animation_cooldown = 100  # Percepat animasi
        self.hero_animation_type = 'warrior' if game.p1 else 'wizard'
        
        # Muat sprite idle
        self.warrior_idle_sheet = pygame.image.load("assets/images/warrior/Sprites/Idle.png").convert_alpha()
        self.wizard_idle_sheet = pygame.image.load("assets/images/wizard/Sprites/Idle.png").convert_alpha()
        
        # Tentukan jumlah frame idle
        self.warrior_idle_frames = 10  # Sesuaikan dengan jumlah frame di Idle.png warrior
        self.wizard_idle_frames = 8   # Sesuaikan dengan jumlah frame di Idle.png wizard

        # Inisialisasi font Turok
        try:
            self.hero_font = pygame.font.Font("assets/fonts/turok.ttf", 48)  # Perbesar ukuran font
            print("Font Turok berhasil dimuat")
        except FileNotFoundError:
            print("Font Turok tidak ditemukan, menggunakan font default")
            self.hero_font = pygame.font.SysFont(None, 48)

    def draw_bg(self):
        scaled_bg = pygame.transform.scale(self.game.bg_image, (self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT))
        self.game.screen.blit(scaled_bg, (0, 0))
        
    def draw_button(self, text, rect):
        pygame.draw.rect(self.game.screen, (254, 182, 120), rect)
        button_text = self.font.render(text, True, self.game.WHITE)
        text_rect = button_text.get_rect(center=rect.center)
        self.game.screen.blit(button_text, text_rect)
   
    def draw_stats(self):
        # Load gambar border
        border = pygame.image.load("assets/images/background/border_stats.png").convert_alpha()
        original_width, original_height = border.get_size()
        scale_factor = 0.66
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        border = pygame.transform.scale(border, (new_width, new_height))

        # Posisi border (misalnya tengah layar)
        border_x = (self.game.screen.get_width() - new_width) // 2 + 180
        border_y = 100  # bisa disesuaikan

        # Tampilkan border
        self.game.screen.blit(border, (border_x, border_y))

        # Padding teks di dalam border
        padding_x = 80
        padding_y = 100
        line_spacing = 40

        # Daftar teks statistik
        stats_text = [
            f"{self.game.player.get('nickname', 'Unknown User')}",
            f"Level: {self.game.player.get('level', 0)}",
            f"Exp: {self.game.player.get('exp', 0)}",
            f"HP: {self.game.player.get('hp', 0)}",
            f"Attack: {self.game.player.get('attack', 0)}",
            f"Armor: {self.game.player.get('armor', 0)}",
            f"Total Match: {self.game.player.get('jumlah_match', 0)}",
            f"Winrate: {self.game.player.get('winrate', 0)}%",
        ]

        # Render dan tampilkan semua teks secara vertikal
        for i, text in enumerate(stats_text):
            rendered_text = self.font.render(text, True, (252, 231, 138))
            self.game.screen.blit(rendered_text, (
                border_x + padding_x,
                border_y + padding_y + i * line_spacing
            ))

        pygame.display.update()

    def fetch_data(self):
        try:
            request = f"GET /user/{self.game.player_id} HTTP/1.1"
            request += "Host: localhost\r\n"
            request += "\r\n"
            
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('localhost', 8888))
            print(f"Mengirim permintaan: {request}")
            s.sendall(request.encode())
            response = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response += chunk

            # Decode response
            decoded = response.decode()

            headers, _, body = decoded.partition("\r\n\r\n")
            print(f"Response Headers:\n{headers}\n")
            return body 
        except Exception as e:
            self.login_message = f"Gagal koneksi: {e}"
    
    def draw_hero(self):
        """Draw animated hero sprite from warrior or wizard idle sheet"""
        # Pilih sheet dan data berdasarkan tipe hero
        if self.hero_animation_type == 'warrior':
            hero_sheet = self.warrior_idle_sheet
            hero_animation_steps = self.warrior_idle_frames
            hero_scale = self.game.WARRIOR_SCALE * 1.5  # Perbesar sedikit
            hero_offset = self.game.WARRIOR_OFFSET
            hero_name = "Warrior"
            
            # Posisi khusus untuk warrior
            x_offset = -100  # Sesuaikan horizontal
            y_offset = -80   # Sesuaikan vertikal
        else:
            hero_sheet = self.wizard_idle_sheet
            hero_animation_steps = self.wizard_idle_frames
            hero_scale = self.game.WIZARD_SCALE * 1.6  # Perbesar sedikit
            hero_offset = self.game.WIZARD_OFFSET
            hero_name = "Wizard"
            
            # Posisi khusus untuk wizard
            x_offset = -170  # Sesuaikan horizontal
            y_offset = -220  # Sesuaikan vertikal

        # Hitung ukuran sprite
        sprite_width = hero_sheet.get_width() // hero_animation_steps
        sprite_height = hero_sheet.get_height()

        # Perbarui frame animasi
        current_time = pygame.time.get_ticks()
        if current_time - self.hero_animation_timer > self.hero_animation_cooldown:
            self.hero_frame_index = (self.hero_frame_index + 1) % hero_animation_steps
            self.hero_animation_timer = current_time

        # Ambil frame saat ini
        frame_x = self.hero_frame_index * sprite_width
        frame_rect = pygame.Rect(frame_x, 0, sprite_width, sprite_height)
        frame = hero_sheet.subsurface(frame_rect)

        # Scale frame
        scaled_width = int(sprite_width * hero_scale)
        scaled_height = int(sprite_height * hero_scale)
        scaled_frame = pygame.transform.scale(frame, (scaled_width, scaled_height))

        # Posisikan frame - geser ke kiri
        x = x_offset - hero_offset[0]
        y = y_offset - hero_offset[1]
        self.game.screen.blit(scaled_frame, (x, y))

        # Render teks nama karakter
        hero_text = self.hero_font.render(hero_name, True, (255, 255, 255))  # Warna putih
        
        # Posisikan teks di tengah atas sprite
        text_x = 240
        text_y = 120
        # Gambar teks
        self.game.screen.blit(hero_text, (text_x, text_y))

    def handle_screen_resize(self, new_width, new_height):
        """Handle screen resize and reposition game elements"""
        self.game.SCREEN_WIDTH = new_width
        self.game.SCREEN_HEIGHT = new_height
        
        # Update screen surface
        if hasattr(self, 'is_fullscreen') and self.is_fullscreen:
            self.game.screen = pygame.display.set_mode((self.game.FULLSCREEN_WIDTH, self.game.FULLSCREEN_HEIGHT), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
        else:
            self.game.screen = pygame.display.set_mode((self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT), pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF)
        
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        self.is_fullscreen = not self.is_fullscreen
        
        if self.is_fullscreen:
            self.handle_screen_resize(self.game.FULLSCREEN_WIDTH, self.game.FULLSCREEN_HEIGHT)
        else:
            self.handle_screen_resize(self.game.WINDOW_WIDTH, self.game.WINDOW_HEIGHT)
        
    def toggle_hero(self, direction='next'):
        """Toggle between warrior and wizard hero"""
        if direction == 'next':
            self.hero_animation_type = 'wizard' if self.hero_animation_type == 'warrior' else 'warrior'
        elif direction == 'prev':
            self.hero_animation_type = 'warrior' if self.hero_animation_type == 'wizard' else 'wizard'
        
        # Reset animasi
        self.hero_frame_index = 0
        self.hero_animation_timer = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                print("Masuk ke Battle Page")
                self.game.switch_to("battle")
            elif event.key == pygame.K_LEFT:  # Tombol panah kiri untuk ganti karakter
                self.toggle_hero('prev')
            elif event.key == pygame.K_RIGHT:  # Tombol panah kanan untuk ganti karakter
                self.toggle_hero('next')
            elif event.key == pygame.K_F11:
                self.toggle_fullscreen()
            elif event.key == pygame.K_RETURN and (
                pygame.key.get_pressed()[pygame.K_LALT] or 
                pygame.key.get_pressed()[pygame.K_RALT]
            ):
                self.toggle_fullscreen()
        elif event.type == pygame.VIDEORESIZE:
            if not hasattr(self, 'is_fullscreen') or not self.is_fullscreen:
                self.handle_screen_resize(event.w, event.h)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: 
                if self.battle_button_rect.collidepoint(event.pos):
                    print("Battle button clicked")
                    print("Mencari lawan...")
                    self.finding_match = True
                    self.match_start_time = pygame.time.get_ticks()
                    
                    threading.Thread(target=self.search_battle, daemon=True).start()
                elif self.logout_button.collidepoint(event.pos):
                    self.handle_logout()
                    
    def search_battle(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost', 8888))
        
        request = "POST /search_battle HTTP/1.1\r\n"
        request += "Host: localhost\r\n"
        request += "Content-Type: application/json\r\n"
        request += "Content-Length: 0\r\n"
        request += "\r\n"
        
        if self.game.token is None or self.game.player_id is None:
            print("Token atau Player ID tidak ditemukan.")
            return
        
        data = {
            "token": self.game.token,
            "player_id": self.game.player_id
        }
        request += json.dumps(data)
        
        s.sendall(request.encode())
        try:
            response = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response += chunk

            response = response.decode()
            # ambil body dari HTTP response
            response = response.split("\r\n\r\n", 1)[1] if "\r\n\r\n" in response else response
            # Parse JSON dari body
            response_data = json.loads(response)
            
            if response_data.get("status") == "ok":
                self.game.room_id = response_data.get("room_id")
                self.game.enemy_token = response_data.get("enemy_token")
                self.game.p1 = response_data.get("p1")
                self.game.current_page = "battle"
                self.finding_match = False
            else:
                print("Tidak ada lawan yang ditemukan.")
                self.finding_match = False
                self.match_start_time = None
                self.game.current_page = "home"
                self.data = "{}"
                # Reset data pemain
                self.data = self.fetch_data()
            
        except Exception as e:
            print(f"Error: {e}")

    def handle_logout(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('localhost', 8888))
        
        request = "POST /logout HTTP/1.1\r\n"
        request += "Host: localhost\r\n"
        request += "Content-Type: application/json\r\n"
        request += "Content-Length: 0\r\n"
        request += "\r\n"
        
        data = {
            "token": self.game.token
        }
        request += json.dumps(data)
        
        s.sendall(request.encode())
        response = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            response += chunk
        
        response = response.decode()
        # ambil body dari HTTP response
        response = response.split("\r\n\r\n", 1)[1] if "\r\n\r\n" in response else response
        # Parse JSON dari body
        response_data = json.loads(response)
        
        if response_data.get("status") == "ok":
            s.close()
            self.game.token = None
            self.game.player_id = None
            self.game.room_id = None
            self.game.p1 = None
            self.game.enemy_token = None
            self.game.player = None
            self.game.current_page = "login"
        else:
            print("Gagal logout.")
        
    def render(self, events):
        if self.game.player is None:
            result = self.fetch_data()
            if result:
                data = json.loads(result)
                if data.get("status") == "ok":
                    self.game.player = data.get("data", "{}")
            else:
                print("Gagal mengambil data pemain.")
                self.logout_message = "Gagal memuat data. Coba lagi nanti."
                self.game.player = "{}"

        self.draw_bg()
        self.draw_button("Battle", self.battle_button_rect)
        self.draw_button("Logout", self.logout_button)
        self.draw_hero()
        self.draw_stats()
        
        # draw logout_message if any
        if self.logout_message:
            logout_text = self.font.render(self.logout_message, True, (255, 100, 100))
            self.game.screen.blit(logout_text, (200, 610))
        
        # Tambahkan petunjuk untuk mengganti hero
        hint_font = pygame.font.SysFont(None, 25)
        hint_text = hint_font.render("Left/right arrows to see hero list", True, self.game.WHITE)
        self.game.screen.blit(hint_text, (10, self.game.SCREEN_HEIGHT - 40))
        
        for event in events:
            self.handle_event(event)

        # Timer Pencarian Lawan
        if self.finding_match:
            now = pygame.time.get_ticks()
            elapsed = now - self.match_start_time
            remaining = max(0, self.timeout_limit - elapsed)

            minutes = remaining // 60000
            seconds = (remaining % 60000) // 1000
            timer_text = self.font.render(f"Mencari lawan... {minutes:02}:{seconds:02}", True, (255, 255, 255))
            self.game.screen.blit(timer_text, (200, 460))

            # Jika timeout
            if elapsed >= self.timeout_limit:
                self.finding_match = False
                timeout_msg = self.font.render("Pencarian gagal: Waktu habis.", True, (255, 100, 100))
                self.game.screen.blit(timeout_msg, (200, 430))
                
        pygame.display.update()
        