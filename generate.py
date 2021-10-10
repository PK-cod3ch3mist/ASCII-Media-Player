import sys
from PIL import Image
import numpy as np
import os
import cv2

ASCII_CHARS = "`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
MAX_PIXEL_VALUE = 255

def set_brightness(r, g, b, option):
    """Set the measure of brightness to be used depending upon the
    option chosen, we chose between three measures namely luminance,
    lightness and average pixel values
    """
    brightness = 0
    if option == 1:
        # average of RGB as brightness
        brightness = (r + g + b) / 3
    elif option == 2:
        # lightness of pixel as brightness
        brightness = (max(r, g, b) + min(r, g, b)) / 2
    elif option == 3:
        # luminance being square root of weighted RGB values (weighted according to the perception of the human eye)
        brightness = (0.299 * r * r + 0.587 * g * g + 0.114 * b * b) ** 0.5
    return brightness

def print_matrix(ascii_matrix):
    for line in ascii_matrix:
        line_extended = [p + p + p for p in line]
        print("".join(line_extended))

def rgbx_approx(red, green, blue, x):
    threshold = (x + 1) * 255 / 3
    r = 1 if red > threshold else 0
    g = 1 if green > threshold else 0
    b = 1 if blue > threshold else 0
    return (r, g, b)

def rgbi_to_rgb24(r, g, b, i):
    red = (2 * r + i) * 255 / 3
    green = (2 * g + i) * 255 / 3
    blue = (2 * b + i) * 255 / 3
    return (red, green, blue)

def color_distance(red_a, green_a, blue_a, red_b, green_b, blue_b):
    d_red = red_a - red_b
    d_green = green_a - green_b
    d_blue = blue_a - blue_b
    return (d_red * d_red) + (d_green * d_green) + (d_blue * d_blue)

def rgbi_approx(red, green, blue):
    r0, g0, b0 = rgbx_approx(red, green, blue, 0)
    r1, g1, b1 = rgbx_approx(red, green, blue, 1)

    red0, green0, blue0 = rgbi_to_rgb24(r0, g0, b0, 0)
    red1, green1, blue1 = rgbi_to_rgb24(r1, g1, b1, 1)

    d0 = color_distance(red, green, blue, red0, green0, blue0)
    d1 = color_distance(red, green, blue, red1, green1, blue1)

    if d0 <= d1:
        return (r0, g0, b0, 0)
    return (r1, g1, b1, 1)

def find_closest_color(pixel):
    red, green, blue = pixel
    r, g, b, i = rgbi_approx(red, green, blue)
    if i == 1:
        # increase the values by one, to signal the dither algo to play more effect on the surrounding areas
        r = 2 if r == 1 else 0
        g = 2 if g == 1 else 0
        b = 2 if b == 1 else 0
    return (r, g, b)

def convert_color_to_code(r, g, b):
    if r + g + b == 3:
        return "\033[37m"
    if r + g + b == 6:
        return "\033[97m"
    if r + g + b == 0:
        return "\033[30m"
    if r == 1:
        if g == 1:
            return "\033[33m"
        if b == 1:
            return "\033[35m"
        return "\033[31m"
    if g == 1:
        if b == 1:
            return "\033[36m"
        return "\033[32m"
    if b == 1:
        return "\033[34m"
    if r == 2:
        if g == 2:
            return "\033[93m"
        if b == 2:
            return "\033[95m"
        return "\033[91m"
    if g == 2:
        if b == 2:
            return "\033[96m"
        return "\033[92m"
    return "\033[94m"

def dither(pixels, d1, d2):
    """Floyd-Steinberg Dithering implementation
    to correctly encode the RGB data to B&W and set pixel data
    """
    output = pixels

    for y in range(1, d2 - 1):
        for x in range(1, d1 - 1):
            oldpix = output[y, x]
            newpix = find_closest_color(oldpix)
            error = (0, 0, 0)
            error = tuple(np.subtract(oldpix, newpix))
            output[y, x] = newpix

            output[y    , x + 1] = tuple([np.add(output[y    , x + 1], tuple(int(x * 7/16) for x in error))])
            output[y + 1, x - 1] = tuple([np.add(output[y + 1, x - 1], tuple(int(x * 3/16) for x in error))])
            output[y + 1, x    ] = tuple([np.add(output[y + 1, x    ], tuple(int(x * 5/16) for x in error))])
            output[y + 1, x + 1] = tuple([np.add(output[y + 1, x + 1], tuple(int(x * 1/16) for x in error))])

    return (output)

def print_from_image(filename):
    """Taking in an image, use its RGB values to decide upon an ASCII character
    to represent it. This ASCII character will be based upon the brightness
    measure calculated
    """
    try:
        with Image.open(filename) as im:
            im = im.convert("RGB")
            
            # current row and column size definitions
            # TODO: make this dynamic to set according to terminals current size
            ac_row, ac_col = im.size
            # d1 and d2 are the width and height of image resp
            d2 = 36
            d1 = min(52, int((ac_row * d2) / ac_col))

            # set image to determined d1 and column size
            small_im = im.resize((d1, d2))
            pixels = small_im.load()

            # pixels = dither(pixels, d1, d2)

            ascii_matrix = []
            for i in range(d2):
                ascii_row = []
                for j in range(d1):
                    r, g, b = pixels[j, i]
                    brightness = set_brightness(r, g, b, 2)
                    symbol_index = int((brightness / MAX_PIXEL_VALUE) * len(ASCII_CHARS)) - 1
                    r, g, b = find_closest_color(pixels[j, i])
                    ascii_row.append(convert_color_to_code(r, g, b))
                    ascii_row.append(ASCII_CHARS[symbol_index])
                ascii_matrix.append(ascii_row)

            print_matrix(ascii_matrix)
    except OSError: 
        print("Could not open image file!")

def read_media(infile):
    vidcap = cv2.VideoCapture(infile)
    i = 0
    frame_skip = 0
    while vidcap.isOpened():
        success, image = vidcap.read()
        if not success:
            break
        if i > frame_skip - 1:
            # image = cv2.convertScaleAbs(image, alpha=1.25, beta=60)
            cv2.imwrite("frame.jpg", image)
            i = 0
            print("\033[40m", end='')
            print_from_image("frame.jpg")
            print("\033[0m", end='')
            continue
        i += 1
    vidcap.release()
    cv2.destroyAllWindows()

infile = sys.argv[1];
read_media(infile)