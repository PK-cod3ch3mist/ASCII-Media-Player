<a href="https://github.com/PK-cod3ch3mist/ANSIArtGenerator"><img src="https://raw.githubusercontent.com/PK-cod3ch3mist/ANSIArtGenerator/main/assets/AMP.svg" alt="ASCII Media Player" width="1000"></a>

A python program that creates ASCII graphics (with true color support if enabled) from images and videos. It can also play videos with subtitle support! :scream:

## Dependencies
The program runs using python3
The following python packages are used in the program:
- opencv-python
- Pillow
- numpy

These packages can be installed using any package manager for python like pip, conda, etc.

**A true-colour terminal is required to see videos and images in colour.**

Also since the program **uses ANSI escape sequences**, all POSIX compliant terminals should work well. If you use windows, and the program doesn't work well, try switching to WSL (Windows Subsystem for Linux)

## A Demo
Click below to view a demo for the usage of the program. It is of lesser quality than what you would witness though, since I had to compress the screen recording to a managable size.

<a href="https://drive.google.com/file/d/1B22lxNd0hxzxyd1Mgg0j_70LVKEbwZpn/view?usp=sharing">Demo Link</a>

## Usage
Navigate to the directory of the python script and run the following command
```shell
python generate.py $FILENAME $OPTION
```
Here `$FILENAME` is the full path to the media file and `$OPTION` takes values **0 for black and white output** and **1 for true color output** (see if your terminal supports true color before enabling)

## TODO
- [ ] Support 3-bit RGB (8-colors) with dithering
- [x] Support true color (24-bit RGB)
- [x] Support automatic resizing
- [x] Support B&W output
