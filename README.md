# ANSI Art Generator
A python program that creates ASCII art (with true color support if enabled) from images and videos

## Dependencies
The program runs using python3
The following python packages are used in the program:
- opencv-python
- Pillow
- numpy
These packages can be installed using any package manager for python like pip, conda, etc.

## A Demo
Below is a GIF file (of lesser quality than the original screen-capture) showing the output on a true-color terminal
![Gif](https://github.com/PK-cod3ch3mist/ANSIArtGenerator/blob/main/demo.gif)

## Usage
Navigate to the directory of the python script and run the following command
```shell
python generate.py $FILENAME $OPTION
```
Here `$FILENAME` is the full path to the media file and `$OPTION` takes values **0 for black and white output** and **1 for true color output** (see if your terminal supports true color before enabling)

## My video appears glitchy...
If your video appears glitchy, you can try changing the `frame_skip` variable to a higher values (instead of 0), in effect dropping the frame-rate. This gives the generator more time to draw the characters to screen.

## The image runs out of window...
Again you can change the values of the `d2` (height) and `d1` (width) variables according to the terminal *(Currently they are set to a full-screen terminal on a 13-inch laptop)*. I am working on a system that can automatically get your terminal size and work accordingly.

## TODO
- [ ] Support 3-bit RGB (8-colors) with dithering
- [x] Support true color (24-bit RGB)
- [ ] Support automatic resizing
- [x] Support B&W output