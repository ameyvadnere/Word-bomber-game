import pygame as pg
import pygame.freetype
import random
import sys
import os
from itertools import cycle

class Config:
    pg.init()
    resolution = (pg.display.Info().current_w, pg.display.Info().current_h)
    font_style = 'calibri'
    font_size = 20
    fps = 60
    word_speed = 2
    max_lives = 3
    done_color = 'grey'
    present_color = 'yellow'
    left_color = 'darkorange'
    word_file_path = os.path.join('assets', 'word_list.txt')
    bg_img_path = os.path.join('assets', 'background-black.png')
    rocket_img_path = os.path.join('assets', 'pixel_ship_yellow.png')
    heart_img_path =  os.path.join('assets', 'heart_img.png')


class Word:
    wordqueue = None
    font = None
    instances = []
    last_spawn_time = 0
    initiated = False
    word_obj = None
    total_word_list = None
    words_left = None

    def __init__(self, word):
        self.word = word
        self.word_length = len(word)
        self.current_index = 0
        self.metrics = Word.font.get_metrics(word)
        self.text_surf_rect = Word.font.get_rect(word)
        self.baseline = self.text_surf_rect.y
        self.text_surf = pg.Surface(self.text_surf_rect.size, pg.SRCALPHA)
        self.text_surf_rect.center = Word.get_randomized_word_spawn_positions()
        self.__class__.instances.append(self)

    @classmethod
    def initialize_word_class(cls):
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
        left_bound = 100
        right_bound = Config.resolution[1] - 100
        return (random.randrange(left_bound, right_bound), 0)


    @classmethod
    def render_words(cls, word_obj):
        instance_list = [word_obj]*bool(word_obj) + cls.instances

        for obj in instance_list:
            obj.text_surf.convert_alpha()    

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
        instance_list = [Word.word_obj]*bool(Word.word_obj) + cls.instances
        for instance in instance_list:
            instance.text_surf_rect.move_ip(0, Config.word_speed)

    @classmethod
    def generate_word(cls):
        now = pg.time.get_ticks()
        if now - Word.last_spawn_time >= random.randrange(1000, 2500):
            if Word.wordqueue:
                temp = Word(Word.wordqueue.pop(0))
                Word.last_spawn_time = now

    
    @classmethod
    def initiate_word(cls, keypress):
        print('Entered!!!!')
        for i, obj in enumerate(cls.instances):
            if keypress == obj.word[0]:
                cls.initiated = True
                obj.current_index = 1
                cls.instances[0], cls.instances[i] = cls.instances[i], cls.instances[0]
                Word.word_obj = obj
                print(keypress)
                break

    @classmethod
    def fill_word_queue(cls, wave):
        Word.wordqueue = random.sample(Word.total_word_list, wave + 2)
        Word.words_left = wave+2    
    
    @classmethod
    def check_for_collisions(cls):
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
    screen = None
    wave = None
    score = 0
    lives = None
    clock = pg.time.Clock()
    bg_obj = None
    rocket_obj = None
    heart_obj = None

    @classmethod
    def show_main_menu(cls):
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
        Game.screen = pg.display.set_mode(Config.resolution)
        Game.heart_obj = pg.transform.scale(pg.image.load(Config.heart_img_path).convert_alpha(), (50, 50))
        Game.bg_obj = pg.transform.scale(pg.image.load(Config.bg_img_path), Config.resolution)
        Game.rocket_obj = pg.image.load(Config.rocket_img_path)
        Game.wave = 1
        Game.lives = Config.max_lives
        Game.score = 0


    @classmethod
    def initialize(cls):
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
        wave_font = pg.font.SysFont(Config.font_style, 50)
        Game.screen.blit(Game.bg_obj, (0,0))
        wave_label = wave_font.render('Wave ' + str(cls.wave), 1, 'yellow')
        wave_rect = wave_label.get_rect(center = Game.screen.get_rect().center)
        Game.screen.blit(wave_label, wave_rect)
        pg.display.flip()
        pg.time.delay(2000)


    @classmethod
    def handle_events(cls):

        word_obj = Word.word_obj  
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                return
            if e.type == pg.KEYDOWN:
                keypress = e.unicode
                if not Word.initiated:
                    Word.initiate_word(keypress)
                    if Word.initiated:
                        Word.word_obj = Word.instances.pop(0)
                elif not word_obj:
                    pass
                elif (word_obj.current_index < word_obj.word_length and keypress == word_obj.word[word_obj.current_index]) or word_obj.current_index >= word_obj.word_length:
                    word_obj.current_index += 1
                    if word_obj.current_index >= word_obj.word_length:
                        Word.initiated = False
                        Word.word_obj = None
                        Game.score += 10
                        Word.words_left -= 1
                        if not Word.instances and Word.words_left == 0:
                            Game.wave += 1
                            Game.show_wave_screen()
                            Word.fill_word_queue(Game.wave)
                            
    @classmethod
    def check_lives(cls):
        if Game.lives <= 0:
            Game.show_game_over_screen()

    @classmethod
    def show_game_over_screen(cls):
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
        
        Game.initialize()
        while True:
            Game.clock.tick(Config.fps)
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