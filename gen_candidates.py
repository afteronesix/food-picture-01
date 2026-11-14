#!/usr/bin/env python3
"""Draw 3 food-picture candidates for make.fun food-picture-01 (PIL, deterministic).
Build tooling only — NOT part of the final entry. Seed fixed; same bytes every run.
"""
import math, random, os
from PIL import Image, ImageDraw, ImageFilter

W = H = 1024
RNG = random.Random(42)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "candidates")

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def vgrad(size, top, bottom):
    img = Image.new("RGB", size)
    px = img.load()
    for y in range(size[1]):
        c = lerp(top, bottom, y / max(1, size[1] - 1))
        for x in range(size[0]):
            px[x, y] = c
    return img

def radial_glow(size, center, radius, color, peak=255):
    """Soft radial glow layer (RGBA), brightest at center."""
    glow = Image.new("L", size, 0)
    d = ImageDraw.Draw(glow)
    steps = 48
    for i in range(steps, 0, -1):
        r = radius * i / steps
        a = int(peak * (1 - i / steps) ** 1.6)
        d.ellipse([center[0] - r, center[1] - r, center[0] + r, center[1] + r], fill=a)
    glow = glow.filter(ImageFilter.GaussianBlur(radius * 0.12))
    solid = Image.new("RGB", size, color)
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.paste(solid, (0, 0), glow)
    return out

