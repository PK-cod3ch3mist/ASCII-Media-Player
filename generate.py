import sys
<<<<<<< HEAD
<<<<<<< HEAD
import keyboard
=======
>>>>>>> parent of d4052fc (add play/pause video commands)
=======
>>>>>>> parent of d4052fc (add play/pause video commands)
from PIL import Image
import numpy as np
import os
import cv2
import pysrt

ASCII_CHARS = "`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
MAX_PIXEL_VALUE = 255

def vid_render(st_matrix, st, ed, option):
    pixels = [st_matrix[i][:] for i in range (st, ed)]
    # CONFIG OPTION - intensity measure
    intensity_matrix = get_intensity_matrix(pixels, 3)
    intensity_matrix = normalize_intensity_matrix(intensity_matrix)
    color_matrix = get_color_matrix(pixels)

    ascii_matrix = []
    for i in range(len(intensity_matrix)):
        ascii_row = []
        for j in range(len(intensity_matrix[0])):
            intensity = intensity_matrix[i][j]
            symbol_index = int(intensity / MAX_PIXEL_VALUE * len(ASCII_CHARS)) - 1
            symbol_index = symbol_index + 1 if symbol_index < 0 else symbol_index
            if option == 1:
                color = color_matrix[i][j]
                ascii_row.append(color)
            ascii_row.append(ASCII_CHARS[symbol_index])
        ascii_matrix.append(ascii_row)

    print_matrix(ascii_matrix, st)

def subtitle_show(subs, tstamp_ms):
    # minutes = 
    parts = subs.slice(starts_before={'milliseconds': int(tstamp_ms)}, ends_after={'milliseconds': int(tstamp_ms)})
    size = os.get_terminal_size()
    print("\033[" + str(size.lines - 2) + ";1H", end='')
    for i in range(0, 2):
        print(" " * int(size.columns))
    print("\033[" + str(size.lines - 2) + ";1H", end='')
    for part in parts:
        print(part.text)

def get_pixel_matrix(image):
    image = image.convert("RGB")
            
    # current row and column size definitions
    ac_row, ac_col = image.size
    # d1 and d2 are the width and height of image resp
    size = os.get_terminal_size()
    d2 = min(size.lines - 3, int((ac_col * size.columns) / ac_row))
    d1 = min(int(size.columns / 3), int((ac_row * d2) / ac_col))

    # set image to determined d1 and column size
    im = image.resize((d1, d2))
    pixels = list(im.getdata())
    return [pixels[i:i+im.width] for i in range(0, len(pixels), im.width)]

def print_matrix(ascii_matrix, st):
    count = 1
    for line in ascii_matrix:
        line_extended = [p + p + p for p in line]
        print("\033[" + str(st + count)+ ";1H", end='')
        print("".join(line_extended))
        count += 1

def get_color_matrix(pixels):
    color_matrix = []
    for row in pixels:
        color_matrix_row = []
        for p in row:
            color_matrix_row.append("\033[38;2;" + str(p[0]) + ";" + str(p[1]) + ";" + str(p[2]) + "m")
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

            print("\033[40m\033[37m", end='')
            vid_render(pixels, 0, len(pixels), option)
            print("\033[0m", end='')
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
            if keyboard.is_pressed("alt+s"):
                keyboard.wait("s")
            # CONFIG OPTION - contrast and brightness
            # enhance the image (increase contrast and brightness) for terminal display
            # TURN OFF (by commenting) IF YOU PREFER THE ORIGINAL COLOURS
            if option == 1:
                image = cv2.convertScaleAbs(image, alpha=1.25, beta=50)
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
<<<<<<< HEAD
<<<<<<< HEAD
            if keyboard.is_pressed("alt+s"):
                keyboard.wait("s")

=======
>>>>>>> parent of d4052fc (add play/pause video commands)
=======
>>>>>>> parent of d4052fc (add play/pause video commands)
            # CONFIG OPTION - contrast and brightness
            # enhance the image (increase contrast and brightness) for terminal display
            # TURN OFF (by commenting) IF YOU PREFER THE ORIGINAL COLOURS
            if option == 1:
                image = cv2.convertScaleAbs(image, alpha=1.25, beta=50)
            cv2.imwrite("./data/frame.jpg", image)
            i = 0
            print_from_image("./data/frame.jpg", option)
            continue
        i += 1
    vidcap.release()
    cv2.destroyAllWindows()

if len(sys.argv) == 3:
    vidfile = sys.argv[1]
    colored_output = int(sys.argv[2])
    read_media(vidfile, colored_output)
else:
    vidfile = sys.argv[1]
    subfile = sys.argv[2]
    colored_output = int(sys.argv[3])
    read_media_sub(vidfile, subfile, colored_output)
