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
           
    def draw_bg(self):
        """Draw background"""
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
        
        # Ambil ukuran asli
        original_width, original_height = border.get_size()

        # Hitung ukuran baru (90%)
        scale_factor = 0.9
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)

        # Skala ulang gambar border
        border = pygame.transform.scale(border, (new_width, new_height))

        # Posisi border (misalnya tengah layar)
        border_x = (self.game.screen.get_width() - new_width) // 2 + 200
        border_y = 100  # bisa disesuaikan

        # Tampilkan border
        self.game.screen.blit(border, (border_x, border_y))

        # Padding teks di dalam border
        padding_x = 40
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
        """Draw cropped hero sprite from warrior_sheet"""
        # draw hero sprite
        self.warrior_background = pygame.image.load("assets/images/warrior/Sprites/warrior_backgorund.png").convert_alpha()
        self.game.screen.blit(self.warrior_background, (150, 80))
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                print("Masuk ke Battle Page")
                self.game.switch_to("battle")
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
        