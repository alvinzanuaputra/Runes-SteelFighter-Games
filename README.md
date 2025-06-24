# Runes & Steel Fighter
Pixel RPG Multiplayer (referensi game Street Fighter)

## Deskripsi Proyek

Proyek ini adalah game pertarungan multiplayer bergaya piksel yang terinspirasi dari mekanika klasik Street Fighter, dikembangkan menggunakan bahasa pemrograman Python dan library Pygame.

## Teknologi Stack yang DKugunakan

- Python 3.10.9
- Pygame
- Multiplayer Networking
- Pygame

## Instalasi

1. Kloning repositori:
```bash
git clone https://github.com/alvinzanuaputra/Runes-SteelFighter-Games.git
```

2. Masuk ke folder proyek:
```bash
cd Runes-SteelFighter-Games
```

3. Instal dependensi:
```bash
pip install pygame
```

4. Jalankan permainan:
```bash
python main.py
```

## Fitur Utama

- Pertarungan gaya piksel
- Sistem pertarungan terinspirasi Street Fighter
- Mode multiplayer BY ONE
- Karakter unik dengan kemampuan berbeda
- Grafis retro yang menarik


## Penjelasan Kode 

### 1. `client2.py :`

```py
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

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False

    if intro_count <= 0:
        local_fighter.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, remote_fighter, round_over, events)
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
            # intro_count = 3
            run = False

    if local_fighter.health <= 0:
        print("HP habis, keluar dari game...")
        run = False

    pygame.display.update()

pygame.quit()

```


**Penjelasan Simple nya :**

### 1. `client2.py`:
File `client2.py` adalah inti dari game Runes & Steel Fighter. Berikut adalah fungsi utamanya:
- Inisialisasi: Setup pygame, layar, audio, dan variabel game
- Asset Loading: Memuat gambar, suara, font, dan spritesheet
- Game Loop:
  - Menangani input keyboard
  - Mengelola pergerakan, animasi, serangan
  - Sinkronisasi data ke server dan menerima update lawan
  - Render UI: health bar, nama pemain, dan karakter
  - Deteksi akhir ronde dan exit otomatis saat HP habis
- Rendering: Menggambar background, health bar, skor, dan karakter
- Game Logic: Mengatur hitungan mundur, deteksi kemenangan, dan reset ronde


### 2. `fighter.py :`

```py
import pygame

class Fighter():
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound):
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
        self.attack_sound = sound
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

        if self.attacking == False and self.alive == True and round_over == False:
            if self.player == 1:
                if key[pygame.K_a]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_d]:
                    dx = SPEED
                    self.running = True
                if key[pygame.K_w] and self.jump == False:
                    self.vel_y = -30
                    self.jump = True
            if self.player == 2:
                if key[pygame.K_LEFT]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_RIGHT]:
                    dx = SPEED
                    self.running = True
                if key[pygame.K_UP] and self.jump == False:
                    self.vel_y = -30
                    self.jump = True

            for event in events:
                if event.type == pygame.KEYDOWN:
                    if self.player == 1:
                        if event.key == pygame.K_r:
                            self.attack_type = 1
                            self.attack(target)
                        elif event.key == pygame.K_t:
                            self.attack_type = 2
                            self.attack(target)
                    elif self.player == 2:
                        if event.key == pygame.K_j:
                            self.attack_type = 1
                            self.attack(target)
                        elif event.key == pygame.K_k:
                            self.attack_type = 2
                            self.attack(target)

        self.vel_y += GRAVITY
        dy += self.vel_y

        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > screen_height - 110:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 110 - self.rect.bottom

        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self.rect.x += dx
        self.rect.y += dy

    def update(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(6)
        elif self.hit == True:
            self.update_action(5)
        elif self.attacking == True:
            if self.attack_type == 1:
                self.update_action(3)
            elif self.attack_type == 2:
                self.update_action(4)
        elif self.jump == True:
            self.update_action(2)
        elif self.running == True:
            self.update_action(1)
        else:
            self.update_action(0)

        animation_cooldown = 50
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.alive == False:
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
        if self.attack_cooldown == 0:
            self.attacking = True
            self.attack_sound.play()
            attacking_rect = pygame.Rect(
                self.rect.centerx - (2 * self.rect.width * self.flip),
                self.rect.y, 2 * self.rect.width, self.rect.height)
            if attacking_rect.colliderect(target.rect):
                # Di multiplayer, sebenarnya ini tidak diperlukan karena HP dikendalikan server
                target.hit = True

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
```


**Penjelasan Simplenya :**

### 2. `fighter.py`:
File `fighter.py` mendefinisikan kelas `Fighter`yang bertanggung jawab atas perilaku lokal setiap karakter dalam game dan `RemoteFighter` yang bertanggung jawab atas perilaku multiplayer setiap karakater dalam game:
- Constructor: Inisialisasi semua properti karakter fighter
- Animation System: Sistem untuk memuat dan mengatur animasi karakter
- Movement System: Sistem pergerakan dengan kontrol keyboard dan gravitasi
- Combat System: 
  - Tombol serang dikaitkan dengan attack_type
  - Mengaktifkan animasi serangan
  - Deteksi collision untuk visual feedback
