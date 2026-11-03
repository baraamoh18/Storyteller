"""Usage: python make_loop.py in.mp3 out.mp3 TAIL_SECONDS   (TAIL_SECONDS: how much of a fade-out / silent ending to drop)

Rebuild a seamless loop: skip the old blended start, drop a dead tail, pick a beat-aligned loop length,
equal-power crossfade the tail into the head, and set one fixed gain (no time-varying loudness)."""
import sys, subprocess, numpy as np
src, out, tail_cut = sys.argv[1], sys.argv[2], float(sys.argv[3])
R = 44100
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", src, "-ac", "1", "-ar", str(R), "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
x = np.frombuffer(raw, dtype=np.float32).copy()
a = int(1.6 * R)                     # the old start held the old (loudness-ramped) crossfade
end = len(x) - int(tail_cut * R)     # drop a musical ending / silence
F = int(1.0 * R)                     # new crossfade length

# onset envelope (spectral flux) at 100 frames per second
hop, n = 441, 2048
w = np.hanning(n)
frames = np.lib.stride_tricks.sliding_window_view(x, n)[::hop] * w
mag = np.log1p(np.abs(np.fft.rfft(frames, axis=1)))
flux = np.r_[0, np.maximum(0, np.diff(mag, axis=0)).sum(1)]
flux = (flux - flux.mean()) / (flux.std() + 1e-9)

# loop body D = L - F: pick the D (as long as possible) whose rhythm lines up with the start
fa, Wf = a // hop, 300               # compare 3 s of onsets
best, bestD = -9, None
for D in range(int((end - a - F) * 0.8) // hop, (end - a - F) // hop + 1):
    seg = flux[fa + D: fa + D + Wf]
    if len(seg) < Wf: break
    c = np.dot(flux[fa:fa + Wf], seg) / Wf
    if c > best: best, bestD = c, D
D = bestD * hop
L = D + F
seg = x[a:a + L].copy()
t = np.linspace(0, np.pi / 2, F, dtype=np.float32)
loop = seg[:L - F].copy()
loop[:F] = seg[:F] * np.sin(t) + seg[L - F:] * np.cos(t)   # equal power

# one fixed gain to about -16 LUFS (measured by ffmpeg's EBU R128 meter), peak kept under -1 dBFS
tmp = out + ".wav"
import wave
def write(path, y):
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(R)
        f.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
write(tmp, loop)
meter = subprocess.run(["ffmpeg", "-nostats", "-i", tmp, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float([l for l in meter.splitlines() if l.strip().startswith("I:")][-1].split()[1])
gain = 10 ** ((-16 - I) / 20)
gain = min(gain, 10 ** (-1 / 20) / np.abs(loop).max())
write(tmp, loop * gain)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", tmp, "-c:a", "libmp3lame", "-b:a", "128k", out], check=True)
import os; os.remove(tmp)
seam = abs(loop[0] - loop[-1])
print(f"{os.path.basename(out)}: {L/R - F/R:.2f} s loop, rhythm match {best:.2f}, loudness {I:.1f} -> {I + 20*np.log10(gain):.1f} LUFS, edge step {seam:.4f}")
