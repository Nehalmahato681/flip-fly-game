__version__ = "1.0"
# flip-fly-game
import pygame
import random
import sys

pygame.init()

# ---------------- SCREEN ----------------
info = pygame.display.Info()
W = info.current_w
H = info.current_h

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Flappy Sky")

clock = pygame.time.Clock()
FPS = 60

# ---------------- COLORS ----------------
SKY = (105, 200, 245)
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
GREEN = (55, 190, 75)
DARK_GREEN = (35, 140, 50)
YELLOW = (255, 220, 40)
ORANGE = (245, 145, 30)
GROUND = (220, 180, 70)

font = pygame.font.Font(None, max(40, W // 10))
small_font = pygame.font.Font(None, max(28, W // 18))

# ---------------- GAME SETTINGS ----------------
bird_x = W // 4
bird_size = max(35, W // 18)

gravity = 0.55
flap_power = -9
pipe_speed = max(3, W / 250)

pipe_width = max(65, W // 12)
pipe_gap = max(170, H // 4)

ground_height = max(45, H // 16)
game_bottom = H - ground_height

# ---------------- GAME VARIABLES ----------------
bird_y = H // 2
bird_velocity = 0

pipes = []
score = 0
best_score = 0

game_started = False
game_over = False


def create_pipe(x):
    margin = 80

    gap_center = random.randint(
        margin + pipe_gap // 2,
        game_bottom - margin - pipe_gap // 2
    )

    top_height = gap_center - pipe_gap // 2

    return {
        "x": float(x),
        "top": top_height,
        "bottom": gap_center + pipe_gap // 2,
        "passed": False
    }


def reset_game():
    global bird_y, bird_velocity, pipes
    global score, game_started, game_over

    bird_y = H // 2
    bird_velocity = 0

    pipes = [
        create_pipe(W + W // 3),
        create_pipe(W + W)
    ]

    score = 0
    game_started = False
    game_over = False


def flap():
    global bird_velocity, game_started

    if not game_over:
        game_started = True
        bird_velocity = flap_power


def draw_bird():
    x = int(bird_x)
    y = int(bird_y)

    # Body
    pygame.draw.circle(
        screen,
        YELLOW,
        (x, y),
        bird_size // 2
    )

    # Wing
    pygame.draw.ellipse(
        screen,
        ORANGE,
        (
            x - bird_size // 3,
            y,
            bird_size // 2,
            bird_size // 3
        )
    )

    # Eye
    pygame.draw.circle(
        screen,
        WHITE,
        (x + bird_size // 5, y - bird_size // 6),
        bird_size // 7
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (x + bird_size // 5, y - bird_size // 6),
        bird_size // 14
    )

    # Beak
    pygame.draw.polygon(
        screen,
        ORANGE,
        [
            (x + bird_size // 2, y),
            (x + bird_size, y + bird_size // 8),
            (x + bird_size // 2, y + bird_size // 4)
        ]
    )


def draw_pipe(pipe):
    x = int(pipe["x"])

    top_rect = pygame.Rect(
        x,
        0,
        pipe_width,
        int(pipe["top"])
    )

    bottom_rect = pygame.Rect(
        x,
        int(pipe["bottom"]),
        pipe_width,
        game_bottom - int(pipe["bottom"])
    )

    pygame.draw.rect(screen, GREEN, top_rect)
    pygame.draw.rect(screen, GREEN, bottom_rect)

    # Pipe edges
    pygame.draw.rect(
        screen,
        DARK_GREEN,
        top_rect,
        4
    )

    pygame.draw.rect(
        screen,
        DARK_GREEN,
        bottom_rect,
        4
    )

    # Pipe caps
    cap_height = 25

    top_cap = pygame.Rect(
        x - 8,
        int(pipe["top"]) - cap_height,
        pipe_width + 16,
        cap_height
    )

    bottom_cap = pygame.Rect(
        x - 8,
        int(pipe["bottom"]),
        pipe_width + 16,
        cap_height
    )

    pygame.draw.rect(screen, GREEN, top_cap)
    pygame.draw.rect(screen, GREEN, bottom_cap)

    pygame.draw.rect(screen, DARK_GREEN, top_cap, 3)
    pygame.draw.rect(screen, DARK_GREEN, bottom_cap, 3)


def check_collision(pipe):
    bird_rect = pygame.Rect(
        int(bird_x - bird_size // 2),
        int(bird_y - bird_size // 2),
        bird_size,
        bird_size
    )

    top_rect = pygame.Rect(
        int(pipe["x"]),
        0,
        pipe_width,
        int(pipe["top"])
    )

    bottom_rect = pygame.Rect(
        int(pipe["x"]),
        int(pipe["bottom"]),
        pipe_width,
        game_bottom - int(pipe["bottom"])
    )

    return (
        bird_rect.colliderect(top_rect)
        or bird_rect.colliderect(bottom_rect)
    )


def draw_text_center(text, y, selected_font=font):
    image = selected_font.render(text, True, WHITE)

    screen.blit(
        image,
        (
            W // 2 - image.get_width() // 2,
            y
        )
    )


# ---------------- START ----------------
reset_game()

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Tap / mouse
        if event.type == pygame.MOUSEBUTTONDOWN:

            if game_over:
                reset_game()
            else:
                flap()

        # Finger touch
        if event.type == pygame.FINGERDOWN:

            if game_over:
                reset_game()
            else:
                flap()

        # Keyboard support
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:

                if game_over:
                    reset_game()
                else:
                    flap()

    # ---------------- UPDATE ----------------
    if game_started and not game_over:

        bird_velocity += gravity
        bird_y += bird_velocity

        # Move pipes
        for pipe in pipes:
            pipe["x"] -= pipe_speed

        # Add new pipes
        if pipes[-1]["x"] < W - W // 2:
            pipes.append(create_pipe(W + W // 2))

        # Remove old pipes
        if pipes[0]["x"] < -pipe_width - 30:
            pipes.pop(0)

        # Score
        for pipe in pipes:

            if not pipe["passed"] and pipe["x"] + pipe_width < bird_x:
                pipe["passed"] = True
                score += 1

                if score > best_score:
                    best_score = score

        # Collision with top/bottom
        if bird_y - bird_size // 2 <= 0:
            game_over = True

        if bird_y + bird_size // 2 >= game_bottom:
            game_over = True

        # Collision with pipes
        for pipe in pipes:

            if check_collision(pipe):
                game_over = True

    # ---------------- DRAW ----------------
    screen.fill(SKY)

    # Clouds
    for cx, cy in [
        (W // 5, H // 6),
        (W * 3 // 5, H // 8),
        (W * 4 // 5, H // 4)
    ]:
        pygame.draw.circle(screen, WHITE, (cx, cy), 25)
        pygame.draw.circle(screen, WHITE, (cx + 25, cy + 5), 32)
        pygame.draw.circle(screen, WHITE, (cx + 50, cy), 23)

    # Pipes
    for pipe in pipes:
        draw_pipe(pipe)

    # Ground
    pygame.draw.rect(
        screen,
        GROUND,
        (0, game_bottom, W, ground_height)
    )

    # Ground lines
    for x in range(0, W, 35):
        pygame.draw.line(
            screen,
            (170, 130, 45),
            (x, game_bottom),
            (x + 20, H),
            3
        )

    draw_bird()

    # Score
    score_image = font.render(
        str(score),
        True,
        WHITE
    )

    screen.blit(
        score_image,
        (
            W // 2 - score_image.get_width() // 2,
            35
        )
    )

    # Start message
    if not game_started and not game_over:

        draw_text_center(
            "TAP TO FLAP",
            H // 2 - 80
        )

        draw_text_center(
            "Avoid the pipes",
            H // 2 - 30,
            small_font
        )

    # Game over
    if game_over:

        overlay = pygame.Surface(
            (W, H),
            pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 130))
        screen.blit(overlay, (0, 0))

        draw_text_center(
            "GAME OVER",
            H // 2 - 100
        )

        draw_text_center(
            "Score: " + str(score),
            H // 2 - 40,
            small_font
        )

        draw_text_center(
            "Best: " + str(best_score),
            H // 2,
            small_font
        )

        draw_text_center(
            "Tap to restart",
            H // 2 + 60,
            small_font
        )

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
