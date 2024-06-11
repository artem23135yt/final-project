import random
import sys
import pygame
from pygame.locals import *

# Global constants
FPS = 32
SCR_WIDTH = 289
SCR_HEIGHT = 511
PLAY_GROUND = SCR_HEIGHT * 0.8

class Resources:
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.player_frames = []
        self.load_images()
        self.load_sounds()

    def load_images(self):
        """Load all images"""
        self.images['numbers'] = self.load_number_images()
        self.images['message'] = self.load_image('images/message.png')
        self.images['base'] = self.load_image('images/base.png')
        self.images['background'] = self.load_image('images/background.png', convert=True)
        self.images['pipe'] = self.load_pipes()
        self.set_player_frames('red')

    def load_image(self, path, convert_alpha=True, convert=False):
        if convert_alpha:
            return pygame.image.load(path).convert_alpha()
        if convert:
            return pygame.image.load(path).convert()
        return pygame.image.load(path)

    def load_number_images(self):
        return [self.load_image(f'images/{i}.png') for i in range(10)]

    def load_pipes(self):
        pipe_image = self.load_image('images/pipe.png')
        return (
            pygame.transform.rotate(pipe_image, 180),
            pipe_image
        )

    def load_sounds(self):
        """Load all sounds"""
        self.sounds['die'] = pygame.mixer.Sound('sounds/die.wav')
        self.sounds['hit'] = pygame.mixer.Sound('sounds/hit.wav')
        self.sounds['point'] = pygame.mixer.Sound('sounds/point.wav')
        self.sounds['swoosh'] = pygame.mixer.Sound('sounds/swoosh.wav')
        self.sounds['wing'] = pygame.mixer.Sound('sounds/wing.wav')

    def set_player_frames(self, color):
        """Set player frames based on selected color"""
        colors = {
            'red': ['images/redbird-downflap.png', 'images/redbird-midflap.png', 'images/redbird-upflap.png'],
            'blue': ['images/bluebird-downflap.png', 'images/bluebird-midflap.png', 'images/bluebird-upflap.png'],
            'yellow': ['images/yellowbird-downflap.png', 'images/yellowbird-midflap.png', 'images/yellowbird-upflap.png']
        }
        self.player_frames = [self.load_image(frame) for frame in colors[color]]
        self.images['player'] = self.player_frames


class Screen:
    def __init__(self, display, resources):
        self.display = display
        self.resources = resources

    def run(self):
        raise NotImplementedError


class WelcomeScreen(Screen):
    def run(self):
        p_x = int(SCR_WIDTH / 5)
        p_y = int((SCR_HEIGHT - self.resources.images['player'][0].get_height()) / 2)
        msgx = int((SCR_WIDTH - self.resources.images['message'].get_width()) / 2)
        msgy = int(SCR_HEIGHT * 0.13)
        b_x = 0

        while True:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                    return 'gameplay'
                elif event.type == KEYDOWN and event.key == K_c:
                    return 'character_select'

            self.display.fill((0, 0, 0))
            self.display.blit(self.resources.images['background'], (0, 0))
            self.display.blit(self.resources.images['player'][0], (p_x, p_y))
            self.display.blit(self.resources.images['message'], (msgx, msgy))
            self.display.blit(self.resources.images['base'], (b_x, PLAY_GROUND))
            pygame.display.update()
            pygame.time.Clock().tick(FPS)


class CharacterSelectScreen(Screen):
    def run(self):
        characters = ['red', 'blue', 'yellow']
        character_names = ["Red Bird", "Blue Bird", "Yellow Bird"]
        selected_character = 0

        font = pygame.font.Font(None, 36)

        while True:
            for event in pygame.event.get():
                if self.is_quit_event(event):
                    pygame.quit()
                    sys.exit()
                elif self.is_next_character_event(event):
                    selected_character = (selected_character + 1) % len(characters)
                elif self.is_previous_character_event(event):
                    selected_character = (selected_character - 1) % len(characters)
                elif self.is_select_character_event(event):
                    self.resources.set_player_frames(characters[selected_character])
                    return 'welcome'

            self.resources.set_player_frames(characters[selected_character])
            self.display_character_select_screen(font, character_names, selected_character)
            pygame.display.update()
            pygame.time.Clock().tick(FPS)

    def is_quit_event(self, event):
        return event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE)

    def is_next_character_event(self, event):
        return event.type == KEYDOWN and event.key == K_RIGHT

    def is_previous_character_event(self, event):
        return event.type == KEYDOWN and event.key == K_LEFT

    def is_select_character_event(self, event):
        return event.type == KEYDOWN and event.key == K_RETURN

    def display_character_select_screen(self, font, character_names, selected_character):
        self.display.fill((0, 0, 0))
        self.display.blit(self.resources.images['background'], (0, 0))

        character_text = font.render("Select Character", True, (255, 255, 255))
        text_rect = character_text.get_rect(center=(SCR_WIDTH / 2, SCR_HEIGHT / 4))
        self.display.blit(character_text, text_rect)

        name_text = font.render(character_names[selected_character], True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(SCR_WIDTH / 2, SCR_HEIGHT / 2))
        self.display.blit(name_text, name_rect)

        character_images = self.resources.player_frames
        self.display.blit(character_images[0], (SCR_WIDTH / 2 - character_images[0].get_width() / 2, SCR_HEIGHT / 2 + 20))


