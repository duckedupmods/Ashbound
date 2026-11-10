"""The bow's bare frame for the icon: a limb bent along a curve from the top right tip to the bottom left one, bulging
up and left, and the string straight between them. Letters: h outer edge, s limb, d inner edge, g grip, t tips,
w string, o outline. Each bow paints its own look over this."""
import math


def frame(c=(2.2, 2.2), thick=2.1, a=(13.6, 1.4), b=(1.4, 13.6), grip=0.16, tip=0.07, string=True):
    pts = []
    for i in range(401):
        t = i / 400
        x = (1 - t) ** 2 * a[0] + 2 * t * (1 - t) * c[0] + t * t * b[0]
        y = (1 - t) ** 2 * a[1] + 2 * t * (1 - t) * c[1] + t * t * b[1]
        pts.append((t, x, y))
    g = [["."] * 16 for _ in range(16)]
    lx, ly = b[0] - a[0], b[1] - a[1]
    ln = math.hypot(lx, ly)
    for y in range(16):
        for x in range(16):
            px, py = x + 0.5, y + 0.5
            t, qx, qy = min(pts, key=lambda p: (p[1] - px) ** 2 + (p[2] - py) ** 2)
            d = math.hypot(qx - px, qy - py)
            if d <= thick / 2:
                side = ((px - a[0]) * ly - (py - a[1]) * lx) / ln   # >0 away from the string, up-left
                qs = ((qx - a[0]) * ly - (qy - a[1]) * lx) / ln
                if abs(t - 0.5) < grip / 2:
                    g[y][x] = "g"
                elif t < tip or t > 1 - tip:
                    g[y][x] = "t"
                elif d > thick / 2 - 0.75 and side < qs:
                    g[y][x] = "h"
                elif d > thick / 2 - 0.75:
                    g[y][x] = "d"
                else:
                    g[y][x] = "s"
            elif string and abs((px - a[0]) * ly - (py - a[1]) * lx) / ln < 0.55 and \
                    0 <= ((px - a[0]) * lx + (py - a[1]) * ly) / ln <= ln:
                g[y][x] = "w"
    out = [r[:] for r in g]
    for y in range(16):
        for x in range(16):
            if g[y][x] == ".":
                if any(0 <= x + u < 16 and 0 <= y + v < 16 and g[y + v][x + u] in "hsdgt"
                       for u, v in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    out[y][x] = "o"
    return ["".join(r) for r in out]


if __name__ == "__main__":
    print("\n".join(frame()))
