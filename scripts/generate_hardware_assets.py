from __future__ import annotations
import math, os, random, sys
from pathlib import Path
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
from shapely.geometry import Polygon
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / 'public' / 'models'
ART_DIR = ROOT / 'public' / 'hardware'
MODEL_DIR.mkdir(parents=True, exist_ok=True)
ART_DIR.mkdir(parents=True, exist_ok=True)

# Original published bounding boxes (centre + extents per axis). Every regenerated
# model is normalised onto these so the FIT_SIZE hotspot coordinates authored
# against the originals keep landing on the right structures.
TARGET_BBOX = {
    "case":        {"center": [0.0375, 0.0, 0.0],      "extents": [3.275, 3.4, 2.39]},
    "cooling":     {"center": [0.0, -0.0375, 0.265],   "extents": [2.5, 2.625, 1.83]},
    "cpu":         {"center": [0.0, 0.0, 0.0],         "extents": [45.0, 37.5, 4.8]},
    "gpu":         {"center": [0.0, 0.075, 0.295],     "extents": [3.8, 2.41, 1.47]},
    "memory":      {"center": [0.0, -0.045, 0.125],    "extents": [3.6, 1.34, 0.41]},
    "motherboard": {"center": [0.0, 0.0025, 0.1925],   "extents": [3.6, 3.255, 0.515]},
    "network":     {"center": [-0.0075, 0.0, 0.1737],  "extents": [3.565, 2.2, 0.4925]},
    "power":       {"center": [0.0, 0.0625, 0.1075],   "extents": [3.25, 2.825, 2.665]},
    "storage":     {"center": [0.0, -0.0475, 0.11],    "extents": [3.55, 1.345, 0.34]},
}

# ---------------------------------------------------------------- palette ---
# Real hardware palette: matte solder mask, bare aluminium, gold contacts,
# copper heat-pipes, black plastic. No synthetic lab-instrument glow colours —
# the only emissive material is the frosted RGB diffuser used where real
# consumer hardware actually has RGB (memory, GPU logo, fans).
C = {
    'board': '#151a16',       # motherboard PCB — near-black solder mask
    'board2': '#181d18',      # CPU substrate / DIMM PCB — dark green mask
    'black': '#141517',       # black plastic (shroud, slots, connectors)
    'deep': '#0c0e10',        # deep recess / vent well
    'silver': '#a4abb0',      # bare aluminium
    'metal': '#8c9398',       # darker machined metal
    'darkmetal': '#393f45',   # stamped / painted dark metal
    'graphite': '#2b2f34',    # brushed dark metal (shroud, backplate)
    'red': '#c33a3a',         # anodised red heatsink fins (gaming look)
    'reddark': '#8e2b2b',     # deeper red for recesses / fan rims
    'white': '#e9ecef',       # white painted metal / fan hub
    'blue': '#3e5ba8',        # cobalt-blue plastic accent (case)
    'gold': '#d4a85c',        # gold contact fingers / pads
    'copper': '#c07a3e',      # copper heat-pipe
    'cream': '#e5e0d2',       # ceramic / label paper
    'rgb': '#e6e7ea',         # frosted RGB diffuser (base albedo)
}

def _rgb(hexstr):
    h = hexstr.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

# ---------------------------------------------------------------- fonts -----
FONT_CANDIDATES = [
    'C:/Windows/Fonts/arial.ttf',
    'C:/Windows/Fonts/consola.ttf',
    'C:/Windows/Fonts/cour.ttf',
    'C:/Windows/Fonts/segoeui.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf',
]
FONT_BOLD_CANDIDATES = [
    'C:/Windows/Fonts/arialbd.ttf',
    'C:/Windows/Fonts/consolab.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf',
]

def getfont(size, bold=False):
    for f in (FONT_BOLD_CANDIDATES if bold else FONT_CANDIDATES):
        try:
            if os.path.exists(f):
                return ImageFont.truetype(f, size)
        except Exception:
            continue
    return ImageFont.load_default()

# ---------------------------------------------------------------- PBR textures
# The lever that makes hard-surface hardware read as "real": structured surface
# relief (not random noise) baked into normal maps, per-pixel roughness/metalness
# variation, and per-material detail (solder mask + gold vias + silkscreen for
# PCBs, directional brushing for metal). Each set is generated once and shared by
# every mesh of a material, then baked into the GLB as PNG for MeshStandardMaterial.

N_HI = 512   # hero surfaces: PCB, brushed metal, heatsink, backplate
N_LO = 256   # simple surfaces: gold, copper, plastic, chip, ceramic, rgb

def _speckle(img, amp=2.0):
    """Very low-amplitude grain — structured textures, not noise."""
    n = (np.random.rand(*img.shape[:2], 1).astype(np.float32) - 0.5) * 2 * amp
    return np.clip(img + n, 0, 255)

def _h2n(h, strength=1.6):
    h = h.astype(np.float32)
    gy = np.zeros_like(h); gx = np.zeros_like(h)
    gy[1:-1, :] = h[2:, :] - h[:-2, :]
    gx[:, 1:-1] = h[:, 2:] - h[:, :-2]
    # A single global gain keeps every surface's relief in the same range while
    # per-material `strength` still weights how deep its detail should read. The
    # fields were authored too conservatively before, so brushed metal and PCB
    # traces read as flat plastic instead of catching grazing light.
    gain = strength * 1.6
    nx = -gx * gain; ny = -gy * gain; nz = np.ones_like(h)
    norm = np.sqrt(nx*nx + ny*ny + nz*nz) + 1e-8
    arr = np.stack([nx/norm, ny/norm, nz/norm], -1)
    return Image.fromarray(((arr * 0.5 + 0.5) * 255).clip(0, 255).astype(np.uint8))

def _rgba(arr):
    a = np.full((*arr.shape[:2], 1), 255, dtype=np.uint8)
    return Image.fromarray(np.concatenate([arr.astype(np.uint8), a], -1))

def _mr(met, rough, N, met_var=0.02, rough_var=0.03):
    m = np.clip(np.random.normal(met, met_var, N*N).reshape(N, N), 0, 1)
    r = np.clip(np.random.normal(rough, rough_var, N*N).reshape(N, N), 0, 1)
    out = np.zeros((N, N, 3), dtype=np.uint8)
    out[..., 1] = (r * 255).astype(np.uint8)   # G = roughness
    out[..., 2] = (m * 255).astype(np.uint8)   # B = metalness
    out[..., 0] = 255
    return _rgba(out)

def _draw(img):
    return ImageDraw.Draw(img)

