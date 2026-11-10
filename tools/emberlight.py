"""Emberlight, Ashbound's Iris shader pack. The shaders are in tools/shaderpack; this writes the small per-program files.

    python tools/emberlight.py          write the program files, compile everything, install into run/shaderpacks
    python tools/emberlight.py --zip    also build release/Ashbound-Emberlight-<VERSION>.zip

The compile is the real graphics driver's, through a hidden window that never shows, so it finds what the game would.
"""
import ctypes
import os
import re
import shutil
import sys
import zipfile
from ctypes import wintypes as W

VERSION = "1.0"
HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.join(HERE, "shaderpack")
SHADERS = os.path.join(PACK, "shaders")
INSTALL = os.path.join(HERE, "..", "run", "shaderpacks", "Emberlight")
RELEASE = os.path.join(HERE, "..", "..", "release")
HEAD = "#version 330 compatibility\n"

# program: the defines it's built with, and which lib files make it
WORLD = ("/lib/gbuffer.vsh", "/lib/gbuffer.fsh")
PROGRAMS = {
    "gbuffers_basic": ((), ("/lib/gbuffer.vsh", "/lib/basic.fsh")),
    "gbuffers_textured": (("FLAT",), WORLD),
    "gbuffers_weather": (("FLAT",), WORLD),
    "gbuffers_clouds": (("CLOUDS",), WORLD),
    "gbuffers_terrain": (("TERRAIN",), WORLD),
    "gbuffers_block": ((), WORLD),
    "gbuffers_entities": (("ENTITY",), WORLD),
    "gbuffers_hand": (("HAND",), WORLD),
    "gbuffers_water": (("TERRAIN", "WATER"), WORLD),
    "gbuffers_beaconbeam": (("UNLIT",), WORLD),
    "gbuffers_spidereyes": (("UNLIT",), WORLD),
    "gbuffers_armor_glint": (("UNLIT",), WORLD),
    "gbuffers_skybasic": ((), ("/lib/sky.vsh", "/lib/sky.fsh")),
    "gbuffers_skytextured": ((), ("/lib/gbuffer.vsh", "/lib/skytextured.fsh")),
}
QUADS = ("composite", "composite1", "composite2", "composite3", "composite4", "composite5", "final")
BLURS = {  # the bloom: a tight one at a quarter size, a wide one at a sixteenth
    "composite2": ("colortex2", 3, "4.0", "vec2(1.0, 0.0)"),
    "composite3": ("colortex3", 2, "4.0", "vec2(0.0, 1.0)"),
    "composite4": ("colortex2", 4, "16.0", "vec2(1.0, 0.0)"),
    "composite5": ("colortex4", 5, "16.0", "vec2(0.0, 1.0)"),
}
STUBS = "#define MC_RENDER_STAGE_SUN 1\n#define MC_RENDER_STAGE_MOON 2\n"


def write(path, text):
    with open(path, "w", encoding="utf8", newline="\n") as f:
        f.write(text)


def programs():
    for name, (defs, (vsh, fsh)) in PROGRAMS.items():
        d = "".join(f"#define {x}\n" for x in defs)
        write(os.path.join(SHADERS, name + ".vsh"), f'{HEAD}{d}#include "{vsh}"\n')
        write(os.path.join(SHADERS, name + ".fsh"), f'{HEAD}{d}#include "{fsh}"\n')
    for name in QUADS:
        write(os.path.join(SHADERS, name + ".vsh"), f'{HEAD}#include "/lib/quad.vsh"\n')
    for name, (src, out, size, way) in BLURS.items():
        write(os.path.join(SHADERS, name + ".fsh"),
              f'{HEAD}#define FROM {src}\n#define SIZE {size}\n#define STEP {way}\n/* RENDERTARGETS: {out} */\n#include "/lib/blur.fsh"\n')


def expand(path, seen=None):
    out = []
    for line in open(path, encoding="utf8").read().split("\n"):
        m = re.match(r'\s*#include\s+"(.*)"', line)
        out.append(expand(SHADERS + m[1]) if m else line)
    return "\n".join(out)


