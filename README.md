<a href="https://github.com/PK-cod3ch3mist/ANSIArtGenerator"><img src="https://raw.githubusercontent.com/PK-cod3ch3mist/ANSIArtGenerator/main/assets/AMP.svg" alt="ASCII Media Player" width="1000"></a>

A python program that creates ASCII graphics (with true color support if enabled) from images and videos. It can also play videos with subtitle support (given a .srt file)! :scream:

## Dependencies
The program runs using python3
The following python packages are used in the program:
- pysrt
- opencv-python
- Pillow
- numpy

These packages can be installed using any package manager for python like pip, conda, etc.

**A true-colour terminal is required to see videos and images in colour.**

Also since the program **uses ANSI escape sequences**, all POSIX compliant terminals should work well. If you use windows, and the program doesn't work well, try switching to WSL (Windows Subsystem for Linux)

## A Demo
Click below to view a demo for the usage of the program with subtitles. Due to Google Drive's colour codec however, the video may appear of a more dull colour than actual output. Moreover, you can easily change the contrast and brightness in the code (the part commented as `CONFIG OPTION - contrast and brightness`)

<a href="https://drive.google.com/file/d/1oRp_8KH3wkewvEIJVMmbMsoDMug9EiFl/view?usp=sharing">Demo Link</a>

## Usage
Navigate to the directory of the python script and run the following command
```shell
python generate.py $VIDEO_FILENAME $SUBTITLE_FILENAME $OPTION
```
If you want to run without subtitles then
```shell
python generate.py $VIDEO_FILENAME $OPTION
```
Here `$VIDEO_FILENAME` and `$SUBTITLE_FILENAME` are the full path to the files and `$OPTION` takes values **0 for black and white output** and **1 for true color output** (see if your terminal supports true color before enabling)

## TODO
- [ ] Support 3-bit RGB (8-colors) with dithering
- [x] Support true color (24-bit RGB)
- [x] Support automatic resizing
- [x] Support B&W output
- [x] Support subtitles