def tex_pcb(color, N=N_HI):
    """Real solder mask: uniform matte green/black with exposed gold pads, gold
    vias, white silkscreen and faint copper traces showing through the mask.
    Traces read as slightly lighter/darker routes under the surface — the tell
    that separates a real board from a painted slab."""
    rng = random.Random(7)
    base = np.array(Image.new('RGB', (N, N), _rgb(color))).astype(np.float32)
    alb = Image.fromarray(base.astype(np.uint8)); da = _draw(alb)
    h = np.zeros((N, N), dtype=np.float32)
    gold = (198, 163, 92); hole = (16, 20, 16); sil = (224, 227, 222)
    # copper trace tone: a touch lighter/warmer than the mask so it glints faintly
    col = _rgb(color)
    trace = tuple(min(255, int(c * 0.72) + 40) for c in col)

    # faint solder-mask mottling: a few broad darker blobs (very subtle)
    for _ in range(26):
        x, y = rng.randint(0, N), rng.randint(0, N)
        r = rng.randint(24, 90)
        da.ellipse([x-r, y-r, x+r, y+r], fill=tuple(max(0, c-6) for c in col))

    # copper traces: 45/90-degree routes between pads and vias, 1–2 px wide
    for _ in range(72):
        x0, y0 = rng.randint(0, N), rng.randint(0, N)
        x1, y1 = rng.randint(0, N), rng.randint(0, N)
        if abs(x1 - x0) < 18 and abs(y1 - y0) < 18:
            continue
        w = 1 if rng.random() < 0.7 else 2
        # route with a single 45° or 90° jog — the classic PCB dog-leg
        if rng.random() < 0.5:
            mid = rng.randint(min(x0, x1), max(x0, x1)) if x1 != x0 else x0
            da.line([x0, y0, mid, y0], fill=trace, width=w)
            da.line([mid, y0, mid, y1], fill=trace, width=w)
            da.line([mid, y1, x1, y1], fill=trace, width=w)
        else:
            mid = rng.randint(min(y0, y1), max(y0, y1)) if y1 != y0 else y0
            da.line([x0, y0, x0, mid], fill=trace, width=w)
            da.line([x0, mid, x1, mid], fill=trace, width=w)
            da.line([x1, mid, x1, y1], fill=trace, width=w)
    # slight normal lift where traces sit, so they catch grazing light
    h = np.clip(np.asarray(alb.convert('L'), dtype=np.float32), 0, 255)
    h = (h - float(np.mean(h))) * 0.03

    # gold vias: tiny circle with a dark drill hole
    for _ in range(120):
        x, y = rng.randint(0, N-5), rng.randint(0, N-5)
        r = rng.randint(2, 4)
        da.ellipse([x-r, y-r, x+r, y+r], fill=gold)
        h[y-r:y+r, x-r:x+r] = 1.0
        da.ellipse([x-r//2, y-r//2, x+r//2, y+r//2], fill=hole)

    # exposed gold pads (SMD): small rectangles, often in rows
    for _ in range(46):
        x, y = rng.randint(0, N-14), rng.randint(0, N-8)
        w, hh = rng.randint(8, 18), rng.randint(3, 6)
        da.rectangle([x, y, x+w, y+hh], fill=gold)
        h[y:y+hh, x:x+w] = 0.8

    # silkscreen: white component outlines with a pin-1 dot
    for _ in range(12):
        x, y = rng.randint(6, N-46), rng.randint(6, N-38)
        w, hh = rng.randint(20, 44), rng.randint(14, 28)
        da.rectangle([x, y, x+w, y+hh], outline=sil, width=1)
        da.ellipse([x+3, y+3, x+8, y+8], outline=sil, width=1)
        h[y:y+hh, x:x+w] = 0.4

    # silkscreen text labels (technical, generic)
    fnt = getfont(max(11, N // 26))
    for _ in range(7):
        x, y = rng.randint(4, N-60), rng.randint(4, N-16)
        da.text((x, y), rng.choice(['CPU', 'DIMM', 'PCIe', 'M.2', 'USB3.2', 'SATA', 'ATX', 'PWM']),
                fill=sil, font=fnt)
    base = _speckle(np.array(alb).astype(np.float32), 2.0)
    return _rgba(base), _h2n(h, 1.4), _mr(0.0, 0.62, N, 0.02, 0.04)

def tex_brush(color, N=N_HI):
    """Directional brushed metal: fine, regular parallel grain + low-frequency
    sheen. The regular grain reads as brushed aluminium under the environment map."""
    rng = random.Random(3)
    base = np.array(Image.new('RGB', (N, N), _rgb(color))).astype(np.float32)
    h = np.zeros((N, N), dtype=np.float32)
    for c in range(N):
        v = math.sin(c * 1.6) * 3.5 + rng.uniform(-1.4, 1.4)
        base[:, c, :] += v
        h[:, c] += v * 0.16
    # occasional deeper scratch line
    for _ in range(14):
        c = rng.randint(0, N-1); v = rng.uniform(-8, -4)
        base[:, c, :] += v; h[:, c] += v * 0.3
    base = _speckle(base, 1.2)
    return _rgba(base), _h2n(h, 1.2), _mr(0.98, 0.20, N, 0.015, 0.03)

def tex_heatsink(color, N=N_HI):
    """Brushed aluminium with faint vertical fin seams (for solid fin blocks)."""
    rng = random.Random(21)
    base = np.array(Image.new('RGB', (N, N), _rgb(color))).astype(np.float32)
    h = np.zeros((N, N), dtype=np.float32)
    for c in range(N):
        v = math.sin(c * 1.6) * 3 + rng.uniform(-1.2, 1.2)
        base[:, c, :] += v; h[:, c] += v * 0.14
    for c in range(0, N, 7):
        base[:, c:c+1, :] *= 0.86
        h[:, c:c+1] = -0.5
    base = _speckle(base, 1.2)
    return _rgba(base), _h2n(h, 1.2), _mr(0.98, 0.24, N, 0.015, 0.03)

def tex_backplate(color, N=N_HI):
    """Brushed dark metal with a faint embossed wordmark, used for GPU backplates."""
    rng = random.Random(33)
    base = np.array(Image.new('RGB', (N, N), _rgb(color))).astype(np.float32)
    h = np.zeros((N, N), dtype=np.float32)
    for c in range(N):
        v = math.sin(c * 1.6) * 3 + rng.uniform(-1.2, 1.2)
        base[:, c, :] += v; h[:, c] += v * 0.14
    alb = Image.fromarray(base.astype(np.uint8)); da = _draw(alb)
    light = tuple(min(255, c + 38) for c in _rgb(color))
    try:
        fnt = getfont(max(18, N // 12), bold=True)
        da.text((N*0.14, N*0.42), 'GPU', fill=light, font=fnt)
    except Exception:
        pass
    base = _speckle(np.array(alb).astype(np.float32), 1.2)
    return _rgba(base), _h2n(h, 1.2), _mr(0.95, 0.26, N, 0.015, 0.03)

def tex_gold(color, N=N_LO):
    """Gold contact: uniform warm gold with fine grain, low roughness."""
    base = np.array(Image.new('RGB', (N, N), _rgb(color))).astype(np.float32)
    h = np.zeros((N, N), dtype=np.float32)
    for c in range(0, N, 6):
        base[:, c, :] *= 0.97; h[:, c] = -0.2
    base = _speckle(base, 1.6)
    return _rgba(base), _h2n(h, 0.6), _mr(1.0, 0.16, N, 0.01, 0.02)

def tex_copper(color, N=N_LO):
    """Copper heat-pipe: smooth warm copper with a soft cylindrical sheen."""
    rng = random.Random(9)
    base = np.array(Image.new('RGB', (N, N), _rgb(color))).astype(np.float32)
    h = np.zeros((N, N), dtype=np.float32)
    for y in range(N):
        v = math.sin(y / N * math.pi) * 7 - 3
        base[y, :, :] += v; h[y, :] += v * 0.05
    base = _speckle(base, 1.4)
    return _rgba(base), _h2n(h, 0.7), _mr(1.0, 0.20, N, 0.01, 0.02)

def tex_plastic(color, N=N_LO):
    """Matte plastic: uniform with a very subtle grain."""
    base = np.array(Image.new('RGB', (N, N), _rgb(color))).astype(np.float32)
    base = _speckle(base, 2.2)
    h = (np.random.rand(N, N).astype(np.float32) - 0.5) * 0.08
    return _rgba(base), _h2n(h, 0.4), _mr(0.0, 0.48, N, 0.015, 0.03)

def tex_chip(color=C['black'], N=N_LO):
    """Black IC package: laser-etched marking frame, pin-1 dot, faint text lines."""
    rng = random.Random(11)
    base = np.array(Image.new('RGB', (N, N), _rgb(color))).astype(np.float32)
    alb = Image.fromarray(base.astype(np.uint8)); da = _draw(alb)
    mk = tuple(max(0, c + 42) for c in _rgb(color))
    da.rectangle([N*0.14, N*0.18, N*0.86, N*0.82], outline=mk, width=1)
    da.ellipse([N*0.08, N*0.08, N*0.18, N*0.18], fill=mk)
    for y in np.linspace(N*0.28, N*0.74, 5):
        da.line([N*0.20, y, N*0.80, y], fill=mk, width=1)
    try:
        fnt = getfont(N // 14)
        da.text((N*0.30, N*0.50), 'IC', fill=mk, font=fnt)
    except Exception:
        pass
    base = _speckle(np.array(alb).astype(np.float32), 2.0)
    # The laser-etched marking reads as relief (raised above the package) rather
    # than printed ink — derived from the drawn albedo so it catches grazing light.
    lum = np.asarray(alb.convert('L'), dtype=np.float32)
    h = (lum - float(np.mean(lum))) * 0.30
    return _rgba(base), _h2n(h, 0.9), _mr(0.0, 0.42, N, 0.015, 0.03)

def tex_ceramic(color, N=N_LO):
    """Ceramic / label paper: uniform matte with faint grain."""
    base = np.array(Image.new('RGB', (N, N), _rgb(color))).astype(np.float32)
    base = _speckle(base, 2.4)
    h = (np.random.rand(N, N).astype(np.float32) - 0.5) * 0.10
    return _rgba(base), _h2n(h, 0.5), _mr(0.05, 0.55, N, 0.015, 0.03)

def tex_recess(color, N=N_LO):
    """Deep recess / vent well: dark matte."""
    base = np.array(Image.new('RGB', (N, N), _rgb(color))).astype(np.float32)
    base = _speckle(base, 1.8)
    h = (np.random.rand(N, N).astype(np.float32) - 0.5) * 0.05
    return _rgba(base), _h2n(h, 0.3), _mr(0.2, 0.6, N, 0.02, 0.03)

def tex_rgb(color, N=N_LO):
    """Frosted RGB diffuser: translucent-white base; emissive colour set in material."""
    base = np.array(Image.new('RGB', (N, N), _rgb(color))).astype(np.float32)
    h = np.zeros((N, N), dtype=np.float32)
    for c in range(0, N, 8):
        base[:, c, :] *= 0.985
    base = _speckle(base, 1.4)
    return _rgba(base), _h2n(h, 0.2), _mr(0.1, 0.35, N, 0.01, 0.02)

# ---------------------------------------------------------------- photo PBR --
# CC0 photo-scanned metal PBR sets (ambientCG, public domain) replace the
# synthetic grain for bare-metal materials. Real brushed scratches and per-pixel
# roughness variation are what stop metal reading as painted plastic.
TEX_DIR = Path(__file__).resolve().parent / 'assets' / 'textures'

def _photo_set(asset, size=N_HI):
    """Loads a 1K ambientCG set and returns (albedo, normal, mr) at `size`."""
    d = TEX_DIR / asset
    alb = Image.open(d / f'{asset}_Color.jpg').convert('RGB').resize((size, size), Image.LANCZOS)
    nrm = Image.open(d / f'{asset}_NormalGL.jpg').convert('RGB').resize((size, size), Image.LANCZOS)
    rough = np.asarray(Image.open(d / f'{asset}_Roughness.jpg').convert('L').resize((size, size), Image.LANCZOS), dtype=np.float32)
    metal = np.asarray(Image.open(d / f'{asset}_Metalness.jpg').convert('L').resize((size, size), Image.LANCZOS), dtype=np.float32)
    mr = np.zeros((size, size, 3), dtype=np.uint8)
    mr[..., 1] = rough.astype(np.uint8)   # G = roughness
    mr[..., 2] = metal.astype(np.uint8)   # B = metalness
    mr[..., 0] = 255
    return alb, nrm, _rgba(mr)

def tex_photo(asset):
    """A TEXFN-style callable that ignores the tint and returns the scanned set."""
    alb, nrm, mr = _photo_set(asset)
    return lambda _color: (alb, nrm, mr)

def tex_photo_tint(asset, tint):
    """Photo-scanned grain tinted toward a target colour — gives anodised/painted
    metal the same real brushed scratches as the bare-aluminium set, but coloured."""
    alb, nrm, mr = _photo_set(asset)
    arr = np.asarray(alb, dtype=np.float32)
    t = np.array(_rgb(tint), dtype=np.float32) / 255.0
    tinted = np.clip(arr * t, 0, 255).astype(np.uint8)
    return lambda _color: (Image.fromarray(tinted), nrm, mr)

TEXFN = {'pcb': tex_pcb, 'brush': tex_brush, 'plastic': tex_plastic,
         'gold': tex_gold, 'copper': tex_copper, 'ceramic': tex_ceramic,
         'recess': tex_recess, 'chip': tex_chip, 'heatsink': tex_heatsink,
         'backplate': tex_backplate, 'rgb': tex_rgb,
         'photo_alu': tex_photo('Metal051C_1K-JPG'),
         'photo_light': tex_photo('Metal014_1K-JPG'),
         'photo_mid': tex_photo('Metal030_1K-JPG'),
         'photo_dark': tex_photo('Metal029_1K-JPG'),
         'photo_red': tex_photo_tint('Metal051C_1K-JPG', C['red']),
         'photo_reddark': tex_photo_tint('Metal051C_1K-JPG', C['reddark'])}

# material spec: name -> (color, metallic, roughness, emissive, tex_kind)
# metallic/roughness are baked into the MR texture; emissive only for RGB.
MATSPEC = {
    'board':      (C['board'],     0.0, 0.62, None,       'pcb'),
    'board2':     (C['board2'],    0.0, 0.60, None,       'pcb'),
    'black':      (C['black'],     0.0, 0.48, None,       'plastic'),
    'graphite':   (C['graphite'],  0.85, 0.38, None,      'photo_dark'),
    'silver':     (C['silver'],    0.92, 0.30, None,      'photo_alu'),
    'metal':      (C['metal'],     0.88, 0.34, None,      'photo_light'),
    'darkmetal':  (C['darkmetal'], 0.80, 0.42, None,      'photo_mid'),
    'red':        (C['red'],       0.55, 0.36, None,      'photo_red'),
    'reddark':    (C['reddark'],   0.50, 0.42, None,      'photo_reddark'),
    'white':      (C['white'],     0.15, 0.40, None,      'plastic'),
    'blue':       (C['blue'],      0.25, 0.45, None,      'plastic'),
    'gold':       (C['gold'],      0.95, 0.20, None,      'gold'),
    'copper':     (C['copper'],    0.95, 0.26, None,      'copper'),
    'cream':      (C['cream'],     0.05, 0.55, None,      'ceramic'),
    'deep':       (C['deep'],      0.20, 0.60, None,      'recess'),
    'chip':       (C['black'],     0.0,  0.42, None,      'chip'),
    'heatsink':   (C['silver'],    0.90, 0.34, None,      'photo_alu'),
    'backplate':  (C['graphite'],  0.85, 0.38, None,      'photo_dark'),
    'rgb':        (C['rgb'],       0.10, 0.35, '#9fc0e8', 'rgb'),
    'rgb_purple': (C['rgb'],       0.10, 0.35, '#9f6be0', 'rgb'),
}

TEX = {name: TEXFN[kind](color) for name, (color, _, _, _, kind) in MATSPEC.items()}

# tiles-per-world-unit when baking UVs; brushed metals want fine grain
DENSITY = {'board': 3, 'board2': 3, 'black': 4, 'graphite': 9,
           'silver': 11, 'metal': 11, 'darkmetal': 11,
           'red': 9, 'reddark': 9, 'white': 5, 'blue': 5,
           'gold': 7, 'copper': 6, 'cream': 6, 'deep': 4,
           'chip': 5, 'heatsink': 11, 'backplate': 8, 'rgb': 4, 'rgb_purple': 4}

def mat(name, color, metallic, rough, emissive, kind):
    alb, normal, mr = TEX[name]
    return PBRMaterial(name=name, baseColorTexture=alb, normalTexture=normal,
                       metallicRoughnessTexture=mr, metallicFactor=1.0, roughnessFactor=1.0,
                       emissiveFactor=(tuple(v/255 for v in _rgb(emissive)) if emissive else None))

M = {name: mat(name, *spec) for name, spec in MATSPEC.items()}

# Tempered-glass side panel: translucent, highly reflective, no albedo texture.
_glass_albedo = Image.new('RGB', (4, 4), (200, 225, 235))
M['glass'] = PBRMaterial(name='glass', baseColorTexture=_glass_albedo,
                         metallicFactor=0.0, roughnessFactor=0.06,
                         alphaMode='BLEND', baseColorFactor=(0.80, 0.88, 0.94, 0.20))
DENSITY['glass'] = 1


def _rainbow_emissive(N=256):
    """A horizontal RGB spectrum baked as an emissive texture, for RGB light bars
    on memory modules and fan rings. The frosted albedo stays near-white; the
    colour comes entirely from the emissive map."""
    im = Image.new('RGB', (N, 16), (230, 231, 234))
    d = ImageDraw.Draw(im)
    stops = [(255, 96, 96), (255, 205, 70), (120, 235, 120), (80, 205, 240),
             (128, 130, 255), (226, 96, 235)]
    for x in range(N):
        t = x / N * (len(stops) - 1)
        i = int(t); f = t - i
        c0 = stops[i]; c1 = stops[min(i + 1, len(stops) - 1)]
        col = tuple(int(c0[k] + (c1[k] - c0[k]) * f) for k in range(3))
        d.line([x, 0, x, 16], fill=col)
    return im

M['rgb_rainbow'] = PBRMaterial(name='rgb_rainbow',
                               baseColorTexture=Image.new('RGB', (4, 4), (230, 231, 234)),
                               emissiveTexture=_rainbow_emissive(),
                               emissiveFactor=(1.0, 1.0, 1.0),
                               metallicFactor=0.1, roughnessFactor=0.35)
DENSITY['rgb_rainbow'] = 4

# ---------------------------------------------------------------- primitives --

def _rounded_rect_points(w, h, r, seg=8):
    """Ordered perimeter points of a rounded rectangle centred on the origin."""
    a, b = w / 2, h / 2
    r = min(r, a * 0.999, b * 0.999)
    pts = []
    corners = [(a - r, b - r, 0), (-a + r, b - r, 90),
               (-a + r, -b + r, 180), (a - r, -b + r, 270)]
    for (cx, cy, sa) in corners:
        for k in range(seg + 1):
            ang = math.radians(sa + 90 * k / seg)
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts

def rbox(extents, pos=(0, 0, 0), material='graphite', radius=0.06, seg=8,
         round_plane='xy'):
    """A box with rounded perimeter edges (the most visible ones) and flat caps.
    Keeps the same outer bounding box as a sharp box of `extents`, so the
    loader's FIT_SIZE normalisation and authored hotspots stay valid."""
    sx, sy, sz = extents
    if round_plane == 'xy':
        w, h, depth = sx, sy, sz
    elif round_plane == 'xz':
        w, h, depth = sx, sz, sy
    else:  # 'yz'
        w, h, depth = sy, sz, sx
    poly = Polygon(_rounded_rect_points(w, h, radius, seg))
    mesh = trimesh.creation.extrude_polygon(poly, height=depth)
    mesh.apply_translation((0, 0, -depth / 2))
    if round_plane == 'xz':
        mesh.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]))
    elif round_plane == 'yz':
        mesh.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
    mesh.apply_translation(pos)
    mesh.metadata['mat'] = material
    return mesh

def box(extents, pos=(0, 0, 0), material='graphite'):
    """Sharp box kept for tiny detail parts where rounding is invisible."""
    mesh = trimesh.creation.box(extents=extents)
    mesh.apply_translation(pos)
    mesh.metadata['mat'] = material
    return mesh

def cyl(radius, height, pos=(0, 0, 0), axis='y', material='metal', sections=32):
    mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    if axis == 'y':
        pass
    elif axis == 'x':
        mesh.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
    elif axis == 'z':
        mesh.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]))
    mesh.apply_translation(pos)
    mesh.metadata['mat'] = material
    return mesh

def screw(pos, axis='y', r=0.05, material='silver', head='graphite'):
    """A small counter-sunk screw: a metal shaft, a recessed head, and a Phillips
    cross slot so the fastener reads as machined rather than a painted stud."""
    parts = [cyl(r, 0.05, pos, axis, material, 18)]
    hp = list(pos)
    if axis == 'y':
        hp[1] += 0.03
    elif axis == 'x':
        hp[0] += 0.03
    else:
        hp[2] += 0.03
    hr = r * 1.15
    parts.append(cyl(hr, 0.025, tuple(hp), axis, head, 18))
    # Phillips cross: two thin crossed bars embossed into the head. Their colour
    # is the dark recess, so it reads as a real slot against the head.
    if axis == 'y':
        parts.append(rbox((hr * 1.7, 0.02, hr * 0.4), (hp[0], hp[1] + 0.014, hp[2]), 'deep', 0.004, 2, 'xz'))
        parts.append(rbox((hr * 0.4, 0.02, hr * 1.7), (hp[0], hp[1] + 0.014, hp[2]), 'deep', 0.004, 2, 'xz'))
    return parts

def tube(radius, length, pos, axis='y', material='copper'):
    return cyl(radius, length, pos, axis=axis, material=material, sections=20)

def box_uv(mesh, density=6.0):
    """Per-face planar (box-projection) UVs so tiled PBR maps read correctly on
    hard-surface parts without a full unwrap. Density is tiles-per-world-unit so
    texel density stays consistent across parts of different sizes."""
    verts = mesh.vertices; faces = mesh.faces; fn = mesh.face_normals
    uv = np.zeros((len(verts), 2), dtype=np.float32)
    for f in range(len(faces)):
        n = fn[f]; ax = int(np.argmax(np.abs(n)))
        axes = [j for j in range(3) if j != ax]
        vc = verts[faces[f]]
        u = vc[:, axes[0]] * density
        v = vc[:, axes[1]] * density
        uv[faces[f]] = np.column_stack([u, v])
    uv -= uv.min(0)
    return uv

def _blade_points(R, r0, bow, n=7):
    """Curved axial-fan blade planform in the XY plane, blade pointing +X.
    Leading edge bows one way, trailing edge the other — a real airfoil sweep."""
    pts = []
    for k in range(n + 1):
        t = k / n
        x = r0 + (R - r0) * t
        y = bow * math.sin(math.pi * t) + (0.16 * R) * t
        pts.append((x, y))
    for k in range(n, -1, -1):
        t = k / n
        x = r0 + (R - r0) * t
        y = bow * math.sin(math.pi * t) - (0.12 * R) * t
        pts.append((x, y))
    return pts

def fan(radius, thick, pos=(0, 0, 0), axis='y', blades=9, material='black',
        hub='silver', ring=False):
    """A realistic axial fan: stepped hub with a printed label cap, curved
    pitched blades, and an optional outer ring."""
    parts = [cyl(radius * 0.30, thick * 1.6, (0, 0, 0), 'y', hub, 40)]
    parts.append(cyl(radius * 0.22, thick * 2.2, (0, 0, 0), 'y', material, 40))
    # centre label: cream sticker with a black outline — reads as a real brand cap
    parts.append(cyl(radius * 0.13, thick * 0.2, (0, 0, 0), 'y', 'cream', 26))
    parts.append(cyl(radius * 0.09, thick * 0.22, (0, 0, 0), 'y', 'black', 26))
    for i in range(blades):
        a = 2 * math.pi * i / blades
        poly = Polygon(_blade_points(radius * 0.94, radius * 0.26, 0.10 * radius))
        bl = trimesh.creation.extrude_polygon(poly, height=thick * 0.5)
        bl.apply_translation((0, 0, -thick * 0.25))
        # pitch the blade so it catches light and reads as a moving airfoil
        bl.apply_transform(trimesh.transformations.rotation_matrix(0.42, [1, 0, 0]))
        bl.apply_transform(trimesh.transformations.rotation_matrix(-a, [0, 0, 1]))
        parts.append(bl)
    if ring:
        parts.append(cyl(radius * 1.02, thick * 0.6, (0, 0, 0), 'y', material, 48))
        parts.append(cyl(radius * 1.06, thick * 0.6, (0, 0, 0), 'y', material, 48))
    rot = None
    if axis == 'x':
        rot = trimesh.transformations.rotation_matrix(math.pi / 2, [0, 0, 1])
    elif axis == 'z':
        rot = trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])
    for p in parts:
        if rot is not None:
            p.apply_transform(rot)
        p.apply_translation(pos)
    return parts

