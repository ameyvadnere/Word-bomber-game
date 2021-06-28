import pygame as pg
from Config import Config
import random

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
        cls.wordqueue = None
        cls.instances = []
        cls.last_spawn_time = 0
        cls.initiated = False
        cls.word_obj = None
        cls.total_word_list = None
        cls.words_left = None
        cls.font = pg.freetype.SysFont(Config.font_style, Config.font_size)
        cls.font.origin = True

    @staticmethod
    def get_randomized_word_spawn_positions():
        """
        Randomly generate x-coordinates for a word.
        """
        left_bound = 100
        right_bound = Config.resolution[0] - 200
        return (random.randrange(left_bound, right_bound), 0)


    @classmethod
    def render_words(cls, word_obj, Game):
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

                cls.font.render_to(obj.text_surf, (x, obj.baseline), letter, color)
                x += metric[4]

            Game.screen.blit(obj.text_surf, obj.text_surf_rect)

    @classmethod
    def move_words(cls, wave):
        """
        Move the current word and each word corresponding to each object in Word.instances
        """
        instance_list = [cls.word_obj]*bool(cls.word_obj) + cls.instances
        for instance in instance_list:
            instance.text_surf_rect.move_ip(0, Config.word_speed + wave/2)

    @classmethod
    def generate_word(cls):
        """
        Spawn a word on screen after some random interval of time from the last spawned word.
        """
        now = pg.time.get_ticks()
        if now - cls.last_spawn_time >= random.randrange(1000, 2500):
            if cls.wordqueue:
                temp = Word(cls.wordqueue.pop(0))
                cls.last_spawn_time = now

    
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
                cls.word_obj = obj
                break

    @classmethod
    def fill_word_queue(cls, wave):
        """
        Fill Word.wordqueue with randomly selected word from Word.total_word_list.
        The size of the wordqueue depends on the wave.
        """
        cls.wordqueue = random.sample(cls.total_word_list, wave + 2)
        cls.words_left = wave+2    
    
    @classmethod
    def check_for_collisions(cls, Game):
        """
        Check whether any word has passed the bottom of the screen.
        """

        # If some word passes the bottom, we remove it from Word.instances
        # and reduce the number of words. Also the lives decrease.
        instance_list = [cls.word_obj]*bool(cls.word_obj) + cls.instances
        for obj in instance_list:
            if obj.text_surf_rect.y >= Config.resolution[1]:
                if obj in cls.instances:
                    cls.instances.remove(obj)

                if cls.word_obj is obj:
                    cls.word_obj, cls.initiated = None, None

                cls.words_left -= 1
                Game.screen.fill('red')
                Game.lives -= 1
                pg.mixer.Sound(Config.life_lost_music_path).play()
                pg.display.flip()
                pg.time.delay(200)
                if not cls.instances and cls.words_left == 0:
                    Game.check_lives()
                    Game.wave += 1
                    Game.show_wave_screen()
                    cls.fill_word_queue(Game.wave)