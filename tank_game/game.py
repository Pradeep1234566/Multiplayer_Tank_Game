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

        self.radius = 8
        self.speed = 12

        self.bounces = 1

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


# ---------------- OBSTACLE CLASS ----------------
class Obstacle:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(
            x,
            y,
            width,
            height
        )

    def draw(self, screen):
        pygame.draw.rect(
            screen,
            (120, 120, 120),
            self.rect)


# ---------------- TANK CLASS ----------------
class Tank:
    def __init__(self, x, y, controls, color):
        self.x = x
        self.y = y

        self.controls = controls
        self.color = color

        self.speed = 6
        self.rotation_speed = 4

        self.angle = 0

    def move(self, keys):

        old_x = self.x
        old_y = self.y

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

        # Screen boundaries
        self.x = max(60, min(WIDTH - 60, self.x))
        self.y = max(60, min(HEIGHT - 60, self.y))

        # Obstacle collision
        tank_rect = self.get_rect()

        for obstacle in obstacles:
            if tank_rect.colliderect(
                obstacle.rect
            ):
                self.x = old_x
                self.y = old_y

    def get_rect(self):
        return pygame.Rect(
            self.x - 50,
            self.y - 50,
            100,
            100
        )

    def draw(self, screen):

        center_x = self.x
        center_y = self.y

        # Bigger tank
        tank_points = [
            (-60, -40),
            (30, -40),
            (60, 0),
            (30, 40),
            (-60, 40)
        ]

        rotated_points = []

        for px, py in tank_points:

            rotated_x = (
                px * math.cos(
                    math.radians(self.angle)
                )
                - py * math.sin(
                    math.radians(self.angle)
                )
            )

            rotated_y = (
                px * math.sin(
                    math.radians(self.angle)
                )
                + py * math.cos(
                    math.radians(self.angle)
                )
            )

            rotated_points.append(
                (
                    center_x + rotated_x,
                    center_y + rotated_y
                )
            )

        # Tank body
        pygame.draw.polygon(
            screen,
            self.color,
            rotated_points
        )

        # Bigger turret
        turret_length = 80

        turret_x = (
            center_x
            + math.cos(
                math.radians(self.angle)
            ) * turret_length
        )

        turret_y = (
            center_y
            - math.sin(
                math.radians(self.angle)
            ) * turret_length
        )

        pygame.draw.line(
            screen,
            (150, 150, 150),
            (center_x, center_y),
            (turret_x, turret_y),
            12
        )


# ---------------- INITIALIZE ----------------
pygame.init()

WIDTH, HEIGHT = 1400, 900

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "Tank Battle"
)

clock = pygame.time.Clock()
FPS = 60

font = pygame.font.Font(
    None,
    50
)

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
    250,
    450,
    controls1,
    (0, 200, 0)
)

player_tank2 = Tank(
    1150,
    450,
    controls2,
    (200, 0, 0)
)

bullets = []


# ---------------- OBSTACLES ----------------
obstacles = [

    Obstacle(
        600,
        150,
        40,
        300
    ),

    Obstacle(
        800,
        500,
        300,
        40
    ),

    Obstacle(
        250,
        650,
        350,
        40
    ),

    Obstacle(
        1000,
        200,
        40,
        250
    )
]


# ---------------- GAME LOOP ----------------
while True:

    # Events
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            # Player 1 Shoot
            if event.key == pygame.K_SPACE:

                bullet_x = (
                    player_tank.x
                    + math.cos(
                        math.radians(
                            player_tank.angle
                        )
                    ) * 80
                )

                bullet_y = (
                    player_tank.y
                    - math.sin(
                        math.radians(
                            player_tank.angle
                        )
                    ) * 80
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
                        math.radians(
                            player_tank2.angle
                        )
                    ) * 80
                )

                bullet_y = (
                    player_tank2.y
                    - math.sin(
                        math.radians(
                            player_tank2.angle
                        )
                    ) * 80
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

        bullet_rect = pygame.Rect(
            bullet.x - 5,
            bullet.y - 5,
            10,
            10
        )

        # Bounce off obstacles
        for obstacle in obstacles:

            if bullet_rect.colliderect(
                obstacle.rect
            ):

                overlap_left = abs(
                    bullet_rect.right
                    - obstacle.rect.left
                )

                overlap_right = abs(
                    bullet_rect.left
                    - obstacle.rect.right
                )

                overlap_top = abs(
                    bullet_rect.bottom
                    - obstacle.rect.top
                )

                overlap_bottom = abs(
                    bullet_rect.top
                    - obstacle.rect.bottom
                )

                min_overlap = min(
                    overlap_left,
                    overlap_right,
                    overlap_top,
                    overlap_bottom
                )

                # Side bounce
                if (
                    min_overlap
                    == overlap_left
                    or min_overlap
                    == overlap_right
                ):
                    bullet.angle = (
                        180 - bullet.angle
                    )

                # Top/bottom bounce
                else:
                    bullet.angle = (
                        -bullet.angle
                    )

                bullet.bounces -= 1
                break

        if bullet.bounces < 0:
            bullets.remove(bullet)
            continue

        # Off screen
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

            player_tank2.x = 1150
            player_tank2.y = 450
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

            player_tank.x = 250
            player_tank.y = 450
            player_tank.angle = 0

    # Draw
    screen.fill((30, 30, 30))

    # Obstacles
    for obstacle in obstacles:
        obstacle.draw(screen)

    player_tank.draw(screen)
    player_tank2.draw(screen)

    for bullet in bullets:
        bullet.draw(screen)

    # Score
    score_text = font.render(
        f"P1: {score1}     P2: {score2}",
        True,
        (255, 255, 255)
    )

    screen.blit(
        score_text,
        (20, 20)
    )

    pygame.display.flip()

    clock.tick(FPS)