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

    def draw_bg(self):
        scaled_bg = pygame.transform.scale(self.game.bg_image, (self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT))
        self.game.screen.blit(scaled_bg, (0, 0))
        
    def handle_events(self, events):
        for event in events:
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
            s.sendall(request.encode())

            response = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response += chunk

            response = response.decode()
            response = response.split("\r\n\r\n", 1)[1] if "\r\n\r\n" in response else response
            response_data = json.loads(response)

            if response_data.get("status") == "ok":
                self.register_message = "Registrasi berhasil!"
            else:
                self.register_message = response_data.get("message")
        except Exception as e:
            self.register_message = f"{e}"