def vignette(img, strength=110):
    ov = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(ov)
    d.ellipse([-220, -220, W + 220, H + 220], fill=255)
    ov = ov.filter(ImageFilter.GaussianBlur(220))
    black = Image.new("RGBA", img.size, (0, 0, 0, 255))
    img.paste(black, (0, 0), Image.eval(ov, lambda v: strength * (255 - v) // 255))
    return img

def soft_shadow(img, box, blur=28, alpha=150):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)
    d.ellipse(box, fill=(0, 0, 0, alpha))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(sh)
    return img

def steam(img, wisps):
    """wisps: list of (x_base, y_base, height, amp, width, alpha)."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for (xb, yb, hgt, amp, wdt, alpha) in wisps:
        pts = []
        steps = 40
        for i in range(steps + 1):
            t = i / steps
            y = yb - hgt * t
            x = xb + math.sin(t * math.pi * 2.2) * amp * t
            pts.append((x, y))
        d.line(pts, fill=(255, 255, 255, alpha), width=wdt, joint="curve")
    layer = layer.filter(ImageFilter.GaussianBlur(7))
    img.alpha_composite(layer)
    return img

def gloss(img, box, start_deg, end_deg, color=(255, 255, 255), alpha=110, width=14, blur=6):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.arc(box, start_deg, end_deg, fill=color + (alpha,), width=width)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(layer)
    return img

def speckle(img, box, n, colors, rmin=1, rmax=3, alpha=200):
    d = ImageDraw.Draw(img, "RGBA")
    x0, y0, x1, y1 = box
    for _ in range(n):
        x = RNG.uniform(x0, x1); y = RNG.uniform(y0, y1)
        r = RNG.uniform(rmin, rmax)
        c = RNG.choice(colors)
        d.ellipse([x - r, y - r, x + r, y + r], fill=c + (alpha,))
    return img

# ---------------------------------------------------------------- A: SHRIMP
def draw_shrimp():
    img = vgrad((W, H), (26, 15, 8), (52, 30, 13)).convert("RGBA")
    img.alpha_composite(radial_glow((W, H), (300, 220), 520, (255, 150, 50), 90))
    img.alpha_composite(radial_glow((W, H), (512, 560), 430, (255, 120, 30), 55))
    # faint wood planks
    d = ImageDraw.Draw(img, "RGBA")
    for y in (180, 400, 640, 880):
        d.line([(0, y), (W, y)], fill=(0, 0, 0, 45), width=3)
    img = vignette(img, 120)

    cx, cy, pan_r = 512, 565, 385
    img = soft_shadow(img, [cx - pan_r, cy - pan_r + 55, cx + pan_r, cy + pan_r + 55], 34, 170)
    # pan handle (to upper right)
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([cx + 300, cy - 330, cx + 560, cy - 250], radius=28, fill=(16, 12, 9, 255))
    d.rounded_rectangle([cx + 300, cy - 330, cx + 560, cy - 250], radius=28, outline=(90, 70, 50, 255), width=4)
    d.ellipse([cx + 490, cy - 302, cx + 530, cy - 278], fill=(0, 0, 0, 255))
    # pan body
    d.ellipse([cx - pan_r, cy - pan_r, cx + pan_r, cy + pan_r], fill=(22, 16, 11, 255))
    d.ellipse([cx - pan_r, cy - pan_r, cx + pan_r, cy + pan_r], outline=(96, 74, 52, 255), width=7)
    d.ellipse([cx - pan_r + 26, cy - pan_r + 26, cx + pan_r - 26, cy + pan_r - 26],
              fill=(30, 21, 13, 255))
    gloss(img, [cx - pan_r + 40, cy - pan_r + 40, cx + pan_r - 40, cy + pan_r - 40],
          195, 265, alpha=70, width=22, blur=10)
    # melted butter pools
    for (bx, by, brx, bry, col) in [
            (430, 470, 150, 70, (245, 166, 38)), (620, 640, 170, 80, (238, 150, 28)),
            (560, 420, 110, 55, (250, 184, 60)), (400, 660, 120, 60, (240, 158, 32))]:
        d.ellipse([bx - brx, by - bry, bx + brx, by + bry], fill=col + (255,))
        d.ellipse([bx - brx * 0.6, by - bry * 0.6, bx + brx * 0.2, by + bry * 0.1],
                  fill=(255, 214, 110, 200))
    # shrimp: individual crescents, each a plump C with stripes + tail fan
    def crescent(sx, sy, r_out, r_in, a0, a1):
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(layer)
        steps = 48
        pts = []
        for i in range(steps + 1):
            a = math.radians(a0 + (a1 - a0) * i / steps)
            pts.append((sx + r_out * math.cos(a), sy + r_out * math.sin(a)))
        for i in range(steps, -1, -1):
            a = math.radians(a0 + (a1 - a0) * i / steps)
            pts.append((sx + r_in * math.cos(a), sy + r_in * math.sin(a)))
        dl.polygon(pts, fill=(255, 112, 56, 255))
        pts2 = []
        for i in range(steps + 1):
            a = math.radians(a0 + (a1 - a0) * i / steps)
            pts2.append((sx + (r_out - 16) * math.cos(a), sy + (r_out - 16) * math.sin(a)))
        for i in range(steps, -1, -1):
            a = math.radians(a0 + (a1 - a0) * i / steps)
            pts2.append((sx + (r_in + 10) * math.cos(a), sy + (r_in + 10) * math.sin(a)))
        dl.polygon(pts2, fill=(255, 158, 96, 255))
        # rounded caps at both ends
        for ae in (a0, a1):
            ex = sx + (r_out + r_in) / 2 * math.cos(math.radians(ae))
            ey = sy + (r_out + r_in) / 2 * math.sin(math.radians(ae))
            dl.ellipse([ex - 27, ey - 27, ex + 27, ey + 27], fill=(255, 112, 56, 255))
            dl.ellipse([ex - 18, ey - 18, ex + 18, ey + 18], fill=(255, 158, 96, 255))
        # segment stripes across the band
        for k in range(6):
            a = math.radians(a0 + (a1 - a0) * (k + 0.5) / 6)
            x1 = sx + (r_in + 2) * math.cos(a); y1 = sy + (r_in + 2) * math.sin(a)
            x2 = sx + (r_out - 2) * math.cos(a); y2 = sy + (r_out - 2) * math.sin(a)
            dl.line([(x1, y1), (x2, y2)], fill=(216, 64, 26, 230), width=6)
        # tail fan at the a1 end
        ex = sx + (r_out + r_in) / 2 * math.cos(math.radians(a1))
        ey = sy + (r_out + r_in) / 2 * math.sin(math.radians(a1))
        tang = math.radians(a1 + 90)
        for off in (-18, 0, 18):
            tx = ex + 30 * math.cos(tang + math.radians(off))
            ty = ey + 30 * math.sin(tang + math.radians(off))
            px = math.cos(tang + math.radians(off + 90))
            py = math.sin(tang + math.radians(off + 90))
            dl.polygon([(ex, ey), (tx + 13 * px, ty + 13 * py), (tx - 13 * px, ty - 13 * py)],
                       fill=(232, 78, 31, 255))
        return layer.filter(ImageFilter.GaussianBlur(1.0))

    for (sx, sy, ro, ri, a0, a1) in [
            (430, 480, 105, 52, 200, 20), (620, 460, 100, 50, 160, 340),
            (680, 620, 105, 52, 90, 270), (520, 690, 100, 50, 20, 200),
            (370, 640, 95, 48, 300, 120), (540, 560, 80, 40, 240, 60)]:
        img.alpha_composite(crescent(sx, sy, ro, ri, a0, a1))
    # garlic chips + parsley + chili
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(14):
        gx = RNG.uniform(200, 824); gy = RNG.uniform(280, 850)
        if (gx - 512) ** 2 + (gy - 565) ** 2 > 330 ** 2:
            continue
        d.ellipse([gx - 13, gy - 8, gx + 13, gy + 8], fill=(242, 193, 78, 255),
                  outline=(190, 130, 40, 255), width=2)
    for _ in range(22):
        gx = RNG.uniform(220, 804); gy = RNG.uniform(300, 830)
        if (gx - 512) ** 2 + (gy - 565) ** 2 > 330 ** 2:
            continue
        d.ellipse([gx - 5, gy - 3, gx + 5, gy + 3], fill=(63, 158, 77, 230))
    for _ in range(16):
        gx = RNG.uniform(220, 804); gy = RNG.uniform(300, 830)
        if (gx - 512) ** 2 + (gy - 565) ** 2 > 330 ** 2:
            continue
        d.ellipse([gx - 3, gy - 3, gx + 3, gy + 3], fill=(200, 40, 30, 230))
    # steam
    img = steam(img, [(430, 330, 260, 34, 16, 70), (560, 300, 300, 40, 18, 80),
                      (640, 360, 220, 28, 14, 60), (350, 380, 200, 26, 13, 55)])
    img = vignette(img, 60)
    return img.convert("RGB")

# ---------------------------------------------------------------- B: BURGER
def draw_burger():
    img = vgrad((W, H), (74, 40, 14), (30, 15, 6)).convert("RGBA")
    img.alpha_composite(radial_glow((W, H), (512, 480), 560, (255, 170, 60), 95))
    img = vignette(img, 110)

    # fries peeking from behind the burger, left + right clusters
    fries = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    df = ImageDraw.Draw(fries)
    for (x0, ang) in [(250, -24), (300, -12), (350, 0), (700, 0), (750, 12), (800, 24)]:
        ln = 330 + RNG.uniform(-20, 30)
        x1 = x0 + ln * math.sin(math.radians(ang)) * 0.55
        y1 = 660 - ln * math.cos(math.radians(ang))
        df.line([(x0, 700), (x1, y1)], fill=(240, 178, 62, 255), width=34)
        df.line([(x0 - 7, 700), (x1 - 7, y1)], fill=(255, 214, 110, 255), width=11)
    fries = fries.filter(ImageFilter.GaussianBlur(5))
    img.alpha_composite(fries)

    # dark slate board
    img = soft_shadow(img, [150, 800, 874, 930], 30, 160)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([140, 780, 884, 940], fill=(56, 40, 27, 255))
    d.ellipse([140, 780, 884, 940], outline=(150, 116, 74, 255), width=5)

    cx = 512
    # bottom bun
    d.rounded_rectangle([cx - 235, 700, cx + 235, 800], radius=46, fill=(232, 155, 45, 255))
    d.rounded_rectangle([cx - 235, 700, cx + 235, 760], radius=40, fill=(247, 186, 84, 255))
    # lettuce ruffle
    for i in range(11):
        x = cx - 240 + i * 48
        d.ellipse([x - 30, 668, x + 30, 716], fill=(111, 174, 63, 255))
    d.ellipse([cx - 250, 668, cx + 250, 700], fill=(140, 196, 84, 255))
    # tomato slice peeking
    d.ellipse([cx - 225, 640, cx + 225, 700], fill=(217, 56, 43, 255))
    d.ellipse([cx - 200, 648, cx + 200, 692], fill=(235, 90, 66, 255))
    # patty 1
    d.rounded_rectangle([cx - 250, 600, cx + 250, 668], radius=30, fill=(90, 46, 20, 255))
    for _ in range(60):
        px = RNG.uniform(cx - 240, cx + 240); py = RNG.uniform(606, 662)
        d.ellipse([px - 4, py - 3, px + 4, py + 3], fill=(58, 28, 12, 220))
    # cheese layer 1 with drips
    d.rounded_rectangle([cx - 245, 566, cx + 245, 606], radius=16, fill=(255, 181, 46, 255))
    for dx, dl in [(-190, 46), (-90, 66), (10, 40), (110, 72), (200, 50)]:
        d.rounded_rectangle([cx + dx - 22, 590, cx + dx + 22, 590 + dl], radius=22,
                            fill=(255, 181, 46, 255))
        d.ellipse([cx + dx - 22, 590 + dl - 22, cx + dx + 22, 590 + dl + 22],
                  fill=(255, 181, 46, 255))
    d.line([(cx - 220, 574), (cx + 220, 574)], fill=(255, 216, 120, 255), width=8)
    # patty 2
    d.rounded_rectangle([cx - 240, 500, cx + 240, 566], radius=28, fill=(96, 50, 22, 255))
    for _ in range(50):
        px = RNG.uniform(cx - 230, cx + 230); py = RNG.uniform(506, 560)
        d.ellipse([px - 4, py - 3, px + 4, py + 3], fill=(62, 30, 12, 220))
    # cheese layer 2, smaller drips
    d.rounded_rectangle([cx - 235, 470, cx + 235, 504], radius=14, fill=(255, 190, 60, 255))
    for dx, dl in [(-150, 40), (-30, 54), (90, 38), (180, 46)]:
        d.rounded_rectangle([cx + dx - 20, 492, cx + dx + 20, 492 + dl], radius=20,
                            fill=(255, 190, 60, 255))
        d.ellipse([cx + dx - 20, 492 + dl - 20, cx + dx + 20, 492 + dl + 20],
                  fill=(255, 190, 60, 255))
    # top bun dome — solid down to the cheese so it never floats
    d.pieslice([cx - 250, 190, cx + 250, 560], 180, 360, fill=(240, 168, 50, 255))
    d.pieslice([cx - 250, 190, cx + 250, 560], 180, 360, fill=(252, 200, 100, 255))
    d.pieslice([cx - 250, 230, cx + 250, 560], 180, 360, fill=(240, 168, 50, 255))
    d.rounded_rectangle([cx - 250, 360, cx + 250, 478], radius=28, fill=(240, 168, 50, 255))
    d.rectangle([cx - 250, 452, cx + 250, 478], fill=(216, 138, 31, 255))
    gloss(img, [cx - 260, 180, cx + 260, 560], 200, 290, alpha=120, width=26, blur=9)
    # sesame seeds
    for _ in range(26):
        sx = RNG.uniform(cx - 190, cx + 190)
        sy = RNG.uniform(250, 400)
        # keep seeds on the dome: y must be above the dome curve
        rel = abs(sx - cx) / 250.0
        topy = 315 - 125 * math.sqrt(max(0.0, 1 - rel ** 2)) + 125
        if sy < topy - 60 or sy > 440:
            continue
        d.ellipse([sx - 9, sy - 5, sx + 9, sy + 5], fill=(255, 232, 170, 255),
                  outline=(200, 150, 60, 255), width=1)
    # steam wisp above burger
    img = steam(img, [(470, 220, 190, 26, 13, 55), (560, 210, 210, 30, 14, 60)])
    img = vignette(img, 60)
    return img.convert("RGB")

# ---------------------------------------------------------------- C: MANGO
def draw_mango():
    img = vgrad((W, H), (253, 246, 233), (228, 238, 224)).convert("RGBA")
    img.alpha_composite(radial_glow((W, H), (760, 200), 480, (255, 244, 200), 110))
    # soft table edge at the bottom
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 880, W, H], fill=(214, 226, 212, 255))
    d.line([(0, 880), (W, 880)], fill=(190, 204, 190, 255), width=3)
    img = vignette(img, 45)

    cx, cy = 512, 545
    img = soft_shadow(img, [cx - 430, cy - 40, cx + 430, cy + 230], 30, 90)
    # ceramic plate — big, fills the frame
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([cx - 440, cy - 170, cx + 440, cy + 220], fill=(255, 255, 255, 255))
    d.ellipse([cx - 440, cy - 170, cx + 440, cy + 220], outline=(214, 220, 214, 255), width=4)
    d.ellipse([cx - 390, cy - 138, cx + 390, cy + 188], outline=(232, 236, 232, 255), width=3)
    # plate shadow-side tint
    d.arc([cx - 440, cy - 170, cx + 440, cy + 220], 10, 170, fill=(200, 208, 204, 160), width=16)

    # sticky rice mound — tall dome with a soft edge shadow
    img = soft_shadow(img, [cx - 300, cy - 120, cx + 300, cy + 165], 18, 70)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([cx - 300, cy - 150, cx + 300, cy + 150], fill=(255, 248, 234, 255),
              outline=(226, 208, 178, 255), width=3)
    d.ellipse([cx - 300, cy - 150, cx + 300, cy + 30], fill=(255, 252, 244, 255))
    gloss(img, [cx - 300, cy - 190, cx + 300, cy + 150], 200, 320, alpha=90, width=16, blur=8)
    # rice grains: tiny strokes, subtle
    for _ in range(260):
        gx = RNG.uniform(cx - 280, cx + 280); gy = RNG.uniform(cy - 150, cy + 130)
        rel = ((gx - cx) / 300) ** 2 + ((gy - cy) / 150) ** 2
        if rel > 0.92:
            continue
        ln = RNG.uniform(5, 10); an = RNG.uniform(0, math.pi)
        d.line([(gx, gy), (gx + ln * math.cos(an), gy + ln * math.sin(an))],
               fill=(239, 227, 200, 140), width=2)
    # coconut cream drizzle ribbons
    for (y0, amp, ph) in [(cy - 60, 14, 0.0), (cy - 10, 18, 1.3), (cy + 42, 14, 2.6)]:
        pts = []
        for i in range(41):
            t = i / 40
            x = cx - 270 + t * 540
            y = y0 + math.sin(t * math.pi * 2 + ph) * amp
            pts.append((x, y))
        d.line(pts, fill=(255, 255, 255, 235), width=13, joint="curve")
        d.line(pts, fill=(255, 255, 255, 255), width=6, joint="curve")
    # mango fan: overlapping petals on the right
    petal_specs = [
        (730, 520, 190, 74, -38), (680, 580, 200, 78, -18),
        (610, 615, 190, 74, 2), (540, 605, 165, 66, 20),
    ]
    for (px, py, ln, wd, rot) in petal_specs:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(layer)
        dl.ellipse([px - ln // 2, py - wd // 2, px + ln // 2, py + wd // 2],
                   fill=(255, 178, 44, 255))
        dl.ellipse([px - ln // 2 + 12, py - wd // 2 + 8, px + ln // 2 - 8, py + wd // 2 - 6],
                   fill=(255, 196, 80, 255))
        dl.ellipse([px - ln // 2 + 26, py - wd // 2 + 14, px + ln // 2 - 26, py + wd // 2 - 12],
                   fill=(255, 214, 120, 230))
        layer = layer.rotate(rot, center=(px, py), resample=Image.BICUBIC)
        img.alpha_composite(layer)
        d = ImageDraw.Draw(img, "RGBA")
        d.ellipse([px - ln // 2 + 20, py - wd // 2 + 6, px + ln // 2 - 60, py - wd // 2 + 22],
                  fill=(255, 235, 170, 200))
    # mango cubes on the left of the mound
    for (qx, qy, s, rot) in [(330, 540, 80, 12), (400, 500, 72, -8), (300, 610, 70, 28)]:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dl = ImageDraw.Draw(layer)
        dl.rounded_rectangle([qx - s // 2, qy - s // 2, qx + s // 2, qy + s // 2],
                             radius=12, fill=(255, 170, 36, 255))
        dl.rounded_rectangle([qx - s // 2 + 6, qy - s // 2 + 5, qx + s // 2 - 6, qy + s // 2 - 14],
                             radius=9, fill=(255, 196, 82, 255))
        layer = layer.rotate(rot, center=(qx, qy), resample=Image.BICUBIC)
        img.alpha_composite(layer)
    # toasted sesame + mint leaf + coconut flakes
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(30):
        sx = RNG.uniform(cx - 270, cx + 270); sy = RNG.uniform(cy - 130, cy + 130)
        rel = ((sx - cx) / 300) ** 2 + ((sy - cy) / 150) ** 2
        if rel > 0.9:
            continue
        d.ellipse([sx - 4, sy - 2, sx + 4, sy + 2], fill=(176, 128, 66, 255))
    # mint leaf: pointed oval with center vein, tilted
    mx, my = 740, 720
    leaf_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(leaf_layer)
    leaf_pts = []
    for i in range(21):
        t = i / 20
        wdt = 32 * math.sin(math.pi * t ** 0.9)
        leaf_pts.append((mx - wdt, my + 46 - 92 * t))
    for i in range(20, -1, -1):
        t = i / 20
        wdt = 32 * math.sin(math.pi * t ** 0.9)
        leaf_pts.append((mx + wdt, my + 46 - 92 * t))
    dl.polygon(leaf_pts, fill=(74, 160, 92, 255), outline=(46, 120, 66, 255))
    dl.line([(mx, my + 42), (mx, my - 42)], fill=(46, 120, 66, 255), width=3)
    leaf_layer = leaf_layer.rotate(-28, center=(mx, my), resample=Image.BICUBIC)
    img.alpha_composite(leaf_layer)
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(8):
        fx = RNG.uniform(cx - 240, cx + 240); fy = RNG.uniform(cy - 110, cy + 110)
        d.arc([fx - 12, fy - 5, fx + 12, fy + 5], 200, 340, fill=(255, 255, 255, 230), width=4)
    img = vignette(img, 30)
    return img.convert("RGB")

def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in [("a_shrimp", draw_shrimp), ("b_burger", draw_burger),
                     ("c_mango", draw_mango)]:
        im = fn()
        path = os.path.join(OUT, name + ".png")
        im.save(path, optimize=True)
        print(name, os.path.getsize(path), "bytes", im.size)

if __name__ == "__main__":
    main()
