<p align="center"><a href="https://github.com/PK-cod3ch3mist/ANSIArtGenerator"><img src="./assets/AMP.png" alt="ASCII Media Player" width="450px"></a></p>

A python program that creates ASCII graphics from images and videos. It can also play videos with subtitle support (given a .srt file)! :scream:

# 🍎 Motivation

You have seen Music Players, Stack-overflow surfers, Hacker News portals etc. in the terminal, so it is the logical next step 😅. Besides, the terminal makes almost everything appear x10 times more cool.

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

All POSIX compliant terminals should work well. If you use windows, and the program doesn't work well, try switching to WSL (Windows Subsystem for Linux)

# 🎥 A Demo

https://user-images.githubusercontent.com/55488899/161427699-1d606858-4a3d-4490-b21e-ecd4ac56a83b.mp4

# 🛠️ Usage

Navigate to the directory of the python script and run the following command
```shell
python generate.py $VIDEO_FILENAME $SUBTITLE_FILENAME $OPTION
```
If you want to run without subtitles then
```shell
python generate.py $VIDEO_FILENAME $OPTION
```
Here `$VIDEO_FILENAME` and `$SUBTITLE_FILENAME` are the full path to the files and `$OPTION` takes values **0 for black and white output** and **1 for true colour output** (see if your terminal supports true colour before enabling)

# 📝 TODO and Future Plans

- [x] Support 3-bit RGB (8-colours)
- [x] Support true colour (24-bit RGB) *visit tc-version branch*
- [x] Support automatic resizing
- [x] Support B&W output
- [x] Support subtitles