def fin_stack(w, h, d, n, pos, material='heatsink', fill=0.7):
    """Heatsink fin stack (thin fins spaced along Y) — the signature detail of
    real coolers and VRM/chipset blocks. A thin fin with a real air gap between
    reads far more 'metal' than a solid slab."""
    parts = []; gap = h / n
    for i in range(n):
        parts.append(rbox((w, gap * fill, d), (0, -h/2 + gap * (i + 0.5), 0), material, .008, 3, 'xz'))
    for p in parts:
        p.apply_translation(pos)
    return parts

def grille(w, h, pos, pitch=0.16, bar=0.03, border=0.08, depth=0.05,
           material='darkmetal', plane='xy'):
    """Perforated vent panel approximated by a frame plus intersecting bars."""
    parts = [rbox((w, h, depth), (0, 0, 0), material, .02, 4, 'xy')]
    nx = max(2, int(round((w - 2 * border) / pitch)))
    ny = max(2, int(round((h - 2 * border) / pitch)))
    bw = (w - 2 * border) / nx; bh = (h - 2 * border) / ny
    for i in range(nx + 1):
        x = -w / 2 + border + i * bw
        parts.append(rbox((bar, h - 2 * border, depth * 0.9), (x, 0, 0), material, .008, 3, 'xy'))
    for j in range(ny + 1):
        y = -h / 2 + border + j * bh
        parts.append(rbox((w - 2 * border, bar, depth * 0.9), (0, y, 0), material, .008, 3, 'xy'))
    rot = (trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]) if plane == 'xz'
           else trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]) if plane == 'yz' else None)
    for p in parts:
        if rot is not None:
            p.apply_transform(rot)
        p.apply_translation(pos)
    return parts

