#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Created on: 18/6/21 21:43:30 (IST)
version: 1.0
author: Ameya Vadnere
email: amey619rocks@gmail.com

Documentation:
    Word Bomber is a simple word typing game. Multiple words appear on the screen (moving downwards) from the top with some time interval between each other.
    The player has to type the words correctly before they reach the bottom to earn points, else the player loses a life. The words appear in waves, with
    the number of words increasing with each wave. After a certain number of lives are lost, the game ends. The player can choose to replay the game or quit.
---------------------------------------------------------------------------------------------------------------------------------------------------------------
"""


import pygame as pg                                                 # For all rendering/event-handling/displaying operations
import pygame.freetype                                              # Enhanced pygame module for loading and rendering computer fonts
import random                                                       # For introducing randomization in generation of words
import sys                                                          # For system related operations, like exiting out of a program
import os                                                           # For interacting with the operating system, here for file paths
from itertools import cycle                                         # For ease of cycling through a list


class Config:
    """
    Consists of all preset configuration settings
    which will be used for the entire program.
    """
    pg.init()                                                                           # Initializing pygame
    resolution = (pg.display.Info().current_w, pg.display.Info().current_h)             # Display mode, set to default
    font_style = 'calibri'                                                              # Font style of falling words/menu text
    font_size = 20                                                                      # Font size of falling words
    fps = 60                                                                            # Frames per second/refresh rate
    word_speed = 2                                                                      # How quickly words fall
    max_lives = 3                                                                       # No. of chances/lives
    done_color = 'grey'                                                                 # Color of letters done typing in a word
    present_color = 'yellow'                                                            # Color of the letter to be typed next in a word
    left_color = 'darkorange'                                                           # Color of the letters remaining to be typed
    word_file_path = os.path.join('assets', 'word_list.txt')                            # Path to the word file from which words would be generated
    bg_img_path = os.path.join('assets', 'background-black.png')                        # Path to the background image
    rocket_img_path = os.path.join('assets', 'pixel_ship_yellow.png')                   # Path to the rocket image
    heart_img_path =  os.path.join('assets', 'heart_img.png')                           # Path to the heart image (for showing lives)


class Word:
    """
    Generating an instance of a word whenever it is spawned. Some
    helpful class attributes are also defined for word-related operations
    like rendering/moving/deleting words.
    """
    wordqueue = None                        # Queue in which randomly generated words are stored
    font = None                             # Font style of falling words
    instances = []                          # List of Word() objects/instances
    last_spawn_time = 0                     # Recorded tick of when the last word just appeared on screen
    initiated = False                       # Whether we have started typing a new word
    word_obj = None                         # Storing the instance corresponding to the word being currently typed
    total_word_list = None                  # The complete list of words from which random words would be selected for play
    words_left = None                       # The number of words yet to be typed in the current wave

    def __init__(self, word):
        self.word = word                                                           # The generated word in string form
        self.word_length = len(word)                                               # Length of the generated word
        self.current_index = 0                                                     # The index of the letter which is currently being typed
        self.metrics = Word.font.get_metrics(word)                                 # Glyph metrics like width, height, etc. for each letter of self.word. This is useful in rendering text
        self.text_surf_rect = Word.font.get_rect(word)                             # Bounding box of the text
        self.baseline = self.text_surf_rect.y                                      # y-coordinate of the upper-left corner of the rectangle
        self.text_surf = pg.Surface(self.text_surf_rect.size, pg.SRCALPHA)         # Surface for rendering images/text
        self.text_surf_rect.center = Word.get_randomized_word_spawn_positions()    # Center text surfaces randomly within a range
        self.__class__.instances.append(self)                                      # Append object to Word.instances

    @classmethod
    def initialize_word_class(cls):
        """
        Initializes class attibutes at the beginning of a game.
        """
        Word.wordqueue = None
        Word.instances = []
        Word.last_spawn_time = 0
        Word.initiated = False
        Word.word_obj = None
        Word.total_word_list = None
        Word.words_left = None
        Word.font = pg.freetype.SysFont(Config.font_style, Config.font_size)
        Word.font.origin = True

    @staticmethod
    def get_randomized_word_spawn_positions():
        """
        Randomly generate x-coordinates for a word.
        """
        left_bound = 100
        right_bound = Config.resolution[1] - 100
        return (random.randrange(left_bound, right_bound), 0)


    @classmethod
    def render_words(cls, word_obj):
        """
        Render the current word and each word corresponding to each object in Word.instances
        """
        instance_list = [word_obj]*bool(word_obj) + cls.instances

        
        for obj in instance_list:
            obj.text_surf.convert_alpha()    

            # Note that as not all letters of a word have the same color, each letter of the word should 
            # be rendered separately. Hence there is a for loop for each word. For each word, we get the 
            # metrics (min_x, max_x, min_y, max_y, horizontal_advance_x, horizontal_advance_y) for each letter
            # to get rendering positions. After rendering, we move distance horizontal_advance_x to the right. 

            x = 0
            for (idx, (letter, metric)) in enumerate(zip(obj.word, obj.metrics)):
                if idx == obj.current_index:
                    color = Config.present_color
                elif idx < obj.current_index:
                    color = Config.done_color
                else:
                    color = Config.left_color

                Word.font.render_to(obj.text_surf, (x, obj.baseline), letter, color)
                x += metric[4]

            Game.screen.blit(obj.text_surf, obj.text_surf_rect)

    @classmethod
    def move_words(cls, wave):
        """
        Move the current word and each word corresponding to each object in Word.instances
        """
        instance_list = [Word.word_obj]*bool(Word.word_obj) + cls.instances
        for instance in instance_list:
            instance.text_surf_rect.move_ip(0, Config.word_speed)

    @classmethod
    def generate_word(cls):
        """
        Spawn a word on screen after some random interval of time from the last spawned word.
        """
        now = pg.time.get_ticks()
        if now - Word.last_spawn_time >= random.randrange(1000, 2500):
            if Word.wordqueue:
                temp = Word(Word.wordqueue.pop(0))
                Word.last_spawn_time = now

    
    @classmethod
    def initiate_word(cls, keypress):
        """
        Start typing a new word and set Word.word_obj.
        """
        # We can have multiple words on the screen. So we select the 
        # word which has the first letter same as the keypress. If no keypress
        # matches, we keep checking until some word does.
        for i, obj in enumerate(cls.instances):
            if keypress == obj.word[0]:
                cls.initiated = True
                obj.current_index = 1
                cls.instances[0], cls.instances[i] = cls.instances[i], cls.instances[0]
                Word.word_obj = obj
                break

    @classmethod
    def fill_word_queue(cls, wave):
        """
        Fill Word.wordqueue with randomly selected word from Word.total_word_list.
        The size of the wordqueue depends on the wave.
        """
        Word.wordqueue = random.sample(Word.total_word_list, wave + 2)
        Word.words_left = wave+2    
    
    @classmethod
    def check_for_collisions(cls):
        """
        Check whether any word has passed the bottom of the screen.
        """

        # If some word passes the bottom, we remove it from Word.instances
        # and reduce the number of words. Also the lives decrease.
        instance_list = [Word.word_obj]*bool(Word.word_obj) + cls.instances
        for obj in instance_list:
            if obj.text_surf_rect.y >= Config.resolution[1]:
                print(obj.text_surf_rect.y)
                if obj in Word.instances:
                    Word.instances.remove(obj)
                Word.word_obj, Word.initiated = None, None
                Word.words_left -= 1
                Game.screen.fill('red')
                Game.lives -= 1
                pg.display.flip()
                pg.time.delay(200)
                if not Word.instances and Word.words_left == 0:
                    Game.check_lives()
                    Game.wave += 1
                    Game.show_wave_screen()
                    Word.fill_word_queue(Game.wave)
            

class Game:
    """
    Consists of several game-related attributes.
    """
    screen = None                      # Screen object
    wave = None                        # Wave of words (level/stage)
    score = 0                          # Player score
    lives = None                       # No. of lives/chances
    clock = pg.time.Clock()            # Pygame clock objec
    bg_obj = None                      # For loading background image
    rocket_obj = None                  # For loading rocket image
    heart_obj = None                   # For loading heart image

    @classmethod
    def show_main_menu(cls):
        """
        Display the main menu. Start the game on any keypress.
        """
        Game.screen.blit(Game.bg_obj, (0,0))
        title_font = pg.font.SysFont('Calibri', 70)
        title_label = title_font.render('Word Bomber', True, 'orange')
        title_rect = title_label.get_rect(center = (Config.resolution[0]//2, 0.3*Config.resolution[1]))

        sec_title_font = pg.font.SysFont('Calibri', 40)
        sec_title_label = sec_title_font.render('(C) 2021, Volvo Corporation', True, 'orange')
        sec_title_rect = sec_title_label.get_rect(center = (Config.resolution[0]//2, 0.4*Config.resolution[1]))
        
        tert_title_colors = cycle(['black', 'orange'])

        tert_title_font = pg.font.SysFont('Calibri', 30)
        color = next(tert_title_colors)        
        now = pg.time.get_ticks()
        last = now
        while True:
            
            pygame.draw.rect(Game.screen, 'red', pygame.Rect(0.3*Config.resolution[0], 0.2*Config.resolution[1], 0.4*Config.resolution[0], 0.3*Config.resolution[1]),  10)
            now = pg.time.get_ticks()
            if now - last >= 800:
                color = next(tert_title_colors)
                last = now
            tert_title_label = tert_title_font.render('Press any key . . .', 2, color)
            tert_title_rect = tert_title_label.get_rect(center = (Config.resolution[0]//2, 0.8*Config.resolution[1]))
            Game.screen.blit(title_label, title_rect)
            Game.screen.blit(sec_title_label, sec_title_rect)
            Game.screen.blit(tert_title_label, tert_title_rect)
            pg.display.flip()

            for e in pg.event.get():
                if e.type == pg.QUIT:
                    pg.quit()
                    return
                if e.type == pg.KEYDOWN:
                    return

    @classmethod
    def redraw_window(cls):
        """
        Redraw elements like lives, score, rocket and background.
        """
        lives_font = pg.font.SysFont(Config.font_style, 30)
        score_font = pg.font.SysFont(Config.font_style, 30)
        Game.screen.blit(Game.bg_obj, (0,0))
        lives_label = lives_font.render('Lives: ', 1, 'yellow')
        heart_x = lives_label.get_rect().right + 10
        for _ in range(Game.lives):
            Game.screen.blit(Game.heart_obj, (heart_x, 0.9*Config.resolution[1]))
            heart_x += 60

        score_label = score_font.render('Score: ' + str(Game.score), 1, 'yellow')
        rocket_rect = Game.rocket_obj.get_rect(center=(Config.resolution[0]/2, 0.9*Config.resolution[1]))

        Game.screen.blit(lives_label, (10, 0.9*Config.resolution[1]))
        Game.screen.blit(Game.rocket_obj, rocket_rect)
        Game.screen.blit(score_label, (0.9*Config.resolution[0], 0.9*Config.resolution[1]))

    @classmethod
    def initialize_game_class(cls):
        """
        Initialize/Reset game attributes for a new game.
        """
        Game.screen = pg.display.set_mode(Config.resolution)
        Game.heart_obj = pg.transform.scale(pg.image.load(Config.heart_img_path).convert_alpha(), (50, 50))
        Game.bg_obj = pg.transform.scale(pg.image.load(Config.bg_img_path), Config.resolution)
        Game.rocket_obj = pg.image.load(Config.rocket_img_path)
        Game.wave = 1
        Game.lives = Config.max_lives
        Game.score = 0


    @classmethod
    def initialize(cls):
        """
        Initialize the game.
        """
        pg.init()
        Game.initialize_game_class()
        Word.initialize_word_class()
        Word.total_word_list = [word.strip() for word in open(Config.word_file_path, 'r').readlines()]
        Word.fill_word_queue(Game.wave)
        Game.show_main_menu()
        Word.generate_word()
        Game.show_wave_screen()
        Game.redraw_window()


    @classmethod
    def show_wave_screen(cls):
        """
        Display wave number screen at the beginning of each wave.
        """
        wave_font = pg.font.SysFont(Config.font_style, 50)
        Game.screen.blit(Game.bg_obj, (0,0))
        wave_label = wave_font.render('Wave ' + str(cls.wave), 1, 'yellow')
        wave_rect = wave_label.get_rect(center = Game.screen.get_rect().center)
        Game.screen.blit(wave_label, wave_rect)
        pg.display.flip()
        pg.time.delay(2000)


    @classmethod
    def handle_events(cls):
        """
        Listen for keydown or exit events.
        """
        word_obj = Word.word_obj  
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                return
            
            # If we have not started typing a new word
            if e.type == pg.KEYDOWN:
                keypress = e.unicode
                if not Word.initiated:
                    Word.initiate_word(keypress)        
                    if Word.initiated:                                  
                        Word.word_obj = Word.instances.pop(0)
                elif not word_obj:
                    pass

                # If we have started typing a new word AND:
                    # First OR condition:  That word is not done and the keypress matches the corresponding letter.
                    # Second OR condition: The word is done. 
                elif (word_obj.current_index < word_obj.word_length and keypress == word_obj.word[word_obj.current_index]) or word_obj.current_index >= word_obj.word_length:
                    # If the word is not done, increase index and continue.
                    word_obj.current_index += 1
                    # If the word is done, make following changes:
                    if word_obj.current_index >= word_obj.word_length:
                        Word.initiated = False
                        Word.word_obj = None
                        Game.score += 10
                        Word.words_left -= 1
                        # If the wave is over, make a new wave.
                        if not Word.instances and Word.words_left == 0:
                            Game.wave += 1
                            Game.show_wave_screen()
                            Word.fill_word_queue(Game.wave)
                            
    @classmethod
    def check_lives(cls):
        """
        Check for left lives.
        """
        if Game.lives <= 0:
            Game.show_game_over_screen()

    @classmethod
    def show_game_over_screen(cls):
        """
        Display the game over screen. The player can play again or quit.
        """
        Game.screen.blit(Game.bg_obj, (0,0))
        title_font = pg.font.SysFont('Calibri', 70)
        title_label = title_font.render('Game Over', 2, 'orange')
        title_rect = title_label.get_rect(center = (Config.resolution[0]//2, 0.3*Config.resolution[1]))

        sec_title_font = pg.font.SysFont('Calibri', 50)
        sec_title_label = sec_title_font.render('Your Score: ' + str(Game.score), 2, 'orange')
        sec_title_rect = sec_title_label.get_rect(center = (Config.resolution[0]//2, 0.4*Config.resolution[1]))

        tert_title_font = pg.font.SysFont('Calibri', 70)
        tert_title_label = tert_title_font.render("Press 'p' to play again, 'q' to give up.", 2, 'red')
        tert_title_rect = tert_title_label.get_rect(center = (Config.resolution[0]//2, 0.8*Config.resolution[1]))

        while True:
            Game.screen.blit(title_label, title_rect)
            Game.screen.blit(sec_title_label, sec_title_rect)
            Game.screen.blit(tert_title_label, tert_title_rect)
            pg.display.flip()

            for e in pg.event.get():
                if e.type == pg.QUIT:
                    pg.quit()
                    return
                if e.type == pg.KEYDOWN:
                    if e.unicode == 'q' or e.unicode == 'Q':
                        sys.exit()
                    if e.unicode == 'p' or e.unicode == 'P':
                        Game.run()


    @classmethod
    def run(cls):
        """
        Run the game.
        """
        Game.initialize()
        while True:
            Game.clock.tick(Config.fps)   # The program will not run more than 'fps' times per second.
            Game.check_lives()
            Word.generate_word()
            Word.check_for_collisions()
            Game.redraw_window()
            Word.move_words(Game.wave)
            Game.handle_events()
            Word.render_words(Word.word_obj)
            pg.display.flip()
        
if __name__ == '__main__':
    Game.run()