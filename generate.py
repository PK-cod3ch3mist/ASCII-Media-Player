import sys
from PIL import Image
import numpy as np
import os
import cv2
import time

ASCII_CHARS = "`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
MAX_PIXEL_VALUE = 255

infile = sys.argv[1];

def print_from_image(filename):
    try:
        with Image.open(filename) as im:
            im = im.convert("RGB")
            ac_row, ac_col = im.size
            col = 36
            row = min(52, int((ac_row * col) / ac_col))
            small_im = im.resize((row, col))
            pixels = small_im.load()
            ascii_matrix = []
            for i in range(col):
                ascii_row = []
                for j in range(row):
                    r, g, b = pixels[j, i]
                    luminosity = 0.21 * r + 0.72 * g + 0.07 * b;
                    # average_rgb = (r + g + b) / 3;
                    # lightness = (max(r, g, b) + min(r, g, b)) / 2;
                    symbol_index = int((luminosity / MAX_PIXEL_VALUE) * len(ASCII_CHARS)) - 1
                    colour = "\033[38;2;" + str(r) + ";" + str(g) + ";" + str(b) + "m"
                    ascii_row.append(colour)
                    ascii_row.append(ASCII_CHARS[symbol_index])
                    ascii_row.append("\033[0m")
                ascii_matrix.append(ascii_row)
            for line in ascii_matrix:
                line_extended = [p + p + p for p in line]
                print("".join(line_extended))
    except OSError: 
        print("Could not open image file!")

vidcap = cv2.VideoCapture(infile)
i = 0
frame_skip = 0
while vidcap.isOpened():
    success, image = vidcap.read()
    if not success:
        break
    if i > frame_skip - 1:
        cv2.imwrite("frame.jpg", image)
        i = 0
        print_from_image("frame.jpg")
        continue
    i += 1

vidcap.release()
cv2.destroyAllWindows()