def cap_can(r, h, pos, axis='y', material='silver', top='graphite'):
    """Electrolytic capacitor: bare-aluminium can with a shrink-sleeve base, a
    dark crimp ring, and a scored vent pattern (cross) on the domed top."""
    parts = [cyl(r, h, pos, axis, material, 28)]
    top_pos = list(pos); bot_pos = list(pos)
    if axis == 'y':
        top_pos[1] += h / 2; bot_pos[1] -= h / 2
    elif axis == 'x':
        top_pos[0] += h / 2; bot_pos[0] -= h / 2
    else:
        top_pos[2] += h / 2; bot_pos[2] -= h / 2
    # top cap + crimp ring (slightly smaller, darker)
    parts.append(cyl(r * 0.96, h * 0.06, tuple(top_pos), axis, top, 28))
    parts.append(cyl(r * 1.0, h * 0.02, tuple(top_pos), axis, 'black', 28))
    # bottom rubber/plastic bung (the sleeve that insulates the can)
    parts.append(cyl(r * 0.92, h * 0.10, tuple(bot_pos), axis, 'black', 28))
    # scored vent cross on the top face, reading as a real safety vent
    if axis == 'y':
        parts.append(rbox((r * 1.5, 0.006, r * 0.18), (top_pos[0], top_pos[1] + 0.012, top_pos[2]), 'deep', 0.003, 2, 'xz'))
        parts.append(rbox((r * 0.18, 0.006, r * 1.5), (top_pos[0], top_pos[1] + 0.012, top_pos[2]), 'deep', 0.003, 2, 'xz'))
    return parts

def chip(w, d, h, pos, plane='xz', material='chip'):
    """Surface-mount IC package; `tex_chip` supplies the etched marking."""
    return [rbox((w, h, d), pos, material, .02, 4, plane)]

def smd(w, d, pos, material='cream', axis='x'):
    """A tiny surface-mount component (resistor/capacitor): a ceramic body with
    two silver end caps. The two-tone read is what makes it a real SMD part
    rather than a stray box, and a board full of them is the single strongest
    cue that a PCB is populated rather than painted."""
    x, z = pos
    y = 0.062
    h = 0.026
    parts = [rbox((w, h, d), (x, y, z), material, 0.004, 2, 'xz')]
    capw = max(0.010, w * 0.24)
    for dx in (-w / 2 + capw / 2, w / 2 - capw / 2):
        parts.append(rbox((capw, h * 1.08, d * 1.05), (x + dx, y, z), 'silver', 0.003, 2, 'xz'))
    return parts

def smd_field(x0, x1, z0, z1, n, materials=('cream', 'black', 'darkmetal'), seed=0):
    """Scatters `n` SMD components across a board rectangle with jitter, so the
    area reads as a densely populated PCB."""
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        x = rng.uniform(x0, x1)
        z = rng.uniform(z0, z1)
        w = rng.choice([0.05, 0.06, 0.08, 0.10])
        d = rng.choice([0.024, 0.030, 0.036])
        out += smd(w, d, (x, z), material=rng.choice(materials))
    return out

def vent_slats(w, h, pos, plane='xy', n=7, gap=0.07, depth=0.04, material='darkmetal'):
    """Parallel ventilation slats on a panel."""
    parts = []
    span = h if plane == 'xy' else w
    for i in range(n):
        off = -span / 2 + (i + 0.5) * (span / n)
        if plane == 'xy':
            parts.append(rbox((w, gap, depth), (pos[0], pos[1] + off, pos[2]), material, .01, 3, 'xy'))
        else:
            parts.append(rbox((gap, h, depth), (pos[0] + off, pos[1], pos[2]), material, .01, 3, 'xy'))
    return parts

def scene_export(name, meshes):
    sc = trimesh.Scene()
    flat = []
    for m in meshes:
        if isinstance(m, list):
            flat.extend(m)
        else:
            flat.append(m)
    for i, m in enumerate(flat):
        key = m.metadata.get('mat', 'graphite')
        m.visual = trimesh.visual.TextureVisuals(
            uv=box_uv(m, DENSITY.get(key, 5)),
            material=M[key],
        )
        sc.add_geometry(m, node_name=f'{name}_{i:03d}', geom_name=f'{name}_{i:03d}')
    (MODEL_DIR / f'{name}.glb').write_bytes(sc.export(file_type='glb'))


def normalize_model(name):
    """Scale + translate the freshly written model onto its original bounding box
    so the FIT_SIZE hotspot anchors stay valid for every regeneration."""
    path = MODEL_DIR / f'{name}.glb'
    scene = trimesh.load(str(path))
    box = scene.bounding_box
    nc = np.asarray(box.centroid)
    ne = np.asarray(box.extents)
    tgt = TARGET_BBOX[name]
    oc = np.asarray(tgt["center"], dtype=float)
    oe = np.asarray(tgt["extents"], dtype=float)
    scale = (oe / ne).tolist()
    T = np.eye(4)
    T[:3, :3] = np.diag(scale)
    T[:3, 3] = oc - nc * np.asarray(scale)
    scene.apply_transform(T)
    path.write_bytes(scene.export(file_type='glb'))

# ---------------------------------------------------------------- models ----

