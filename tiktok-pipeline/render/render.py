#!/usr/bin/env python3
"""
Renderer "pixel-story" : prend une spec JSON de scènes et produit une vidéo 1080x1920 (9:16)
dans le style : fond noir + halo chaud, illustration pixel-art centrée, grosses captions animées,
petites étiquettes encadrées avec flèche, HUD (année / compteur), poussières.
Usage : python3 render.py spec.json out.mp4 [--palette yellow] [--audio voice.mp3] [--assets-dir DIR] [--timing timing.json] [--frame 12.3 out.png]
Spec : {"handle": "", "assets": [{"id","description_fr","prompt"}], "scenes": [{"id","vo","asset","caption",...}]}
- Un plan peut donner "duration" (s) ; sinon la durée vient de --timing {scene_id: {"start","end"}} (issu de la voix) ; sinon estimée depuis "vo" (≈15 caractères/s).
- "asset" = id résolu en <assets-dir>/<id>.png ; si le fichier manque, un placeholder est dessiné (utile pour prévisualiser un storyboard avant les images).
- Compatibilité : "image" = chemin direct vers un PNG (anciennes specs).
"""
import json, math, random, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")

PALETTES = {
    # accent = couleur dominante (captions, HUD, halo), sprite_hue = rotation de teinte des illustrations (0 = inchangé)
    "yellow": {"accent": (247, 192, 61), "light": (255, 228, 140), "glow": (92, 62, 14), "hue": 0},
    "orange": {"accent": (255, 122, 40), "light": (255, 190, 140), "glow": (96, 40, 10), "hue": -20},
    "cyan":   {"accent": (62, 220, 230), "light": (170, 245, 250), "glow": (10, 70, 80), "hue": 140},
    "green":  {"accent": (120, 230, 110), "light": (200, 255, 190), "glow": (20, 80, 25), "hue": 80},
    "violet": {"accent": (190, 120, 255), "light": (225, 195, 255), "glow": (60, 20, 90), "hue": 220},
    "red":    {"accent": (255, 70, 70), "light": (255, 170, 160), "glow": (100, 15, 15), "hue": -40},
}
BG = (6, 4, 2)
WHITE = (246, 242, 232)
GREY = (150, 145, 135)

def font(name, size):
    path = {"big": "Montserrat-ExtraBold.ttf", "black": "Montserrat-Black.ttf",
            "pixel": "Silkscreen-Bold.ttf", "pixel_r": "Silkscreen-Regular.ttf",
            "retro": "PressStart2P.ttf", "mono": "VT323.ttf"}[name]
    return ImageFont.truetype(os.path.join(FONTS, path), size)

# ---------- easing ----------
def ease_out_back(t, s=1.70158):
    t = min(max(t, 0), 1); t -= 1
    return t * t * ((s + 1) * t + s) + 1
def ease_out_cubic(t):
    t = min(max(t, 0), 1); return 1 - (1 - t) ** 3
def ease_in_out(t):
    t = min(max(t, 0), 1); return t * t * (3 - 2 * t)

# ---------- background ----------
_bg_cache = {}
def background(pal):
    key = pal["glow"]
    if key in _bg_cache: return _bg_cache[key]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W / 2, H * 0.47
    d = np.sqrt(((xx - cx) / (W * 0.62)) ** 2 + ((yy - cy) / (H * 0.36)) ** 2)
    k = np.clip(1 - d, 0, 1) ** 1.6
    arr = np.zeros((H, W, 3), np.float32)
    for i in range(3):
        arr[..., i] = BG[i] + (pal["glow"][i] - BG[i]) * k
    img = Image.fromarray(arr.astype(np.uint8), "RGB")
    _bg_cache[key] = img
    return img

class Dust:
    def __init__(self, n=70, seed=3):
        rnd = random.Random(seed)
        self.p = [(rnd.random() * W, rnd.random() * H, rnd.uniform(8, 20), rnd.uniform(2, 4), rnd.random()) for _ in range(n)]
    def draw(self, draw, t, pal):
        for (x, y, speed, size, ph) in self.p:
            yy = (y - t * speed) % H
            xx = x + math.sin(t * 0.7 + ph * 6.28) * 6
            a = 0.25 + 0.25 * math.sin(t * 2 + ph * 6.28)
            col = tuple(int(BG[i] + (pal["light"][i] - BG[i]) * a) for i in range(3))
            draw.rectangle([xx, yy, xx + size, yy + size], fill=col)

