Storyteller reader: read the chapters on this computer and on your phone
=========================================================================

First time
1. Unzip this folder somewhere, for example D:\Work\StoryTelling website\Storyteller Reader
2. Python must be installed (the same one the chapter-making kit uses):
   https://www.python.org/downloads/release/python-3128/  ->  "Windows installer (64-bit)".
   In the installer, tick "Add python.exe to PATH".

Every time
1. Double-click "Read Storyteller" (if Windows warns about it, click "More info" -> "Run anyway").
   A black window opens and the reader opens in your browser.
2. The first time only, Windows asks whether Python may use the network: tick "Private networks"
   and click "Allow access". (This is what lets your phone in.)
3. Keep the black window open while you read. Closing it stops the reader.

On your phone
- The phone must be on the same Wi-Fi as the computer.
- The reader's first screen on the computer shows a QR code: scan it with the phone's camera.
  Or type the address the black window shows after "On your phone", for example http://192.168.1.23:8000/
- Tip: in the phone's browser, Share -> "Add to Home Screen" makes it an app icon.
- If the phone cannot open it:
  * check that both are on the same Wi-Fi (not the phone's mobile data);
  * Windows Settings -> Network & internet -> Wi-Fi (or Ethernet) -> your network -> Network profile type:
    choose "Private";
  * if you clicked "Cancel" at step 2 above: Windows Security -> Firewall & network protection ->
    "Allow an app through firewall" -> Change settings -> tick "Private" next to Python.

New chapters
- When Claude sends a reader pack (a zip called reader-pack_<chapter>.zip), put it in the
  "new chapters" folder, then double-click "Read Storyteller". It is added by itself and the zip moves
  to "new chapters\added". The chapter menu updates by itself.
- Chapter zips from the chapter-making kit (chapter_<number>.zip) are not reader packs: those go to
  Claude first, to be directed.

The reader needs an internet connection for its animation library and fonts.
