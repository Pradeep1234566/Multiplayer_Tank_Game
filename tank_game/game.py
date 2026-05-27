import pygame
import sys
import math


# ---------------- BULLET CLASS ----------------
class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle

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
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.speed = 5
        self.rotation_speed = 4

        self.angle = 0

    def move(self, keys):

        # WASD movement
        if keys[pygame.K_w]:
            self.y -= self.speed

        if keys[pygame.K_s]:
            self.y += self.speed

        if keys[pygame.K_a]:
            self.x -= self.speed

        if keys[pygame.K_d]:
            self.x += self.speed

        # Rotate using numpad
        if keys[pygame.K_KP4]:
            self.angle += self.rotation_speed

        if keys[pygame.K_KP6]:
            self.angle -= self.rotation_speed

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

WIDTH, HEIGHT = 800, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank Battle")

clock = pygame.time.Clock()
FPS = 60

player_tank = Tank(400, 300)

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
                        player_tank.angle
                    )
                )

    # Update
    keys = pygame.key.get_pressed()

    player_tank.move(keys)

    for bullet in bullets[:]:
        bullet.move()

        # Remove offscreen bullets
        if (
            bullet.x < 0
            or bullet.x > WIDTH
            or bullet.y < 0
            or bullet.y > HEIGHT
        ):
            bullets.remove(bullet)

    # Draw
    screen.fill((30, 30, 30))

    player_tank.draw(screen)

    for bullet in bullets:
        bullet.draw(screen)

    pygame.display.flip()

    clock.tick(FPS)