# ---------- sprites ----------
_sprite_cache = {}
def load_sprite(path, hue):
    key = (path, hue)
    if key in _sprite_cache: return _sprite_cache[key]
    im = Image.open(path).convert("RGBA")
    if hue:
        hsv = np.array(im.convert("RGB").convert("HSV")).astype(np.int16)
        hsv[..., 0] = (hsv[..., 0] + int(hue * 255 / 360)) % 256
        rgb = Image.fromarray(hsv.astype(np.uint8), "HSV").convert("RGB")
        im = Image.merge("RGBA", (*rgb.split(), im.split()[3]))
    # fond noir -> transparent (pour les captures de référence) ; sans effet si déjà transparent
    arr = np.array(im)
    dark = (arr[..., :3].max(axis=2) < 22)
    arr[dark, 3] = 0
    im = Image.fromarray(arr, "RGBA")
    _sprite_cache[key] = im
    return im

def paste_sprite(canvas, sprite, cx, cy, scale, alpha=1.0):
    w, h = sprite.size
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    sp = sprite.resize((nw, nh), Image.NEAREST)
    if alpha < 1:
        a = sp.split()[3].point(lambda v: int(v * alpha))
        sp.putalpha(a)
    canvas.alpha_composite(sp, (int(cx - nw / 2), int(cy - nh / 2)))

