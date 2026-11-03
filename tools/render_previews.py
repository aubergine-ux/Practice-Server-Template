#!/usr/bin/env python3
"""
Renders top-down previews of the generated maps into docs/previews/.

    python3 tools/render_previews.py      (needs Pillow)

It replays the fill/setblock commands from generate_maps.py into a voxel grid,
so the pictures always match what actually gets built.
"""
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_maps as gm  # noqa: E402

OUT = gm.ROOT / "docs/previews"
SCALE = 8

COLORS = {
    "smooth_stone": (158, 158, 158), "stone": (125, 125, 125), "andesite": (136, 136, 137),
    "polished_andesite": (132, 134, 133), "polished_diorite": (192, 193, 194), "tuff": (108, 109, 102),
    "cobbled_deepslate": (77, 77, 80), "deepslate": (80, 80, 82), "sea_lantern": (172, 199, 190),
    "polished_blackstone_bricks": (48, 42, 49), "polished_blackstone_brick_wall": (48, 42, 49),
    "polished_blackstone_brick_stairs": (48, 42, 49), "polished_blackstone_brick_slab": (48, 42, 49),
    "chiseled_polished_blackstone": (53, 48, 56), "polished_blackstone": (53, 48, 56), "blackstone": (42, 36, 41),
    "gilded_blackstone": (56, 43, 38), "lantern": (227, 160, 74), "grass_block": (127, 178, 56),
    "short_grass": (110, 160, 50), "fern": (90, 140, 50), "moss_block": (89, 109, 45),
    "cherry_log": (54, 33, 44), "cherry_leaves": (229, 172, 194), "oak_log": (109, 85, 50),
    "oak_leaves": (60, 120, 40), "birch_log": (216, 215, 210), "birch_leaves": (110, 150, 70),
    "flowering_azalea_leaves": (110, 130, 70), "azalea_leaves": (90, 120, 50),
    "poppy": (190, 30, 30), "dandelion": (240, 220, 40), "cornflower": (70, 100, 220),
    "azure_bluet": (220, 220, 230), "oxeye_daisy": (230, 230, 210),
    "smooth_sandstone": (223, 214, 170), "sandstone": (216, 203, 155), "cut_sandstone": (218, 206, 160),
    "chiseled_sandstone": (216, 202, 155), "sand": (219, 207, 163), "sandstone_slab": (216, 203, 155),
    "cut_red_sandstone": (186, 99, 29), "orange_terracotta": (161, 83, 37), "red_terracotta": (143, 61, 46),
    "dirt": (134, 96, 67), "coarse_dirt": (119, 85, 59), "podzol": (91, 63, 24), "rooted_dirt": (144, 103, 76),
    "mossy_stone_bricks": (115, 121, 105), "stone_bricks": (122, 121, 122), "cracked_stone_bricks": (118, 117, 118),
    "chiseled_stone_bricks": (119, 118, 119), "mossy_cobblestone": (110, 118, 94), "cobblestone": (127, 127, 127),
    "mossy_stone_brick_wall": (115, 121, 105), "gravel": (131, 127, 126),
    "nether_bricks": (44, 21, 26), "red_nether_bricks": (69, 7, 9), "netherrack": (97, 38, 38),
    "crimson_nylium": (130, 31, 31), "polished_basalt": (99, 98, 100), "basalt": (80, 81, 86),
    "shroomlight": (240, 146, 70), "crying_obsidian": (32, 10, 60), "glass": (175, 213, 219), "lava": (207, 92, 15),
    "snow_block": (249, 254, 254), "packed_ice": (141, 180, 250), "blue_ice": (116, 167, 253),
    "white_concrete_powder": (225, 227, 227), "white_concrete": (207, 213, 214), "red_concrete": (142, 32, 32),
    "light_gray_concrete": (125, 125, 115), "smooth_quartz": (235, 229, 222), "quartz_bricks": (234, 229, 221),
    "water": (63, 118, 228),
}
TRANSPARENT = {"air", "barrier"}
CMD = re.compile(r"^(fill|setblock) (-?\d+) (-?\d+) (-?\d+)(?: (-?\d+) (-?\d+) (-?\d+))? (\S+)")


def voxels(build):
    grid = {}
    for cmd in build.cmds:
        m = CMD.match(cmd)
        if not m:
            continue
        kind, *nums, block = m.groups()
        block = block.split("[")[0]
        if kind == "setblock":
            x1, y1, z1 = map(int, nums[:3])
            x2, y2, z2 = x1, y1, z1
        else:
            x1, y1, z1, x2, y2, z2 = map(int, nums)
        for x in range(x1, x2 + 1):
            for z in range(z1, z2 + 1):
                for y in range(y1, y2 + 1):
                    if block in TRANSPARENT:
                        grid.pop((x, y, z), None)
                    else:
                        grid[(x, y, z)] = block
    return grid


def render(build, name):
    grid = voxels(build)
    top = {}
    for (x, y, z), block in grid.items():
        if (x, z) not in top or y > top[(x, z)][0]:
            top[(x, z)] = (y, block)
    xs = [x for x, _ in top]
    zs = [z for _, z in top]
    x0, z0 = min(xs) - 2, min(zs) - 2
    w, h = max(xs) - x0 + 3, max(zs) - z0 + 3
    ys = [y for y, _ in top.values()]
    ylo, yhi = min(ys), max(ys)

    img = Image.new("RGB", (w * SCALE, h * SCALE), (22, 24, 29))
    draw = ImageDraw.Draw(img)
    for (x, z), (y, block) in top.items():
        r, g, b = COLORS.get(block, (200, 0, 200))
        light = 0.75 + 0.35 * ((y - ylo) / max(1, yhi - ylo))
        north = top.get((x, z - 1), (y, None))[0]
        if north > y:
            light *= 0.82
        elif north < y:
            light *= 1.08
        c = tuple(max(0, min(255, int(v * light))) for v in (r, g, b))
        px, pz = (x - x0) * SCALE, (z - z0) * SCALE
        draw.rectangle([px, pz, px + SCALE - 1, pz + SCALE - 1], fill=c)
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / f"{name}.png", optimize=True)
    missing = {b for _, b in top.values() if b not in COLORS}
    print(f"{name:10s} {img.size[0]}x{img.size[1]}" + (f"  no colour for: {', '.join(sorted(missing))}" if missing else ""))


def main():
    render(gm.lobby(), "lobby")
    for i, fn in enumerate(gm.ARENA_BUILDERS):
        b, _ = fn(i * gm.ARENA_SPACING)
        render(b, b.name)


if __name__ == "__main__":
    main()
