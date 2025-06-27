import pygame
import os
from pygame import mixer
from pages.home import HomePage
from pages.battle import BattlePage
from pages.login import LoginPage
from pages.register import RegisterPage
import socket


class GameClient:
    """Main game client class for Runes & Steel Fighter"""
    
    def __init__(self):
        """Initialize game client"""
        self.token = ""
        self.enemy_token = ""
        self.player_id = 0
        self.room_id = ""
        self.p1 = None
        self.player = None
        
        self.current_page = "login"
        self.run = True
        self._init_pygame()
        self._init_display()
        self._init_game_constants()
        self._init_assets()
        self._init_fonts()
        
        self.pages = {
            "login": LoginPage(self),
            "register": RegisterPage(self),
            "home": HomePage(self),
            "battle": BattlePage(self),
        }

    def _init_pygame(self):
        """Initialize pygame modules"""
        mixer.init()
        pygame.init()
        pygame.font.init()
        self.info = pygame.display.Info()
        self.clock = pygame.time.Clock()
        
    def _init_display(self):
        """Initialize display settings"""
        self.WINDOW_WIDTH = 1280
        self.WINDOW_HEIGHT = 720
        self.FULLSCREEN_WIDTH = self.info.current_w
        self.FULLSCREEN_HEIGHT = self.info.current_h
        
        self.is_fullscreen = False
        self.SCREEN_WIDTH = self.WINDOW_WIDTH
        self.SCREEN_HEIGHT = self.WINDOW_HEIGHT
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption("Runes & Steel Fighter")
        
    def _init_game_constants(self):
        """Initialize game constants"""
        self.FPS = 60
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)
        self.WHITE = (255, 255, 255)
        
        self.intro_count = 3
        self.last_count_update = pygame.time.get_ticks()
        self.score = [0, 0]
        self.round_over = False
        self.ROUND_OVER_COOLDOWN = 2000
        
        # Fighter data
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
        
    def _init_assets(self):
        """Initialize game assets (images, sounds)"""
        # Music
        # pygame.mixer.music.load("assets/audio/music.mp3")
        # pygame.mixer.music.set_volume(0.5)
        # pygame.mixer.music.play(-1, 0.0, 5000)
        
        # Sound effects
        self.sword_fx = pygame.mixer.Sound("assets/audio/sword.wav")
        self.sword_fx.set_volume(0.5)
        self.magic_fx = pygame.mixer.Sound("assets/audio/magic.wav")
        self.magic_fx.set_volume(0.75)
        
        # Images
        try:
            self.bg_image = pygame.image.load("assets/images/background/background.jpg").convert_alpha()
            self.warrior_sheet = pygame.image.load("assets/images/warrior/Sprites/warrior.png").convert_alpha()
            self.wizard_sheet = pygame.image.load("assets/images/wizard/Sprites/wizard.png").convert_alpha()
            self.victory_img = pygame.image.load("assets/images/icons/victory.png").convert_alpha()
        except FileNotFoundError as e:
            print(f"Asset file not found: {e}")
        
    def _init_fonts(self):
        """Initialize fonts"""
        try:
            self.count_font = pygame.font.Font("assets/fonts/turok.ttf", 80)
            self.score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)
        except FileNotFoundError:
            print("Font file not found!")
            self.count_font = pygame.font.SysFont("Arial", 80)
            self.score_font = pygame.font.SysFont("Arial", 30)
     
    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.run = False
        return events
      
    def draw_text(self, text, font, color, x, y):
        """Draw text to the screen"""
        img = font.render(text, True, color)
        self.screen.blit(img, (x, y))

    def run_game(self):
        while self.run:
            self.clock.tick(self.FPS)
            events = self.handle_events()
            self.pages[self.current_page].render(events)
                 
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'sock'):
            self.sock.close()
        pygame.quit()

def main():
    """Main function to run the game"""
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