# ---------- text ----------
def wrap(draw, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=f) <= maxw or not cur: cur = test
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def draw_caption(canvas, text, y, t_in, pal, color="white", size=84, align="center", highlight=None, shadow=True):
    """Grosse caption : pop-in avec overshoot. highlight = mot(s) en couleur accent."""
    if t_in < 0: return
    k = ease_out_back(t_in / 0.28)
    f = font("black", int(size * (0.75 + 0.25 * k)))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    col = pal["accent"] if color == "accent" else WHITE
    lines = wrap(d, text.upper(), f, W - 160)
    lh = int(f.size * 1.18)
    total = lh * len(lines)
    yy = y - total / 2
    for line in lines:
        tw = d.textlength(line, font=f)
        x = (W - tw) / 2 if align == "center" else 80
        # mots en highlight
        cx = x
        for word in line.split(" "):
            wcol = pal["accent"] if (highlight and word.strip(".,!?").lower() in highlight) else col
            if shadow: d.text((cx + 5, yy + 5), word, font=f, fill=(0, 0, 0))
            d.text((cx, yy), word, font=f, fill=wcol)
            cx += d.textlength(word + " ", font=f)
        yy += lh
    a = int(255 * min(1, t_in / 0.12))
    if a < 255: layer.putalpha(layer.split()[3].point(lambda v: v * a // 255))
    canvas.alpha_composite(layer)

def draw_label(canvas, text, x, y, t_in, pal, arrow_to=None, color="white", size=30):
    """Petite étiquette encadrée (style pixel) + flèche optionnelle vers un point."""
    if t_in < 0: return
    k = ease_out_cubic(t_in / 0.2)
    f = font("pixel", size)
    d = ImageDraw.Draw(canvas)
    tw = d.textlength(text.upper(), font=f); th = size
    pad = 14
    bw, bh = tw + pad * 2, th + pad * 2
    bx, by = x - bw / 2, y - bh / 2
    border = pal["accent"] if color == "accent" else WHITE
    # apparition par "scan" de gauche à droite
    vis_w = bw * k
    d.rectangle([bx, by, bx + vis_w, by + bh], fill=(10, 8, 4), outline=border, width=4)
    if k > 0.6:
        d.text((bx + pad, by + pad - 2), text.upper(), font=f, fill=border)
    if arrow_to and k >= 1:
        tx, ty = arrow_to
        # ligne en escalier (pixel) : vertical puis horizontal
        d.line([(x, by + bh if ty > y else by), (x, ty)], fill=border, width=5)
        d.line([(x, ty), (tx, ty)], fill=border, width=5)
        s = 14
        dirx = 1 if tx > x else -1
        d.polygon([(tx, ty), (tx - dirx * s, ty - s), (tx - dirx * s, ty + s)], fill=border)

def draw_year(canvas, text, t_in, pal, pos=(W - 80, 200)):
    if t_in < 0: return
    f = font("retro", 54)
    d = ImageDraw.Draw(canvas)
    tw = d.textlength(text, font=f)
    x, y = pos[0] - tw, pos[1]
    # effet "compteur" : chiffres qui défilent pendant 0.35s
    if t_in < 0.35 and text.strip().isdigit():
        rnd = random.Random(int(t_in * 60))
        text = "".join(str(rnd.randint(0, 9)) if ch.isdigit() else ch for ch in text)
    d.text((x + 4, y + 4), text, font=f, fill=(0, 0, 0))
    d.text((x, y), text, font=f, fill=pal["accent"])

def draw_bars(canvas, bars, t_in, pal, y_base=1250, maxh=520):
    """Diagramme en barres pixel : bars = [{label, value, color?}] ; montée animée."""
    if t_in < 0: return
    d = ImageDraw.Draw(canvas)
    n = len(bars); gap = 40; bw = min(170, (W - 200 - gap * (n - 1)) // n)
    total = n * bw + (n - 1) * gap; x0 = (W - total) / 2
    vmax = max(b["value"] for b in bars)
    fl = font("pixel", 26); fv = font("retro", 30)
    for i, b in enumerate(bars):
        k = ease_out_cubic((t_in - i * 0.15) / 0.5)
        h = maxh * (b["value"] / vmax) * k
        x = x0 + i * (bw + gap)
        col = pal["accent"] if b.get("color", "accent") == "accent" else GREY
        d.rectangle([x, y_base - h, x + bw, y_base], fill=col)
        # texture pixel : lignes horizontales sombres tous les 12px
        for yy in range(int(y_base - h), y_base, 12):
            d.line([(x, yy), (x + bw, yy)], fill=tuple(int(c * 0.82) for c in col), width=2)
        lab = b["label"].upper(); tw = d.textlength(lab, font=fl)
        d.text((x + bw / 2 - tw / 2, y_base + 18), lab, font=fl, fill=WHITE)
        if k > 0.9:
            val = b.get("display", str(b["value"])); tw = d.textlength(val, font=fv)
            d.text((x + bw / 2 - tw / 2, y_base - h - 46), val, font=fv, fill=WHITE)

def draw_handle(canvas, handle, pal):
    if not handle: return
    d = ImageDraw.Draw(canvas); f = font("pixel_r", 26)
    tw = d.textlength(handle, font=f)
    d.text(((W - tw) / 2, H - 330), handle, font=f, fill=tuple(int(c * 0.55) for c in WHITE))


# ---------- assets : résolution + placeholder ----------
_placeholder_cache = {}
def placeholder_sprite(asset_id, desc, pal):
    key = (asset_id, pal["accent"])
    if key in _placeholder_cache: return _placeholder_cache[key]
    size = 640
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = tuple(int(c * 0.55) for c in pal["accent"])
    # cadre en pointillés "pixel"
    step = 24
    for x in range(16, size - 16, step):
        d.rectangle([x, 16, x + 12, 24], fill=col); d.rectangle([x, size - 24, x + 12, size - 16], fill=col)
    for y in range(16, size - 16, step):
        d.rectangle([16, y, 24, y + 12], fill=col); d.rectangle([size - 24, y, size - 16, y + 12], fill=col)
    f1 = font("pixel", 30); f2 = font("pixel_r", 22)
    d.text((48, 60), "ASSET", font=f1, fill=col)
    d.text((48, 100), asset_id.upper()[:26], font=f1, fill=pal["light"])
    lines = wrap(d, desc or "", f2, size - 96)[:7]
    for i, line in enumerate(lines):
        d.text((48, 170 + i * 34), line, font=f2, fill=(170, 165, 150))
    _placeholder_cache[key] = im
    return im

def estimate_duration(vo):
    return max(1.8, min(6.0, len(vo) / 15.0))

def prepare(spec, assets_dir, timing, spec_dir=None):
    """Résout durée et image de chaque plan (clés privées _dur / _img / _ph)."""
    assets = {a["id"]: a for a in spec.get("assets", [])}
    spec_dir = spec_dir or HERE
    for sc in spec["scenes"]:
        if "duration" in sc: sc["_dur"] = float(sc["duration"])
        elif timing and sc.get("id") in timing:
            t = timing[sc["id"]]; sc["_dur"] = max(0.8, float(t["end"]) - float(t["start"]))
        else: sc["_dur"] = estimate_duration(sc.get("vo", ""))
        sc["_img"] = None; sc["_ph"] = None
        if sc.get("image"):
            sc["_img"] = sc["image"] if os.path.isabs(sc["image"]) else os.path.join(spec_dir, sc["image"])
        elif sc.get("asset"):
            cand = os.path.join(assets_dir or os.path.join(HERE, "assets"), sc["asset"] + ".png")
            if os.path.exists(cand): sc["_img"] = cand
            else: sc["_ph"] = (sc["asset"], assets.get(sc["asset"], {}).get("description_fr", ""))
    return spec

# ---------- scene ----------
def render_frame(spec, pal, t, dust):
    scenes = spec["scenes"]
    # trouver la scène courante
    acc = 0; cur = None; t_local = 0
    for sc in scenes:
        if t < acc + sc["_dur"]: cur = sc; t_local = t - acc; break
        acc += sc["_dur"]
    if cur is None: cur = scenes[-1]; t_local = cur["_dur"]
    canvas = background(pal).convert("RGBA")
    d = ImageDraw.Draw(canvas)
    dust.draw(d, t, pal)
    # flash blanc très court à la coupe (comme un "pop")
    # illustration
    sp = None
    if cur.get("_img"): sp = load_sprite(cur["_img"], pal["hue"])
    elif cur.get("_ph"): sp = placeholder_sprite(cur["_ph"][0], cur["_ph"][1], pal)
    if sp is not None:
        base = cur.get("scale", 1.0) * (W * 0.86) / sp.size[0]
        # entrée : pop (0.25s) puis zoom lent
        k = ease_out_back(t_local / 0.25) if cur.get("enter", "pop") == "pop" else 1
        zoom = 1 + 0.045 * (t_local / max(cur["_dur"], 0.1))
        cy = H * cur.get("y", 0.52)
        paste_sprite(canvas, sp, W / 2, cy, base * zoom * (0.85 + 0.15 * k), alpha=min(1, t_local / 0.1))
    if cur.get("bars"):
        draw_bars(canvas, cur["bars"], t_local - cur.get("bars_delay", 0.2), pal)
    # caption principale
    if cur.get("caption"):
        draw_caption(canvas, cur["caption"], H * cur.get("caption_y", 0.17), t_local - cur.get("caption_delay", 0),
                     pal, color=cur.get("caption_color", "white"), size=cur.get("caption_size", 84),
                     highlight=set(w.lower() for w in cur.get("highlight", [])))
    if cur.get("sub"):
        draw_caption(canvas, cur["sub"], H * cur.get("sub_y", 0.27), t_local - cur.get("sub_delay", 0.35),
                     pal, color=cur.get("sub_color", "accent"), size=cur.get("sub_size", 54))
    for lab in cur.get("labels", []):
        draw_label(canvas, lab["text"], lab["x"] * W, lab["y"] * H, t_local - lab.get("delay", 0.4), pal,
                   arrow_to=(lab["to"][0] * W, lab["to"][1] * H) if lab.get("to") else None,
                   color=lab.get("color", "white"))
    if cur.get("year"):
        draw_year(canvas, cur["year"], t_local - cur.get("year_delay", 0.1), pal)
    draw_handle(canvas, spec.get("handle"), pal)
    return canvas.convert("RGB")

def main():
    args = sys.argv[1:]
    spec = json.load(open(args[0])); out = args[1]
    pal = PALETTES[args[args.index("--palette") + 1]] if "--palette" in args else PALETTES["yellow"]
    audio = args[args.index("--audio") + 1] if "--audio" in args else None
    assets_dir = args[args.index("--assets-dir") + 1] if "--assets-dir" in args else None
    timing = json.load(open(args[args.index("--timing") + 1])) if "--timing" in args else None
    prepare(spec, assets_dir, timing, spec_dir=os.path.dirname(os.path.abspath(args[0])))
    dust = Dust()
    if "--frame" in args:  # rendu d'une seule image pour contrôle
        t = float(args[args.index("--frame") + 1]); png = args[args.index("--frame") + 2]
        render_frame(spec, pal, t, dust).save(png); print("frame", png); return
    total = sum(s["_dur"] for s in spec["scenes"])
    n = int(total * FPS)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    if audio: cmd += ["-i", audio, "-shortest"]
    else: cmd += ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(render_frame(spec, pal, i / FPS, dust).tobytes())
        if i % 150 == 0: print(f"  {i}/{n} frames", flush=True)
    p.stdin.close(); p.wait()
    print("done", out, f"{total:.1f}s")

if __name__ == "__main__":
    main()