- State Management:
  - Status hidup/mati, menyerang, terkena hit
  - Cooldown antara serangan
  - Update posisi berdasarkan gravitasi dan input


### 3. `server.py :`

```py
import socket
import threading
import pickle

players = [{}, {}] 
lock = threading.Lock()

def handle_client(conn, player_id):
    players[player_id] = {
        "x": 100 if player_id == 0 else 700,  # Contoh posisi default
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
                
                #players[player_id] = data
                enemy_id = 1 - player_id
                if players[enemy_id]:  # pastikan lawan sudah connect & kirim data
                    att_x = players[player_id].get("x", 0)
                    att_y = players[player_id].get("y", 0)
                    target_x = players[enemy_id].get("x", 0)
                    target_y = players[enemy_id].get("y", 0)

                if data.get("attack_type", 0) in [1, 2]:
                    if abs(att_x - target_x) < 150 and abs(att_y - target_y) < 100:
                        players[enemy_id]["health"] = max(0, players[enemy_id].get("health", 100) - 10)

                reply = {
    "self": players[player_id],
    "enemy": players[enemy_id] if players[enemy_id] else {}
}
            conn.sendall(pickle.dumps(reply))
            print(f"P{player_id} attack_type={data.get('attack_type')} | P{enemy_id} HP={players[enemy_id].get('health')}")

        except:
            break
    conn.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 8889))
    server.listen(2)
    print("Server started...")

    player_id = 0
    while player_id < 2:
        conn, addr = server.accept()
        print(f"Player {player_id} connected from {addr}")
        thread = threading.Thread(target=handle_client, args=(conn, player_id))
        thread.start()
        player_id += 1

if __name__ == "__main__":
    main()
```


**Penjelasan Simplenya :**

### 3. `server.py`:
File ini adalah server TCP multithreaded yang menangani koneksi dua pemain:
- Mengelola data state 2 pemain (players[0] dan players[1])
- Menerima status dari masing-masing client, seperti posisi, aksi, dan sinyal serangan
- Menentukan validasi serangan (jika posisi cukup dekat, dan attack_type aktif)
- Mengurangi HP lawan sekali per serangan
- Mengirimkan kembali self dan enemy state ke masing-masing client
- Reset attack_type setelah satu serangan untuk mencegah spam damage



## Panduan Kontrol dan Cara Bermain Game :

## **Kontrol Game**

### **🗡️ PLAYER 0 (WARRIOR) - Sisi Server 0**
| Tombol | Fungsi |
|--------|--------|
| **A** | Bergerak ke Kiri |
| **D** | Bergerak ke Kanan |
| **W** | Melompat |
| **R** | Serangan 1 (Attack 1) |
| **T** | Serangan 2 (Attack 2) |

### **⚕️ PLAYER 1` (WIZARD) - Sisi Server 1**
| Tombol | Fungsi |
|--------|--------|
| **← (Panah Kiri)** | Bergerak ke Kiri |
| **→ (Panah Kanan)** | Bergerak ke Kanan |
| **↑ (Panah Atas)** | Melompat |
| **J** | Serangan 1 (Attack 1) |
| **K** | Serangan 2 (Attack 2) |


### **Untuk Player 0 (Warrior)**
- Karakter fisik dengan serangan pedang
- Fokus pada serangan jarak dekat
- Manfaatkan kecepatan untuk mendekat dan menyerang

### **Untuk Player 1 (Wizard)**
- Karakter sihir dengan serangan magic
- Manfaatkan serangan sihir yang mungkin memiliki range berbeda
- Gunakan mobility untuk menjaga jarak

## **Pengaturan Game**
- **FPS**: 60 frame per second
- **Resolution**: 1000x600 pixels
- **Health**: Setiap karakter memiliki 100 HP
- **Damage**: Setiap serangan memberikan 10 damage
- **Attack Cooldown**: 20 frame (sekitar 0.33 detik)
- **Round Cooldown**: 2 detik setelah kemenangan

## **Cara Keluar Game**
- Klik tombol **X** pada window game, atau
- Tekan **Alt + F4** untuk menutup game

---

## Dokumentasi Game

**GAMBAR :**

- Bar HP dan Score :
  
![alt text](./assets/document/image.png)

- Tampilan Victory 

![alt text](./assets/document/image-1.png)

**VIDEO DEMO :**

https://github.com/user-attachments/assets/cf61b57a-98f0-40c7-84c6-26f0ad48f174

<!-- FOOTER END -->

## Kontak

- Pengembang: **Alvin Zanua Putra**
- Website Developer Pengembang : [Alvin Zanua Putra Website](https://alvinzanuaputra.vercel.app)
