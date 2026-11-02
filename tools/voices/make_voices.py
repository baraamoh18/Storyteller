"""Make the characters' voice lines with Kokoro (free, runs on an ordinary computer, no graphics card needed).

Every character gets a voice of their own by blending Kokoro's preset voices and shifting the pitch.
For each line it writes one take per voice option into out/candidates/ so you can pick by ear,
and the first option's take into out/voice_<line>.mp3, the name the scroll site looks for.

Setup (once):
    pip install kokoro-onnx soundfile
    download kokoro-v1.0.onnx and voices-v1.0.bin from
    https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.1 into this folder
    ffmpeg must be installed (it does the pitch shift and the MP3)

Run:
    python make_voices.py
"""

import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

HERE = Path(__file__).parent

# Each option: preset voices with their weights, pitch shift in semitones, and speaking speed.
CAST = {
    # Arthur Leywin: the main character, a king reborn, so older than he sounds: deep, calm, controlled.
    # Built on am_onyx, Kokoro's deepest voice (about 86 Hz), and taken a little lower still.
    "arthur": {
        "A": {"blend": {"am_onyx": 0.7, "bm_lewis": 0.3}, "pitch": -1.0, "speed": 0.92},
        "B": {"blend": {"am_onyx": 1.0}, "pitch": -1.5, "speed": 0.9},
        "C": {"blend": {"am_onyx": 0.6, "bm_fable": 0.4}, "pitch": -2.0, "speed": 0.92},
    },
    # the armoured swordsman with the headband: younger and lighter than Arthur (about 120 Hz), sure of himself
    "swordsman": {
        "A": {"blend": {"am_michael": 0.7, "am_liam": 0.3}, "pitch": 0.0, "speed": 1.0},
        "B": {"blend": {"am_puck": 0.6, "am_liam": 0.4}, "pitch": 0.5, "speed": 1.02},
        "C": {"blend": {"bm_daniel": 1.0}, "pitch": 0.0, "speed": 1.0},
    },
    # a student watching the duel, impressed: the lightest of the three
    "onlooker": {
        "A": {"blend": {"am_eric": 0.6, "am_adam": 0.4}, "pitch": 0.0, "speed": 1.08},
    },
}

# line name (matches the bubble's `voice` in the site) -> who says it and what
LINES = {
    "very_well": ("swordsman", "Very well."),
    "go_easy": ("swordsman", "I'll be sure to go easy on you."),
    "going_easy_huh": ("arthur", "Going easy, huh?"),
    "not_using_spells": ("onlooker", "He's not using any spells... just strengthening his body and sword with mana."),
}


def blended(kokoro, blend):
    total = sum(blend.values())
    return sum(kokoro.get_voice_style(name) * (weight / total) for name, weight in blend.items()).astype(np.float32)


def finish(wav_path, mp3_path, rate, pitch):
    """Shift the pitch (keeping the speed), add a touch of room so it sounds less like a booth, even out the loudness."""
    factor = 2 ** (pitch / 12)
    shift = f"asetrate={rate * factor:.0f},aresample={rate},atempo={1 / factor:.5f}," if pitch else ""
    filters = f"{shift}aecho=0.8:0.5:45|80:0.10|0.06,loudnorm=I=-16:TP=-1.5:LRA=11"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_path), "-af", filters,
                    "-ar", "44100", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "96k", str(mp3_path)], check=True)


def main():
    kokoro = Kokoro(str(HERE / "kokoro-v1.0.onnx"), str(HERE / "voices-v1.0.bin"))
    out = HERE / "out"
    (out / "candidates").mkdir(parents=True, exist_ok=True)
    for line, (who, text) in LINES.items():
        for option, voice in CAST[who].items():
            samples, rate = kokoro.create(text, voice=blended(kokoro, voice["blend"]), speed=voice["speed"], lang="en-us")
            wav = out / "candidates" / f"{line}__{who}_{option}.wav"
            sf.write(wav, samples, rate)
            finish(wav, wav.with_suffix(".mp3"), rate, voice["pitch"])
            wav.unlink()
            print(f"{line:18} {who} {option}  {len(samples) / rate:.1f}s")
        first = next(iter(CAST[who]))
        (out / f"voice_{line}.mp3").write_bytes((out / "candidates" / f"{line}__{who}_{first}.mp3").read_bytes())
    print(f"Done: {out}")


if __name__ == "__main__":
    main()
