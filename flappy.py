import random
import sys
import pygame
from pygame.locals import *

# Global Variables for the game
FPS = 32
scr_width = 289
scr_height = 511
play_ground = scr_height * 0.8
display_screen_window = pygame.display.set_mode((scr_width, scr_height))
game_image = {}
game_audio_sound = {}
red_bird_frames = ['images/redbird-downflap.png', 'images/redbird-midflap.png', 'images/redbird-upflap.png']
blue_bird_frames = ['images/bluebird-downflap.png', 'images/bluebird-midflap.png', 'images/bluebird-upflap.png']
yellow_bird_frames = ['images/yellowbird-downflap.png', 'images/yellowbird-midflap.png', 'images/yellowbird-upflap.png']
bcg_image = 'images/background.png'
pipe_image = 'images/pipe.png'
new_background = 'images/background-night.png'
new_pipe = 'images/pipe-red.png'

# Starting player frames
player_frames = red_bird_frames


def load_images():
    """Load all images"""
    game_image['numbers'] = (
        pygame.image.load('images/0.png').convert_alpha(),
        pygame.image.load('images/1.png').convert_alpha(),
        pygame.image.load('images/2.png').convert_alpha(),
        pygame.image.load('images/3.png').convert_alpha(),
        pygame.image.load('images/4.png').convert_alpha(),
        pygame.image.load('images/5.png').convert_alpha(),
        pygame.image.load('images/6.png').convert_alpha(),
        pygame.image.load('images/7.png').convert_alpha(),
        pygame.image.load('images/8.png').convert_alpha(),
        pygame.image.load('images/9.png').convert_alpha()
    )

    game_image['message'] = pygame.image.load('images/message.png').convert_alpha()
    game_image['base'] = pygame.image.load('images/base.png').convert_alpha()
    game_image['background'] = pygame.image.load(bcg_image).convert()
    game_image['pipe'] = (
        pygame.transform.rotate(pygame.image.load(pipe_image).convert_alpha(), 180),
        pygame.image.load(pipe_image).convert_alpha()
    )
    game_image['player'] = [pygame.image.load(frame).convert_alpha() for frame in player_frames]


def load_sounds():
    """Load all sounds"""
    game_audio_sound['die'] = pygame.mixer.Sound('sounds/die.wav')
    game_audio_sound['hit'] = pygame.mixer.Sound('sounds/hit.wav')
    game_audio_sound['point'] = pygame.mixer.Sound('sounds/point.wav')
    game_audio_sound['swoosh'] = pygame.mixer.Sound('sounds/swoosh.wav')
    game_audio_sound['wing'] = pygame.mixer.Sound('sounds/wing.wav')


def welcome_main_screen():
    """Shows welcome images on the screen"""
    p_x = int(scr_width / 5)
    p_y = int((scr_height - game_image['player'][0].get_height()) / 2)
    msgx = int((scr_width - game_image['message'].get_width()) / 2)
    msgy = int(scr_height * 0.13)
    b_x = 0
    while True:
        for event in pygame.event.get():
            # if user clicks on cross button, close the game
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            # If the user presses space or up key, start the game for them
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return
            elif event.type == KEYDOWN and event.key == K_c:
                character_selection_screen()

        display_screen_window.blit(game_image['background'], (0, 0))
        display_screen_window.blit(game_image['player'][0], (p_x, p_y))
        display_screen_window.blit(game_image['message'], (msgx, msgy))
        display_screen_window.blit(game_image['base'], (b_x, play_ground))
        pygame.display.update()
        time_clock.tick(FPS)


