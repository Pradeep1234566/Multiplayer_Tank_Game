import pygame

from settings import *


def draw_background(screen):

    # Background
    screen.fill(BG_COLOR)

    # Grid lines
    grid_size = 50

    for x in range(
        0,
        WIDTH,
        grid_size
    ):

        pygame.draw.line(
            screen,
            GRID_COLOR,
            (x, 0),
            (x, HEIGHT)
        )

    for y in range(
        0,
        HEIGHT,
        grid_size
    ):

        pygame.draw.line(
            screen,
            GRID_COLOR,
            (0, y),
            (WIDTH, y)
        )


def draw_score(
    screen,
    font,
    score1,
    score2
):

    # HUD background
    hud_rect = pygame.Rect(
        WIDTH // 2 - 180,
        15,
        360,
        60
    )

    pygame.draw.rect(
        screen,
        (35, 40, 50),
        hud_rect,
        border_radius=15
    )

    pygame.draw.rect(
        screen,
        (80, 90, 110),
        hud_rect,
        width=2,
        border_radius=15
    )

    score_text = font.render(
        f"{score1}   :   {score2}",
        True,
        WHITE
    )

    score_rect = (
        score_text.get_rect(
            center=(
                WIDTH // 2,
                45
            )
        )
    )

    screen.blit(
        score_text,
        score_rect
    )

    # Player labels
    p1_text = font.render(
        "PLAYER 1",
        True,
        GREEN_TANK
    )

    p2_text = font.render(
        "PLAYER 2",
        True,
        RED_TANK
    )

    screen.blit(
        p1_text,
        (
            WIDTH // 2 - 300,
            25
        )
    )

    screen.blit(
        p2_text,
        (
            WIDTH // 2 + 140,
            25
        )
    )