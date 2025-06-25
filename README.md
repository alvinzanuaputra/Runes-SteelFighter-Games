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
- Mode multiplayer BYONE
- Karakter unik dengan kemampuan berbeda
- Grafis retro yang menarik


## Penjelasan Kode 

### 1. `main py :`

```py
import pygame  # Import library pygame untuk membuat game
from pygame import mixer  # Import mixer untuk mengelola audio
from fighter import Fighter  # Import class Fighter dari file fighter.py

mixer.init()  # Inisialisasi mixer untuk audio
pygame.init()  # Inisialisasi pygame

# Membuat jendela game
# Dapatkan resolusi layar monitor
info = pygame.display.Info()  # Dapatkan informasi display
SCREEN_WIDTH = info.current_w  # Lebar layar monitor
SCREEN_HEIGHT = info.current_h  # Tinggi layar monitor

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)  # Membuat window fullscreen
pygame.display.set_caption("Runes & Steel Fighter")  # Mengatur judul window game

# Mengatur framerate
clock = pygame.time.Clock()  # Membuat objek clock untuk mengontrol FPS
FPS = 60  # Mengatur frame per second menjadi 60

# Mendefinisikan warna-warna yang akan digunakan
RED = (255, 0, 0)  # Warna merah dalam format RGB
YELLOW = (255, 255, 0)  # Warna kuning dalam format RGB
WHITE = (255, 255, 255)  # Warna putih dalam format RGB

# Mendefinisikan variabel-variabel game
intro_count = 3  # Hitungan mundur sebelum game dimulai (3 detik)
last_count_update = pygame.time.get_ticks()  # Waktu terakhir hitungan mundur diupdate
score = [0, 0]  # Skor pemain [Player1, Player2]
round_over = False  # Status apakah ronde sudah selesai
ROUND_OVER_COOLDOWN = 2000  # Jeda waktu setelah ronde selesai (dalam milidetik)

# Mendefinisikan variabel-variabel untuk karakter fighter
WARRIOR_SIZE = 162  # Ukuran frame sprite warrior
WARRIOR_SCALE = 4  # Skala pembesaran sprite warrior
WARRIOR_OFFSET = [72, 56]  # Offset posisi untuk menyesuaikan posisi sprite
WARRIOR_DATA = [WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET]  # Data lengkap warrior dalam list

WIZARD_SIZE = 250  # Ukuran frame sprite wizard
WIZARD_SCALE = 3  # Skala pembesaran sprite wizard
WIZARD_OFFSET = [112, 107]  # Offset posisi untuk menyesuaikan posisi sprite
WIZARD_DATA = [WIZARD_SIZE, WIZARD_SCALE, WIZARD_OFFSET]  # Data lengkap wizard dalam list

# Memuat musik dan efek suara
pygame.mixer.music.load("assets/audio/music.mp3")  # Memuat file musik latar
pygame.mixer.music.set_volume(0.5)  # Mengatur volume musik menjadi 50%
pygame.mixer.music.play(-1, 0.0, 5000)  # Memutar musik berulang (-1) dengan fade in 5 detik

sword_fx = pygame.mixer.Sound("assets/audio/sword.wav")  # Memuat efek suara pedang
sword_fx.set_volume(0.5)  # Mengatur volume efek pedang menjadi 50%

magic_fx = pygame.mixer.Sound("assets/audio/magic.wav")  # Memuat efek suara sihir
magic_fx.set_volume(0.75)  # Mengatur volume efek sihir menjadi 75%

# Memuat gambar latar belakang
bg_image = pygame.image.load("assets/images/background/background.jpg").convert_alpha()  # Memuat dan mengkonversi gambar background

# Memuat spritesheet untuk animasi karakter
warrior_sheet = pygame.image.load("assets/images/warrior/Sprites/warrior.png").convert_alpha()  # Memuat spritesheet warrior
wizard_sheet = pygame.image.load("assets/images/wizard/Sprites/wizard.png").convert_alpha()  # Memuat spritesheet wizard

# Memuat gambar kemenangan
victory_img = pygame.image.load("assets/images/icons/victory.png").convert_alpha()  # Memuat gambar yang ditampilkan saat menang

# Mendefinisikan jumlah frame dalam setiap animasi
# [idle, run, jump, attack1, attack2, hit, death]
WARRIOR_ANIMATION_STEPS = [10, 8, 1, 7, 7, 3, 7]  # Jumlah frame untuk setiap animasi warrior
WIZARD_ANIMATION_STEPS = [8, 8, 1, 8, 8, 3, 7]  # Jumlah frame untuk setiap animasi wizard

# Mendefinisikan font untuk teks
count_font = pygame.font.Font("assets/fonts/turok.ttf", 80)  # Font untuk hitungan mundur (ukuran 80)
score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)  # Font untuk skor (ukuran 30)

# Fungsi untuk menggambar teks di layar
def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)  # Membuat surface teks dengan font dan warna yang ditentukan
  screen.blit(img, (x, y))  # Menggambar teks ke layar pada posisi (x, y)

# Fungsi untuk menggambar background
def draw_bg():
  scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))  # Mengubah ukuran background sesuai layar
  screen.blit(scaled_bg, (0, 0))  # Menggambar background di pojok kiri atas layar

# Fungsi untuk menggambar health bar pemain
def draw_health_bar(health, x, y, width=400):
  ratio = health / 100  # Menghitung rasio kesehatan (0-1)
  pygame.draw.rect(screen, WHITE, (x - 2, y - 2, width + 4, 34))  # Menggambar border putih health bar
  pygame.draw.rect(screen, RED, (x, y, width, 30))  # Menggambar background merah health bar
  pygame.draw.rect(screen, YELLOW, (x, y, width * ratio, 30))  # Menggambar health bar kuning sesuai kesehatan

# Membuat dua instance fighter (pemain) - posisi disesuaikan dengan ukuran layar
fighter_1_x = int(SCREEN_WIDTH * 0.2)  # Player 1 di 20% dari kiri layar
fighter_2_x = int(SCREEN_WIDTH * 0.7)  # Player 2 di 70% dari kiri layar
ground_y = int(SCREEN_HEIGHT * 0.7)  # Posisi ground di 70% dari atas layar

fighter_1 = Fighter(1, fighter_1_x, ground_y, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)  # Player 1 (Warrior)
fighter_2 = Fighter(2, fighter_2_x, ground_y, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)  # Player 2 (Wizard)

# Loop utama game
run = True  # Variable untuk mengontrol apakah game masih berjalan
while run:

  clock.tick(FPS)  # Membatasi FPS sesuai yang ditentukan

  # Menggambar background
  draw_bg()

  # Menampilkan statistik pemain (disesuaikan dengan ukuran layar)
  health_bar_width = int(SCREEN_WIDTH * 0.4)  # Lebar health bar 40% dari lebar layar
  margin = int(SCREEN_WIDTH * 0.02)  # Margin 2% dari lebar layar
  
  draw_health_bar(fighter_1.health, margin, 20, health_bar_width)  # Health bar player 1 di kiri atas
  draw_health_bar(fighter_2.health, SCREEN_WIDTH - health_bar_width - margin, 20, health_bar_width)  # Health bar player 2 di kanan atas
  draw_text("P1: " + str(score[0]), score_font, RED, margin, 60)  # Skor player 1
  draw_text("P2: " + str(score[1]), score_font, RED, SCREEN_WIDTH - health_bar_width - margin, 60)  # Skor player 2

  # Update hitungan mundur
  if intro_count <= 0:  # Jika hitungan mundur sudah selesai
    # Gerakkan fighters
    fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2, round_over)  # Update pergerakan fighter 1
    fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1, round_over)  # Update pergerakan fighter 2
  else:  # Jika masih dalam hitungan mundur
    # Tampilkan timer hitungan mundur
    countdown_x = int(SCREEN_WIDTH / 2 - 40)  # Posisi X tengah layar (dikurangi setengah lebar teks)
    countdown_y = int(SCREEN_HEIGHT / 3)  # Posisi Y di 1/3 layar
    draw_text(str(intro_count), count_font, RED, countdown_x, countdown_y)  # Tampilkan angka countdown
    # Update timer hitungan mundur
    if (pygame.time.get_ticks() - last_count_update) >= 1000:  # Jika sudah lewat 1 detik
      intro_count -= 1  # Kurangi hitungan mundur
      last_count_update = pygame.time.get_ticks()  # Update waktu terakhir countdown

  # Update fighters
  fighter_1.update()  # Update animasi dan status fighter 1
  fighter_2.update()  # Update animasi dan status fighter 2

  # Gambar fighters
  fighter_1.draw(screen)  # Gambar fighter 1 ke layar
  fighter_2.draw(screen)  # Gambar fighter 2 ke layar

  # Cek apakah ada pemain yang kalah
  if round_over == False:  # Jika ronde masih berlangsung
    if fighter_1.alive == False:  # Jika fighter 1 mati
      score[1] += 1  # Tambah skor player 2
      round_over = True  # Tandai ronde selesai
      round_over_time = pygame.time.get_ticks()  # Catat waktu ronde selesai
    elif fighter_2.alive == False:  # Jika fighter 2 mati
      score[0] += 1  # Tambah skor player 1
      round_over = True  # Tandai ronde selesai
      round_over_time = pygame.time.get_ticks()  # Catat waktu ronde selesai
  else:  # Jika ronde sudah selesai
    # Tampilkan gambar kemenangan
    screen.blit(victory_img, (360, 150))  # Gambar victory image di tengah layar
    if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:  # Jika cooldown sudah habis
      round_over = False  # Reset status ronde
      intro_count = 3  # Reset hitungan mundur
      # Buat fighter baru untuk ronde berikutnya
      fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
      fighter_2 = Fighter(2, 700, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)

  # Event handler untuk input pemain
  for event in pygame.event.get():  # Loop untuk semua event yang terjadi
    if event.type == pygame.QUIT:  # Jika pemain menutup window
      run = False  # Hentikan loop game
    if event.type == pygame.KEYDOWN:  # Jika ada tombol yang ditekan
      if event.key == pygame.K_ESCAPE:  # Jika tombol ESC ditekan
        run = False  # Keluar dari game

  # Update tampilan layar
  pygame.display.update()  # Refresh layar dengan semua perubahan yang sudah digambar

# Keluar dari pygame
pygame.quit()  # Tutup pygame dan bersihkan resource
```


