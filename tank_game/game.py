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

        # Movement
        if keys[self.controls['up']]:
            self.y -= self.speed

        if keys[self.controls['down']]:
            self.y += self.speed

        if keys[self.controls['left']]:
            self.x -= self.speed

        if keys[self.controls['right']]:
            self.x += self.speed

        # Rotation
        if keys[self.controls['rotate_left']]:
            self.angle += self.rotation_speed

        if keys[self.controls['rotate_right']]:
            self.angle -= self.rotation_speed

        # Wall collision
        if self.x < 30:
            self.x = 30

        if self.x > WIDTH - 30:
            self.x = WIDTH - 30

        if self.y < 30:
            self.y = 30

        if self.y > HEIGHT - 30:
            self.y = HEIGHT - 30

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

        # Draw tank body
        pygame.draw.polygon(
            screen,
            self.color,
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

font = pygame.font.Font(None, 40)

# Scores
score1 = 0
score2 = 0


# ---------------- CONTROLS ----------------
controls1 = {
    'up': pygame.K_w,
    'down': pygame.K_s,
    'left': pygame.K_a,
    'right': pygame.K_d,
    'rotate_left': pygame.K_q,
    'rotate_right': pygame.K_e
}

controls2 = {
    'up': pygame.K_UP,
    'down': pygame.K_DOWN,
    'left': pygame.K_LEFT,
    'right': pygame.K_RIGHT,
    'rotate_left': pygame.K_KP4,
    'rotate_right': pygame.K_KP6
}


# ---------------- PLAYERS ----------------
player_tank = Tank(
    400,
    300,
    controls1,
    (0, 200, 0)
)

player_tank2 = Tank(
    200,
    150,
    controls2,
    (200, 0, 0)
)

bullets = []


# ---------------- GAME LOOP ----------------
while True:

    # Events
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Shoot bullets
        if event.type == pygame.KEYDOWN:

            # Player 1 Shoot
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

            # Player 2 Shoot
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

    # Bullet logic
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
            continue

        # Player 1 hits Player 2
        if (
            bullet.owner == player_tank
            and player_tank2.get_rect().collidepoint(
                bullet.x,
                bullet.y
            )
        ):

            score1 += 1
            bullets.remove(bullet)

            # Respawn player 2
            player_tank2.x = 200
            player_tank2.y = 150
            player_tank2.angle = 0

        # Player 2 hits Player 1
        elif (
            bullet.owner == player_tank2
            and player_tank.get_rect().collidepoint(
                bullet.x,
                bullet.y
            )
        ):

            score2 += 1
            bullets.remove(bullet)

            # Respawn player 1
            player_tank.x = 400
            player_tank.y = 300
            player_tank.angle = 0

    # Draw
    screen.fill((30, 30, 30))

    player_tank.draw(screen)
    player_tank2.draw(screen)

    for bullet in bullets:
        bullet.draw(screen)

    # Draw score
    score_text = font.render(
        f"Player 1: {score1}    Player 2: {score2}",
        True,
        (255, 255, 255)
    )

    screen.blit(score_text, (20, 20))

    pygame.display.flip()

    clock.tick(FPS)