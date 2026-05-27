import pygame
import sys
import math


# ---------------- BULLET CLASS ----------------
class Bullet:
    def __init__(self, x, y, angle, owner):
        self.x = x
        self.y = y
        self.angle = angle
        self.owner = owner
        

        self.radius = 5
        self.speed = 10

    def move(self):
        self.x += math.cos(
            math.radians(self.angle)
        ) * self.speed

        self.y -= math.sin(
            math.radians(self.angle)
        ) * self.speed

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            (255, 255, 0),
            (int(self.x), int(self.y)),
            self.radius
        )


# ---------------- TANK CLASS ----------------
class Tank:
    def __init__(self, x, y, controls, color):
        self.x = x
        self.y = y
        self.controls = controls
        self.color = color


        self.speed = 5
        self.rotation_speed = 4

        self.angle = 0

    def move(self, keys):

        # WASD movement
        if keys[self.controls['up']]:
            self.y -= self.speed

        if keys[self.controls['down']]:
            self.y += self.speed

        if keys[self.controls['left']]:
            self.x -= self.speed

        if keys[self.controls['right']]:
            self.x += self.speed

        if self.x < 30:
            self.x = 30
        
        if self.x > WIDTH - 30:
            self.x = WIDTH - 30
        
        if self.y < 30:
            self.y = 30
        
        if self.y > HEIGHT - 30:
            self.y = HEIGHT - 30

        
        # Rotate using numpad
        if keys[pygame.K_KP4]:
            self.angle += self.rotation_speed

        if keys[pygame.K_KP6]:
            self.angle -= self.rotation_speed

    def get_rect(self):
        return pygame.Rect(
            self.x - 25,
            self.y - 25,
            50,
            50
    )

    def draw(self, screen):

        center_x = self.x
        center_y = self.y

        # Tank body shape
        tank_points = [
            (-30, -20),
            (15, -20),
            (30, 0),
            (15, 20),
            (-30, 20)
        ]

        rotated_points = []

        for px, py in tank_points:

            rotated_x = (
                px * math.cos(math.radians(self.angle))
                - py * math.sin(math.radians(self.angle))
            )

            rotated_y = (
                px * math.sin(math.radians(self.angle))
                + py * math.cos(math.radians(self.angle))
            )

            rotated_points.append(
                (
                    center_x + rotated_x,
                    center_y + rotated_y
                )
            )

        # Draw body
        pygame.draw.polygon(
            screen,
            (0, 200, 0),
            rotated_points
        )

        # Draw turret
        turret_length = 40

        turret_x = center_x + math.cos(
            math.radians(self.angle)
        ) * turret_length

        turret_y = center_y - math.sin(
            math.radians(self.angle)
        ) * turret_length

        pygame.draw.line(
            screen,
            (120, 120, 120),
            (center_x, center_y),
            (turret_x, turret_y),
            8
        )


# ---------------- INITIALIZE ----------------
pygame.init()

score1 = 0
score2 = 0


WIDTH, HEIGHT = 800, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank Battle")

clock = pygame.time.Clock()
FPS = 60

controls1 = {
    'up': pygame.K_w,
    'down': pygame.K_s,
    'left': pygame.K_a,
    'right': pygame.K_d
}
controls2 = {
    'up': pygame.K_UP,
    'down': pygame.K_DOWN,
    'left': pygame.K_LEFT,
    'right': pygame.K_RIGHT
}
player_tank = Tank(400, 300, controls1, (0, 200, 0))
player_tank2 = Tank(200, 150, controls2, (200, 0, 0))
player_tank.x = 400
player_tank.y = 300

player_tank2.x = 200
player_tank2.y = 150


bullets = []


# ---------------- GAME LOOP ----------------
while True:

    # Events
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        
        # Shoot bullet
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:

                bullet_x = (
                    player_tank.x
                    + math.cos(
                        math.radians(player_tank.angle)
                    ) * 40
                )

                bullet_y = (
                    player_tank.y
                    - math.sin(
                        math.radians(player_tank.angle)
                    ) * 40
                )

                bullets.append(
                    Bullet(
                        bullet_x,
                        bullet_y,
                        player_tank.angle,
                        player_tank
                    )
                )
            
            if event.key == pygame.K_RETURN:

                bullet_x = (
                    player_tank2.x
                    + math.cos(
                        math.radians(player_tank2.angle)
                    ) * 40
                )

                bullet_y = (
                    player_tank2.y
                    - math.sin(
                        math.radians(player_tank2.angle)
                    ) * 40
                )

                bullets.append(
                    Bullet(
                        bullet_x,
                        bullet_y,
                        player_tank2.angle,
                        player_tank2
                    )
                )

    # Update
    keys = pygame.key.get_pressed()

    player_tank.move(keys)
    player_tank2.move(keys)
    

    for bullet in bullets[:]:
        bullet.move()

        # Remove offscreen bullets
        if (
            bullet.owner != player_tank and player_tank2.get_rect().collidepoint(bullet.x, bullet.y)
        ):
            score2 += 1
            bullets.remove(bullet)

        elif(bullet.owner != player_tank2 and player_tank.get_rect().collidepoint(bullet.x, bullet.y)):
            score1 += 1
            bullets.remove(bullet)
    # Draw
    screen.fill((30, 30, 30))

    player_tank.draw(screen)
    player_tank2.draw(screen)


    for bullet in bullets:
        bullet.draw(screen)

    pygame.display.flip()

    clock.tick(FPS)