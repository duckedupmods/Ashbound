"""Reads and writes gzipped NBT (structure templates) as plain Python: compounds are dicts, lists are lists,
with each number's tag kept by wrapping it (Tag(type, value)) so a file reads back and writes out unchanged."""
import gzip
import struct


class Tag:
    __slots__ = ("t", "v")

    def __init__(self, t, v):
        self.t, self.v = t, v

    def __repr__(self):
        return "Tag(%d, %r)" % (self.t, self.v)


_FMT = {1: ">b", 2: ">h", 3: ">i", 4: ">q", 5: ">f", 6: ">d"}


def _rstr(b, i):
    n = struct.unpack_from(">H", b, i)[0]
    return b[i + 2:i + 2 + n].decode("utf-8"), i + 2 + n


def _read(t, b, i):
    if t in _FMT:
        f = _FMT[t]
        return Tag(t, struct.unpack_from(f, b, i)[0]), i + struct.calcsize(f)
    if t == 8:
        return _rstr(b, i)
    if t in (7, 11, 12):
        n = struct.unpack_from(">i", b, i)[0]
        i += 4
        f, w = {7: (">b", 1), 11: (">i", 4), 12: (">q", 8)}[t]
        return Tag(t, [struct.unpack_from(f, b, i + k * w)[0] for k in range(n)]), i + n * w
    if t == 9:
        et, n = struct.unpack_from(">bi", b, i)
        i += 5
        out = []
        for _ in range(n):
            v, i = _read(et, b, i)
            out.append(v)
        return ("list", et, out), i
    if t == 10:
        d = {}
        while True:
            tt = b[i]
            i += 1
            if tt == 0:
                return d, i
            k, i = _rstr(b, i)
            d[k], i = _read(tt, b, i)
    raise ValueError(t)


def read(path):
    b = gzip.open(path, "rb").read()
    assert b[0] == 10
    _, i = _rstr(b, 1)
    return _read(10, b, i)[0]


def _wstr(s, out):
    e = s.encode("utf-8")
    out += struct.pack(">H", len(e)) + e


def _tid(v):
    if isinstance(v, Tag):
        return v.t
    if isinstance(v, str):
        return 8
    if isinstance(v, tuple):
        return 9
    if isinstance(v, dict):
        return 10
    raise TypeError(v)


def _write(v, out):
    if isinstance(v, Tag):
        if v.t in _FMT:
            out += struct.pack(_FMT[v.t], v.v)
        else:
            f = {7: ">b", 11: ">i", 12: ">q"}[v.t]
            out += struct.pack(">i", len(v.v))
            for x in v.v:
                out += struct.pack(f, x)
    elif isinstance(v, str):
        _wstr(v, out)
    elif isinstance(v, tuple):
        _, et, items = v
        out += struct.pack(">bi", et if items else 0, len(items))
        for x in items:
            _write(x, out)
    else:
        for k, x in v.items():
            out += struct.pack(">b", _tid(x))
            _wstr(k, out)
            _write(x, out)
        out += b"\x00"


def write(path, root):
    out = bytearray(b"\x0a")
    _wstr("", out)
    _write(root, out)
    with gzip.open(path, "wb") as f:
        f.write(bytes(out))
