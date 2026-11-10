"""Generates Scrappy's sound effects with the ElevenLabs sound-effects API,
then levels them so they sit together in the game.

    python make_sounds.py --dry            what would be made, and what it costs
    python make_sounds.py                  make everything that is missing
    python make_sounds.py --only press_bang footstep_concrete
    python make_sounds.py --redo press_bang     a new take of one (pays again)
    python make_sounds.py --first               only the first take of each
    python make_sounds.py --max-credits 3000    stop before spending more
    python make_sounds.py --process             re-level everything already made
                                                (free: no API calls)

The list lives in sounds.json: id, prompt, seconds, and optionally loop,
takes (variants, so a footstep isn't the same footstep twenty times running),
kind (foley / machine / ui / jingle / ambience / cute - picks the prompt
ending, prompt influence and loudness), level (a loudness override, in LUFS),
and for sounds heard constantly (footsteps): highpass / lowpass (Hz), peak
(dBFS ceiling, lower than the usual -1) and max (seconds, cut to length).

Two folders:
  tools/raw/            what ElevenLabs sent, untouched. Kept so the levelling
                        can be redone for free.
  scrappy/assets/sfx/   what the game plays: Ogg Vorbis, levelled.

The levelling is what game audio does everywhere. Each sound is brought to
the loudness its kind should have (a footstep quiet, a baler slam loud),
peaks are held under -1 dBTP so nothing clips, trailing silence is cut and
a one-shot gets a 15 ms fade so it never ends on a click. Loops are only
turned up or down - cutting anything off a loop would break the seam.
Ogg rather than MP3 because MP3 always pads each end with a little silence,
and a loop made of one clicks every time round.

Anything already made is skipped - running this twice never pays twice.

The key: ELEVENLABS_API_KEY, or E:/ScrappyYard/elevenlabs.key (outside the
game folder on purpose, so it can never be exported with the game). It is
never printed.
"""
import argparse
import array
import json
import math
import os
import re
import shutil
import struct
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
# Ashbound: the Legends' voices (legend_sounds.json) into the mod's sounds; the key stays outside the mod, never printed
OUT = ROOT / "src" / "main" / "resources" / "assets" / "ashbound" / "sounds" / "legend"
RAW = HERE / "sounds_raw"
LIST = HERE / "legend_sounds.json"
KEY_FILE = Path("E:/ScrappyYard/elevenlabs.key")
URL = "https://api.elevenlabs.io/v1/sound-generation"
CREDITS_PER_SECOND = 40

# What each kind of sound gets: a prompt ending in the words the model
# understands (from ElevenLabs' own guidance: material, space, distance,
# "one-shot" or "loop"), how literally to take the prompt, and how loud the
# finished file should be. Positioned sounds are asked for dry and close:
# the game puts them in the yard and adds the distance itself.
KINDS = {
    "foley": (", high quality professionally recorded foley sound effect, "
              "close mic, dry, no reverb, no music", 0.45, -20.0),
    "machine": (", high quality industrial sound effect recording, close mic, "
                "dry, no music", 0.40, -17.0),
    "ui": (", clean modern video game user interface sound, short, no reverb, "
           "no music", 0.55, -22.0),
    "jingle": (", short video game reward jingle, bright and clean", 0.45, -18.0),
    "ambience": (", wide outdoor field recording, calm and continuous, "
                 "no music", 0.25, -27.0),
    # Sweepy: a small character, so a voice rather than a jingle
    # a Legend: huge, menacing, a creature or a thing not a person; the game places it, so mono and dry
    "monster": (", huge monster creature sound effect for a dark fantasy video game, deep and menacing, "
                "close mic, dry, no reverb, no music", 0.45, -16.0),
    "impact": (", heavy dark fantasy video game impact sound effect, close mic, dry, no music", 0.45, -16.0),
    "cute": (", cute cartoon robot character, playful and charming, clean "
             "recording, no reverb", 0.50, -21.0),
}
LOOP_ENDING = ", steady and continuous, seamless loop, no fade in or fade out"
PEAK = -1.0


def api_key() -> str:
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key and KEY_FILE.exists():
        key = KEY_FILE.read_text(encoding="utf-8").strip()
    if not key:
        sys.exit("No API key: set ELEVENLABS_API_KEY or write it into %s" % KEY_FILE)
    return key


def request(key: str, body: dict, fmt: str) -> bytes:
    req = urllib.request.Request(
        URL + "?output_format=" + fmt,
        data=json.dumps(body).encode("utf-8"),
        headers={"xi-api-key": key, "Content-Type": "application/json",
                 "Accept": "audio/*"},
        method="POST")
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300]
            if e.code == 429 and attempt < 3:
                time.sleep(5 * (attempt + 1))
                continue
            raise RuntimeError("HTTP %d: %s" % (e.code, detail)) from None
        except urllib.error.URLError as e:
            if attempt < 3:
                time.sleep(3)
                continue
            raise RuntimeError(str(e)) from None
    raise RuntimeError("gave up after retries")


