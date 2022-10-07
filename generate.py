import sys
from PIL import Image
import time
from cv2 import cv2
import pysrt
import curses
import numpy as np

class AMP():
    def __init__(self, chars_id=3, rLH=159, rUH=14, gLH=36, gUH=80, bLH=104, bUH=138):   
        ASCII_CHAR_ARRAY = (" .:-=+*#%@", " .,:ilwW", " ▏▁░▂▖▃▍▐▒▀▞▚▌▅▆▊▓▇▉█", " `^|1aUBN", " .`!?xyWN")
        
        self.ASCII_CHARS = ASCII_CHAR_ARRAY[chars_id]
        self.MAX_PIXEL_VALUE = 255
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)

        # defining hsv color limits
        # somewhat magic numbers, obtained by opening a color palette and observing the hue at which a color can be described as green
        # same procedure for all numbers
        self.gLowerHue = gLH
        self.gUpperHue = gUH
        self.rLowerHue = rLH
        self.rUpperHue = rUH
        self.bLowerHue = bLH
        self.bUpperHue = bUH


    def vid_render(self, pixels, coloring = True):
        """Function to merge and render the ASCII output to the terminal.
        @param pixels - Pixel matrix of an image
        @param coloring - Option to switch between color and bnw output.
        """
        self.media.addstr(0, 1, "Video Playback")
        intensity_matrix = pixels[:, :, 2]
        intensity_matrix = self.normalize_intensity_matrix(intensity_matrix)
        color_matrix = self.get_color_matrix(pixels)

        for i in range(len(intensity_matrix)):
            offset = 1
            for j in range(len(intensity_matrix[0])):
                symbol_index = int(intensity_matrix[i][j] / self.MAX_PIXEL_VALUE * len(self.ASCII_CHARS)) - 1
                symbol_index += int(symbol_index < 0)
                asciiStr = self.ASCII_CHARS[symbol_index] * 3
                self.media.addstr(i + 1, offset, asciiStr, curses.color_pair(color_matrix[i][j] if coloring else 0))
                offset += 3

        self.media.refresh()

    def subtitle_show(self, subs, tstamp_ms):
        """Function to get subtitles of current frame and display them"""
        self.captions.clear()
        self.captions.border(' ', ' ', 0, 0, ' ', ' ', ' ', ' ')
        parts = subs.slice(starts_before={'milliseconds': int(tstamp_ms)}, ends_after={'milliseconds': int(tstamp_ms)})
        self.captions.addstr(0, 1, "Captions")
        self.captions.move(1, 0)
        for part in parts:
            self.captions.addstr(part.text, curses.A_BOLD)

        self.captions.refresh()


    def get_pixel_matrix(self, image):
        """Function to get image from the self.media file and change its dimensions to fit the terminal, then turning it into pixel matrix."""
        image = image.convert("HSV")
                
        # current row and column size definitions
        ac_row, ac_col = image.size
        # d1 and d2 are the width and height of image resp
        size = self.media.getmaxyx()
        d2 = min((size[0] - 2) - 3, int((ac_col * (size[1] - 2)) / ac_row))
        d1 = min(int((size[1] - 2) / 3), int((ac_row * d2) / ac_col))

        # set image to determined d1 and column size
        im = image.resize((d1, d2))
        pixels = np.reshape(im.getdata(), (d2, d1, 3))
        with open('error.txt', 'a') as f:
            print(pixels.shape, file=f)
        return pixels


    def get_color_matrix(self, pixels):
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
                    if (0 <= hue and hue < self.rUpperHue) or (hue <= 180 and hue > self.rLowerHue):
                        cNum = 4
                    if hue <= self.gUpperHue and hue > self.gLowerHue:
                        cNum = 5
                    if hue <= self.gLowerHue and hue > self.rUpperHue:
                        cNum = 1
                    if hue <= self.bUpperHue and hue > self.bLowerHue:
                        cNum = 6
                    if hue <= self.bLowerHue and hue > self.gUpperHue:
                        cNum = 3
                    if hue <= self.rLowerHue and hue > self.bUpperHue:
                        cNum = 2
                color_matrix_row.append(cNum)
            color_matrix.append(color_matrix_row)
        return np.array(color_matrix)


    def normalize_intensity_matrix(self, intensity_matrix):
        """Function to normalize the intensity matrix so that values fall between acceptable limits."""
        maxval, minval = intensity_matrix.max(), intensity_matrix.min()
        if (maxval != minval): intensity_matrix = (intensity_matrix - minval) * self.MAX_PIXEL_VALUE / maxval
        return intensity_matrix


    def print_from_image(self, filename, coloring):
        """Function to take in an image & use its RGB values to decide upon an ASCII character
        to represent it. This ASCII character will be based upon the brightness
        measure calculated

        Manager function.
        """
        try:
            with Image.open(filename) as image:
                pixels = self.get_pixel_matrix(image)
                self.vid_render(pixels, coloring)
        except OSError: 
            print("Could not open image file!")


    def read_media_sub(self, vidfile, coloring, subfile=''):
        """Function to read the self.media file and pass on data to rendering functions frame by frame."""
        vidcap = cv2.VideoCapture(vidfile)
        if subfile: subs = pysrt.open(subfile,encoding='latin-1')
        fps = vidcap.get(cv2.CAP_PROP_FPS)
        while vidcap.isOpened():
            # read frames from the image
            success, image = vidcap.read()
            if not success: break
            dur = time.process_time()
            cv2.imwrite("./data/frame.jpg", image)
            self.print_from_image("./data/frame.jpg", coloring)
            if subfile: self.subtitle_show(subs, vidcap.get(cv2.CAP_PROP_POS_MSEC))
            dur = (time.process_time() - dur) * 1000
            if (round(1000/fps - dur) >= 0): curses.napms(round(1000/fps - dur))
        vidcap.release()
        cv2.destroyAllWindows()


    def main(self, argv):
        beginX = 0; beginY = 0
        vidfile = argv[1]
        colored_output = int(argv[-1])
                
        if len(argv) == 3: height = curses.LINES; width = curses.COLS
        else: height = curses.LINES - 5; width = curses.COLS

        self.media = curses.newwin(height, width, beginY, beginX)
        self.media.border(0, 0, 0, 0, 0, 0, 0, 0)

        if len(argv) == 3: subfile = ''
        else:
            beginX = 0; beginY = curses.LINES - 5
            height = 5; width = curses.COLS
            self.captions = curses.newwin(height, width, beginY, beginX)
            self.captions.border(0, 0, 0, 0, 0, 0, 0, 0)
            subfile = argv[2]

        self.read_media_sub(vidfile,colored_output,subfile)

        self.media.getch()

def run(stdscr):
    obj = AMP()
    obj.main(sys.argv)

curses.wrapper(run)