**Penjelasan Simple nya :**

### 1. `main.py`:
File `main.py` adalah inti dari game Runes & Steel Fighter. Berikut adalah fungsi utamanya:
- Inisialisasi: Setup pygame, layar, audio, dan variabel game
- Asset Loading: Memuat gambar, suara, font, dan spritesheet
- Game Loop: Loop utama yang mengatur jalannya permainan
- Rendering: Menggambar background, health bar, skor, dan karakter
- Game Logic: Mengatur hitungan mundur, deteksi kemenangan, dan reset ronde


### 2. `fighter py :`

```py
import pygame  # Import library pygame untuk membuat game

class Fighter():  # Class untuk membuat karakter fighter
  def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound):  # Constructor untuk inisialisasi fighter
    self.player = player  # ID pemain (1 atau 2)
    self.size = data[0]  # Ukuran frame sprite dari data
    self.image_scale = data[1]  # Skala pembesaran sprite dari data
    self.offset = data[2]  # Offset posisi sprite dari data
    self.flip = flip  # Apakah sprite harus dibalik (menghadap kiri/kanan)
    self.animation_list = self.load_images(sprite_sheet, animation_steps)  # Load semua animasi dari spritesheet
    # Index animasi: 0:idle, 1:run, 2:jump, 3:attack1, 4:attack2, 5:hit, 6:death
    self.action = 0  # Aksi saat ini (mulai dengan idle)
    self.frame_index = 0  # Index frame animasi saat ini
    self.image = self.animation_list[self.action][self.frame_index]  # Gambar sprite saat ini
    self.update_time = pygame.time.get_ticks()  # Waktu terakhir animasi diupdate
    self.rect = pygame.Rect((x, y, 80, 180))  # Rectangle untuk collision detection dan posisi
    self.vel_y = 0  # Kecepatan vertikal (untuk gravitasi dan lompat)
    self.running = False  # Status apakah sedang berlari
    self.jump = False  # Status apakah sedang melompat
    self.attacking = False  # Status apakah sedang menyerang
    self.attack_type = 0  # Jenis serangan (1 atau 2)
    self.attack_cooldown = 0  # Cooldown setelah menyerang
    self.attack_sound = sound  # Efek suara saat menyerang
    self.hit = False  # Status apakah sedang terkena serangan
    self.health = 100  # Kesehatan fighter (maksimal 100)
    self.alive = True  # Status apakah fighter masih hidup

  def load_images(self, sprite_sheet, animation_steps):  # Fungsi untuk memuat semua frame animasi
    animation_list = []  # List untuk menyimpan semua animasi
    for y, animation in enumerate(animation_steps):  # Loop untuk setiap jenis animasi
      temp_img_list = []  # List sementara untuk frame dalam satu animasi
      for x in range(animation):  # Loop untuk setiap frame dalam animasi
        # Potong frame dari spritesheet berdasarkan posisi x,y dan ukuran
        temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size)
        # Skala frame sesuai dengan image_scale dan tambahkan ke list
        temp_img_list.append(pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale)))
      animation_list.append(temp_img_list)  # Tambahkan animasi lengkap ke list utama
    return animation_list  # Return list semua animasi

  def move(self, screen_width, screen_height, surface, target, round_over):  # Fungsi untuk menggerakkan fighter
    SPEED = 10  # Kecepatan pergerakan horizontal
    GRAVITY = 2  # Kekuatan gravitasi
    dx = 0  # Perubahan posisi horizontal
    dy = 0  # Perubahan posisi vertikal
    self.running = False  # Reset status berlari
    self.attack_type = 0  # Reset jenis serangan

    key = pygame.key.get_pressed()  # Dapatkan status semua tombol yang ditekan

    # Hanya proses input jika tidak sedang menyerang, masih hidup, dan ronde belum selesai
    if self.attacking == False and self.alive == True and round_over == False:
    
      if self.player == 1:  # Kontrol untuk player 1
        # Pergerakan
        if key[pygame.K_a]:  # Tombol A untuk bergerak ke kiri
          dx = -SPEED  # Set pergerakan ke kiri
          self.running = True  # Set status berlari
        if key[pygame.K_d]:  # Tombol D untuk bergerak ke kanan
          dx = SPEED  # Set pergerakan ke kanan
          self.running = True  # Set status berlari
        # Lompat
        if key[pygame.K_w] and self.jump == False:  # Tombol W untuk lompat (jika belum melompat)
          self.vel_y = -30  # Set kecepatan vertikal ke atas
          self.jump = True  # Set status melompat
        # Serangan
        if key[pygame.K_r] or key[pygame.K_t]:  # Tombol R atau T untuk menyerang
          self.attack(target)  # Jalankan fungsi serangan
          # Tentukan jenis serangan yang digunakan
          if key[pygame.K_r]:  # Jika tombol R ditekan
            self.attack_type = 1  # Set jenis serangan 1
          if key[pygame.K_t]:  # Jika tombol T ditekan
            self.attack_type = 2  # Set jenis serangan 2

      # Cek kontrol player 2
      if self.player == 2:  # Kontrol untuk player 2
        # Pergerakan
        if key[pygame.K_LEFT]:  # Tombol panah kiri untuk bergerak ke kiri
          dx = -SPEED  # Set pergerakan ke kiri
          self.running = True  # Set status berlari
        if key[pygame.K_RIGHT]:  # Tombol panah kanan untuk bergerak ke kanan
          dx = SPEED  # Set pergerakan ke kanan
          self.running = True  # Set status berlari
        # Lompat
        if key[pygame.K_UP] and self.jump == False:  # Tombol panah atas untuk lompat
          self.vel_y = -30  # Set kecepatan vertikal ke atas
          self.jump = True  # Set status melompat
        # Serangan
        if key[pygame.K_j] or key[pygame.K_k]:  # Tombol J atau K untuk menyerang
          self.attack(target)  # Jalankan fungsi serangan
          # Tentukan jenis serangan yang digunakan
          if key[pygame.K_j]:  # Jika tombol J ditekan
            self.attack_type = 1  # Set jenis serangan 1
          if key[pygame.K_k]:  # Jika tombol K ditekan
            self.attack_type = 2  # Set jenis serangan 2


    # Terapkan gravitasi
    self.vel_y += GRAVITY  # Tambahkan gravitasi ke kecepatan vertikal
    dy += self.vel_y  # Tambahkan kecepatan vertikal ke perubahan posisi

    # Pastikan player tetap di dalam layar
    if self.rect.left + dx < 0:  # Jika akan keluar dari sisi kiri layar
      dx = -self.rect.left  # Set dx agar tepat di tepi kiri
    if self.rect.right + dx > screen_width:  # Jika akan keluar dari sisi kanan layar
      dx = screen_width - self.rect.right  # Set dx agar tepat di tepi kanan
    if self.rect.bottom + dy > screen_height - 110:  # Jika akan jatuh melewati lantai
      self.vel_y = 0  # Reset kecepatan vertikal
      self.jump = False  # Reset status lompat
      dy = screen_height - 110 - self.rect.bottom  # Set dy agar tepat di lantai

    # Pastikan pemain saling berhadapan
    if target.rect.centerx > self.rect.centerx:  # Jika target di sebelah kanan
      self.flip = False  # Menghadap ke kanan (tidak dibalik)
    else:  # Jika target di sebelah kiri
      self.flip = True  # Menghadap ke kiri (dibalik)

    # Terapkan cooldown serangan
    if self.attack_cooldown > 0:  # Jika masih dalam cooldown
      self.attack_cooldown -= 1  # Kurangi cooldown

    # Update posisi player
    self.rect.x += dx  # Terapkan perubahan posisi horizontal
    self.rect.y += dy  # Terapkan perubahan posisi vertikal

  # Menangani update animasi
  def update(self):
    # Cek aksi apa yang sedang dilakukan player
    if self.health <= 0:  # Jika kesehatan habis
      self.health = 0  # Set kesehatan ke 0
      self.alive = False  # Set status mati
      self.update_action(6)  # Jalankan animasi kematian (index 6)
    elif self.hit == True:  # Jika sedang terkena serangan
      self.update_action(5)  # Jalankan animasi terkena hit (index 5)
    elif self.attacking == True:  # Jika sedang menyerang
      if self.attack_type == 1:  # Jika jenis serangan 1
        self.update_action(3)  # Jalankan animasi serangan 1 (index 3)
      elif self.attack_type == 2:  # Jika jenis serangan 2
        self.update_action(4)  # Jalankan animasi serangan 2 (index 4)
    elif self.jump == True:  # Jika sedang melompat
      self.update_action(2)  # Jalankan animasi lompat (index 2)
    elif self.running == True:  # Jika sedang berlari
      self.update_action(1)  # Jalankan animasi berlari (index 1)
    else:  # Jika tidak melakukan apa-apa
      self.update_action(0)  # Jalankan animasi idle (index 0)

    animation_cooldown = 50  # Waktu delay antar frame animasi (milidetik)
    # Update gambar
    self.image = self.animation_list[self.action][self.frame_index]  # Set gambar sesuai aksi dan frame saat ini
    # Cek apakah sudah cukup waktu berlalu sejak update terakhir
    if pygame.time.get_ticks() - self.update_time > animation_cooldown:  # Jika sudah melewati cooldown
      self.frame_index += 1  # Lanjut ke frame berikutnya
      self.update_time = pygame.time.get_ticks()  # Update waktu terakhir animasi
    # Cek apakah animasi sudah selesai
    if self.frame_index >= len(self.animation_list[self.action]):  # Jika sudah mencapai frame terakhir
      # Jika player sudah mati, hentikan di frame terakhir
      if self.alive == False:
        self.frame_index = len(self.animation_list[self.action]) - 1  # Set ke frame terakhir
      else:  # Jika masih hidup
        self.frame_index = 0  # Reset ke frame pertama (loop animasi)
        # Cek apakah serangan sudah dieksekusi
        if self.action == 3 or self.action == 4:  # Jika animasi serangan selesai
          self.attacking = False  # Reset status menyerang
          self.attack_cooldown = 20  # Set cooldown serangan
        # Cek apakah damage sudah diterima
        if self.action == 5:  # Jika animasi hit selesai
          self.hit = False  # Reset status terkena hit
          # Jika player sedang menyerang saat terkena hit, hentikan serangan
          self.attacking = False  # Reset status menyerang
          self.attack_cooldown = 20  # Set cooldown serangan

  def attack(self, target):  # Fungsi untuk melakukan serangan
    if self.attack_cooldown == 0:  # Jika tidak dalam cooldown
      # Eksekusi serangan
      self.attacking = True  # Set status menyerang
      self.attack_sound.play()  # Mainkan efek suara serangan
      # Buat rectangle untuk area serangan
      attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 2 * self.rect.width, self.rect.height)
      if attacking_rect.colliderect(target.rect):  # Jika area serangan bersentuhan dengan target
        target.health -= 10  # Kurangi kesehatan target sebesar 10
        target.hit = True  # Set status target terkena hit

  def update_action(self, new_action):  # Fungsi untuk mengganti aksi/animasi
    # Cek apakah aksi baru berbeda dengan aksi sebelumnya
    if new_action != self.action:  # Jika aksi berubah
      self.action = new_action  # Set aksi baru
      # Update pengaturan animasi
      self.frame_index = 0  # Reset ke frame pertama
      self.update_time = pygame.time.get_ticks()  # Reset waktu update animasi

  def draw(self, surface):  # Fungsi untuk menggambar fighter ke layar
    img = pygame.transform.flip(self.image, self.flip, False)  # Balik gambar horizontal jika perlu
    # Gambar sprite dengan offset yang sesuai
    surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))
```