def character_selection_screen():
    """Shows character selection screen"""
    characters = [red_bird_frames, blue_bird_frames, yellow_bird_frames]
    character_names = ["Red Bird", "Blue Bird", "Yellow Bird"]
    selected_character = 0

    font = pygame.font.Font(None, 36)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and (event.key == K_RIGHT):
                selected_character = (selected_character + 1) % len(characters)
            elif event.type == KEYDOWN and (event.key == K_LEFT):
                selected_character = (selected_character - 1) % len(characters)
            elif event.type == KEYDOWN and (event.key == K_RETURN):
                global player_frames
                player_frames = characters[selected_character]
                load_images()
                return

        display_screen_window.fill((0, 0, 0))
        display_screen_window.blit(game_image['background'], (0, 0))

        character_text = font.render("Select Character", True, (255, 255, 255))
        text_rect = character_text.get_rect(center=(scr_width / 2, scr_height / 4))
        display_screen_window.blit(character_text, text_rect)

        name_text = font.render(character_names[selected_character], True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(scr_width / 2, scr_height / 2))
        display_screen_window.blit(name_text, name_rect)

        character_images = [pygame.image.load(frame).convert_alpha() for frame in characters[selected_character]]
        display_screen_window.blit(character_images[0],
                                   (scr_width / 2 - character_images[0].get_width() / 2, scr_height / 2 + 20))

        pygame.display.update()
        time_clock.tick(FPS)


def main_gameplay():
    """Basic gameplay"""
    score = 0
    frame_index = 0

    game_image['background'] = pygame.image.load(bcg_image).convert()
    game_image['pipe'] = (pygame.transform.rotate(pygame.image.load(pipe_image).convert_alpha(), 180),
                          pygame.image.load(pipe_image).convert_alpha())
    game_image['player'] = [pygame.image.load(frame).convert_alpha() for frame in player_frames]

    p_x = int(scr_width / 5)
    p_y = int(scr_width / 2)
    b_x = 0

    n_pip1 = get_Random_Pipes()
    n_pip2 = get_Random_Pipes()

    up_pips = [
        {'x': scr_width + 200, 'y': n_pip1[0]['y']},
        {'x': scr_width + 200 + (scr_width / 2), 'y': n_pip2[0]['y']},
    ]

    low_pips = [
        {'x': scr_width + 200, 'y': n_pip1[1]['y']},
        {'x': scr_width + 200 + (scr_width / 2), 'y': n_pip2[1]['y']},
    ]

    pip_Vx = -4

    p_vx = -9
    p_mvx = 10
    p_mvy = -8
    p_accuracy = 1

    p_flap_accuracy = -8
    p_flap = False

    frame_rate = 5  # Control the speed of animation (frames per second)
    frame_counter = 0  # Counter to track the frame rate

    high_score = load_high_score()  # Load the high score

    game_paused = False  # Flag for game pause

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if p_y > 0:
                    p_vx = p_flap_accuracy
                    p_flap = True
                    game_audio_sound['wing'].play()
            if event.type == KEYDOWN and event.key == K_p:
                game_paused = not game_paused  # Toggle pause state

        if game_paused:
            font = pygame.font.Font(None, 72)
            text = font.render("Paused", True, (255, 255, 255))
            text_rect = text.get_rect(center=(scr_width / 2, scr_height / 2))
            display_screen_window.blit(text, text_rect)
            pygame.display.update()
            continue

        cr_tst = is_Colliding(p_x, p_y, up_pips, low_pips, frame_index)
        if cr_tst:
            if score > high_score:
                high_score = score
                save_high_score(high_score)
            return

        p_middle_positions = p_x + game_image['player'][frame_index].get_width() / 2
        for pipe in up_pips:
            pip_middle_positions = pipe['x'] + game_image['pipe'][0].get_width() / 2
            if pip_middle_positions <= p_middle_positions < pip_middle_positions + 4:
                score += 1
                print(f"Your score is {score}")
                game_audio_sound['point'].play()

                # Change levels based on score
                if score == 12:
                    game_image['background'] = pygame.image.load(new_background).convert()
                    game_image['pipe'] = (pygame.transform.rotate(pygame.image.load(new_pipe).convert_alpha(), 180),
                                          pygame.image.load(new_pipe).convert_alpha())

                    display_screen_window.blit(game_image['background'], (0, 0))
                    font = pygame.font.Font(None, 36)
                    text = font.render(f"Level {score // 12}", True, (255, 255, 255))
                    text_rect = text.get_rect(center=(scr_width / 2, scr_height / 2))
                    display_screen_window.blit(text, text_rect)
                    pygame.display.update()
                    pygame.time.wait(2000)

        if p_vx < p_mvx and not p_flap:
            p_vx += p_accuracy

        if p_flap:
            p_flap = False
        p_height = game_image['player'][frame_index].get_height()
        p_y = p_y + min(p_vx, play_ground - p_y - p_height)

        for pip_upper, pip_lower in zip(up_pips, low_pips):
            pip_upper['x'] += pip_Vx
            pip_lower['x'] += pip_Vx

        if 0 < up_pips[0]['x'] < 5:
            new_pip = get_Random_Pipes()
            up_pips.append(new_pip[0])
            low_pips.append(new_pip[1])

        if up_pips[0]['x'] < -game_image['pipe'][0].get_width():
            up_pips.pop(0)
            low_pips.pop(0)

        display_screen_window.blit(game_image['background'], (0, 0))
        for pip_upper, pip_lower in zip(up_pips, low_pips):
            display_screen_window.blit(game_image['pipe'][0], (pip_upper['x'], pip_upper['y']))
            display_screen_window.blit(game_image['pipe'][1], (pip_lower['x'], pip_lower['y']))

        display_screen_window.blit(game_image['base'], (b_x, play_ground))

        # Update frame for animation
        frame_counter += 1
        if frame_counter % frame_rate == 0:
            frame_index = (frame_index + 1) % len(game_image['player'])

        display_screen_window.blit(game_image['player'][frame_index], (p_x, p_y))

        # Display current score
        d = [int(x) for x in list(str(score))]
        w = 0
        for digit in d:
            w += game_image['numbers'][digit].get_width()
        Xoffset = (scr_width - w) / 2

        for digit in d:
            display_screen_window.blit(game_image['numbers'][digit], (Xoffset, scr_height * 0.12))
            Xoffset += game_image['numbers'][digit].get_width()

        # Display high score
        best_score_text = pygame.font.Font(None, 36).render(f'Best score: {high_score}', True, (255, 255, 255))
        display_screen_window.blit(best_score_text, (scr_width - best_score_text.get_width() - 10, 10))

        pygame.display.update()
        time_clock.tick(FPS)



