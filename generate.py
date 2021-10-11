import sys
from PIL import Image
import numpy as np
import os
import cv2

ASCII_CHARS = "`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
MAX_PIXEL_VALUE = 255

def set_brightness(pixel, option):
    """Set the measure of brightness to be used depending upon the
    option chosen, we chose between three measures namely luminance,
    lightness and average pixel values
    """
    r, g, b = pixel
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

def find_color_rgb24(pixel):
    red, green, blue = pixel
    return "\033[38;2;" + str(red) + ";" + str(green) + ";" + str(blue) + "m"

# def find_color_rgb(r, g, b):
#     if r + g + b == 765:
#         return "\033[37m"
#     if r + g + b == 0:
#         return "\033[30m"
#     if r == 255:
#         if g == 255:
#             return "\033[33m"
#         if b == 255:
#             return "\033[35m"
#         return "\033[31m"
#     if g == 255:
#         if b == 255:
#             return "\033[36m"
#         return "\033[32m"
#     return "\033[34m"

# def dither(colour_matrix, d1, d2):
#     """Floyd-Steinberg Dithering implementation
#     to correctly encode the RGB data to B&W and set pixel data
#     """

#     output = colour_matrix

#     for y in range(1, d2 - 1):
#         for x in range(1, d1 - 1):
#             oldpix = output[y][x]
#             newpix = round(oldpix/255) * 255
#             error = oldpix - newpix
#             output[y][x] = newpix

#             output[y    ][x + 1] += (7/16.0 * error)
#             output[y + 1][x - 1] += (3/16.0 * error)
#             output[y + 1][x    ] += (5/16.0 * error)
#             output[y + 1][x + 1] += (1/16.0 * error)

#     return (output)

def print_from_image(filename, option):
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

            # if option == 0:
            #     # 4-bit color terminal
            #     blue_matrix = []
            #     green_matrix = []
            #     red_matrix = []

            #     for i in range(d2):
            #         blue_row = []
            #         green_row = []
            #         red_row = []
            #         for j in range(d1):
            #             r, g, b = pixels[j, i]
            #             blue_row.append(b)
            #             green_row.append(g)
            #             red_row.append(r)

            #         blue_matrix.append(blue_row)
            #         red_matrix.append(red_row)
            #         green_matrix.append(green_row)

            #     blue_matrix = dither(blue_matrix, d1, d2)
            #     green_matrix = dither(green_matrix, d1, d2)
            #     red_matrix = dither(red_matrix, d1, d2)

            ascii_matrix = []
            for i in range(d2):
                ascii_row = []
                for j in range(d1):
                    brightness = set_brightness(pixels[j, i], 3)
                    symbol_index = int((brightness / MAX_PIXEL_VALUE) * len(ASCII_CHARS)) - 1
                    if option == 1:
                        color = find_color_rgb24(pixels[j, i])
                        ascii_row.append(color)
                    ascii_row.append(ASCII_CHARS[symbol_index])
                ascii_matrix.append(ascii_row)

            print("\033[40m\033[37m", end='')
            print_matrix(ascii_matrix)
            print("\033[0m", end='')
    except OSError: 
        print("Could not open image file!")

def read_media(infile, option):
    vidcap = cv2.VideoCapture(infile)
    i = 0
    # control frame rate in image
    frame_skip = 0
    while vidcap.isOpened():
        # read frames from the image
        success, image = vidcap.read()
        if not success:
            break
        if i > frame_skip - 1:
            # enhance the image for terminal display
            if option == 1:
                image = cv2.convertScaleAbs(image, alpha=1.25, beta=50)
            cv2.imwrite("frame.jpg", image)
            i = 0
            print_from_image("frame.jpg", option)
            continue
        i += 1
    vidcap.release()
    cv2.destroyAllWindows()

infile = sys.argv[1]
colored_output = int(sys.argv[2])
read_media(infile, colored_output)