import random
import sys

import pygame as pg

pg.init()


def draw_ground():
    screen.blit(ground, (ground_x, 450))
    screen.blit(ground, (ground_x + 288, 450))


def plane_rotate(plane):
    new_plane = pg.transform.rotozoom(plane, -plane_acceleration * 5, 1.15)
    return new_plane


def plane_animation():
    new_plane = plane_list[plane_frame]
    new_plane_rect = new_plane.get_rect(center=(50, plane_rect.centery))
    return new_plane, new_plane_rect


def create_pipes(passed_road, score):
    random_pipe_pos = random.choice(pipe_height)
    bottom_pipe = pipe_surface.get_rect(midtop=(350 + passed_road, random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midbottom=(350 + passed_road, random_pipe_pos - 15000))
    if score > 10:
        top_pipe = pipe_surface.get_rect(midbottom=(350 + passed_road, random_pipe_pos - 150))
    return bottom_pipe, top_pipe


def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= 512:
            screen.blit(pipe_surface, pipe)
        else:
            flipped_pipe = pg.transform.flip(pipe_surface, False, True)
            screen.blit(flipped_pipe, pipe)


def move_pipes(pipes, score):
    for pipe in pipes:
        pipe.centerx -= ((score / 5) + 4) * 0.5
    return pipes


def collision_control(pipes):
    for pipe in pipes:
        if plane_rect.colliderect(pipe):
            crash.play()
            return False
        if plane_rect.top <= -50 or plane_rect.bottom >= 450:
            crash.play()
            return False
    return True


def update_hscore(pscore, phscore):
    if pscore > phscore:
        phscore = pscore
        plus_one.play()
    return phscore


def scale_image(image, scale):
    w = image.get_width()
    h = image.get_height()
    return pg.transform.scale(image, (w * scale, h * scale))


def show_score(game_state):
    if game_state == "game_over":
        if score <= 0:
            score_surface = newFont.render(str(int(0)), True, (255, 255, 255))
        else:
            score_surface = newFont.render(str(int(score)), True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(144, 50))
        screen.blit(score_surface, score_rect)

        hscore_surface = newFont.render(f'Best: {int(hscore)}', True, (255, 255, 255))
        hscore_rect = score_surface.get_rect(center=(90, 425))
        screen.blit(hscore_surface, hscore_rect)

    if game_state == "main_game":
        if score <= 0:
            score_surface = newFont.render(str(int(0)), True, (255, 255, 255))
        else:
            score_surface = newFont.render(str(int(score)), True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(144, 50))
        screen.blit(score_surface, score_rect)


screen = pg.display.set_mode((288, 512))
clock = pg.time.Clock()

pg.display.set_caption("Avoid the Pipes")
icon = pg.image.load("Objects/plane_straight.png").convert_alpha()
pg.display.set_icon(icon)

# Background images
bg_surface = scale_image(pg.image.load("Objects/background.png").convert_alpha(), 2)
ground = pg.image.load("Objects/ground.png").convert_alpha()

# Plane frames
plane_straight = pg.image.load("Objects/plane_straight.png").convert_alpha()
plane_forward = pg.image.load("Objects/plane_forward.png").convert_alpha()
crashed_plane = pg.image.load("Objects/crashed_plane.png").convert_alpha()
plane_frame = 0
plane_list = [plane_straight, plane_forward, crashed_plane]
plane_surface = plane_list[plane_frame]

# Pipes
pipe_surface = pg.image.load("Objects/pipe.png").convert_alpha()
pipe_list = []
CREATE_PIPE = pg.USEREVENT + 1
pg.time.set_timer(CREATE_PIPE, 1200)
pipe_height = [200, 250, 300, 350, 400]

# Plane rect
plane_rect = plane_surface.get_rect(center=(50, 256))

# For plane movement logic
gravity = 0.125
plane_acceleration = 0

# Font
newFont = pg.font.Font("Objects/04B_19.TTF", 40)

# For ground move logic
ground_x = 0

ROTATE_PLANE = pg.USEREVENT + 0
pg.time.set_timer(ROTATE_PLANE, 150)

game_over_surface = pg.image.load("Objects/start_screen.png")
game_over_rect = game_over_surface.get_rect(center=(110, 100))
game_over_surface = pg.transform.rotozoom(game_over_surface, 0, 1.4)

game_ongoing = False

# Score variables
score = -1.38888889
hscore = 0
passed_road = 0

# Sound effects
jump = pg.mixer.Sound("Objects/flying.ogg")
crash = pg.mixer.Sound("Objects/crash.wav")
passed = pg.mixer.Sound("Objects/pass.ogg")
plus_one = pg.mixer.Sound("Objects/plusone.ogg")

# Game Loop
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE and game_ongoing:
                plane_acceleration = -4
                jump.play()
            if event.key == pg.K_SPACE and not game_ongoing:
                game_ongoing = True
                passed.play()
                pipe_list.clear()
                plane_rect.center = (50, 256)
                plane_acceleration = 0
                passed_time = pg.time.get_ticks() % 1200
                passed_time = 60 * (passed_time / 1000) * 3
                score = -1.38888889
        if event.type == ROTATE_PLANE:
            if plane_frame < 2:
                plane_frame += 1
            else:
                plane_frame = 0
            plane_surface, plane_rect = plane_animation()
        if event.type == CREATE_PIPE:
            pipe_list.extend(create_pipes(passed_road, score))

    screen.blit(bg_surface, (0, 0))

    if game_ongoing:
        game_ongoing = collision_control(pipe_list)

        # Pipe movement
        pipe_list = move_pipes(pipe_list, score)
        draw_pipes(pipe_list)

        # Plane movement logic
        plane_acceleration += gravity
        rotated_plane = plane_rotate(plane_surface)
        plane_rect.centery += plane_acceleration
        screen.blit(rotated_plane, plane_rect)

        # Increment score every frame
        score += 0.01388888889
        show_score("main_game")

    else:
        screen.blit(game_over_surface, game_over_rect)
        hscore = update_hscore(score, hscore)
        show_score("game_over")

    # Ground logic
    ground_x -= ((score / 5) + 4) * 0.5
    draw_ground()
    if ground_x <= -288:
        ground_x = 0

    pg.display.update()
    clock.tick(60)
