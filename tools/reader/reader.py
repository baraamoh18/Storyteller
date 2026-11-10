"""The Storyteller reader on your PC (and on your phone, over your home Wi-Fi).

Started by "Read Storyteller.bat". It
  1. adds any chapter packs waiting in the "new chapters" folder (zips Claude sends) to the reader,
  2. serves the reader folder to this computer and to phones on the same Wi-Fi (browsers block music and
     chapter loading on pages opened straight from a file, so the reader needs a tiny web server),
  3. opens the reader in your browser and prints the address to type (or scan) on your phone.

Only the standard library: any Python 3.8 or newer works. Close the window to stop it.

    python reader.py [--port 8000] [--no-browser]
"""

import argparse
import http.server
import json
import re
import shutil
import socket
import sys
import webbrowser
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE / "reader"
if not (ROOT / "index.html").exists() and (HERE.parents[1] / "site" / "index.html").exists():
    ROOT = HERE.parents[1] / "site"  # run straight from a download of the GitHub project: serve its site folder
INBOX = HERE / "new chapters"
# what a reader pack may contain: chapter folders, and updates to the reader itself
PACK_PARTS = {"chapters", "music", "sfx", "vendor", "index.html", "series.js"}
TYPES = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".json": "application/json",
         ".css": "text/css", ".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml",
         ".mp3": "audio/mpeg", ".txt": "text/plain; charset=utf-8", ".woff2": "font/woff2"}


# ---------------------------------------------------------------- chapter packs

def safe_member(name):
    parts = Path(name.replace("\\", "/")).parts
    return bool(parts) and not name.startswith(("/", "\\")) and ".." not in parts and ":" not in parts[0] \
        and parts[0] in PACK_PARTS


def add_packs():
    """Unzip every reader pack in "new chapters" into the reader, then move it to "new chapters/added"."""
    INBOX.mkdir(exist_ok=True)
    for pack in sorted(INBOX.glob("*.zip")):
        try:
            with zipfile.ZipFile(pack) as z:
                names = [n for n in z.namelist() if not n.endswith("/")]
                if not names or not all(safe_member(n) for n in names):
                    print(f"  Skipped {pack.name}: it is not a reader pack. (A chapter zip from the chapter maker goes to"
                          " Claude first, to be directed.)")
                    continue
                z.extractall(ROOT)
            chapters = sorted({Path(n).parts[1] for n in names if n.startswith("chapters/") and len(Path(n).parts) > 2})
            done = INBOX / "added"
            done.mkdir(exist_ok=True)
            if (done / pack.name).exists():  # the same pack sent again
                (done / pack.name).unlink()
            shutil.move(str(pack), str(done / pack.name))
            print(f"  Added {pack.name}" + (f": chapter {', '.join(chapters)}" if chapters else ": reader update"))
        except (zipfile.BadZipFile, OSError) as e:
            print(f"  Could not add {pack.name}: {e}")


def chapter_list():
    """Every chapter in reader/chapters, in series order, read from its chapter.js."""
    found = []
    for js in (ROOT / "chapters").glob("*/chapter.js"):
        text = js.read_text(encoding="utf-8", errors="replace")
        head = text[text.find("registerChapter("):]
        cid = re.search(r'\bid:\s*"([^"]+)"', head)
        if not cid:
            continue
        title = re.search(r'\btitle:\s*"((?:[^"\\]|\\.)*)"', head)
        number = re.search(r'\bnumber:\s*([0-9.]+)', head.split("scenes:")[0])
        found.append({
            "id": cid.group(1),
            "title": json.loads(f'"{title.group(1)}"') if title else cid.group(1),
            "number": float(number.group(1)) if number else None,
            "panels": len(re.findall(r'\{\s*id:\s*"panel_', text)),
        })
    found.sort(key=lambda c: (c["number"] is None, c["number"] or 0, c["id"]))
    for c in found:
        if c["number"] is not None and c["number"].is_integer():
            c["number"] = int(c["number"])
    return found


# ---------------------------------------------------------------- addresses

def phone_addresses(port):
    """This computer's addresses on the home network, the one the internet goes through first."""
    found = []
    try:  # asks the system which address it would send from; nothing is actually sent
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        found.append(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    try:
        found += socket.gethostbyname_ex(socket.gethostname())[2]
    except OSError:
        pass
    good = []
    for a in found:
        if a not in good and not a.startswith(("127.", "169.254.", "0.")):
            good.append(a)
    return [f"http://{a}:{port}/" for a in good]


# ---------------------------------------------------------------- the server

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def guess_type(self, path):
        return TYPES.get(Path(path).suffix.lower()) or super().guess_type(path)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")  # a chapter added or changed shows on the next reload
        super().end_headers()

    def send_text(self, body, kind):
        data = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def route(self):
        path = self.path.split("?", 1)[0]
        if path == "/__chapters.js":  # the chapter menu, from the chapters folder itself
            self.send_text("window.LOCAL_CHAPTERS = " + json.dumps(chapter_list()) + ";\n", TYPES[".js"])
            return True
        if path == "/__phone.json":  # shown on the PC's title card as a QR code
            self.send_text(json.dumps({"urls": phone_addresses(self.server.server_address[1])}), TYPES[".json"])
            return True
        return False

    def do_GET(self):
        if not self.route():
            super().do_GET()

    def do_HEAD(self):
        if not self.route():
            super().do_HEAD()

    def log_message(self, *args):  # quiet: the window is for the addresses
        pass

    def handle(self):
        try:
            super().handle()
        except (ConnectionError, TimeoutError):  # a phone that locks its screen mid-image
            pass


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true", help="do not open the browser")
    args = parser.parse_args()

    print("\n  Storyteller reader\n  ==================\n")
    if not (ROOT / "index.html").exists():
        print(f"  The reader files are missing: there should be a folder called reader next to this file ({ROOT}),"
              " or this file should sit in tools/reader of the Storyteller project.")
        return 1
    add_packs()
    server = None
    for port in range(args.port, args.port + 11):  # the next free one, if another program has this port
        try:
            server = http.server.ThreadingHTTPServer(("", port), Handler)
            break
        except OSError:
            continue
    if not server:
        print(f"  Could not start: ports {args.port}-{args.port + 10} are all in use.")
        return 1
    server.daemon_threads = True
    port = server.server_address[1]
    chapters = chapter_list()
    print(f"  Chapters: {', '.join(c['id'] for c in chapters) or 'none yet'}")
    bare = [c["id"] for c in chapters if not any((ROOT / "chapters" / c["id"]).glob("*.webp"))]
    if bare:
        print(f"  No pictures yet for: {', '.join(bare)}. Put their reader pack (reader-pack_<chapter>.zip) in the"
              f" \"new chapters\" folder ({INBOX}) and start the reader again.")
    print(f"\n  On this computer:  http://localhost:{port}/")
    phones = phone_addresses(port)
    if phones:
        print(f"  On your phone:     {phones[0]}   (same Wi-Fi; or scan the QR code on the reader's first screen)")
        for other in phones[1:]:
            print(f"                     {other}   (if the first one does not open)")
    print("\n  Keep this window open while you read. Close it to stop the reader.\n")
    if not args.no_browser:
        webbrowser.open(f"http://localhost:{port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