def wav(pcm: bytes, rate: int = 44100) -> bytes:
    """ElevenLabs' sound-effect PCM with a WAV header on. It is 16-bit
    STEREO, left and right interleaved (measured: the two halves of each
    frame correlate at 0.998) - labelled as mono it plays at half speed, an
    octave down, twice as long as asked for."""
    return (b"RIFF" + struct.pack("<I", 36 + len(pcm)) + b"WAVEfmt "
            + struct.pack("<IHHIIHH", 16, 1, 2, rate, rate * 4, 4, 16)
            + b"data" + struct.pack("<I", len(pcm)) + pcm)


def kind_of(s: dict) -> str:
    if s.get("kind"):
        return s["kind"]
    if s["id"].endswith("ambience_loop"):
        return "ambience"
    if s["id"].startswith("ui_") or s["id"] in ("xp", "news"):
        return "ui"
    return "foley"


def names(s: dict) -> list:
    n = int(s.get("takes", 1))
    if n == 1:
        return [s["id"]]
    return ["%s_%d" % (s["id"], i + 1) for i in range(n)]


def raw_path(name: str) -> Path | None:
    for ext in (".wav", ".mp3"):
        if (RAW / (name + ext)).exists():
            return RAW / (name + ext)
    return None


# ================================================================ levelling

FFMPEG = shutil.which("ffmpeg")


