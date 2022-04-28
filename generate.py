import sys
from PIL import Image
import numpy as np
import time
import cv2
import pysrt
import curses

ASCII_CHAR_ARRAY = (" .:-=+*#%@", " .,:ilwW", " ▏▁░▂▖▃▍▐▒▀▞▚▌▅▆▊▓▇▉█", " `^|1aUBN", " .`!?xyWN")

ASCII_CHARS = ASCII_CHAR_ARRAY[0]
MAX_PIXEL_VALUE = 255

def vid_render(st_matrix, st, ed, option):
    media.addstr(0, 1, "Video Playback")
    pixels = [st_matrix[i][:] for i in range (st, ed)]
    # CONFIG OPTION - intensity measure
    intensity_matrix = get_intensity_matrix(pixels, 3)
    intensity_matrix = normalize_intensity_matrix(intensity_matrix)
    color_matrix = get_color_matrix(pixels)

    for i in range(len(intensity_matrix)):
        offset = 1
        for j in range(len(intensity_matrix[0])):
            intensity = intensity_matrix[i][j]
            symbol_index = int(intensity / MAX_PIXEL_VALUE * len(ASCII_CHARS)) - 1
            symbol_index = symbol_index + 1 if symbol_index < 0 else symbol_index
            asciiStr = ASCII_CHARS[symbol_index] + ASCII_CHARS[symbol_index] + ASCII_CHARS[symbol_index]
            if option == 1:
                color = color_matrix[i][j]
                media.addstr(i + 1, offset, asciiStr, curses.color_pair(color))
            else:
                media.addstr(i + 1, offset, asciiStr, curses.color_pair(0))
            offset += 3

    media.refresh()

def subtitle_show(subs, tstamp_ms):
    """Function to get subtitles of current frame and display them"""
    parts = subs.slice(starts_before={'milliseconds': int(tstamp_ms)}, ends_after={'milliseconds': int(tstamp_ms)})
    captions.addstr(0, 1, "Captions")
    captions.move(1, 1)
    for part in parts:
        captions.addstr(part.text, curses.A_BOLD)

    captions.refresh()

def get_pixel_matrix(image):
    """Function to get image from the media file and change its dimensions to fit the terminal, then turning it into pixel matrix."""
    image = image.convert("HSV")
            
    # current row and column size definitions
    ac_row, ac_col = image.size
    # d1 and d2 are the width and height of image resp
    size = media.getmaxyx()
    d2 = min((size[0] - 2) - 3, int((ac_col * (size[1] - 2)) / ac_row))
    d1 = min(int((size[1] - 2) / 3), int((ac_row * d2) / ac_col))

    # set image to determined d1 and column size
    im = image.resize((d1, d2))
    pixels = list(im.getdata())
    return [pixels[i:i+im.width] for i in range(0, len(pixels), im.width)]

def get_color_matrix(pixels):
    """Function to get the colour codes (ANSI escape sequences) from RGB values of pixel."""
    color_matrix = []
    for row in pixels:
        color_matrix_row = []
        for p in row:
            # Convert values to percentages and normalize
            hue = (p[0] / 255) * 179
            sat = (p[1] / 255) * 100
            cNum = 0
            if sat >= 30:
                if (0 <= hue and hue < rUpperHue) or (hue <= 180 and hue > rLowerHue):
                    cNum = 4
                if hue <= gUpperHue and hue > gLowerHue:
                    cNum = 5
                if hue <= gLowerHue and hue > rUpperHue:
                    cNum = 1
                if hue <= bUpperHue and hue > bLowerHue:
                    cNum = 6
                if hue <= bLowerHue and hue > gUpperHue:
                    cNum = 3
                if hue <= rLowerHue and hue > bUpperHue:
                    cNum = 2
            color_matrix_row.append(cNum)
        color_matrix.append(color_matrix_row)
    return color_matrix

def get_intensity_matrix(pixels, option):
    """Function to set the measure of brightness to be used depending upon the
    option, choose between three measures namely luminance,
    lightness and average pixel values
    """
    intensity_matrix = []
    for row in pixels:
        intensity_matrix_row = []
        for p in row:
            intensity = 0
            intensity = p[2]
            # if option == 1:
            #     intensity = ((p[0] + p[1] + p[2]) / 3.0)
            # elif option == 2:
            #     intensity = (max(p[0], p[1], p[2]) + min(p[0], p[1], p[2])) / 2
            # elif option == 3:
            #     intensity = (0.299 * p[0] * p[0] + 0.587 * p[1] * p[1] + 0.114 * p[2] * p[2]) ** 0.5
            # else:
            #     raise Exception("Unrecognised intensity option: %d" % option)
            intensity_matrix_row.append(intensity)
        intensity_matrix.append(intensity_matrix_row)

    return intensity_matrix

