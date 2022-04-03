<a href="https://github.com/PK-cod3ch3mist/ANSIArtGenerator"><img src="https://raw.githubusercontent.com/PK-cod3ch3mist/ANSIArtGenerator/main/assets/AMP.svg" alt="ASCII Media Player" width="1000"></a>

A python program that creates ASCII graphics from images and videos. It can also play videos with subtitle support (given a .srt file)! :scream:

This is the alpha branch of the application that supports 8 color terminals. It uses ncurses and hence works in WSL, Linux and macOS.

# 🍎 Motivation
You have seen Music Players, Stackoverflow surfers, Hacker News portals etc. in the terminal, so it is the logical next step 😅. Besides, the terminal makes almost everything appear x10 times more cool.

# ⚗️ Dependencies

## Language and Packages
The program runs using python3
The following python packages are used in the program:
- pysrt
- opencv-python
- Pillow
- numpy

These packages can be installed using any package manager for python like pip, conda, etc.

## Terminal Requirements
**A true-colour terminal is required to see videos and images in colour.**

Also since the program **uses ANSI escape sequences**, all POSIX compliant terminals should work well. If you use windows, and the program doesn't work well, try switching to WSL (Windows Subsystem for Linux)

# 🎥 A Demo

https://user-images.githubusercontent.com/55488899/140598521-2b67960c-3cf4-4b52-b4a4-385237366e07.mov

# 🛠️ Usage
Navigate to the directory of the python script and run the following command
```shell
python generate.py $VIDEO_FILENAME $SUBTITLE_FILENAME $OPTION
```
If you want to run without subtitles then
```shell
python generate.py $VIDEO_FILENAME $OPTION
```
Here `$VIDEO_FILENAME` and `$SUBTITLE_FILENAME` are the full path to the files and `$OPTION` takes values **0 for black and white output** and **1 for true color output** (see if your terminal supports true color before enabling)

# 📝 TODO and Future Plans
- [ ] Support 3-bit RGB (8-colors) with dithering
- [x] Support true color (24-bit RGB)
- [x] Support automatic resizing
- [x] Support B&W output
- [x] Support subtitles