class GameplayScreen(Screen):
    def __init__(self, display, resources):
        super().__init__(display, resources)
        self.high_score = self.load_high_score()
        self.game_paused = False
        self.frame_counter = 0
        self.frame_rate = 10
        self.initialize_game_variables()

    def reset_game(self):
        self.score = 0
        self.frame_index = 0
        self.player_x = int(SCR_WIDTH / 5)
        self.player_y = int(SCR_WIDTH / 2)
        self.base_x = 0
        self.initialize_pipes()
        self.initialize_player_velocity()
        return 'welcome'

    def run(self):
        self.load_images()
        while True:
            self.handle_events()
            if self.game_paused:
                self.display_paused_message()
                continue
            self.update_score()
            self.update_player_position()
            self.update_pipes()
            self.display_gameplay()
            self.update_frame_index()
            if self.check_collision():
                pygame.time.wait(2000)
                return self.reset_game()
            pygame.time.Clock().tick(FPS)
    def load_images(self):
        """Load images required for the game."""
        self.resources.images['background'] = pygame.image.load('images/background.png').convert()
        self.resources.images['pipe'] = (
            pygame.transform.rotate(pygame.image.load('images/pipe.png').convert_alpha(), 180),
            pygame.image.load('images/pipe.png').convert_alpha()
        )

    def initialize_game_variables(self):
        """Initialize variables for the game."""
        self.score = 0
        self.frame_index = 0
        self.player_x = int(SCR_WIDTH / 5)
        self.player_y = int(SCR_WIDTH / 2)
        self.base_x = 0
        self.initialize_pipes()
        self.initialize_player_velocity()

    def initialize_pipes(self):
        """Initialize pipes for the game."""
        n_pip1 = self.get_random_pipes()
        n_pip2 = self.get_random_pipes()
        self.up_pipes = [{'x': SCR_WIDTH + 200, 'y': n_pip1[0]['y']},
                         {'x': SCR_WIDTH + 200 + (SCR_WIDTH / 2), 'y': n_pip2[0]['y']}]
        self.low_pipes = [{'x': SCR_WIDTH + 200, 'y': n_pip1[1]['y']},
                          {'x': SCR_WIDTH + 200 + (SCR_WIDTH / 2), 'y': n_pip2[1]['y']}]


    def initialize_player_velocity(self):
        """Initialize player velocity."""
        self.pipe_velocity_x = -4
        self.player_velocity_x = -9
        self.player_max_velocity_x = 10
        self.player_max_velocity_y = -8
        self.player_accuracy = 1
        self.player_flap_accuracy = -8
        self.player_flap = False

    def handle_events(self):
        """Handle game events such as quitting and player input."""
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if self.player_y > 0:
                    self.player_velocity_x = self.player_flap_accuracy
                    self.player_flap = True
                    self.resources.sounds['wing'].play()
            if event.type == KEYDOWN and event.key == K_p:
                self.game_paused = not self.game_paused


    def check_collision(self):
        """Check if collision occurred."""
        if self.player_y > PLAY_GROUND - 25 or self.player_y < 0:
            self.resources.sounds['hit'].play()
            return True
        for pipe in self.up_pipes:
            if self.check_upper_pipe_collision(pipe):
                return True
        for pipe in self.low_pipes:
            if self.check_lower_pipe_collision(pipe):
                return True
        return False

    def check_upper_pipe_collision(self, pipe):
        """Check collision with upper pipe."""
        pip_h = self.resources.images['pipe'][0].get_height()
        return (self.player_y < pip_h + pipe['y'] and
                abs(self.player_x - pipe['x']) < self.resources.images['pipe'][0].get_width())

    def check_lower_pipe_collision(self, pipe):
        """Check collision with lower pipe."""
        return (self.player_y + self.resources.images['player'][self.frame_index].get_height() > pipe['y'] and
                abs(self.player_x - pipe['x']) < self.resources.images['pipe'][0].get_width())

    def update_score(self):
        """Update the game score."""
        for pipe in self.up_pipes:
            if self.check_score_collision(pipe):
                self.resources.sounds['point'].play()
                self.score += 1
                if self.score == 12:
                    self.change_level()

    def check_score_collision(self, pipe):
        """Check if score collision occurred."""
        pip_middle_positions = pipe['x'] + self.resources.images['pipe'][0].get_width() / 2
        p_middle_positions = self.player_x + self.resources.images['player'][self.frame_index].get_width() / 2
        return pip_middle_positions <= p_middle_positions < pip_middle_positions + 4

    def update_player_position(self):
        """Update player position."""
        if self.player_velocity_x < self.player_max_velocity_x and not self.player_flap:
            self.player_velocity_x += self.player_accuracy
        if self.player_flap:
            self.player_flap = False
        p_height = self.resources.images['player'][self.frame_index].get_height()
        self.player_y += min(self.player_velocity_x, PLAY_GROUND - self.player_y - p_height)

    def update_pipes(self):
        """Update pipes position."""
        for pipe_upper, pipe_lower in zip(self.up_pipes, self.low_pipes):
            pipe_upper['x'] += self.pipe_velocity_x
            pipe_lower['x'] += self.pipe_velocity_x
        self.update_pipes_positions()

    def update_pipes_positions(self):
        """Update pipes positions and add new pipes."""
        if 0 < self.up_pipes[0]['x'] < 5:
            new_pipes = self.get_random_pipes()
            self.up_pipes.append(new_pipes[0])
            self.low_pipes.append(new_pipes[1])
        if self.up_pipes[0]['x'] < -self.resources.images['pipe'][0].get_width():
            self.up_pipes.pop(0)
            self.low_pipes.pop(0)

    def display_paused_message(self):
        """Display paused message."""
        font = pygame.font.Font(None, 72)
        text = font.render("Paused", True, (255, 255, 255))
        text_rect = text.get_rect(center=(SCR_WIDTH / 2, SCR_HEIGHT / 2))
        self.display.blit(text, text_rect)
        pygame.display.update()

    def change_level(self):
        """Change game level."""
        new_background = 'images/background-night.png'
        new_pipe = 'images/pipe-red.png'
        self.resources.images['background'] = pygame.image.load(new_background).convert()
        self.resources.images['pipe'] = (
            pygame.transform.rotate(pygame.image.load(new_pipe).convert_alpha(), 180),
            pygame.image.load(new_pipe).convert_alpha()
        )
        self.display.fill((0, 0, 0))
        font = pygame.font.Font(None, 36)
        text = font.render("Level 1", True, (255,255, 255))
        text_rect = text.get_rect(center=(SCR_WIDTH / 2, SCR_HEIGHT / 2))
        self.display.blit(text, text_rect)
        pygame.display.update()
        pygame.time.wait(2000)

    def update_frame_index(self):
        """Update frame index for animation."""
        self.frame_counter += 1
        if self.frame_counter % self.frame_rate == 0:
            self.frame_index = (self.frame_index + 1) % len(self.resources.images['player'])

    def get_random_pipes(self):
        """Generate random pipes."""
        pip_h = self.resources.images['pipe'][0].get_height()
        off_s = SCR_HEIGHT / 3
        yes2 = off_s + random.randrange(0, int(SCR_HEIGHT - self.resources.images['base'].get_height() - 1.2 * off_s))
        pipe_x = SCR_WIDTH + 10
        y1 = pip_h - yes2 + off_s
        y2 = yes2
        pipe = [{'x': pipe_x, 'y': -y1}, {'x': pipe_x, 'y': y2}]
        return pipe

    def load_high_score(self):
        """Load the high score from file."""
        try:
            with open('high_score.txt', 'r') as file:
                return int(file.read())
        except FileNotFoundError:
            return 0

    def save_high_score(self, high_score):
        """Save the high score to file."""
        with open('high_score.txt', 'w') as file:
            file.write(str(high_score))

    def display_gameplay(self):
        """Display the gameplay."""
        self.display.fill((0, 0, 0))
        self.display.blit(self.resources.images['background'], (0, 0))
        for pipe_upper, pipe_lower in zip(self.up_pipes, self.low_pipes):
            self.display.blit(self.resources.images['pipe'][0], (pipe_upper['x'], pipe_upper['y']))
            self.display.blit(self.resources.images['pipe'][1], (pipe_lower['x'], pipe_lower['y']))
        self.display.blit(self.resources.images['base'], (self.base_x, PLAY_GROUND))
        self.display.blit(self.resources.images['player'][self.frame_index], (self.player_x, self.player_y))

        self.display_score()
        self.display_best_score()

        pygame.display.update()

    def display_score(self):
        """Display the current score."""
        d = [int(x) for x in list(str(self.score))]
        w = sum(self.resources.images['numbers'][digit].get_width() for digit in d)
        Xoffset = (SCR_WIDTH - w) / 2
        for digit in d:
            self.display.blit(self.resources.images['numbers'][digit], (Xoffset, SCR_HEIGHT * 0.12))
            Xoffset += self.resources.images['numbers'][digit].get_width()

    def display_best_score(self):
        """Display the best score."""
        best_score_text = pygame.font.Font(None, 36).render(f'Best score: {self.high_score}', True, (255, 255, 255))
        self.display.blit(best_score_text, (SCR_WIDTH - best_score_text.get_width() - 10, 10))
        pygame.display.update()


class FlappyBirdGame:
    def __init__(self):
        pygame.init()
        self.display = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT))
        pygame.display.set_caption('Flappy Bird Game')
        self.resources = Resources()
        self.screens = {
            'welcome': WelcomeScreen(self.display, self.resources),
            'character_select': CharacterSelectScreen(self.display, self.resources),
            'gameplay': GameplayScreen(self.display, self.resources),
        }

    def run(self):
        current_screen = 'welcome'
        while True:
            current_screen = self.screens[current_screen].run()


if __name__ == "__main__":
    game = FlappyBirdGame()
    game.run()