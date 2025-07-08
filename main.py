from pygame import Rect
import random

WIDTH = 800
HEIGHT = 600
MAP_WIDTH = 2400
GROUND_Y = HEIGHT - 70

game_state = "menu"
sound_enabled = True

start_button = Rect(300, 200, 200, 50)
sound_button = Rect(300, 270, 200, 50)
exit_button = Rect(300, 340, 200, 50)
game_over_button = Rect(300, 340, 200, 50)

GRAVITY = 0.5
JUMP_STRENGTH = -10
MAX_LIVES = 3
player_lives = MAX_LIVES
camera_x = 0

ground_tiles = []
decor_plants = []
decor_rocks = []
decor_bushes = []
decor_clouds = []

flag = None
enemies = []

# -------------------------------
# CAMERA SEGUIR O JOGADOR
# -------------------------------
def draw_clipped(actor):
    screen.blit(actor.image, (actor.x - camera_x - actor.width // 2, actor.y - actor.height // 2))

# -------------------------------
# CLASSES
# -------------------------------

class Hero:
    def __init__(self):
        self.walk_right = [f"p1_walk0{i}_right" for i in range(1, 7)]
        self.walk_left = [f"p1_walk0{i}_left" for i in range(1, 7)]
        self.stand_right_frames = ["p1_stand_right", "p1_stand2_right"]
        self.stand_left_frames = ["p1_stand_left", "p1_stand2_left"]
        self.stand_index = 0
        self.stand_timer = 0
        self.jump_right = "alien_green_jump_right"
        self.jump_left = "alien_green_jump_left"

        self.actor = Actor(self.stand_right_frames[0])
        self.actor.pos = (100, 400)
        self.direction = "right"
        self.walk_index = 0
        self.y_velocity = 0
        self.jumping = False
        self.walking = False

    def update(self):
        self.walking = False
        if keyboard.right:
            self.actor.x += 2
            self.direction = "right"
            self.walking = True
        elif keyboard.left:
            self.actor.x -= 2
            self.direction = "left"
            self.walking = True

        if keyboard.space and not self.jumping:
            self.y_velocity = JUMP_STRENGTH
            self.jumping = True
            if sound_enabled:
                sounds.jump.play()

        self.y_velocity += GRAVITY
        self.actor.y += self.y_velocity

        self.check_ground_collision()
        self.update_sprite()

    def check_ground_collision(self):
        margin = 5
        player_bottom = self.actor.y + self.actor.height // 2
        self.on_ground = False

        for tile in ground_tiles:
            tile_top = tile.y - tile.height // 2
            tile_left = tile.x - tile.width // 2
            tile_right = tile.x + tile.width // 2

            if tile_left <= self.actor.x <= tile_right and abs(player_bottom - tile_top) <= margin and self.y_velocity >= 0:
                self.actor.y = tile_top - self.actor.height // 2
                self.y_velocity = 0
                self.jumping = False
                self.on_ground = True
                return

        self.jumping = True

    def update_sprite(self):
        if self.jumping:
            new_image = self.jump_right if self.direction == "right" else self.jump_left
        elif self.walking:
            self.walk_index = (self.walk_index + 1) % len(self.walk_right)
            new_image = self.walk_right[self.walk_index] if self.direction == "right" else self.walk_left[self.walk_index]
        else:
            self.stand_timer += 1
            if self.stand_timer % 30 == 0:
                self.stand_index = (self.stand_index + 1) % 2
            if self.direction == "right":
                new_image = self.stand_right_frames[self.stand_index]
            else:
                new_image = self.stand_left_frames[self.stand_index]

        if self.actor.image != new_image:
            self.actor.image = new_image

    def draw(self):
        draw_clipped(self.actor)

class SlimeEnemy:
    def __init__(self, x, y):
        self.walk_images = ["slime_walk1", "slime_walk2"]
        self.dead_image = "slime_dead"
        self.walk_index = 0
        self.actor = Actor(self.walk_images[self.walk_index])
        self.actor.pos = (x, y)
        self.speed = 1
        self.timer = 0
        self.direction = "left"
        self.dead = False
        self.min_x = x - 100
        self.max_x = x + 100

    def update(self):
        if self.dead:
            self.actor.image = self.dead_image
            return

        self.timer += 1
        if self.timer % 15 == 0:
            self.walk_index = (self.walk_index + 1) % len(self.walk_images)
            self.actor.image = self.walk_images[self.walk_index]

        if self.direction == "left":
            self.actor.x -= self.speed
            if self.actor.x <= self.min_x:
                self.direction = "right"
        else:
            self.actor.x += self.speed
            if self.actor.x >= self.max_x:
                self.direction = "left"

    def draw(self):
        draw_clipped(self.actor)

class FlyEnemy:
    def __init__(self, x, y):
        self.fly_images = ["fly_fly1", "fly_fly2"]
        self.dead_image = "fly_dead"
        self.fly_index = 0
        self.actor = Actor(self.fly_images[self.fly_index])
        self.actor.pos = (x, y)
        self.speed = 1.5
        self.timer = 0
        self.direction = "right"
        self.dead = False

    def update(self):
        if self.dead:
            self.actor.image = self.dead_image
            return

        self.timer += 1
        if self.timer % 10 == 0:
            self.fly_index = (self.fly_index + 1) % len(self.fly_images)
            self.actor.image = self.fly_images[self.fly_index]

        if self.direction == "right":
            self.actor.x += self.speed
            if self.actor.x > MAP_WIDTH - 100:
                self.direction = "left"
        else:
            self.actor.x -= self.speed
            if self.actor.x < 100:
                self.direction = "right"

    def draw(self):
        draw_clipped(self.actor)

class Flag:
    def __init__(self, x, y):
        self.frames = ["flag_blue", "flag_blue2", "flag_blue_banging"]
        self.index = 0
        self.timer = 0
        self.actor = Actor(self.frames[self.index])
        self.actor.pos = (x, y)

    def update(self):
        self.timer += 1
        if self.timer % 10 == 0:
            self.index = (self.index + 1) % len(self.frames)
            self.actor.image = self.frames[self.index]

    def draw(self):
        draw_clipped(self.actor)

    def collides_with(self, other):
        return self.actor.colliderect(other)

# -------------------------------
# CRIAÇÃO
# -------------------------------

def create_ground():
    global ground_tiles
    tile_width = 70
    y = HEIGHT - tile_width
    tile_count = MAP_WIDTH // tile_width
    ground_tiles = []

    for i in range(tile_count):
        x = (i * tile_width) + tile_width // 2
        tile_type = "ground_left" if i == 0 else "ground_right" if i == tile_count - 1 else "ground_mid"
        ground_tiles.append(Actor(tile_type, (x, y + tile_width // 2)))

def create_decorations():
    global decor_plants, decor_rocks, decor_bushes, decor_clouds
    decor_plants = [Actor("plant", (x, HEIGHT - 100)) for x in (300, 850, 1600)]
    decor_rocks = [Actor("rock", (x, HEIGHT - 100)) for x in (500, 1200, 1900)]
    decor_bushes = [Actor("bush", (x, HEIGHT - 100)) for x in (650, 1350, 2100)]
    decor_clouds = [Actor("cloud1", (x, y)) for x, y in [(200, 100), (800, 150), (1400, 120), (2000, 90)]]

def create_enemies():
    global enemies
    enemies = []
    for _ in range(10):
        x = random.randint(200, MAP_WIDTH - 200)
        enemies.append(SlimeEnemy(x, GROUND_Y))
    enemies.append(FlyEnemy(1200, 200))
    enemies.append(FlyEnemy(1800, 150))

def create_flag():
    global flag
    flag_y = GROUND_Y - images.flag_blue.get_height() // 2
    flag = Flag(MAP_WIDTH - 100, flag_y)

# -------------------------------
# INICIALIZAÇÃO
# -------------------------------
player = Hero()
create_ground()
create_decorations()
create_enemies()
create_flag()

# -------------------------------
# DRAW
# -------------------------------

def draw():
    screen.clear()
    screen.fill((0, 0, 148))

    if game_state == "menu":
        draw_menu()
    elif game_state == "jogo":
        draw_game()
    elif game_state == "game_over":
        draw_game_over()
    elif game_state == "victory":
        draw_victory()

def draw_game():
    for x in range(0, MAP_WIDTH, images.bg.get_width()):
        for y in range(0, HEIGHT, images.bg.get_height()):
            screen.blit("bg", (x - camera_x, y))

    for cloud in decor_clouds:
        screen.blit(cloud.image, (cloud.x - camera_x, cloud.y))

    for tile in ground_tiles:
        draw_clipped(tile)

    for plant in decor_plants:
        draw_clipped(plant)
    for rock in decor_rocks:
        draw_clipped(rock)
    for bush in decor_bushes:
        draw_clipped(bush)

    for enemy in enemies:
        enemy.draw()

    if flag:
        flag.draw()

    player.draw()
    draw_hearts()

def draw_menu():
    screen.clear()
    screen.fill((80, 150, 255))
    screen.blit("hill_small", (100, HEIGHT - 170))
    screen.blit("hill_large", (500, HEIGHT - 200))
    for i in range(5):
        screen.blit("grass_mid", (i * 70, HEIGHT - 70))
    screen.blit("grass_right", (280, HEIGHT - 70))
    for i in range(7):
        x = 350 + i * 70
        screen.blit("liquidwatertop", (x, HEIGHT - 90))
        screen.blit("liquid_water", (x, HEIGHT - 50))
    screen.draw.text("Alien Jumper ", center=(WIDTH // 2, 100), fontsize=60, color="white")
    screen.draw.text("Iniciar Jogo", center=start_button.center, fontsize=28, color="black")
    screen.draw.text("Som: " + ("Ligado" if sound_enabled else "Desligado"), center=sound_button.center, fontsize=24, color="black")
    screen.draw.text("Sair", center=exit_button.center, fontsize=28, color="black")

def draw_game_over():
    screen.clear()
    screen.fill((20, 20, 20))
    screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 2 - 50), fontsize=60, color="red")
    screen.draw.text("Clique para retornar para o menu", center=(WIDTH // 2, HEIGHT // 2), fontsize=30, color="white")

def draw_victory():
    screen.clear()
    screen.fill((0, 100, 0))
    screen.draw.text("Voce Venceu!", center=(WIDTH // 2, HEIGHT // 2 - 50), fontsize=60, color="yellow")
    screen.draw.text("Clique para retornar para o menu", center=(WIDTH // 2, HEIGHT // 2 + 20), fontsize=30, color="white")

def draw_hearts():
    for i in range(MAX_LIVES):
        x = 20 + i * 50
        image = "hud_heart_full" if i < player_lives else "hud_heart_empty"
        screen.blit(image, (x, 20))

# -------------------------------
# UPDATE
# -------------------------------

def update():
    global camera_x
    if game_state == "jogo":
        player.update()
        for enemy in enemies:
            enemy.update()
        if flag:
            flag.update()
        check_enemy_collision()
        check_flag_collision()
        check_fall_out()
        camera_x = max(0, min(player.actor.x - WIDTH // 2, MAP_WIDTH - WIDTH))

def check_enemy_collision():
    global player_lives, game_state
    for enemy in enemies:
        if not enemy.dead and player.actor.colliderect(enemy.actor):
            if player.y_velocity > 0 and player.actor.y < enemy.actor.y:
                enemy.dead = True
                player.y_velocity = JUMP_STRENGTH / 2
            else:
                player_lives -= 1
                if player_lives <= 0:
                    game_state = "game_over"
                    sounds.bg_music.stop()
                else:
                    reset_player_position()
            return

def check_flag_collision():
    global game_state
    if flag and flag.collides_with(player.actor):
        game_state = "victory"
        sounds.bg_music.stop()

def check_fall_out():
    global player_lives, game_state
    if player.actor.y > HEIGHT + 50:
        player_lives -= 1
        if player_lives <= 0:
            game_state = "game_over"
            sounds.bg_music.stop()
        else:
            reset_player_position()

def reset_player_position():
    player.actor.pos = (100, 400)
    player.y_velocity = 0
    player.jumping = False

def reset_game():
    global player_lives
    player_lives = MAX_LIVES
    reset_player_position()
    create_enemies()
    create_flag()

# -------------------------------
# INPUT
# -------------------------------

def on_mouse_down(pos):
    global game_state, sound_enabled
    if game_state == "menu":
        if start_button.collidepoint(pos):
            game_state = "jogo"
            if sound_enabled:
                sounds.bg_music.play(-1)
        elif sound_button.collidepoint(pos):
            sound_enabled = not sound_enabled
            if not sound_enabled:
                sounds.bg_music.stop()
        elif exit_button.collidepoint(pos):
            exit()
    elif game_state in ["game_over", "victory"]:
        reset_game()
        game_state = "menu"
