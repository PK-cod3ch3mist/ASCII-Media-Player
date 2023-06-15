import sys
import time
import cv2 as cv
import pysrt
import curses
import numpy as np
from scipy import signal
import os

startSize = os.get_terminal_size()
startSize2 = os.get_terminal_size()

class AMP:
    def __init__(self, chars_id=3, rLH=159, rUH=14, gLH=36, gUH=80, bLH=104, bUH=138):
        ASCII_CHAR_ARRAY = (
            " .:-=+*#%@",
            " .,:ilwW",
            " ▏▁░▂▖▃▍▐▒▀▞▚▌▅▆▊▓▇▉█",
            " `^|1aUBN",
            " .`!?xyWN",
        )

        self.ASCII_CHARS = ASCII_CHAR_ARRAY[chars_id]
        self.MAX_PIXEL_VALUE = 255
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)

        # defining hsv colour limits
        # somewhat magic numbers, obtained by opening a colour palette and observing the hue at which a colour can be described as green
        # same procedure for all numbers
        self.gLowerHue = gLH
        self.gUpperHue = gUH
        self.rLowerHue = rLH
        self.rUpperHue = rUH
        self.bLowerHue = bLH
        self.bUpperHue = bUH

        self.SPACEBAR_KEY = (32,)
        self.QUIT_KEYS = (113, 81)

    def vid_render(self, pixels, coloring=True, edgeOnly=False):
        """Function to merge and render the ASCII output to the terminal.

        pixels - Pixel matrix of an image
        
        colouring - Option to switch between colour and bnw output.
        """
        self.media.addstr(0, 1, "Video Playback")
        intensity_matrix = pixels[:, :, 2]
        if edgeOnly:
            sharp_matrix = self.get_edge_matrix(intensity_matrix)
            np.clip(sharp_matrix, 0, 255, sharp_matrix)
        else:
            sharp_matrix = intensity_matrix - self.normalize_intensity_matrix(
                self.get_edge_matrix(intensity_matrix)
            )
            sharp_matrix = self.normalize_intensity_matrix(sharp_matrix)
        color_matrix = self.get_color_matrix(pixels)

        for i in range(len(sharp_matrix)):
            offset = 1
            for j in range(len(sharp_matrix[0])):
                symbol_index = (
                    int(sharp_matrix[i][j] / self.MAX_PIXEL_VALUE * len(self.ASCII_CHARS)) - 1
                )
                symbol_index += int(symbol_index < 0)
                asciiStr = self.ASCII_CHARS[symbol_index] * 3
                self.media.addstr(
                    i + 1,
                    offset,
                    asciiStr,
                    curses.color_pair(color_matrix[i][j] if coloring else 0),
                )
                offset += 3

        self.media.refresh()

    def get_edge_matrix(self, img):
        """Function to get the edges of the current frame for display"""
        laplace_op = np.array([[1.0, 1.0, 1.0], [1.0, -8.0, 1.0], [1.0, 1.0, 1.0]])

        laplace_out = signal.convolve2d(img, laplace_op, "same")
        return laplace_out

    def subtitle_show(self, subs, tstamp_ms):
        """Function to get subtitles of current frame and display them"""
        parts = subs.slice(
            starts_before={"milliseconds": int(tstamp_ms)},
            ends_after={"milliseconds": int(tstamp_ms)},
        )
        if parts:
            self.captions.clear()
            self.captions.border(" ", " ", 0, 0, " ", " ", " ", " ")

        self.captions.addstr(0, 1, "Captions")
        self.captions.move(1, 0)
        for part in parts:
            self.captions.addstr(part.text, curses.A_BOLD)

        self.captions.refresh()

    def get_pixel_matrix(self, image):
        """Function to get image from the self.media file and change its dimensions to fit the terminal, then turning it into pixel matrix."""
        image = cv.cvtColor(image, cv.COLOR_BGR2HSV)

        # current row and column size definitions
        ac_col, ac_row = image.shape[:2]
        # d1 and d2 are the width and height of image resp
        size = self.media.getmaxyx()
        d2 = min((size[0] - 2) - 3, int((ac_col * (size[1] - 2)) / ac_row))
        d1 = min(int((size[1] - 2) / 3), int((ac_row * d2) / ac_col))

        # set image to determined d1 and column size
        im = cv.resize(image, (d1, d2), interpolation=cv.INTER_AREA)
        # image[:,:,2] = cv.equalizeHist(image[:,:,2])
        pixels = np.reshape(im, (d2, d1, 3))
        return pixels

    def get_color_matrix(self, pixels):
        """Function to get the colour codes (ANSI escape sequences) from RGB values of pixel."""
        color_matrix = []
        for row in pixels:
            color_matrix_row = []
            for p in row:
                # Convert values to percentages and normalise
                hue = p[0]
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
        if maxval != minval:
            intensity_matrix = (
                (intensity_matrix - minval) * self.MAX_PIXEL_VALUE / (maxval - minval)
            )
        return intensity_matrix

    def print_from_image(self, image, mode):
        """Function to take in an image & use its RGB values to decide upon an ASCII character
        to represent it. This ASCII character will be based upon the brightness
        measure calculated

        Manager function.
        """
        pixels = self.get_pixel_matrix(image)
        self.vid_render(pixels, mode == 1, mode == 2)

    def read_media_sub(self, vidfile, mode, subfile=""):
        """Function to read the self.media file and pass on data to rendering functions frame by frame."""
        vidcap = cv.VideoCapture(vidfile)
        if subfile:
            subs = pysrt.open(subfile, encoding="latin-1")
        fps = vidcap.get(cv.CAP_PROP_FPS)

        self.media.nodelay(True)

        user_input = curses.ERR

        while vidcap.isOpened():
            # Read frames from the image
            success, image = vidcap.read()
            if not success:
                break

            # Check for user input
            user_input = self.media.getch()

            if user_input in self.SPACEBAR_KEY:
                user_input = self.media.getch()
                while user_input == curses.ERR:
                    user_input = self.media.getch()

            if user_input in self.QUIT_KEYS:
                break

            # Process a frame
            dur = time.process_time()
            
            #using global and local variables to check if terminal size changed
            global startSize
            global startSize2
            
            currentSize=os.get_terminal_size() 
            currentSize2=os.get_terminal_size() 

            #print and update subs
            if(startSize2 == currentSize2 and subfile !=''):
                self.subtitle_show(subs, vidcap.get(cv.CAP_PROP_POS_MSEC))
            elif( subfile !='' ):
                curses.update_lines_cols()
                beginX = 0
                beginY = curses.LINES - 5
                height = 5
                width = curses.COLS
                self.captions = curses.newwin(height, width, beginY, beginX)
                self.captions.border(0, 0, 0, 0, 0, 0, 0, 0)
                self.subtitle_show(subs, vidcap.get(cv.CAP_PROP_POS_MSEC))
                startSize2=currentSize2    

            #play and update video resolution
            if(startSize == currentSize):
                self.print_from_image(image, mode)
            else:
                curses.update_lines_cols()
                if (subfile !=''):
                    height = curses.LINES - 5
                    width = curses.COLS
                else:
                    height = curses.LINES 
                    width = curses.COLS 
                self.media.clear()
                self.media.resize(height, width)
                self.media.border(0, 0, 0, 0, 0, 0, 0, 0) 
                startSize=currentSize     


            
            dur = (time.process_time() - dur) * 1000
            if round(1000 / fps - dur) >= 0:
                curses.napms(round(1000 / fps - dur))
        vidcap.release()
        cv.destroyAllWindows()

        self.media.nodelay(False)
        return user_input

    def main(self, argv):
        beginX = 0
        beginY = 0
        vidfile = argv[1]
        output_mode = int(argv[-1])

        #disables cursor
        curses.curs_set(False)

        if len(argv) == 3:
            height = curses.LINES
            width = curses.COLS
        else:
            height = curses.LINES - 5
            width = curses.COLS

        self.media = curses.newwin(height, width, beginY, beginX)
        self.media.border(0, 0, 0, 0, 0, 0, 0, 0)

        if len(argv) == 3:
            subfile = ""
        else:
            beginX = 0
            beginY = curses.LINES - 5
            height = 5
            width = curses.COLS
            self.captions = curses.newwin(height, width, beginY, beginX)
            self.captions.border(0, 0, 0, 0, 0, 0, 0, 0)
            subfile = argv[2]

        return_val = self.read_media_sub(vidfile, output_mode, subfile)

        if return_val not in self.QUIT_KEYS:
            self.media.getch()


def run(stdscr):
    obj = AMP()
    obj.main(sys.argv)


curses.wrapper(run)