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