**Penjelasan Simplenya :**

### 2. `fighter.py`:
File `fighter.py` mendefinisikan kelas `Fighter` yang bertanggung jawab atas perilaku setiap karakter dalam game:
- Constructor: Inisialisasi semua properti karakter fighter
- Animation System: Sistem untuk memuat dan mengatur animasi karakter
- Movement System: Sistem pergerakan dengan kontrol keyboard dan gravitasi
- Combat System: Sistem pertarungan dengan serangan dan deteksi collision
- State Management: Mengelola status karakter (hidup/mati, menyerang, terkena hit, dll.)


## Panduan Kontrol dan Cara Bermain Game :

## **Kontrol Game**

### **🗡️ PLAYER 1 (WARRIOR) - Sisi Kiri**
| Tombol | Fungsi |
|--------|--------|
| **A** | Bergerak ke Kiri |
| **D** | Bergerak ke Kanan |
| **W** | Melompat |
| **R** | Serangan 1 (Attack 1) |
| **T** | Serangan 2 (Attack 2) |

### **PLAYER 2 (WIZARD) - Sisi Kanan**
| Tombol | Fungsi |
|--------|--------|
| **← (Panah Kiri)** | Bergerak ke Kiri |
| **→ (Panah Kanan)** | Bergerak ke Kanan |
| **↑ (Panah Atas)** | Melompat |
| **J** | Serangan 1 (Attack 1) |
| **K** | Serangan 2 (Attack 2) |


### **Untuk Player 1 (Warrior)**
- Karakter fisik dengan serangan pedang
- Fokus pada serangan jarak dekat
- Manfaatkan kecepatan untuk mendekat dan menyerang

### **Untuk Player 2 (Wizard)**
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



<!-- FOOTER END -->

## Kontak

- Pengembang: **Alvin Zanua Putra**
- Website Developer Pengembang : [Alvin Zanua Putra Website](https:alvinzanuaputra.vercel.app)