def is_Colliding(p_x, p_y, up_pipes, low_pipes, frame_index):
    """Collision check"""
    if p_y > play_ground - 25 or p_y < 0:
        game_audio_sound['hit'].play()
        return True

    for pipe in up_pipes:
        pip_h = game_image['pipe'][0].get_height()
        if (p_y < pip_h + pipe['y'] and abs(p_x - pipe['x']) < game_image['pipe'][0].get_width()):
            game_audio_sound['hit'].play()
            return True

    for pipe in low_pipes:
        if (p_y + game_image['player'][frame_index].get_height() > pipe['y']) and abs(p_x - pipe['x']) < \
                game_image['pipe'][0].get_width():
            game_audio_sound['hit'].play()
            return True

    return False


def get_Random_Pipes():
    """Generate positions of two pipes(one bottom straight and one top rotated) for blitting on the screen"""
    pip_h = game_image['pipe'][0].get_height()
    off_s = scr_height / 3
    yes2 = off_s + random.randrange(0, int(scr_height - game_image['base'].get_height() - 1.2 * off_s))
    pipe_x = scr_width + 10
    y1 = pip_h - yes2 + off_s
    y2 = yes2
    pipe = [
        {'x': pipe_x, 'y': -y1},  # Upper pipe
        {'x': pipe_x, 'y': y2}  # Lower pipe
    ]
    return pipe

"""Loading the record"""
def load_high_score():
    try:
        with open('high_score.txt', 'r') as file:
            return int(file.read())
    except FileNotFoundError:
        return 0

"""Saving the record"""
def save_high_score(high_score):
    with open('high_score.txt', 'w') as file:
        file.write(str(high_score))


if __name__ == "__main__":
    # Initialize all pygame's modules
    pygame.init()
    time_clock = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird Game')

    # Load all images and sounds
    load_images()
    load_sounds()

    while True:
        welcome_main_screen()  # Shows welcome screen to the user until they press a button
        main_gameplay()  # This is the main game function
