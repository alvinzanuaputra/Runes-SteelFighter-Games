from time import sleep
import pygame
import json
import socket

from pages.login import InputBox

class RegisterPage:
    def __init__(self, game):
        self.game = game
        self.x_offset = (self.game.SCREEN_WIDTH - 300) // 2
        self.nickname_box = InputBox(self.x_offset, 200, 300, 40, game.score_font)
        self.username_box = InputBox(self.x_offset, 280, 300, 40, game.score_font)
        self.password_box = InputBox(self.x_offset, 360, 300, 40, game.score_font, is_password=True)
        self.register_button = pygame.Rect(self.x_offset, 420, 300, 40)
        self.login_button = pygame.Rect(self.x_offset, 470, 300, 40)
        self.register_message = ""
        self.is_fullscreen = False

    def handle_screen_resize(self, new_width, new_height):
        """Handle screen resize and reposition game elements"""
        self.game.SCREEN_WIDTH = new_width
        self.game.SCREEN_HEIGHT = new_height
        
        # Update screen surface
        if hasattr(self, 'is_fullscreen') and self.is_fullscreen:
            self.game.screen = pygame.display.set_mode((self.game.FULLSCREEN_WIDTH, self.game.FULLSCREEN_HEIGHT), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
        else:
            self.game.screen = pygame.display.set_mode((self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT), pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF)
        
        # Recalculate x_offset
        self.x_offset = (self.game.SCREEN_WIDTH - 300) // 2
        
        # Update input box positions
        self.nickname_box.rect.x = self.x_offset
        self.username_box.rect.x = self.x_offset
        self.password_box.rect.x = self.x_offset
        self.register_button.x = self.x_offset
        self.login_button.x = self.x_offset
        
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        self.is_fullscreen = not self.is_fullscreen
        
        if self.is_fullscreen:
            self.handle_screen_resize(self.game.FULLSCREEN_WIDTH, self.game.FULLSCREEN_HEIGHT)
        else:
            self.handle_screen_resize(self.game.WINDOW_WIDTH, self.game.WINDOW_HEIGHT)
        
    def draw_bg(self):
        scaled_bg = pygame.transform.scale(self.game.bg_image, (self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT))
        self.game.screen.blit(scaled_bg, (0, 0))
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_RETURN and (
                    pygame.key.get_pressed()[pygame.K_LALT] or 
                    pygame.key.get_pressed()[pygame.K_RALT]
                ):
                    self.toggle_fullscreen()
            elif event.type == pygame.VIDEORESIZE:
                if not hasattr(self, 'is_fullscreen') or not self.is_fullscreen:
                    self.handle_screen_resize(event.w, event.h)
            
            self.nickname_box.handle_event(event)
            self.username_box.handle_event(event)
            self.password_box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.register_button.collidepoint(event.pos):
                    self.send_register()
                elif self.login_button.collidepoint(event.pos):
                    self.game.current_page = "login"

    def render(self, events):
        self.draw_bg()
        text_surface = self.game.count_font.render("Register", True, self.game.WHITE)
        text_rect = text_surface.get_rect(center=(self.game.SCREEN_WIDTH // 2, 100)) 
        self.game.screen.blit(text_surface, text_rect)

        self.handle_events(events)

        # Nickname
        self.game.draw_text("Nickname:", self.game.score_font, self.game.WHITE, self.x_offset, 165)
        self.nickname_box.draw(self.game.screen)

        # Username
        self.game.draw_text("Username:", self.game.score_font, self.game.WHITE, self.x_offset, 245)
        self.username_box.draw(self.game.screen)

        # Password
        self.game.draw_text("Password:", self.game.score_font, self.game.WHITE, self.x_offset, 325)
        self.password_box.draw(self.game.screen)

        # Register Button
        pygame.draw.rect(self.game.screen, (254, 182, 120), self.register_button)
        text_surface = self.game.score_font.render("Daftar", True, self.game.WHITE)
        text_rect = text_surface.get_rect(center=self.register_button.center)
        self.game.screen.blit(text_surface, text_rect)

        # Message
        if self.register_message:
            self.game.draw_text(self.register_message, self.game.score_font, self.game.WHITE, self.x_offset, 520)

        pygame.draw.rect(self.game.screen, (254, 182, 120), self.login_button)
        text_surface = self.game.score_font.render("Login", True, self.game.WHITE)
        text_rect = text_surface.get_rect(center=self.login_button.center)
        self.game.screen.blit(text_surface, text_rect)

        pygame.display.update()

    def send_register(self):
        nickname = self.nickname_box.text.strip()
        username = self.username_box.text.strip()
        password = self.password_box.text.strip()

        if not nickname or not username or not password:
            self.register_message = "Isi semua field!"
            return

        try:
            data = json.dumps({
                "nickname": nickname,
                "username": username,
                "password": password
            })

            request = f"POST /register HTTP/1.1\r\n"
            request += "Host: localhost\r\n"
            request += "Content-Type: application/json\r\n"
            request += f"Content-Length: {len(data)}\r\n"
            request += "Connection: close\r\n\r\n"
            request += data

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('localhost', 8888))
            s.sendall(request.encode('utf-8'))

            response = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response += chunk

            response = response.decode('utf-8')
            response = response.split("\r\n\r\n", 1)[1] if "\r\n\r\n" in response else response
            response_data = json.loads(response)

            if response_data.get("status") == "ok":
                self.register_message = "Registrasi berhasil!"
            else:
                self.register_message = response_data.get("message")
        except Exception as e:
            self.register_message = f"{e}"