def normalize_intensity_matrix(intensity_matrix):
    """Function to normalize the intensity matrix so that values fall between acceptable limits."""
    normalized_intensity_matrix = []
    max_pixel = max(map(max, intensity_matrix))
    min_pixel = min(map(min, intensity_matrix))
    for row in intensity_matrix:
        rescaled_row = []
        for p in row:
            denm = float(max_pixel - min_pixel)
            if denm == 0:
                denm = 1
            r = MAX_PIXEL_VALUE * (p - min_pixel) / denm
            rescaled_row.append(r)
        normalized_intensity_matrix.append(rescaled_row)

    return normalized_intensity_matrix

def print_from_image(filename, option):
    """Function to take in an image & use its RGB values to decide upon an ASCII character
    to represent it. This ASCII character will be based upon the brightness
    measure calculated

    Manager function.
    """
    try:
        with Image.open(filename) as image:
            pixels = get_pixel_matrix(image)
            vid_render(pixels, 0, len(pixels), option)
    except OSError: 
        print("Could not open image file!")

def read_media_sub(vidfile, subfile, option):
    """Function to read the media file and pass on data to rendering functions frame by frame."""
    vidcap = cv2.VideoCapture(vidfile)
    subs = pysrt.open(subfile)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    while vidcap.isOpened():
        # read frames from the image
        success, image = vidcap.read()
        if not success:
            break
        dur = time.process_time()
        cv2.imwrite("./data/frame.jpg", image)
        print_from_image("./data/frame.jpg", option)
        subtitle_show(subs, vidcap.get(cv2.CAP_PROP_POS_MSEC))
        dur = (time.process_time() - dur)
        dur *= 1000
        if (round(1000/fps - dur) >= 0):
            curses.napms(round(1000/fps - dur))
    vidcap.release()
    cv2.destroyAllWindows()

def read_media(vidfile, option):
    """Function to read the media file and pass on data to rendering functions frame by frame."""
    vidcap = cv2.VideoCapture(vidfile)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    while vidcap.isOpened():
        # read frames from the image
        success, image = vidcap.read()
        if not success:
            break
        dur = time.process_time()
        cv2.imwrite("./data/frame.jpg", image)
        print_from_image("./data/frame.jpg", option)
        dur = (time.process_time() - dur)
        dur *= 1000
        if (round(1000/fps - dur) >= 0):
            curses.napms(round(1000/fps - dur))
    vidcap.release()
    cv2.destroyAllWindows()

stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
curses.start_color()
curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)

# defining hsv color limits
# somewhat magic numbers, obtained by opening a color palette and observing the hue at which a color can be described as green
# same procedure for all numbers
gLowerHue = 36
gUpperHue = 80
rLowerHue = 159
rUpperHue = 14
bLowerHue = 104
bUpperHue = 138

if len(sys.argv) == 3:
    beginX = 0; beginY = 0
    height = curses.LINES; width = curses.COLS
    media = curses.newwin(height - 1, width - 1, beginY, beginX)
    media.border(0, 0, 0, 0, 0, 0, 0, 0)
    vidfile = sys.argv[1]
    colored_output = int(sys.argv[2])
    read_media(vidfile, colored_output)
else:
    beginX = 0; beginY = 0
    height = curses.LINES - 5; width = curses.COLS
    media = curses.newwin(height, width, beginY, beginX)
    media.border(0, 0, 0, 0, 0, 0, 0, 0)
    beginX = 0; beginY = curses.LINES - 5
    height = 5; width = curses.COLS
    captions = curses.newwin(height, width, beginY, beginX)
    captions.border(0, 0, 0, 0, 0, 0, 0, 0)
    vidfile = sys.argv[1]
    subfile = sys.argv[2]
    colored_output = int(sys.argv[3])
    read_media_sub(vidfile, subfile, colored_output)

media.getch()
curses.nocbreak()
curses.echo()
curses.endwin()