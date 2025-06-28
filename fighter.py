import pygame

class Fighter():
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound, sound_graunt=None):
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
        self.attack_sound = sound
        self.attack_graunt_sound = sound_graunt
        self.hit = False
        self.health = 100
        self.alive = True
        self.ATTACK_COOLDOWN = 500
        self.last_attack_time = 0
        self.attack_animation_duration = 350
        self.attack_animation_started = 0

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
        current_time = pygame.time.get_ticks()
        if self.attacking and current_time - self.attack_animation_started > self.attack_animation_duration:
            self.attacking = False
            self.attack_type = 0
        if not self.attacking and self.alive and not round_over:
            if key[pygame.K_a]:
                dx = -SPEED
                self.running = True
                self.flip = True  
            if key[pygame.K_d]:
                dx = SPEED
                self.running = True
                self.flip = False 
            if key[pygame.K_w] and self.jump == False:
                self.vel_y = -30
                self.jump = True

            for event in events:
                if event.type == pygame.KEYDOWN:
                    # Tambahkan pengecekan cooldown serangan yang lebih ketat
                    if event.key == pygame.K_k and current_time - self.last_attack_time > self.ATTACK_COOLDOWN:
                        self.attack_type = 1
                        self.attack(target)
                        self.last_attack_time = current_time
                        self.attacking = True
                        self.attack_animation_started = current_time
                    elif event.key == pygame.K_l and current_time - self.last_attack_time > self.ATTACK_COOLDOWN:
                        self.attack_type = 2
                        self.attack(target)
                        self.last_attack_time = current_time
                        self.attacking = True
                        self.attack_animation_started = current_time

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
        
        # Reset frame index dan status serangan setelah animasi selesai
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.alive == False:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_type = 0
                if self.action == 5:
                    self.hit = False
                    self.attacking = False

    def attack(self, target):
        if self.attack_type == 1 or self.attack_type == 2:
            self.attack_sound.play()
            if self.attack_graunt_sound:
                self.attack_graunt_sound.play()
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
    def __init__(self, x, y, flip, sprite_sheet, image_scale, offset):
        self.image_scale = image_scale
        self.offset = offset
        self.action = 0
        self.frame_index = 0
        self.sprite_sheet = sprite_sheet
        self.image = None
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect(x, y, 80, 180)
        self.health = 100
        self.flip = flip

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