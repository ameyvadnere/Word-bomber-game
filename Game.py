#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Created on: 18/6/21 21:43:30 (IST)
version: 1.2
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
from Config import Config
from Word import Word                                         
 
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
        
        version_font = pg.font.SysFont('Calibri', 20)
        version_label = version_font.render('v'+str(Config.version), True, 'orange')
        version_rect = version_label.get_rect(center=(0.95*Config.resolution[0], 0.95*Config.resolution[1]))

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
            Game.screen.blit(version_label, version_rect)
            Game.screen.blit(sec_title_label, sec_title_rect)
            Game.screen.blit(tert_title_label, tert_title_rect)
            pg.display.flip()

            for e in pg.event.get():
                if e.type == pg.QUIT:
                    pg.quit()
                    return
                if e.type == pg.KEYDOWN:
                    pg.mixer.music.stop()
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

    @staticmethod
    def play_sound(path, loop=False):
        mode = 1 if not loop else -1
        pg.mixer.music.load(path)
        pg.mixer.music.play(mode, 0.0)

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
        pg.init()                   # Initializing pygame
        pg.mixer.init()             # Initializing pygame's audio library
        
        Config.resolution = (pg.display.Info().current_w, pg.display.Info().current_h) if not Config.resolution else Config.resolution
        Game.initialize_game_class()
        Word.initialize_word_class()
        Word.total_word_list = [word.strip() for word in open(Config.word_file_path, 'r').readlines()]
        Word.fill_word_queue(Game.wave)
        Game.play_sound(Config.menu_music_path)
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
                        Game.play_sound(Config.word_typed_music_path)
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

        Game.play_sound(Config.game_over_music_path)

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
            Game.clock.tick_busy_loop(Config.fps)   # The program will not run more than 'fps' times per second.
            Game.check_lives()
            Word.generate_word()
            Word.check_for_collisions(Game)
            Game.redraw_window()
            Word.move_words(Game.wave)
            Game.handle_events()
            Word.render_words(Word.word_obj, Game)
            pg.display.flip()
        

Game.run()