def motherboard():
    ms = [rbox((3.6, .1, 3.25), (0, 0, 0), 'board', .05, 8, 'xz')]
    # --- CPU socket: retention frame + socket body + LGA pin grid + load lever
    ms += [rbox((1.2, .1, 1.2), (-.55, .1, -.18), 'silver', .03, 6, 'xz'),
           rbox((1.02, .09, 1.02), (-.55, .17, -.18), 'black', .025, 6, 'xz')]
    # gold LGA contact pads inside the socket
    for x in np.linspace(-.95, -.15, 8):
        for z in np.linspace(-.6, .24, 8):
            ms.append(cyl(.022, .02, (float(x), .22, float(z)), 'y', 'gold', 10))
    # load lever arm along one edge
    ms += [rbox((.08, .03, 1.0), (-1.13, .23, -.18), 'silver', .015, 3, 'xz'),
           rbox((.5, .04, .1), (-.9, .27, -.66), 'metal', .015, 3, 'xz')]
    # --- four DIMM slots: slot body + gold contacts + two clip tabs
    for x in [.55, .75, .95, 1.15]:
        ms.append(rbox((.1, .16, 2.2), (x, .16, -.05), 'black', .02, 4, 'xz'))
        ms.append(rbox((.06, .03, 2.0), (x, .25, -.05), 'gold', .012, 3, 'xz'))
        for zc in [-1.0, 1.0]:
            ms.append(rbox((.12, .07, .12), (x, .18, zc), 'black', .015, 3, 'xz'))
    # --- PCIe x16 slots (two, with lane gap) + a short x1, gold fingers + tabs
    for z, long in [(1.34, True), (.72, True)]:
        ms.append(rbox((.34, .11, .1), (-.7, .14, z), 'black', .02, 4, 'xy'))
        ms.append(rbox((.34, .11, .1), (.7, .14, z), 'black', .02, 4, 'xy'))
        ms.append(rbox((.44, .025, .045), (-.35, .21, z), 'gold', .01, 3, 'xy'))
        ms.append(rbox((.12, .07, .12), (-.95, .18, z), 'black', .015, 3, 'xz'))
    ms.append(rbox((.5, .12, .09), (-.55, .14, 1.04), 'black', .02, 4, 'xy'))
    ms.append(rbox((.42, .025, .04), (-.5, .22, 1.04), 'gold', .01, 3, 'xy'))
    # --- VRM: anodised-red fin-stack heatsinks + chokes + capacitor cans
    ms += fin_stack(.4, .5, .24, 12, (-1.22, .5, -1.02), 'red', fill=.7)
    ms += fin_stack(.4, .5, .24, 12, (-1.22, .5, -.68), 'red', fill=.7)
    for i in range(4):
        ms.append(rbox((.16, .08, .16), (-1.28 + i * .22, .28, -.85), 'darkmetal', .02, 4, 'xz'))
    for i in range(5):
        ms += cap_can(.07, .2, (-1.05 + i * .2, .2, -.6), 'y', 'silver', 'graphite')
    # --- chipset heatsink (red fin block with a silver accent cap, subtle logo)
    ms += [rbox((.66, .12, .66), (.92, .2, .88), 'red', .03, 5, 'xz'),
           fin_stack(.52, .16, .52, 8, (.92, .4, .88), 'red', fill=.7),
           rbox((.3, .03, .3), (.92, .52, .88), 'silver', .015, 4, 'xz')]
    # --- M.2 slot + standoff
    ms += [rbox((.95, .08, .25), (.3, .14, -1.15), 'black', .02, 4, 'xz'),
           cyl(.05, .08, (.7, .2, -1.15), 'y', 'silver', 18)]
    # --- rear I/O shield with port cut-outs (USB / LAN / audio / video)
    ms += [rbox((.72, .62, .08), (0, .22, -1.46), 'silver', .03, 4, 'xy')]
    for i, col in enumerate(['darkmetal', 'darkmetal', 'black', 'black', 'black']):
        ms.append(rbox((.13, .13, .1), (-.24 + i * .12, .2 + (i % 2) * .26, -1.46), col, .01, 3, 'xy'))
    ms.append(cyl(.09, .12, (.26, .22, -1.46), 'x', 'black', 18))
    # --- 24-pin ATX power (right edge, tall connector, 2 rows of gold pins)
    ms += [rbox((.56, .5, .18), (.2, .45, 1.5), 'black', .03, 4, 'xy')]
    for r_ in [-.16, .16]:
        for k in range(12):
            ms.append(cyl(.018, .06, (-.1 + k * .05, .55, 1.5 + r_), 'z', 'gold', 8))
    # --- 8-pin EPS (top-left)
    ms += [rbox((.36, .28, .16), (-1.35, .38, -.95), 'black', .03, 4, 'xy')]
    for k in range(8):
        ms.append(cyl(.016, .05, (-1.52 + (k % 4) * .11, .45, -.95 + (k // 4) * .08), 'z', 'gold', 8))
    # --- SATA ports (right edge, lower)
    for i in range(3):
        ms += [rbox((.16, .12, .1), (.1, .2, 1.3 - i * .14), 'black', .015, 3, 'xy'),
               rbox((.12, .05, .07), (.1, .24, 1.3 - i * .14), 'darkmetal', .01, 3, 'xy')]
    # --- capacitor array (electrolytic cans near the edge)
    for i in range(8):
        ms += cap_can(.065, .18, (-1.05 + i * .22, .16, .2), 'y', 'silver', 'graphite')
    # --- corner screws
    for sx_, sz_ in [(-1.7, -1.5), (1.7, -1.5), (-1.7, 1.5), (1.7, 1.5)]:
        ms += screw((sx_, .06, sz_), 'y', .045, 'silver', 'graphite')
    # --- dense SMD population + scattered driver ICs: a real board is covered in
    # tiny passives, the single strongest cue that it is populated rather than painted.
    ms += smd_field(-1.55, -0.8, 0.55, 1.2, 22, seed=101)
    ms += smd_field(1.3, 1.68, 0.55, 1.2, 18, seed=102)
    ms += smd_field(1.3, 1.68, -1.0, 0.2, 16, seed=103)
    ms += smd_field(-1.55, -0.85, -0.4, 0.45, 20, seed=105)
    for x, z, w in [(-1.05, 0.9, .3), (1.45, -0.6, .34), (-0.15, -0.95, .28), (0.15, 0.9, .32)]:
        ms += chip(w, w, .12, (x, .09, z))
    return ms

def cpu():
    # Intel 12th-gen "Alder Lake" LGA1700 CPU (e.g. Core i9-12900K): a real
    # 45 × 37.5 mm package with a 37.5 mm square nickel-plated IHS. Authored in
    # millimetres so the part carries its true size for later 1:1 assembly.
    W, D = 45.0, 37.5            # package footprint (mm)
    IHS = 37.5                   # IHS is a 37.5 mm square
    SH = 1.4                     # substrate (PCB) thickness
    S_TOP, S_BOT = SH / 2, -SH / 2
    ms = []

    # --- substrate: dark-green fibre PCB with rounded corners ---
    ms.append(rbox((W, SH, D), (0, 0, 0), 'board2', 0.5, 8, 'xz'))

    # --- gold plated seal ring around the IHS footprint ---
    ring = IHS + 1.2
    bar = 0.28
    for s in (+1, -1):
        ms.append(rbox((ring, 0.04, bar), (0, S_TOP + 0.02, s * (ring - bar) / 2), 'gold', 0.02, 3, 'xz'))
        ms.append(rbox((bar, 0.04, ring), (s * (ring - bar) / 2, S_TOP + 0.02, 0), 'gold', 0.02, 3, 'xz'))

    # --- nickel IHS: a stepped two-tier profile (machined bevel) ---
    lower_y = S_TOP + 0.75
    upper_y = lower_y + 1.5
    ms.append(rbox((IHS, 1.5, IHS), (0, lower_y, 0), 'metal', 0.35, 8, 'xz'))
    ms.append(rbox((IHS - 0.5, 1.5, IHS - 0.5), (0, upper_y, 0), 'silver', 0.35, 8, 'xz'))
    IHS_TOP = upper_y + 0.75

    # --- gold orientation triangle in one corner (pin-1 / key marker) ---
    cx, cz = -(IHS / 2 - 2.6), IHS / 2 - 2.6
    for i in range(5):
        ms.append(rbox((0.55, 0.03, 0.55 + i * 0.35), (cx + i * 0.28, IHS_TOP + 0.02, cz - i * 0.35), 'gold', 0.02, 2, 'xz'))

    # --- faint laser-etched marking block (model + batch text) ---
    ms.append(rbox((12.0, 0.02, 6.0), (0, IHS_TOP + 0.015, -4.0), 'graphite', 0.03, 3, 'xz'))
    ms.append(rbox((5.0, 0.015, 1.0), (0, IHS_TOP + 0.018, 2.0), 'graphite', 0.02, 3, 'xz'))

    # --- decoupling MLCC caps ring around the IHS on the substrate top ---
    cap_y = S_TOP + 0.12
    for x in np.arange(-16.0, 16.1, 1.4):
        for z in (IHS / 2 + 2.2, -(IHS / 2 + 2.2)):
            ms.append(rbox((0.85, 0.30, 0.5), (float(x), cap_y, z), 'cream', 0.04, 3, 'xz'))
    for z in np.arange(-13.0, 13.1, 1.4):
        for x in (W / 2 - 2.6, -(W / 2 - 2.6)):
            ms.append(rbox((0.5, 0.30, 0.85), (x, cap_y, float(z)), 'cream', 0.04, 3, 'xz'))

    # --- underside: 1700 flat LGA gold lands, merged into one mesh ---
    pad_meshes = []
    pad_y = S_BOT - 0.06
    for x in np.arange(-21.5, 21.6, 1.05):
        for z in np.arange(-18.0, 18.1, 1.05):
            if abs(x) < 9.5 and abs(z) < 9.5:
                continue
            pad_meshes.append(box((0.85, 0.12, 0.85), (float(x), pad_y, float(z))))
    pads = trimesh.util.concatenate(pad_meshes)
    pads.metadata['mat'] = 'gold'
    ms.append(pads)

    # --- central underside MLCCs (die-side decoupling, inside the pad ring) ---
    for x in np.arange(-7.0, 7.1, 1.5):
        for z in np.arange(-7.0, 7.1, 1.15):
            ms.append(rbox((0.85, 0.30, 0.5), (float(x), S_BOT - 0.15, float(z)), 'cream', 0.04, 3, 'xz'))

    return ms

def gpu():
    # PCB + a stepped, angular shroud (modern triple-fan card read)
    ms = [rbox((3.65, .14, 2.0), (0, 0, 0), 'board', .04, 6, 'xz')]
    ms += [rbox((3.8, .7, 2.2), (0, .32, 0), 'graphite', .05, 8, 'xz'),
           rbox((3.5, .16, 1.9), (0, .66, 0), 'graphite', .04, 7, 'xz'),
           rbox((3.2, .06, 1.6), (0, .74, 0), 'graphite', .03, 6, 'xz')]
    # fin-stack heatsink beneath the shroud (visible from the sides) — anodised
    # red, the signature gaming look, matching the reference's red fin-array.
    ms += fin_stack(3.25, .5, 1.95, 36, (0, .5, 0), 'red', fill=.68)
    # top ventilation slats on the shroud
    ms += vent_slats(3.4, 1.9, (0, .68, 0), 'xz', 12, .1, .06, 'darkmetal')
    # three recessed fan wells + realistic fans (centre fan offset like real cards)
    for x in [-1.2, 0, 1.2]:
        ms.append(rbox((1.1, .02, 1.1), (x, .75, 0), 'deep', .02, 4, 'xz'))
        ms.append(cyl(.55, .03, (x, .78, 0), 'y', 'deep', 32))
        ms += fan(.48, .1, (x, .8, 0), 'y', 9, 'black', 'silver')
    # metal backplate with screws, cut-outs and an RGB brand bar
    ms += [rbox((3.7, .06, 2.15), (0, -.34, 0), 'backplate', .03, 6, 'xz'),
           rbox((.5, .06, .5), (-1.2, -.34, -.4), 'deep', .02, 4, 'xz'),
           rbox((.5, .06, .5), (1.2, -.34, .4), 'deep', .02, 4, 'xz'),
           rbox((.9, .02, .22), (0, -.35, .95), 'rgb', .01, 3, 'xz')]
    for x, z in [(-1.6, -1.0), (1.6, -1.0), (-1.6, 1.0), (1.6, 1.0), (0, -1.0), (0, 1.0)]:
        ms += screw((x, -.32, z), 'y', .04, 'silver', 'graphite')
    # VRM / power-stage blocks on the exposed PCB edge
    for x in [-1.25, -.95, -.65, .45, .75, 1.05]:
        ms.append(rbox((.22, .12, .42), (x, -.24, .55), 'black', .02, 4, 'xz'))
    # PCIe gold fingers
    for x in np.linspace(-1.25, .85, 18):
        ms.append(rbox((.06, .07, .22), (float(x), -.18, 1.02), 'gold', .01, 3, 'xz'))
    # 8-pin PCIe power connectors on the top edge
    ms += [rbox((.5, .34, .3), (1.35, .15, -1.12), 'black', .03, 4, 'xy'),
           rbox((.5, .34, .3), (.85, .15, -1.12), 'black', .03, 4, 'xy'),
           rbox((.3, .05, .18), (1.35, .34, -1.12), 'black', .01, 3, 'xy'),
           rbox((.3, .05, .18), (.85, .34, -1.12), 'black', .01, 3, 'xy')]
    # display-output L-bracket with real rectangular port cut-outs (3 DP + 1 HDMI)
    ms += [rbox((.08, 1.0, .34), (1.95, -.1, 0), 'silver', .015, 3, 'xz'),
           rbox((.18, .9, .04), (1.97, -.1, 0), 'metal', .01, 3, 'xy')]
    for i in range(4):
        y = .32 - i * .22
        ms.append(rbox((.05, .12, .18), (1.99, y, 0), 'deep', .006, 3, 'xy'))
        ms.append(rbox((.04, .1, .16), (1.99, y, 0), 'black', .006, 3, 'xy'))
    return ms

def memory():
    ms = [rbox((3.6, .1, 1.25), (0, 0, 0), 'board2', .04, 6, 'xz')]
    # ten DRAM ICs (etched black packages)
    for x in np.linspace(-1.5, 1.5, 10):
        ms.append(chip(.3, .62, .13, (float(x), .11, -.05), 'xz', 'chip'))
    # twin bare-aluminium heatspreaders wrapping both faces of the DIMM,
    # a finned top edge, and a frosted RGB light bar along the crown that glows
    # in a running rainbow (the reference memory's signature).
    ms += [rbox((3.45, .14, .46), (0, .2, -.38), 'silver', .03, 5, 'xz'),
           rbox((3.45, .12, .46), (0, .18, .38), 'silver', .03, 5, 'xz'),
           rbox((3.4, .2, .05), (0, .3, 0), 'black', .015, 4, 'xz'),
           fin_stack(3.3, .18, .1, 8, (0, .34, 0), 'heatsink', fill=.5),
           rbox((3.1, .04, .08), (0, .36, 0), 'rgb_rainbow', .01, 3, 'xz')]
    # gold edge contacts + key notch
    for x in np.linspace(-1.62, 1.62, 28):
        ms.append(rbox((.07, .04, .17), (float(x), -.05, .63), 'gold', .01, 3, 'xz'))
    ms.append(rbox((.16, .16, .18), (.25, .02, .58), 'black', .02, 3, 'xz'))
    return ms

def storage():
    ms = [rbox((3.55, .1, 1.25), (0, 0, 0), 'board', .04, 6, 'xz')]
    # NAND / controller / DRAM packages with exposed gold lead fingers on the edge
    for cx, cw in [(-1.12, .7), (.2, .7), (1.16, .5)]:
        ms.append(chip(cw, .62, .14, (cx, .1, 0), 'xz', 'chip'))
        for k in range(6):
            z = -.28 + k * .11
            ms.append(rbox((cw * .82, .02, .03), (cx, .06, z), 'gold', .006, 2, 'xz'))
    # large label sticker with a printed brand block + barcode strip
    ms += [rbox((2.6, .03, .9), (0, .17, 0), 'cream', .02, 4, 'xz'),
           rbox((1.0, .012, .3), (-.55, .185, -.15), 'black', .006, 3, 'xz'),
           rbox((.5, .012, .5), (1.0, .185, .1), 'black', .006, 3, 'xz')]
    # a few SMD passives (capacitors / resistors) near the controller
    for x, z in [(-.8, .45), (-.65, .45), (-.5, .45), (1.3, -.45), (1.45, -.45)]:
        ms.append(rbox((.1, .03, .05), (x, .08, z), 'cream', .006, 2, 'xz'))
    # M.2 gold edge connector (single notch) + mounting screw hole
    for x in np.linspace(-1.65, -1.28, 8):
        ms.append(rbox((.035, .04, .22), (float(x), -.02, .61), 'gold', .008, 3, 'xz'))
    for x in np.linspace(-1.15, -.65, 9):
        ms.append(rbox((.035, .04, .22), (float(x), -.02, .61), 'gold', .008, 3, 'xz'))
    ms += [cyl(.12, .06, (1.62, .06, 0), 'y', 'silver', 28),
           cyl(.055, .09, (1.62, .07, 0), 'y', 'black', 28)]
    ms += smd_field(-1.5, 1.5, 0.18, 0.5, 20, seed=201)
    ms += smd_field(-1.5, 0.6, -0.5, -0.15, 14, seed=202)
    return ms

def power():
    # Squared steel shell (barely-rounded corners, like stamped sheet metal).
    ms = [rbox((3.25, 2.7, 2.45), (0, 0, 0), 'graphite', .03, 6, 'xy')]
    # top fan recessed in a well + stamped wire grille
    ms.append(rbox((1.15, .02, 1.15), (0, 1.36, 0), 'deep', .02, 4, 'xy'))
    ms += fan(.9, .06, (0, 1.40, 0), 'y', 13, 'black', 'silver')
    ms += grille(1.9, 1.9, (0, 1.46, 0), pitch=.2, bar=.035, border=.12, depth=.05, material='darkmetal', plane='xy')
    # modular connector panel (recessed) with keyed 8/6-pin bodies and gold pins
    ms.append(rbox((1.7, 1.0, .04), (0, .2, 1.28), 'black', .015, 3, 'xy'))
    for r_ in [-.55, 0, .55]:
        for c in [-.55, .0, .55]:
            ms.append(rbox((.4, .22, .06), (c, .2 + r_ * .55, 1.32), 'black', .01, 3, 'xy'))
            for k in range(4):
                ms.append(cyl(.02, .07, (c - .13 + k * .085, .2 + r_ * .55, 1.36), 'z', 'gold', 10))
    # rear AC inlet + rocker switch
    ms += [rbox((.42, .42, .1), (-.7, -.5, 1.32), 'black', .015, 3, 'xy'),
           rbox((.28, .16, .06), (-.7, -.5, 1.38), 'darkmetal', .01, 3, 'xy'),
           cyl(.09, .06, (-.7, -.5, 1.39), 'z', 'metal', 18),
           rbox((.3, .2, .08), (.55, -.5, 1.34), 'black', .01, 3, 'xy'),
           rbox((.14, .08, .05), (.55, -.5, 1.4), 'cream', .005, 2, 'xy')]
    # internals (revealed by the cross-section tool): a small PCB, a switching
    # transformer with copper windings, main filter capacitors and toroid chokes.
    ms += [rbox((2.5, .06, 1.7), (0, -.5, -.15), 'board', .02, 4, 'xy')]
    ms += [rbox((.85, .78, .78), (-.72, -.1, -.15), 'deep', .02, 4, 'xy'),
           rbox((.85, .5, .78), (-.72, .05, -.15), 'copper', .02, 4, 'xy'),
           rbox((.6, .16, .78), (-.72, .3, -.15), 'copper', .02, 3, 'xy')]
    for _ in range(6):
        ms.append(rbox((.86, .05, .7), (-.72, -.02, -.15), 'metal', .008, 3, 'xy'))
    ms += cap_can(.27, .82, (.58, -.1, -.45), 'y', 'silver', 'graphite')
    ms += cap_can(.27, .82, (1.0, -.1, -.45), 'y', 'silver', 'graphite')
    for x in [-.1, .2, .5]:
        ms.append(cyl(.18, .12, (x, -.32, .35), 'y', 'copper', 24))
        ms.append(cyl(.16, .5, (x, -.4, .35), 'y', 'darkmetal', 24))
    # aluminium primary heatsink fins near the rectifier
    ms += fin_stack(.7, .5, .5, 9, (.9, .15, .5), 'heatsink', fill=.55)
    # spec label + corner screws
    ms += [rbox((1.6, 1.2, .03), (.2, .0, -1.23), 'cream', .02, 4, 'xy'),
           rbox((1.2, .12, .015), (.2, -.45, -1.24), 'deep', .005, 2, 'xy')]
    for sx_, sz_ in [(-1.45, -1.05), (1.45, -1.05), (-1.45, 1.05), (1.45, 1.05)]:
        ms += screw((sx_, 1.37, sz_), 'y', .06, 'silver', 'graphite')
    # rear ventilation slots (exhaust side)
    for i in range(7):
        ms.append(rbox((2.0, .06, .04), (0, 1.2 - i * .14, -1.24), 'darkmetal', .008, 3, 'xy'))
    return ms

def cooling():
    ms = []
    # copper base plate with mounting hardware (contacts the CPU IHS)
    ms += [rbox((1.5, .22, 1.35), (0, -1.25, 0), 'silver', .04, 5, 'xz')]
    for x, z in [(-.55, -.45), (.55, -.45), (-.55, .45), (.55, .45)]:
        ms += screw((x, -1.13, z), 'y', .045, 'silver', 'graphite')
    # U-shaped heatpipes: four vertical legs rising from the base plus a top run
    for x in [-.55, -.2, .2, .55]:
        ms += [tube(.07, 2.6, (x, 0, 0), 'y', 'copper'),
               tube(.07, 1.05, (x, 1.2, .35), 'z', 'copper'),
               tube(.07, 2.6, (x, 0, .7), 'y', 'copper')]
    ms.append(tube(.07, 1.5, (0, 1.2, .35), 'x', 'copper'))
    ms.append(tube(.07, 1.5, (0, 1.2, .7), 'x', 'copper'))
    # dense aluminium fin stack (the signature tower look)
    ms += fin_stack(2.5, 2.1, 1.3, 44, (0, .0, .2), 'heatsink', fill=.6)
    # front fan + wire mounting clips (tower coolers clip the fan, no grille)
    ms += fan(.82, .12, (0, .2, 1.05), 'z', 9, 'black', 'silver')
    # purple RGB ring around the fan — the reference cooler's coloured glow
    ring = trimesh.creation.torus(major_radius=.86, minor_radius=.05, major_sections=40, minor_sections=16)
    ring.apply_translation((0, .2, 1.06))
    ring.metadata['mat'] = 'rgb_purple'
    ms.append(ring)
    for x in [-1.15, 1.15]:
        ms.append(cyl(.03, 1.9, (x, .2, .55), 'y', 'silver', 10))
    for y in [-.7, .7, 1.1]:
        ms.append(rbox((2.35, .025, .05), (0, y, .55), 'silver', .006, 2, 'xy'))
    return ms

def network():
    ms = [rbox((3.55, .1, 2.0), (0, 0, 0), 'board', .04, 6, 'xz')]
    # metal bracket + RJ45 port with gold pin contacts + activity LEDs
    ms += [rbox((.14, .2, 2.2), (-1.72, .1, 0), 'silver', .02, 4, 'xz'),
           rbox((.5, .34, .55), (-1.55, .18, .55), 'black', .03, 4, 'xz'),
           rbox((.4, .26, .46), (-1.55, .2, .55), 'deep', .02, 3, 'xz')]
    for k in range(8):
        ms.append(rbox((.02, .05, .3), (-1.55, .2, .44 - k * .05), 'gold', .005, 2, 'xz'))
    ms += [rbox((.05, .04, .08), (-1.55, .36, .72), 'rgb', .005, 2, 'xz'),
           rbox((.05, .04, .08), (-1.55, .36, .82), 'rgb', .005, 2, 'xz')]
    # controller + PHY ICs (etched packages) with a finned heatsink
    ms += [chip(1.0, 1.0, .26, (-.2, .18, 0), 'xz', 'chip'),
           fin_stack(.72, .14, .72, 7, (-.2, .36, 0), 'heatsink', fill=.55)]
    for x, z in [(.7, .5), (1.15, .5), (.7, -.35), (1.15, -.35)]:
        ms.append(chip(.34, .34, .15, (x, .13, z), 'xz', 'chip'))
    # crystal oscillator + decoupling caps
    ms += [rbox((.45, .18, .22), (.55, .15, -.85), 'silver', .02, 4, 'xz')]
    for x in [.85, 1.1, 1.35]:
        ms += cap_can(.07, .18, (x, .14, -.85), 'y', 'silver', 'graphite')
    # PCIe gold fingers
    for x in np.linspace(-.7, 1.55, 22):
        ms.append(rbox((.055, .045, .18), (float(x), -.05, 1.0), 'gold', .01, 3, 'xz'))
    ms += smd_field(-1.15, -0.45, -0.75, 0.25, 18, seed=301)
    ms += smd_field(0.5, 1.4, 0.05, 0.55, 14, seed=302)
    return ms

def case():
    ms = []
    # --- white steel shell: flat stamped panels (a real tower, not a wireframe)
    # left side (solid white), right side (tempered glass), top/bottom/front/back
    ms += [rbox((.08, 3.25, 2.2), (-1.5, .1, 0), 'white', .02, 4, 'xy'),
           rbox((.04, 2.95, 2.3), (1.56, .1, 0), 'glass', .02, 5, 'xy'),
           rbox((3.0, .08, 2.2), (0, -1.62, 0), 'white', .02, 4, 'xz'),
           rbox((3.0, .08, 2.2), (0, 1.62, 0), 'white', .02, 4, 'xz'),
           rbox((3.0, 3.25, .08), (0, .1, -1.12), 'white', .02, 4, 'xy')]
    # cobalt-blue accent strip running up the front edge (the reference's blue)
    ms += [rbox((.06, 3.2, .18), (0, .1, 1.14), 'blue', .015, 3, 'xy')]
    # front mesh bezel + three intake fans behind it (RGB)
    ms += grille(2.7, 2.8, (-.18, .1, 1.16), pitch=.26, bar=.05, border=.12, depth=.06, material='darkmetal', plane='xy')
    for y in [-.75, .05, .85]:
        ms += fan(.38, .08, (1.55, y, .6), 'x', 9, 'black', 'rgb')
    # top dust-filter grille
    ms += grille(2.9, 2.3, (-.18, 1.64, 0), pitch=.3, bar=.05, border=.1, depth=.05, material='darkmetal', plane='xz')
    # front I/O: red power button + two USB ports
    ms += [cyl(.14, .1, (-.18, 1.5, 1.05), 'z', 'red', 20),
           rbox((.18, .1, .12), (-.7, 1.5, 1.05), 'black', .02, 3, 'xy'),
           rbox((.18, .1, .12), (-.45, 1.5, 1.05), 'black', .02, 3, 'xy')]
    # internal: motherboard plane + CPU cooler + RAM + GPU + PSU + storage
    ms += [rbox((2.45, 2.65, .08), (-.18, .1, -.72), 'board', .03, 5, 'xy'),
           rbox((.72, .72, .35), (-.45, .55, -.46), 'silver', .04, 5, 'xz'),
           cyl(.3, .14, (-.45, .55, -.22), 'z', 'black', 36)]
    for x in [.05, .22]:
        ms.append(rbox((.09, 1.05, .14), (x, .3, -.52), 'rgb', .015, 3, 'xy'))
    ms += [rbox((2.5, .42, .65), (.1, -.45, .0), 'graphite', .04, 5, 'xz'),
           cyl(.27, .08, (-.55, -.67, .34), 'y', 'black', 32),
           cyl(.27, .08, (.35, -.67, .34), 'y', 'black', 32),
           rbox((1.25, .68, 1.6), (.65, -1.15, -.15), 'graphite', .04, 5, 'xy'),
           rbox((.9, .18, .65), (-.9, -1.25, .2), 'metal', .03, 4, 'xz')]
    # rubber feet
    for sx_, sz_ in [(-1.4, -1.0), (1.4, -1.0), (-1.4, 1.0), (1.4, 1.0)]:
        ms.append(cyl(.12, .14, (sx_, -1.66, sz_), 'y', 'darkmetal', 18))
    return ms

builders = {
    'motherboard': motherboard, 'cpu': cpu, 'gpu': gpu, 'memory': memory,
    'storage': storage, 'power': power, 'cooling': cooling, 'network': network, 'case': case,
}
FLAT = {'motherboard', 'cpu', 'gpu', 'memory', 'storage', 'network'}

GEN_2D = '--with-2d' in sys.argv
GEN_3D = '--2d-only' not in sys.argv
ONLY = next((a.split('=', 1)[1] for a in sys.argv if a.startswith('--only=')), None)

if GEN_3D:
    for name, fn in builders.items():
        if ONLY and name != ONLY:
            continue
        print('generating', name)
        meshes = fn()
        if name in FLAT:
            rot = trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])
            for m in meshes:
                if isinstance(m, list):
                    for sub in m:
                        sub.apply_transform(rot)
                else:
                    m.apply_transform(rot)
        scene_export(name, meshes)
        normalize_model(name)
    print('generated 3D models')

if GEN_2D:
    # --- 2D learning assets -------------------------------------------------
    # Schematic learning cards: dark engineering canvas, cyan centre glow and a
    # per-specimen vector diagram. Deliberately schematic rather than photo-real
    # so they read as anatomy-style diagrams matching the per-specimen accent.
    def rounded(draw, xy, r, fill, outline=None, width=1):
        draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)

    def base_canvas(w=760, h=560):
        im = Image.new('RGB', (w, h), '#071014')
        d = ImageDraw.Draw(im)
        for x in range(0, w, 40):
            d.line((x, 0, x, h), fill='#0d2026', width=1)
        for y in range(0, h, 40):
            d.line((0, y, w, y), fill='#0d2026', width=1)
        glow = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        for r, a in [(250, 12), (190, 16), (130, 20)]:
            gd.ellipse((w // 2 - r, h // 2 - r, w // 2 + r, h // 2 + r), fill=(70, 215, 230, a))
        glow = glow.filter(ImageFilter.GaussianBlur(35))
        return Image.alpha_composite(im.convert('RGBA'), glow).convert('RGB')

    def draw_component_icon(d, name, cx, cy, s=1.0):
        line = '#6be0ea'; fill = '#17323a'; metal = '#9db0b9'; dark = '#0d171c'; amber = '#e9b44c'
        if name == 'motherboard':
            rounded(d, (cx - 150 * s, cy - 115 * s, cx + 150 * s, cy + 115 * s), 12 * s, fill, outline=line, width=max(1, int(3 * s)))
            rounded(d, (cx - 70 * s, cy - 60 * s, cx + 20 * s, cy + 30 * s), 8 * s, metal, outline='#d9e5e8', width=max(1, int(2 * s)))
            for x in [60, 80, 100]:
                rounded(d, (cx + x * s, cy - 75 * s, cx + (x + 8) * s, cy + 60 * s), 3 * s, dark, outline=line)
            for z in [45, 70]:
                rounded(d, (cx - 85 * s, cy + z * s, cx + 70 * s, cy + (z + 8) * s), 3 * s, dark, outline=amber)
        elif name == 'cpu':
            rounded(d, (cx - 125 * s, cy - 125 * s, cx + 125 * s, cy + 125 * s), 18 * s, '#1a3a41', outline=amber, width=max(1, int(3 * s)))
            rounded(d, (cx - 90 * s, cy - 90 * s, cx + 90 * s, cy + 90 * s), 15 * s, metal, outline='#dae6e8', width=max(1, int(3 * s)))
            for dx, dy, co in [(-45, -45, line), (45, -45, '#709cff'), (-45, 45, '#a989e6'), (45, 45, '#45c6ad')]:
                rounded(d, (cx + (dx - 32) * s, cy + (dy - 32) * s, cx + (dx + 32) * s, cy + (dy + 32) * s), 8 * s, co)
        elif name == 'gpu':
            rounded(d, (cx - 170 * s, cy - 80 * s, cx + 170 * s, cy + 80 * s), 18 * s, '#252f36', outline=line, width=max(1, int(3 * s)))
            for x in [-105, 0, 105]:
                d.ellipse((cx + (x - 48) * s, cy - 48 * s, cx + (x + 48) * s, cy + 48 * s), fill=dark, outline=metal, width=max(1, int(3 * s)))
                d.ellipse((cx + (x - 13) * s, cy - 13 * s, cx + (x + 13) * s, cy + 13 * s), fill=line)
        elif name == 'memory':
            rounded(d, (cx - 175 * s, cy - 62 * s, cx + 175 * s, cy + 62 * s), 10 * s, fill, outline=line, width=max(1, int(3 * s)))
            for x in np.linspace(-145, 145, 8):
                rounded(d, (cx + (x - 16) * s, cy - 25 * s, cx + (x + 16) * s, cy + 25 * s), 4 * s, dark)
            for x in np.linspace(-160, 160, 18):
                d.rectangle((cx + (x - 3) * s, cy + 62 * s, cx + (x + 3) * s, cy + 78 * s), fill=amber)
        elif name == 'storage':
            rounded(d, (cx - 175 * s, cy - 62 * s, cx + 175 * s, cy + 62 * s), 10 * s, fill, outline=line, width=max(1, int(3 * s)))
            rounded(d, (cx - 135 * s, cy - 42 * s, cx - 65 * s, cy + 42 * s), 8 * s, metal)
            for x in [-25, 45, 115]:
                rounded(d, (cx + (x - 28) * s, cy - 35 * s, cx + (x + 28) * s, cy + 35 * s), 6 * s, dark)
            d.ellipse((cx + 145 * s, cy - 12 * s, cx + 169 * s, cy + 12 * s), fill='#071014', outline=metal, width=max(1, int(3 * s)))
        elif name == 'power':
            rounded(d, (cx - 145 * s, cy - 110 * s, cx + 145 * s, cy + 110 * s), 16 * s, '#252f36', outline=metal, width=max(1, int(3 * s)))
            d.ellipse((cx - 70 * s, cy - 70 * s, cx + 70 * s, cy + 70 * s), fill=dark, outline=line, width=max(1, int(3 * s)))
            d.ellipse((cx - 17 * s, cy - 17 * s, cx + 17 * s, cy + 17 * s), fill=metal)
        elif name == 'cooling':
            for y in range(-80, 90, 10):
                d.rectangle((cx - 90 * s, cy + (y - 2) * s, cx + 90 * s, cy + (y + 2) * s), fill=metal)
            for x in [-45, -15, 15, 45]:
                d.line((cx + x * s, cy + 95 * s, cx + x * s, cy - 90 * s), fill=amber, width=max(2, int(5 * s)))
            d.ellipse((cx - 70 * s, cy - 60 * s, cx + 70 * s, cy + 80 * s), fill=dark, outline=line, width=max(1, int(3 * s)))
            d.ellipse((cx - 14 * s, cy + 0 * s, cx + 14 * s, cy + 28 * s), fill=metal)
        elif name == 'network':
            rounded(d, (cx - 165 * s, cy - 90 * s, cx + 145 * s, cy + 90 * s), 12 * s, fill, outline=line, width=max(1, int(3 * s)))
            rounded(d, (cx - 55 * s, cy - 48 * s, cx + 35 * s, cy + 42 * s), 8 * s, metal)
            rounded(d, (cx - 155 * s, cy - 35 * s, cx - 105 * s, cy + 35 * s), 4 * s, '#64737c', outline='#d2dde0')
            for x in [65, 105]:
                rounded(d, (cx + (x - 18) * s, cy - 20 * s, cx + (x + 18) * s, cy + 18 * s), 4 * s, dark)
        elif name == 'case':
            rounded(d, (cx - 115 * s, cy - 150 * s, cx + 115 * s, cy + 150 * s), 18 * s, '#142127', outline=metal, width=max(1, int(4 * s)))
            rounded(d, (cx - 90 * s, cy - 120 * s, cx + 90 * s, cy + 115 * s), 8 * s, '#0d1a20', outline=line, width=max(1, int(2 * s)))
            d.rectangle((cx - 68 * s, cy - 80 * s, cx + 42 * s, cy + 20 * s), outline='#2bb7a9', width=max(1, int(3 * s)))
            d.rectangle((cx - 55 * s, cy + 35 * s, cx + 60 * s, cy + 65 * s), fill='#26343c')
            for yy in [-80, 0, 80]:
                d.ellipse((cx + 65 * s, cy + (yy - 22) * s, cx + 109 * s, cy + (yy + 22) * s), outline=line, width=max(1, int(3 * s)))

    LABELS = {
        'motherboard': ('Motherboard', 'System interconnect'), 'cpu': ('CPU', 'Compute engine'),
        'gpu': ('GPU', 'Parallel processor'),
        'memory': ('Memory', 'Working data'), 'storage': ('NVMe SSD', 'Persistent data'),
        'power': ('Power Supply', 'Power conversion'),
        'cooling': ('Cooling', 'Thermal control'), 'network': ('Network Adapter', 'Data link'),
        'case': ('System Chassis', 'Integrated computer')}

    def save_asset(name, kind):
        if kind == 'thumb':
            im = base_canvas(320, 320); d = ImageDraw.Draw(im); draw_component_icon(d, name, 160, 158, .75)
        else:
            im = base_canvas(); d = ImageDraw.Draw(im)
            title, sub = LABELS[name]
            d.text((40, 32), title, font=getfont(34, True), fill='#eaf4f5')
            d.text((42, 75), sub.upper(), font=getfont(13, True), fill='#55d8e8')
            if kind == 'organ':
                draw_component_icon(d, name, 380, 305, 1.15)
                d.text((40, 510), 'INTERACTIVE HARDWARE SPECIMEN', font=getfont(13, True), fill='#6b8089')
            elif kind == 'microscopic':
                draw_component_icon(d, name, 220, 315, .8)
                for i, (tx, ty) in enumerate([(470, 185), (560, 275), (470, 365), (590, 440)]):
                    rounded(d, (tx - 55, ty - 38, tx + 55, ty + 38), 10, '#122a2e', outline='#55d8e8', width=2)
                    d.text((tx - 38, ty - 7), f'L{i+1}', font=getfont(18, True), fill='#eaf4f5')
                    d.line((330, 300, tx - 55, ty), fill='#356d75', width=2)
                d.text((445, 500), 'BOARD / SILICON LEVEL', font=getfont(13, True), fill='#6b8089')
            elif kind == 'compare':
                draw_component_icon(d, name, 205, 300, .72)
                draw_component_icon(d, 'case' if name != 'case' else 'motherboard', 555, 300, .6)
                d.line((380, 145, 380, 470), fill='#2c464e', width=2)
                d.text((338, 276), 'VS', font=getfont(28, True), fill='#efb54a')
                d.text((73, 482), LABELS[name][0], font=getfont(16, True), fill='#eaf4f5')
                other = 'System Chassis' if name != 'case' else 'Motherboard'
                d.text((470, 482), other, font=getfont(16, True), fill='#eaf4f5')
            elif kind == 'location':
                draw_component_icon(d, 'case', 380, 300, 1.0)
                p = {'motherboard': (325, 285), 'cpu': (345, 260), 'gpu': (355, 345), 'memory': (390, 275),
                     'storage': (330, 390), 'power': (430, 390), 'cooling': (345, 245), 'network': (350, 360),
                     'case': (380, 300)}[name]
                for r, a in [(38, '#55d8e8'), (25, '#071014'), (10, '#efb54a')]:
                    d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), outline=a, width=4)
                d.text((40, 510), 'POSITION IN THE COMPUTER SYSTEM', font=getfont(13, True), fill='#6b8089')
        out = ART_DIR / name
        out.mkdir(exist_ok=True)
        im.save(out / f'{kind}.webp', 'WEBP', quality=90, method=6)

    for n in builders:
        for k in ['thumb', 'organ', 'microscopic', 'compare', 'location']:
            save_asset(n, k)
    print('generated 2D learning assets')
