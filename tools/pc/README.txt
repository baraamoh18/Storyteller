Storyteller: make chapters on this computer
===========================================

Uses your NVIDIA graphics card (RTX 5050) to turn chapter CBZ files into ready-to-direct chapters,
the same as the Colab and Kaggle notebooks, with no time limits.

1. Unzip this folder somewhere with space, for example D:\Work\StoryTelling website\pc-tools
   (it needs about 8 GB: the AI tools and models live in here, not on drive C:).
2. Install Python 3.12 if you don't have it:
   https://www.python.org/downloads/release/python-3128/  ->  "Windows installer (64-bit)".
   In the installer, tick "Add python.exe to PATH".
3. Double-click "Setup" (if Windows warns about it, click "More info" -> "Run anyway"). It takes 10-20 minutes, once. At the end it should say
   "OK: the cutout models run on the graphics card." If it doesn't, send Claude a screenshot.
4. Double-click "Make Chapters" whenever you want to make chapters. It asks for the CBZ folder
   (remembered after the first time) and which chapters, e.g. 1-20.
   The finished zips appear in the "finished" folder. Send them to Claude.

Overnight runs: keep the computer plugged in and set Windows not to sleep while it runs.
Closing the window stops it; running "Make Chapters" again skips the chapters already finished.
