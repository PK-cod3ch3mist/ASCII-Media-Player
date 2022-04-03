import sys
from PIL import Image
import numpy as np
import os
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
    # minutes = 
    parts = subs.slice(starts_before={'milliseconds': int(tstamp_ms)}, ends_after={'milliseconds': int(tstamp_ms)})
    captions.addstr(0, 1, "Captions")
    captions.move(1, 1)
    for part in parts:
        captions.addstr(part.text, curses.A_BOLD)

    captions.refresh()

def get_pixel_matrix(image):
    image = image.convert("RGB")
            
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
    color_matrix = []
    for row in pixels:
        color_matrix_row = []
        for p in row:
            r = round(p[0]/127)
            g = round(p[1]/127)
            b = round(p[2]/127)
            cNum = 0
            if r + g + b != 3:
                if r == 1 and g == 1:
                    cNum = 1
                elif r == 1 and b == 1:
                    cNum = 2
                elif g == 1 and b == 1:
                    cNum = 3
                elif r == 1:
                    cNum = 4
                elif g == 1:
                    cNum = 5
                elif b == 1:
                    cNum = 6
            color_matrix_row.append(cNum)
        color_matrix.append(color_matrix_row)
    return color_matrix

def get_intensity_matrix(pixels, option):
    """Set the measure of brightness to be used depending upon the
    option chosen, we chose between three measures namely luminance,
    lightness and average pixel values
    """
    intensity_matrix = []
    for row in pixels:
        intensity_matrix_row = []
        for p in row:
            intensity = 0
            if option == 1:
                intensity = ((p[0] + p[1] + p[2]) / 3.0)
            elif option == 2:
                intensity = (max(p[0], p[1], p[2]) + min(p[0], p[1], p[2])) / 2
            elif option == 3:
                intensity = (0.299 * p[0] * p[0] + 0.587 * p[1] * p[1] + 0.114 * p[2] * p[2]) ** 0.5
            else:
                raise Exception("Unrecognised intensity option: %d" % option)
            intensity_matrix_row.append(intensity)
        intensity_matrix.append(intensity_matrix_row)

    return intensity_matrix

def normalize_intensity_matrix(intensity_matrix):
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
    """Taking in an image, use its RGB values to decide upon an ASCII character
    to represent it. This ASCII character will be based upon the brightness
    measure calculated
    """
    try:
        with Image.open(filename) as image:
            pixels = get_pixel_matrix(image)
            vid_render(pixels, 0, len(pixels), option)
    except OSError: 
        print("Could not open image file!")

def read_media_sub(vidfile, subfile, option):
    vidcap = cv2.VideoCapture(vidfile)
    subs = pysrt.open(subfile)
    i = 0
    # control frame rate in image
    frame_skip = 0
    os.system("clear")
    while vidcap.isOpened():
        # read frames from the image
        success, image = vidcap.read()
        if not success:
            break
        if i > frame_skip - 1:
            cv2.imwrite("./data/frame.jpg", image)
            i = 0
            print_from_image("./data/frame.jpg", option)
            subtitle_show(subs, vidcap.get(cv2.CAP_PROP_POS_MSEC))
            continue
        i += 1
    vidcap.release()
    cv2.destroyAllWindows()

def read_media(vidfile, option):
    vidcap = cv2.VideoCapture(vidfile)
    i = 0
    # control frame rate in image
    frame_skip = 0
    os.system("clear")
    while vidcap.isOpened():
        # read frames from the image
        success, image = vidcap.read()
        if not success:
            break
        if i > frame_skip - 1:
            cv2.imwrite("./data/frame.jpg", image)
            i = 0
            print_from_image("./data/frame.jpg", option)
            continue
        i += 1
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
if len(sys.argv) == 3:
    beginX = 1; beginY = 1
    height = curses.LINES - 1; width = curses.COLS - 1
    media = curses.newwin(height - 1, width - 1, beginY, beginX)
    media.border(0, 0, 0, 0, 0, 0, 0, 0)
    # vidfile = sys.argv[1]
    # colored_output = int(sys.argv[2])
    # read_media(vidfile, colored_output)
else:
    beginX = 1; beginY = 1
    height = curses.LINES - 7; width = curses.COLS - 2
    media = curses.newwin(height, width, beginY, beginX)
    media.border(0, 0, 0, 0, 0, 0, 0, 0)
    beginX = 1; beginY = curses.LINES - 6
    height = 5; width = curses.COLS - 2
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