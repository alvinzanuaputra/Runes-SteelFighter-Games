from time import sleep
import pygame
import json
import socket

class InputBox:
    def __init__(self, x, y, w, h, font, text='', is_password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = pygame.Color('gray')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.text = text
        self.font = font
        self.is_password = is_password
        self.txt_surface = self.font.render(self.display_text(), True, pygame.Color('white'))
        self.active = False

    def display_text(self):
        return '*' * len(self.text) if self.is_password else self.text

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return self.text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.font.render(self.display_text(), True, pygame.Color('white'))
        return None

    def draw(self, screen):
        self.txt_surface = self.font.render(self.display_text(), True, pygame.Color('white'))
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)


class LoginPage:
    def __init__(self, game):
        self.game = game
        self.x_offset = (self.game.SCREEN_WIDTH - 300) // 2
        self.username_box = InputBox(self.x_offset, 240, 300, 40, game.score_font)
        self.password_box = InputBox(self.x_offset, 320, 300, 40, game.score_font, is_password=True)
        self.login_button = pygame.Rect(self.x_offset, 375, 300, 40)
        self.register_button = pygame.Rect(self.x_offset, 420, 300, 40)
        self.login_message = ""
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
        self.username_box.rect.x = self.x_offset
        self.password_box.rect.x = self.x_offset
        self.login_button.x = self.x_offset
        self.register_button.x = self.x_offset
        
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        self.is_fullscreen = not self.is_fullscreen
        
        if self.is_fullscreen:
            self.handle_screen_resize(self.game.FULLSCREEN_WIDTH, self.game.FULLSCREEN_HEIGHT)
        else:
            self.handle_screen_resize(self.game.WINDOW_WIDTH, self.game.WINDOW_HEIGHT)
        
    def draw_bg(self):
        """Draw background"""
        scaled_bg = pygame.transform.scale(self.game.bg_image, (self.game.SCREEN_WIDTH, self.game.SCREEN_HEIGHT))
        self.game.screen.blit(scaled_bg, (0, 0))

    def render(self, events):
        self.draw_bg()
        text_surface = self.game.count_font.render("Login", True, self.game.WHITE)
        text_rect = text_surface.get_rect(center=(self.game.SCREEN_WIDTH // 2, 100)) 
        self.game.screen.blit(text_surface, text_rect)

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
            
            self.username_box.handle_event(event)
            self.password_box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.login_button.collidepoint(event.pos):
                    self.send_login()
                elif self.register_button.collidepoint(event.pos):
                    self.game.current_page = "register"

        # Username box
        username_y = 200
        self.game.draw_text("Username:", self.game.score_font, self.game.WHITE, self.x_offset, username_y + 5)
        self.username_box.draw(self.game.screen)

        # Password box
        password_y = 280
        self.game.draw_text("Password:", self.game.score_font, self.game.WHITE, self.x_offset, password_y + 5)
        self.password_box.draw(self.game.screen)

        pygame.draw.rect(self.game.screen, (254, 182, 120), self.login_button)
        text_surface = self.game.score_font.render("Masuk", True, self.game.WHITE)
        text_rect = text_surface.get_rect(center=self.login_button.center)
        self.game.screen.blit(text_surface, text_rect)

        # Draw message if any
        if self.login_message:
            self.game.draw_text(self.login_message, self.game.score_font, self.game.WHITE, self.x_offset, 475)
            
        pygame.draw.rect(self.game.screen, (254, 182, 120), self.register_button)
        text_surface = self.game.score_font.render("Register", True, self.game.WHITE)
        text_rect = text_surface.get_rect(center=self.register_button.center)
        self.game.screen.blit(text_surface, text_rect)

        pygame.display.update()

    def send_login(self):
        username = self.username_box.text.strip()
        password = self.password_box.text.strip()

        if not username or not password:
            self.login_message = "Isi semua field!"
            return

        try:
            data = json.dumps({
                "username": username,
                "password": password
            })
            
            request = f"POST /login HTTP/1.1\r\n"
            request += "Host: localhost\r\n"
            request += "Content-Type: application/json\r\n"
            request += f"Content-Length: {len(data)}\r\n"
            request += "Connection: close\r\n"
            request += "\r\n"
            request += data
            
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('localhost', 8888))
            s.sendall(request.encode())

            # 🟡 Tunggu semua response
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
                self.game.player_id = response_data.get("player_id")
                self.game.token = response_data.get("token")
                self.game.current_page = "home"
            else:
                self.game.current_page = "login"
                self.login_message = response_data.get("message")
        except Exception as e:
            self.login_message = f"{e}"
