import pygame
import random
from fighter import Fighter, RemoteFighter
import socket
import json

class BattlePage:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 36)
        self.play = False
        self.score = [0, 0]
        self.enemy_connected = False
        self.intro_count = 0
        self.last_count_update = None
        self.round_over = False
        self.round_over_time = 0
        self.remote_animation = None
        self.ground_y = 0
        self.fighter_1_x = 0
        self.fighter_2_x = 0
        self.is_win = None
        self.has_updated_data = None
          
    def init_fighters(self):
        """Initialize fighter objects"""
        self._calculate_fighter_positions()
        
        if self.game.p1:
            self.local_fighter = Fighter(
                1, self.fighter_1_x, self.ground_y, False, 
                self.game.WARRIOR_DATA, self.game.warrior_sheet, 
                self.game.WARRIOR_ANIMATION_STEPS, self.game.sword_fx
            )
            self.remote_fighter = RemoteFighter(
                self.fighter_2_x, self.ground_y, True, 
                self.game.wizard_sheet, self.game.WIZARD_SCALE, self.game.WIZARD_OFFSET
            )
            self.remote_animation = self.remote_fighter.load_images(
                self.game.wizard_sheet, self.game.WIZARD_ANIMATION_STEPS
            )
        else:
            self.local_fighter = Fighter(
                2, self.fighter_2_x, self.ground_y, True, 
                self.game.WIZARD_DATA, self.game.wizard_sheet, 
                self.game.WIZARD_ANIMATION_STEPS, self.game.magic_fx
            )
            self.remote_fighter = RemoteFighter(
                self.fighter_1_x, self.ground_y, False, 
                self.game.warrior_sheet, self.game.WARRIOR_SCALE, self.game.WARRIOR_OFFSET
            )
            self.remote_animation = self.remote_fighter.load_images(
                self.game.warrior_sheet, self.game.WARRIOR_ANIMATION_STEPS
            )
      
    def _calculate_fighter_positions(self):
        """Calculate fighter positions based on screen size"""
        self.fighter_1_x = int(self.game.SCREEN_WIDTH * 0.2)
        self.fighter_2_x = int(self.game.SCREEN_WIDTH * 0.7)
        self.ground_y = int(self.game.SCREEN_HEIGHT * 0.8)
        
    def draw_text(self, text, font, text_col, x, y):
        """Draw text on screen"""
        img = font.render(text, True, text_col)
        self.game.screen.blit(img, (x, y))
        
    def draw_bg(self):
        """Draw background"""
        scaled_bg = pygame.transform.scale(self.game.bg_image, (self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT))
        self.game.screen.blit(scaled_bg, (0, 0))
        
    def draw_health_bar(self, health, x, y, width=400):
        """Draw health bar"""
        ratio = max(0, min(health / 100, 1))  
        pygame.draw.rect(self.game.screen, self.game.WHITE, (x - 2, y - 2, width + 4, 34))  
        pygame.draw.rect(self.game.screen, self.game.RED, (x, y, width, 30)) 
        pygame.draw.rect(self.game.screen, self.game.YELLOW, (x, y, width * ratio, 30))
      
    def handle_screen_resize(self, new_width, new_height):
        """Handle screen resize and reposition game elements"""
        self.game.SCREEN_WIDTH = new_width
        self.game.SCREEN_HEIGHT = new_height
        
        # Update screen surface
        if self.is_fullscreen:
            self.game.screen = pygame.display.set_mode((self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.game.screen = pygame.display.set_mode((self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT), pygame.RESIZABLE)
        
        # Recalculate fighter positions
        self._calculate_fighter_positions()
        
        # Reposition local fighter
        if self.game.p1 == 0:
            self.local_fighter.rect.x = self.fighter_1_x
        else:
            self.local_fighter.rect.x = self.fighter_2_x
        self.local_fighter.rect.y = self.ground_y
        
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        self.is_fullscreen = not self.is_fullscreen
        
        if self.is_fullscreen:
            self.handle_screen_resize(self.FULLSCREEN_WIDTH, self.FULLSCREEN_HEIGHT)
        else:
            self.handle_screen_resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
            
    def handle_events(self):
        """Handle pygame events"""
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.game.run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.run = False
                elif event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_RETURN and (
                    pygame.key.get_pressed()[pygame.K_LALT] or 
                    pygame.key.get_pressed()[pygame.K_RALT]
                ):
                    self.toggle_fullscreen()
            elif event.type == pygame.VIDEORESIZE:
                if not self.is_fullscreen:
                    self.handle_screen_resize(event.w, event.h)
            elif event.type == pygame.VIDEOEXPOSE:
                pygame.display.flip()
        return events
    
    def handle_countdown(self):
        """Handle countdown logic"""
        if self.intro_count > 0:
            # Gambar angka countdown
            countdown_x = int(self.game.SCREEN_WIDTH / 2 - 40)
            countdown_y = int(self.game.SCREEN_HEIGHT / 3)
            self.game.draw_text(str(self.intro_count), self.game.count_font, self.game.RED, countdown_x, countdown_y)

            # Kurangi angka setiap 1000 ms (1 detik)
            current_time = pygame.time.get_ticks()
            if self.last_count_update is None:
                self.last_count_update = current_time
            elif (current_time - self.last_count_update) >= 1000:
                self.intro_count -= 1
                self.last_count_update = current_time
              
    def handle_network(self):
        """Handle network communication"""
        data = json.dumps({
            "x": self.local_fighter.rect.x,
            "y": self.local_fighter.rect.y,
            "health": self.local_fighter.health,
            "action": self.local_fighter.action,
            "flip": self.local_fighter.flip,
            "attack_type": self.local_fighter.attack_type,
            "armor": 1 * self.game.player.get("level", 1),
            "damage": 10 * self.game.player.get("level", 1),
            "token": self.game.token,
            "enemy_token": self.game.enemy_token,
            "room_id": self.game.room_id,
        })
        
        request = f"POST /battle HTTP/1.1\r\n"
        request += "Host: localhost\r\n"
        request += "Content-Type: application/json\r\n"
        request += f"Content-Length: {len(data)}\r\n"
        request += "\r\n"
        request += data

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('localhost', 8888))
            s.sendall(request.encode())

            # Terima semua data sampai server tutup koneksi
            response = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response += chunk

            received = response.decode()

            if received:
                headers, _, body = received.partition("\r\n\r\n")
                all_data = json.loads(body)

                if "self" in all_data:
                    self.local_fighter.health = all_data["self"].get("health", self.local_fighter.health)
                    self.local_fighter.rect.x = all_data["self"].get("x", self.local_fighter.rect.x)
                    self.local_fighter.rect.y = all_data["self"].get("y", self.local_fighter.rect.y)
                    self.local_fighter.action = all_data["self"].get("action", self.local_fighter.action)
                    self.local_fighter.flip = all_data["self"].get("flip", self.local_fighter.flip)

                if all_data.get("enemy"):
                    self.enemy_connected = True
                    self.remote_fighter.update_data(all_data["enemy"])
                else:
                    self.enemy_connected = False

        except Exception as e:
            print(f"[Network Error] {e}")
        finally:
            s.close()

    def handle_round_logic(self):
        """Handle round end logic"""
        self.player_num = 0 if self.game.p1 else 1

        if not self.round_over:
            if not self.local_fighter.alive:
                self.score[1 - self.player_num] += 1
                self.round_over = True
                self.round_over_time = pygame.time.get_ticks()
                
                self.is_win = False
            elif self.remote_fighter.health <= 0:
                self.score[self.player_num] += 1
                self.round_over = True
                self.round_over_time = pygame.time.get_ticks()
                
                self.is_win = True
        else:
            # Tampilkan teks kemenangan
            result_text = "Victory" if self.is_win else "Defeat"
            font = pygame.font.SysFont("arial", 60)
            text_surface = font.render(result_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.game.SCREEN_WIDTH // 2, self.game.SCREEN_HEIGHT // 4))
            self.game.screen.blit(text_surface, text_rect)
            
            if not self.has_updated_data:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect(('localhost', 8888))
                    data = None
                    request = ""
                    
                    if self.is_win:
                        request = f"PUT /update_match HTTP/1.1\r\n"
                        data = json.dumps({
                            "player_id": self.game.player_id,
                            "token": self.game.token,
                            "is_win": True,
                            "room_id": self.game.room_id,
                        })
                    else:
                        request = f"PUT /update_match HTTP/1.1\r\n"
                        data = json.dumps({
                            "player_id": self.game.player_id,
                            "token": self.game.token,
                            "enemy_token": self.game.enemy_token,
                            "is_win": False,
                            "room_id": self.game.room_id
                        })
                    request += "Host: localhost\r\n"
                    request += "Content-Type: application/json\r\n"
                    request += f"Content-Length: {len(data)}\r\n"
                    request += "\r\n"
                    request += data

                    s.sendall(request.encode())
                    response = b""
                    while True:
                        chunk = s.recv(4096)
                        if not chunk:
                            break
                        response += chunk
                        
                    response = response.decode()
                    self.has_updated_data = True
                    s.close()
                except Exception as e:
                    print(f"[Network Error] {e}")

            # Tunggu cooldown untuk reset/keluar
            if pygame.time.get_ticks() - self.round_over_time > self.game.ROUND_OVER_COOLDOWN:
                self.round_over = False
                self.game.player = None
                self.play = False
                self.game.current_page = "home"
             
    def draw_ui(self):
        """Draw user interface elements"""
        self.player_num = 0 if self.game.p1 else 1
        enemy_num = 1 - self.player_num

        health_bar_width = int(self.game.SCREEN_WIDTH * 0.4)
        margin = int(self.game.SCREEN_WIDTH * 0.02)

        # Player's health bar on the left
        self.draw_health_bar(self.local_fighter.health, margin, 20, health_bar_width)
        self.game.draw_text(
            f"You: {self.score[self.player_num]}",
            self.game.score_font, self.game.RED, margin, 60
        )

        # Enemy's health bar on the right
        if self.enemy_connected:
            self.draw_health_bar(
                self.remote_fighter.health,
                self.game.SCREEN_WIDTH - health_bar_width - margin, 20,
                health_bar_width
            )
            self.game.draw_text(
                f"Enemy: {self.score[enemy_num]}",
                self.game.score_font, self.game.RED,
                self.game.SCREEN_WIDTH - health_bar_width - margin, 60
            )       
            
    def update_fighters(self):
        """Update fighter states"""
        self.local_fighter.update()
        
        if self.enemy_connected:
            self.remote_fighter.update(self.remote_animation)
            
    def draw_fighters(self):
        """Draw fighters"""
        self.local_fighter.draw(self.game.screen)
        
        if self.enemy_connected:
            self.remote_fighter.draw(self.game.screen, self.remote_animation)
        
    def on_enter(self):
        self.init_fighters()
        self.intro_count = 3
        self.last_count_update = pygame.time.get_ticks()
        self.round_over = False
        self.round_over_time = 0
        self.is_win = None
        self.has_updated_data = False
        self.score = [0, 0]
        
    def render(self, events):
        if not self.play:
            self.on_enter()
            self.play = True

        self.draw_bg()
        self.draw_ui()
        self.handle_countdown()

        if self.intro_count <= 0:
            self.handle_fighter_movement(events)
            
        self.update_fighters()
        self.handle_network()
        self.draw_fighters()
        self.handle_round_logic()
        pygame.display.update()

    def handle_fighter_movement(self, events):
        self.local_fighter.move(
            self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT, 
            self.game.screen, self.remote_fighter, 
            self.round_over, events
        )

