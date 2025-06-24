import pygame
from pygame import mixer
from fighter import Fighter, RemoteFighter
import socket
import pickle

mixer.init()
pygame.init()
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Runes & Steel Fighter")
clock = pygame.time.Clock()
FPS = 60

RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

intro_count = 3
last_count_update = pygame.time.get_ticks()
score = [0, 0]
round_over = False
ROUND_OVER_COOLDOWN = 2000

WARRIOR_SIZE = 162
WARRIOR_SCALE = 4
WARRIOR_OFFSET = [72, 56]
WARRIOR_DATA = [WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET]

WIZARD_SIZE = 250
WIZARD_SCALE = 3
WIZARD_OFFSET = [112, 107]
WIZARD_DATA = [WIZARD_SIZE, WIZARD_SCALE, WIZARD_OFFSET]

pygame.mixer.music.load("assets/audio/music.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1, 0.0, 5000)

sword_fx = pygame.mixer.Sound("assets/audio/sword.wav")
sword_fx.set_volume(0.5)
magic_fx = pygame.mixer.Sound("assets/audio/magic.wav")
magic_fx.set_volume(0.75)

bg_image = pygame.image.load("assets/images/background/background.jpg").convert_alpha()
warrior_sheet = pygame.image.load("assets/images/warrior/Sprites/warrior.png").convert_alpha()
wizard_sheet = pygame.image.load("assets/images/wizard/Sprites/wizard.png").convert_alpha()
victory_img = pygame.image.load("assets/images/icons/victory.png").convert_alpha()

WARRIOR_ANIMATION_STEPS = [10, 8, 1, 7, 7, 3, 7]
WIZARD_ANIMATION_STEPS = [8, 8, 1, 8, 8, 3, 7]

count_font = pygame.font.Font("assets/fonts/turok.ttf", 80)
score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_bg():
    scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_bg, (0, 0))

def draw_health_bar(health, x, y, width=400):
    ratio = health / 100
    pygame.draw.rect(screen, WHITE, (x - 2, y - 2, width + 4, 34))
    pygame.draw.rect(screen, RED, (x, y, width, 30))
    pygame.draw.rect(screen, YELLOW, (x, y, width * ratio, 30))

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 8889))
player_data = pickle.loads(sock.recv(1024))
player_num = player_data["player"]
print(f"Connected as Player {player_num}")

if player_num == 0:
    local_label = "P1: "
    enemy_label = "P2: "
else:
    local_label = "P2: "
    enemy_label = "P1: "

fighter_1_x = int(SCREEN_WIDTH * 0.2)
fighter_2_x = int(SCREEN_WIDTH * 0.7)
ground_y = int(SCREEN_HEIGHT * 0.7)

if player_num == 0:
    local_fighter = Fighter(1, fighter_1_x, ground_y, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
    remote_fighter = RemoteFighter({}, wizard_sheet, WIZARD_SCALE, WIZARD_OFFSET)
    remote_animation = remote_fighter.load_images(wizard_sheet, WIZARD_ANIMATION_STEPS)
else:
    local_fighter = Fighter(2, fighter_2_x, ground_y, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
    remote_fighter = RemoteFighter({}, warrior_sheet, WARRIOR_SCALE, WARRIOR_OFFSET)
    remote_animation = remote_fighter.load_images(warrior_sheet, WARRIOR_ANIMATION_STEPS)

enemy_connected = False

run = True
while run:
    clock.tick(FPS)
    draw_bg()

    health_bar_width = int(SCREEN_WIDTH * 0.4)
    margin = int(SCREEN_WIDTH * 0.02)

 
    draw_health_bar(local_fighter.health, margin, 20, health_bar_width)
    draw_text(local_label + str(score[player_num]), score_font, RED, margin, 60)

    if enemy_connected:
        draw_health_bar(remote_fighter.health, SCREEN_WIDTH - health_bar_width - margin, 20, health_bar_width)
        draw_text(enemy_label + str(score[1 - player_num]), score_font, RED,
                  SCREEN_WIDTH - health_bar_width - margin, 60)

 
    if intro_count <= 0:
        local_fighter.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, remote_fighter, round_over)
    else:
        countdown_x = int(SCREEN_WIDTH / 2 - 40)
        countdown_y = int(SCREEN_HEIGHT / 3)
        draw_text(str(intro_count), count_font, RED, countdown_x, countdown_y)
        if (pygame.time.get_ticks() - last_count_update) >= 1000:
            intro_count -= 1
            last_count_update = pygame.time.get_ticks()

    local_fighter.update()

    send_data = {
        "x": local_fighter.rect.x,
        "y": local_fighter.rect.y,
        "health": local_fighter.health,
        "action": local_fighter.action,
        "flip": local_fighter.flip,
        "attack_type": local_fighter.attack_type
    }

    try:
        sock.send(pickle.dumps(send_data))
        received = sock.recv(4096)
        if received:
            all_data = pickle.loads(received)
            local_fighter.health = all_data["self"]["health"]
            local_fighter.rect.x = all_data["self"]["x"]
            local_fighter.rect.y = all_data["self"]["y"]
            local_fighter.flip = all_data["self"]["flip"]
            local_fighter.action = all_data["self"]["action"]

            if all_data["enemy"] and "x" in all_data["enemy"]:
                enemy_connected = True
                remote_fighter.update_data(all_data["enemy"])
            else:
                enemy_connected = False

    except:
        pass

    local_fighter.draw(screen)

    if enemy_connected:
        remote_fighter.update(remote_animation)
        remote_fighter.draw(screen, remote_animation)

    if not round_over:
        if not local_fighter.alive:
            score[1 - player_num] += 1
            round_over = True
            round_over_time = pygame.time.get_ticks()
        elif remote_fighter.health <= 0:
            score[player_num] += 1
            round_over = True
            round_over_time = pygame.time.get_ticks()
    else:
        screen.blit(victory_img, (360, 150))
        if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
            round_over = False
            intro_count = 3

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False

    if local_fighter.health <= 0:
        print("HP habis, keluar dari game...")
        run = False

    pygame.display.update()

pygame.quit()
