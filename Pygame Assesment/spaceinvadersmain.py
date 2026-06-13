import pygame
import pygame.math


pygame.init()
#320 = 10 
#256 = 8
WIDTH, HEIGHT = 320, 256
screen = pygame.display.set_mode((WIDTH, HEIGHT),pygame.SCALED)
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 24)
#define sounds
death = pygame.mixer.Sound('explosion.wav')
invader_intro = pygame.mixer.Sound('invaders_intro.wav')
shoot = pygame.mixer.Sound('shoot.wav')

class Enemy:
    def __init__(self, x, y):
        self.image = pygame.Surface((20, 20))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(topleft=(x, y))

        self.speed = 1

    def update(self):
        self.rect.y += self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        
        #self.active = False
        #player_shot = False
    

        self.image = pygame.Surface((5, 5))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=pos)

        self.pos = pygame.math.Vector2(self.rect.center)
        self.vel = pygame.math.Vector2(0, -1)

        self.speed = 5


    def update(self):
        self.pos += self.vel * self.speed
        self.rect.center = self.pos

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=(WIDTH/2, HEIGHT/2))
        
        self.pos = pygame.math.Vector2(self.rect.center)
        self.vel = pygame.math.Vector2(0, 0)
        self.speed = 5

    def update(self):
        self.vel.x = 0
        self.vel.y = 0  
        
        #print (self.pos)
        #print(self.rect)

        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:  self.vel.x = -1 
        if keys[pygame.K_RIGHT]: self.vel.x = 1
        if keys[pygame.K_UP]:    self.vel.y = -1
        if keys[pygame.K_DOWN]:  self.vel.y = 1
 
        
        if self.vel.length() > 0:
            self.vel = self.vel.normalize() * self.speed
        


        self.pos += self.vel
        
        self.rect.center = self.pos

        if self.rect.left <= 0:
            self.rect.left = 0
            self.pos = self.rect.center

        if self.rect.right >= 320:
            self.rect.right = 320
            self.pos = self.rect.center

        if self.rect.top <= 190:
            self.rect.top = 190
            self.pos = self.rect.center
        
        if self.rect.bottom >= 256:
            self.rect.bottom = 256
            self.pos = self.rect.center
    def draw(self, surface):
        surface.blit(self.image, self.rect)

    """def fire_player(self):
        if self.player_shoot:
            bullet.active = True
 """




player = Player()
bullets = []
enemies = []

for row in range(3):
    for col in range(6):
        enemies.append(Enemy(40 + col * 40, 20 + row * 30))

game_state = "playing"  
running = True
invaders_intro.play()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == "playing":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullets.append(Bullet(player.rect.center))
                    shoot.play()

    if game_state == "playing":
  
        player.update()

        for bullet in bullets:
            bullet.update()

        for enemy in enemies:
            enemy.update()

        bullets = [b for b in bullets if b.rect.bottom > 0]

  
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    death.play()
                    break


        for enemy in enemies:
            if enemy.rect.bottom >= HEIGHT:
                game_state = "lose"


        if len(enemies) == 0:
            game_state = "win"


    screen.fill((30, 30, 30))

    if game_state == "playing":
        player.draw(screen)

        for bullet in bullets:
            bullet.draw(screen)

        for enemy in enemies:
            enemy.draw(screen)

    elif game_state == "win":
        text = font.render("YOU WIN!", True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - 40, HEIGHT // 2))

    elif game_state == "lose":
        text = font.render("YOU LOSE!", True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - 45, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
