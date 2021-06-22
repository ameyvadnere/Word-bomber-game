import os

class Config:
    """
    Consists of all preset configuration settings
    which will be used for the entire program.
    """           
    version = 1.2                                                         
    resolution = None                                                                   # Display mode (if None, will be set to default)
    font_style = 'calibri'                                                              # Font style of falling words/menu text
    font_size = 20                                                                      # Font size of falling words
    fps = 360                                                                           # Frames per second/refresh rate
    word_speed = 2                                                                      # How quickly words fall
    max_lives = 3                                                                       # No. of chances/lives
    done_color = 'grey'                                                                 # Color of letters done typing in a word
    present_color = 'yellow'                                                            # Color of the letter to be typed next in a word
    left_color = 'darkorange'                                                           # Color of the letters remaining to be typed
    word_file_path = os.path.join('assets', 'words', 'word_list.txt')                            # Path to the word file from which words would be generated
    bg_img_path = os.path.join('assets', 'images', 'background-black.png')                        # Path to the background image
    rocket_img_path = os.path.join('assets', 'images', 'pixel_ship_yellow.png')                   # Path to the rocket image
    heart_img_path =  os.path.join('assets', 'images', 'heart_img.png')                           # Path to the heart image (for showing lives)
    menu_music_path = os.path.join('assets', 'sounds', 'game-startup.wav')                        # Menu music
    game_over_music_path = os.path.join('assets', 'sounds', 'game-over-music.wav')                # Game over music
    word_typed_music_path = os.path.join('assets', 'sounds', 'word-destroyed.wav')                # Word destroyed music
    life_lost_music_path = os.path.join('assets', 'sounds', 'life-lost.wav')                      # Life lost music