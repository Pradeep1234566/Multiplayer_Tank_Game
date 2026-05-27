class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.speed = 10

    def move(self):
        # Move bullet upward
        self.y -= self.speed

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            (255, 255, 0),  # Yellow bullet
            (self.x, self.y),
            self.radius
        )

class Tank:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 40
        self.speed = 5

    def move(self, keys):
        # Move left
        if keys[pygame.K_a]:
            self.x -= self.speed

        # Move right
        if keys[pygame.K_d]:
            self.x += self.speed

        # Move up
        if keys[pygame.K_w]:
            self.y -= self.speed

        # Move down
        if keys[pygame.K_s]:
            self.y += self.speed

    def draw(self, screen):
        # Tank body
        pygame.draw.rect(
            screen,
            (0, 200, 0),  # Green color
            (self.x, self.y, self.width, self.height)
        )

        # Tank turret
        pygame.draw.rect(
            screen,
            (100, 100, 100),
            (self.x + 20, self.y - 10, 20, 20)
        )



import pygame
import sys

# Initialize pygame
pygame.init()

# Window setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank Battle")

# Clock for controlling framerate
clock = pygame.time.Clock()
FPS = 60
player_tank = Tank(100, 100)
bullets = []

# Game loop
while True:
    # 1. Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Fire a bullet from the tank's turret
                bullet_x = player_tank.x + player_tank.width // 2
                bullet_y = player_tank.y 
                bullets.append(Bullet(bullet_x, bullet_y))
            
    # 2. Update game state (empty for now)
    keys = pygame.key.get_pressed()
    player_tank.move(keys)
    for bullet in bullets:
        bullet.move() 
        
        if bullet.y < 0:  # Remove bullets that go off-screen
            bullets.remove(bullet) 

    # 3. Draw everything
    screen.fill((30, 30, 30))
    player_tank.draw(screen)
    for bullet in bullets:
        bullet.draw(screen)

    pygame.display.flip()

    # 4. Control framerate
    clock.tick(FPS)