def loudness(path: Path) -> float:
    """Integrated loudness in LUFS. Sounds under ~0.4 s are too short to
    gate, so for those the mean level stands in for it."""
    out = subprocess.run([FFMPEG, "-hide_banner", "-nostats", "-i", str(path),
                          "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", out)
    if m and float(m[-1]) > -60.0:
        return float(m[-1])
    out = subprocess.run([FFMPEG, "-hide_banner", "-nostats", "-i", str(path),
                          "-af", "volumedetect", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = re.search(r"mean_volume:\s+(-?[\d.]+) dB", out)
    return float(m.group(1)) if m else -30.0


def first_hit(path: Path) -> tuple:
    """Where the first hit of a step starts and ends (seconds). A generated
    footstep is usually two sounds - the foot, then a scuff or a toe a
    moment later - and the second one is what makes a walk sound wrong, on
    every surface. This keeps the foot: from its onset until it has died
    away, or until something starts again, and never more than 0.12 s."""
    raw = subprocess.run([FFMPEG, "-v", "error", "-i", str(path), "-ac", "1",
                          "-ar", "44100", "-f", "s16le", "-"],
                         capture_output=True).stdout
    x = array.array("h")
    x.frombytes(raw[:len(raw) // 2 * 2])
    w = 220  # 5 ms
    env = []
    for i in range(len(x) // w):
        e = sum(v * v for v in x[i * w:(i + 1) * w]) / w
        env.append(10 * math.log10(e / 32768.0 ** 2 + 1e-12))
    if not env:
        return 0.0, 0.12
    top = max(env)
    on = next(i for i, v in enumerate(env) if v > top - 20)
    peak = max(range(on, min(on + 8, len(env))), key=lambda i: env[i])
    end = min(len(env), peak + 24)
    low = env[peak]
    # the foot itself gets at least 40 ms; only after that can a rise be a
    # second sound rather than the grain of the first
    for i in range(peak + 8, min(len(env), peak + 24)):
        low = min(low, env[i - 1], env[i - 2])
        if env[i] < env[peak] - 26:
            end = i
            break
        # fallen away and coming back up: the second sound
        if env[peak] - low > 9 and min(env[i], env[i - 1]) - low > 5:
            end = i - 1
            break
    return max(0.0, on * w / 44100 - 0.003), end * w / 44100


def level(s: dict, name: str) -> bool:
    src = raw_path(name)
    if src is None:
        return False
    if FFMPEG is None:
        sys.exit("ffmpeg is needed for the levelling step")
    target = float(s.get("level", KINDS[kind_of(s)][2]))
    gain = target - loudness(src)
    loop = bool(s.get("loop"))
    chain = []
    # Footsteps and the like, heard hundreds of times: the low thump is what
    # tires the ear and muddies everything else (the step's character lives
    # at 1-4 kHz), and they are kept short so tails never pile up.
    if s.get("highpass"):
        chain.append("highpass=f=%d:p=2" % int(s["highpass"]))
    if s.get("lowpass"):
        chain.append("lowpass=f=%d" % int(s["lowpass"]))
    if s.get("one_hit"):
        start, end = first_hit(src)
        chain.append("atrim=%.4f:%.4f,asetpts=PTS-STARTPTS" % (start, end))
    elif s.get("max") and not loop:
        chain.append("atrim=0:%.3f" % float(s["max"]))
    if not loop:
        # cut the silence at the end (keep a short tail so reverb isn't chopped)
        chain.append("silenceremove=stop_periods=-1:stop_duration=0.08:"
                     "stop_threshold=-55dB")
    chain.append("volume=%.2fdB" % gain)
    ceiling = float(s.get("peak", PEAK))
    chain.append("alimiter=limit=%.4f:attack=1:release=30:level=false"
                 % (10 ** (ceiling / 20.0)))
    if not loop:
        chain.append("areverse,afade=t=in:d=%.3f,areverse"
                     % (0.025 if s.get("one_hit") else
                        0.06 if s.get("max") else 0.015))
    OUT.mkdir(parents=True, exist_ok=True)
    dst = OUT / (name + ".ogg")
    r = subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
                        "-i", str(src), "-af", ",".join(chain), "-ar", "44100",
                        # placed in the yard: mono (the game does the stereo);
                        # menus, jingles and the ambience bed keep their width
                        "-ac", "2" if kind_of(s) in ("ui", "jingle", "ambience", "cute") and not s.get("mono") else "1",
                        "-c:a", "libvorbis", "-q:a", "6", str(dst)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("  level FAILED %s: %s" % (name, r.stderr.strip()[:200]))
        return False
    return True


# ===================================================================== main

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--redo", nargs="*", default=[])
    ap.add_argument("--first", action="store_true",
                    help="only the first take of each sound (for trying prompts)")
    ap.add_argument("--max-credits", type=int, default=0)
    ap.add_argument("--process", action="store_true",
                    help="re-level every raw file already made; no API calls")
    a = ap.parse_args()

    # "keep": chosen by ear from somewhere else (the footsteps came from
    # step_candidates.py) - never remade or re-levelled over
    sounds = [s for s in json.loads(LIST.read_text(encoding="utf-8"))
              if not s.get("keep")]
    wanted = set(a.only or []) | set(a.redo)

    if a.process:
        n = 0
        for s in sounds:
            if wanted and s["id"] not in wanted:
                continue
            for name in names(s):
                n += level(s, name)
        print("levelled %d files into %s" % (n, OUT))
        return

    todo = []
    for s in sounds:
        if wanted and s["id"] not in wanted:
            continue
        for name in names(s)[:1] if a.first else names(s):
            if raw_path(name) is not None and s["id"] not in a.redo:
                continue
            todo.append((s, name))

    cost = sum(int(round(float(s["seconds"]) * CREDITS_PER_SECOND)) for s, _ in todo)
    print("%d files to make, about %d credits" % (len(todo), cost))
    if a.dry:
        for s, name in todo:
            print("  %-30s %4.1fs %-8s %s" % (name, float(s["seconds"]), kind_of(s),
                                             "loop" if s.get("loop") else ""))
        return

    key = api_key()
    RAW.mkdir(parents=True, exist_ok=True)
    spent = 0
    made = 0
    for s, name in todo:
        credits = int(round(float(s["seconds"]) * CREDITS_PER_SECOND))
        if a.max_credits and spent + credits > a.max_credits:
            print("stopping: the next one would pass --max-credits %d" % a.max_credits)
            break
        ending, influence, _ = KINDS[kind_of(s)]
        text = s["prompt"] + ending + (LOOP_ENDING if s.get("loop") else "")
        body = {
            "text": text[:450],
            "duration_seconds": float(s["seconds"]),
            "prompt_influence": float(s.get("influence", influence)),
        }
        if s.get("loop"):
            body["loop"] = True
        try:
            try:
                # PCM: no MP3 padding, and the levelling works on the real thing
                data = wav(request(key, body, "pcm_44100"))
                ext = ".wav"
            except RuntimeError as e:
                if "HTTP 4" not in str(e) or "401" in str(e):
                    raise
                data = request(key, body, "mp3_44100_128")
                ext = ".mp3"
        except RuntimeError as e:
            print("  FAILED %s: %s" % (name, e))
            if "HTTP 401" in str(e) or "quota" in str(e).lower():
                sys.exit("stopping: key refused or out of credits")
            continue
        for old in (RAW / (name + ".wav"), RAW / (name + ".mp3")):
            old.unlink(missing_ok=True)
        (RAW / (name + ext)).write_bytes(data)
        spent += credits
        made += 1
        ok = level(s, name)
        print("  %-30s %7d bytes %s  (%d credits so far)" % (
            name, len(data), "levelled" if ok else "RAW ONLY", spent))
    print("made %d, about %d credits" % (made, spent))


if __name__ == "__main__":
    main()