class Pixel(ctypes.Structure):
    _fields_ = [("size", W.WORD), ("version", W.WORD), ("flags", W.DWORD), ("type", ctypes.c_ubyte), ("colour", ctypes.c_ubyte),
                ("rest", ctypes.c_ubyte * 18), ("mask", W.DWORD), ("visible", W.DWORD), ("damage", W.DWORD)]


def compiler():
    u, g, o = ctypes.windll.user32, ctypes.windll.gdi32, ctypes.windll.opengl32
    u.CreateWindowExW.restype = W.HWND
    u.CreateWindowExW.argtypes = [W.DWORD, W.LPCWSTR, W.LPCWSTR, W.DWORD, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, W.HWND, W.HMENU, W.HINSTANCE, W.LPVOID]
    u.GetDC.restype, u.GetDC.argtypes = W.HDC, [W.HWND]
    g.ChoosePixelFormat.argtypes, g.SetPixelFormat.argtypes = [W.HDC, ctypes.c_void_p], [W.HDC, ctypes.c_int, ctypes.c_void_p]
    o.wglCreateContext.restype, o.wglCreateContext.argtypes = W.HANDLE, [W.HDC]
    o.wglMakeCurrent.argtypes = [W.HDC, W.HANDLE]
    o.wglGetProcAddress.restype, o.wglGetProcAddress.argtypes = ctypes.c_void_p, [ctypes.c_char_p]
    o.glGetString.restype = ctypes.c_char_p
    win = u.CreateWindowExW(0, "STATIC", "emberlight", 0, 0, 0, 16, 16, None, None, None, None)   # never shown
    dc = u.GetDC(win)
    pf = Pixel(size=40, version=1, flags=0x25, type=0, colour=32)
    pf.rest[13] = 24  # depth bits
    g.SetPixelFormat(dc, g.ChoosePixelFormat(dc, ctypes.byref(pf)), ctypes.byref(pf))
    rc = o.wglCreateContext(dc)
    assert rc and o.wglMakeCurrent(dc, rc), "no GL context"

    def fn(name, res, *args):
        return ctypes.CFUNCTYPE(res, *args)(o.wglGetProcAddress(name))

    create = fn(b"glCreateShader", ctypes.c_uint, ctypes.c_uint)
    source = fn(b"glShaderSource", None, ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_char_p), ctypes.c_void_p)
    comp = fn(b"glCompileShader", None, ctypes.c_uint)
    geti = fn(b"glGetShaderiv", None, ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(ctypes.c_int))
    log = fn(b"glGetShaderInfoLog", None, ctypes.c_uint, ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p)

    def check(kind, text):
        s = create(kind)
        src = ctypes.c_char_p(text.encode())
        source(s, 1, ctypes.byref(src), None)
        comp(s)
        ok = ctypes.c_int(0)
        geti(s, 0x8B81, ctypes.byref(ok))
        buf = ctypes.create_string_buffer(8192)
        log(s, 8192, None, buf)
        return ok.value == 1, buf.value.decode(errors="replace")

    return check, o.glGetString(0x1F01).decode() + " / " + o.glGetString(0x1F02).decode()


def verify():
    check, who = compiler()
    print("compiling on", who)
    bad = 0
    for f in sorted(os.listdir(SHADERS)):
        if not f.endswith((".vsh", ".fsh")):
            continue
        text = expand(os.path.join(SHADERS, f))
        head, rest = text.split("\n", 1)
        ok, log = check(0x8B31 if f.endswith("vsh") else 0x8B30, f"{head}\n{STUBS}{rest}")
        if not ok:
            bad += 1
            print("FAIL", f, "\n" + log[:1500])
    print("failed" if bad else "all compile", bad)
    return bad == 0


def install():
    if os.path.isdir(INSTALL):
        shutil.rmtree(INSTALL)
    shutil.copytree(SHADERS, os.path.join(INSTALL, "shaders"))


def release():
    path = os.path.join(RELEASE, f"Ashbound-Emberlight-{VERSION}.zip")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(SHADERS):
            for f in files:
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, PACK).replace(os.sep, "/"))
    print(path)


if __name__ == "__main__":
    programs()
    if not verify():
        sys.exit(1)
    install()
    if "--zip" in sys.argv:
        release()
