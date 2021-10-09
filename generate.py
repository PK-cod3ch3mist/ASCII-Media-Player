import sys
from PIL import Image
import numpy as np
import os
import cv2

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
                    luminance1 = 0.2126 * r + 0.7152 * g + 0.0722 * b
                    luminance2 = 0.299 * r + 0.587 * g + 0.114 * b
                    luminance3 = (0.299 * r * r + 0.587 * g * g + 0.114 * b * b) ** 0.5
                    # average_rgb = (r + g + b) / 3;
                    # lightness = (max(r, g, b) + min(r, g, b)) / 2;
                    symbol_index = int((luminance3 / MAX_PIXEL_VALUE) * len(ASCII_CHARS)) - 1
                    colour = "\033[38;2;" + str(r) + ";" + str(g) + ";" + str(b) + "m"
                    ascii_row.append(colour)
                    ascii_row.append(ASCII_CHARS[symbol_index])
                    # ascii_row.append("$")
                ascii_matrix.append(ascii_row)
            for line in ascii_matrix:
                line_extended = [p + p + p for p in line]
                print("".join(line_extended))
    except OSError: 
        print("Could not open image file!")

vidcap = cv2.VideoCapture(infile)
i = 0
frame_skip = 1
while vidcap.isOpened():
    success, image = vidcap.read()
    if not success:
        break
    if i > frame_skip - 1:
        image = cv2.convertScaleAbs(image, alpha=1.5, beta=70)
        cv2.imwrite("frame.jpg", image)
        i = 0
        print("\033[48;2;0;0;0m", end='')
        print_from_image("frame.jpg")
        print("\033[0m", end='')
        continue
    i += 1

vidcap.release()
cv2.destroyAllWindows()