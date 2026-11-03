#!/usr/bin/env python3
"""
Writes the first-boot datapack that builds the lobby and arenas.

    python3 tools/generate_maps.py

Output goes to defaults/world/datapacks/practice/. Everything is plain
fill/setblock commands, so it's easy to tweak a map here and regenerate.
The lobby is built in the main world, arenas in ZonePractice's "arenas" world.
"""
import math
import random
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT / "defaults/world/datapacks/practice"
FUNC = PACK / "data/practice/function"

OVERWORLD = "minecraft:overworld"
ARENAS = "minecraft:arenas"
MAX_FILL = 32768

# arena floor height and spacing in the arenas world
FLOOR_Y = 100
ARENA_SPACING = 200


class Build:
    def __init__(self, name, dim, seed=1):
        self.name = name
        self.dim = dim
        self.cmds = []
        self.rng = random.Random(seed)
        self.min_x = self.min_z = 10**9
        self.max_x = self.max_z = -10**9

    def _track(self, x1, z1, x2, z2):
        self.min_x = min(self.min_x, x1, x2)
        self.max_x = max(self.max_x, x1, x2)
        self.min_z = min(self.min_z, z1, z2)
        self.max_z = max(self.max_z, z1, z2)

    def fill(self, x1, y1, z1, x2, y2, z2, block, mode=""):
        x1, x2 = sorted((x1, x2))
        y1, y2 = sorted((y1, y2))
        z1, z2 = sorted((z1, z2))
        self._track(x1, z1, x2, z2)
        layer = (x2 - x1 + 1) * (z2 - z1 + 1)
        step = max(1, MAX_FILL // layer)
        y = y1
        while y <= y2:
            top = min(y2, y + step - 1)
            self.cmds.append(f"fill {x1} {y} {z1} {x2} {top} {z2} {block}{' ' + mode if mode else ''}")
            y = top + 1

    def set(self, x, y, z, block):
        self._track(x, z, x, z)
        self.cmds.append(f"setblock {x} {y} {z} {block}")

    def raw(self, cmd):
        self.cmds.append(cmd)

    def disc(self, cx, y, cz, r, block, r_inner=None):
        """Filled circle (or ring if r_inner is given), one fill per row."""
        ri = math.floor(r)
        for dz in range(-ri, ri + 1):
            half = math.floor(math.sqrt(max(0, r * r - dz * dz)))
            if r_inner is None or abs(dz) > r_inner:
                self.fill(cx - half, y, cz + dz, cx + half, y, cz + dz, block)
            else:
                inner = math.floor(math.sqrt(max(0, r_inner * r_inner - dz * dz)))
                if half > inner:
                    self.fill(cx - half, y, cz + dz, cx - inner - 1, y, cz + dz, block)
                    self.fill(cx + inner + 1, y, cz + dz, cx + half, y, cz + dz, block)

    def ring_points(self, cx, cz, r):
        """Block positions on a 1-wide circle outline."""
        pts = set()
        for dz in range(-math.ceil(r), math.ceil(r) + 1):
            for dx in range(-math.ceil(r), math.ceil(r) + 1):
                d = math.sqrt(dx * dx + dz * dz)
                if r - 1 < d <= r:
                    pts.add((cx + dx, cz + dz))
        return sorted(pts)

    def scatter(self, x1, z1, x2, z2, y, blocks, chance, avoid=None):
        for x in range(x1, x2 + 1):
            for z in range(z1, z2 + 1):
                if avoid and avoid(x, z):
                    continue
                if self.rng.random() < chance:
                    self.set(x, y, z, self.rng.choice(blocks))


# ---------------------------------------------------------------- helpers

def tree(b, x, y, z, log, leaves, height=5):
    leaves = f"{leaves}[persistent=true]"
    b.fill(x - 2, y + height - 2, z - 2, x + 2, y + height - 1, z + 2, leaves)
    b.fill(x - 1, y + height, z - 1, x + 1, y + height, z + 1, leaves)
    b.set(x, y + height + 1, z, leaves)
    for cx, cz in ((x - 2, z - 2), (x + 2, z - 2), (x - 2, z + 2), (x + 2, z + 2)):
        if b.rng.random() < 0.6:
            b.set(cx, y + height - 1, cz, "air")
    b.fill(x, y, z, x, y + height - 1, z, log)


def arena_shell(b, cx, hx, hz, floor, base, wall, wall_h=7):
    """Floor, a couple of underside layers, walls, and an invisible barrier box."""
    y = FLOOR_Y
    b.fill(cx - hx, y, -hz, cx + hx, y, hz, floor)
    b.fill(cx - hx, y - 1, -hz, cx + hx, y - 1, hz, base)
    b.fill(cx - hx + 2, y - 2, -hz + 2, cx + hx - 2, y - 2, hz - 2, base)
    b.fill(cx - hx + 5, y - 3, -hz + 5, cx + hx - 5, y - 3, hz - 5, base)
    for z in (-hz, hz):
        b.fill(cx - hx, y + 1, z, cx + hx, y + wall_h, z, wall)
    for x in (cx - hx, cx + hx):
        b.fill(x, y + 1, -hz, x, y + wall_h, hz, wall)
    top = y + 30
    for z in (-hz, hz):
        b.fill(cx - hx, y + wall_h + 1, z, cx + hx, top, z, "barrier")
    for x in (cx - hx, cx + hx):
        b.fill(x, y + wall_h + 1, -hz, x, top, hz, "barrier")
    b.fill(cx - hx, top, -hz, cx + hx, top, hz, "barrier")


def spawn_pads(b, cx, off, block):
    for x in (cx - off, cx + off):
        b.fill(x - 1, FLOOR_Y, -1, x + 1, FLOOR_Y, 1, block)


def near_spawn_lane(cx, off):
    """True for positions on the straight line between spawns, kept clear of cover."""
    return lambda x, z: abs(z) <= 2 and abs(x - cx) <= off + 2


# ---------------------------------------------------------------- lobby

def lobby():
    b = Build("lobby", OVERWORLD, seed=7)
    R = 26
    y = 63

    # island underside
    layers = [(25, "stone"), (23, "stone"), (21, "andesite"), (18, "tuff"),
              (15, "cobbled_deepslate"), (11, "tuff"), (7, "deepslate"), (3, "cobbled_deepslate")]
    for i, (r, block) in enumerate(layers):
        b.disc(0, y - 1 - i, 0, r, block)

    # floor
    b.disc(0, y, 0, R, "smooth_stone")
    b.disc(0, y, 0, R, "polished_blackstone_bricks", r_inner=R - 1)
    b.disc(0, y, 0, 11.5, "polished_andesite", r_inner=10.5)
    b.disc(0, y, 0, 3.5, "polished_diorite")
    b.set(0, y, 0, "sea_lantern")
    for dx, dz in ((3, 0), (-3, 0), (0, 3), (0, -3)):
        b.set(dx, y, dz, "sea_lantern")

    # edge wall + barrier dome so nobody falls or pearls out
    for x, z in b.ring_points(0, 0, R):
        b.set(x, y + 1, z, "polished_blackstone_brick_wall")
        b.fill(x, y + 2, z, x, y + 22, z, "barrier")
    b.disc(0, y + 22, 0, R, "barrier")

    # npc stage on the north side, players spawn facing it
    b.fill(-11, y + 1, -21, 11, y + 1, -16, "polished_blackstone_bricks")
    b.fill(-11, y + 1, -15, 11, y + 1, -15, "polished_blackstone_brick_stairs[facing=north]")
    b.fill(-12, y + 1, -22, 12, y + 6, -22, "polished_blackstone_bricks")
    for x in (-12, -6, 0, 6, 12):
        b.fill(x, y + 1, -22, x, y + 7, -22, "chiseled_polished_blackstone")
        b.set(x, y + 8, -22, "polished_blackstone_brick_wall")
        b.set(x, y + 9, -22, "lantern")
    b.fill(-11, y + 6, -22, 11, y + 6, -22, "polished_blackstone_brick_slab[type=top]")
    for x in (-9, -3, 3, 9):
        b.set(x, y + 4, -22, "sea_lantern")
    # pedestals the npcs stand on
    for x in (-8, -4, 0, 4, 8):
        b.set(x, y + 1, -19, "chiseled_polished_blackstone")

    # leaderboard pedestals east and west
    for x in (-17, 17):
        b.fill(x - 1, y + 1, -1, x + 1, y + 1, 1, "polished_blackstone_bricks")
        b.set(x, y + 2, 0, "chiseled_polished_blackstone")
        b.set(x, y + 3, 0, "sea_lantern")

    # gardens
    for sx in (-1, 1):
        x = sx * 13
        b.fill(x - 3, y, 11, x + 3, y, 17, "grass_block")
        b.fill(x - 3, y + 1, 11, x + 3, y + 1, 11, "polished_blackstone_brick_wall")
        b.fill(x - 3, y + 1, 17, x + 3, y + 1, 17, "polished_blackstone_brick_wall")
        b.fill(x - 3, y + 1, 11, x - 3, y + 1, 17, "polished_blackstone_brick_wall")
        b.fill(x + 3, y + 1, 11, x + 3, y + 1, 17, "polished_blackstone_brick_wall")
        b.scatter(x - 2, 12, x + 2, 16, y + 1, ["short_grass", "short_grass", "poppy", "cornflower", "azure_bluet", "oxeye_daisy"], 0.45,
                  avoid=lambda px, pz, tx=x: abs(px - tx) <= 0 and pz == 14)
        tree(b, x, y + 1, 14, "cherry_log", "cherry_leaves", height=5)
    for sx in (-1, 1):
        x = sx * 19
        b.fill(x - 1, y, -9, x + 1, y, -7, "moss_block")
        b.fill(x - 1, y + 1, -9, x + 1, y + 2, -7, "flowering_azalea_leaves[persistent=true]")
        b.set(x, y + 3, -8, "azalea_leaves[persistent=true]")

    # lamp posts around the inner ring
    for ang in range(0, 360, 45):
        if 45 < ang < 135:  # skip the stage side
            continue
        x = round(math.cos(math.radians(ang)) * 9)
        z = round(math.sin(math.radians(ang)) * 9)
        b.fill(x, y + 1, z, x, y + 2, z, "polished_blackstone_brick_wall")
        b.set(x, y + 3, z, "lantern")
    return b


# ---------------------------------------------------------------- arenas

def colosseum(cx):
    b = Build("colosseum", ARENAS, seed=11)
    hx, hz, off = 35, 20, 28
    arena_shell(b, cx, hx, hz, "smooth_sandstone", "sandstone", "cut_sandstone")
    b.scatter(cx - hx + 1, -hz + 1, cx + hx - 1, hz - 1, FLOOR_Y, ["sand", "cut_sandstone", "sandstone"], 0.12)
    # wall pillars
    for x in range(cx - hx, cx + hx + 1, 7):
        for z in (-hz, hz):
            b.fill(x, FLOOR_Y + 1, z, x, FLOOR_Y + 8, z, "chiseled_sandstone")
    # stands outside the long walls
    for i in range(5):
        for sz in (-1, 1):
            z = sz * (hz + 1 + i)
            b.fill(cx - hx, FLOOR_Y - 1, z, cx + hx, FLOOR_Y + 2 + i * 2, z,
                   "smooth_sandstone" if i % 2 == 0 else "cut_red_sandstone")
    # centre emblem
    b.fill(cx - 3, FLOOR_Y, -3, cx + 3, FLOOR_Y, 3, "orange_terracotta")
    b.fill(cx - 2, FLOOR_Y, -2, cx + 2, FLOOR_Y, 2, "red_terracotta")
    b.set(cx, FLOOR_Y, 0, "chiseled_sandstone")
    # broken columns for cover
    for dx, dz, h in ((-14, -9, 4), (14, 9, 4), (-14, 9, 2), (14, -9, 2), (0, -12, 3), (0, 12, 3)):
        b.fill(cx + dx, FLOOR_Y + 1, dz, cx + dx, FLOOR_Y + h, dz, "cut_sandstone")
        b.set(cx + dx, FLOOR_Y + h + 1, dz, "sandstone_slab")
    spawn_pads(b, cx, off, "chiseled_sandstone")
    return b, dict(hx=hx, hz=hz, off=off, extra_z=hz + 5)


def grove(cx):
    b = Build("grove", ARENAS, seed=12)
    hx, hz, off = 35, 20, 28
    arena_shell(b, cx, hx, hz, "grass_block", "dirt", "mossy_stone_bricks")
    for z in (-hz, hz):
        b.scatter(cx - hx, z, cx + hx, z, FLOOR_Y + 1, ["stone_bricks", "cracked_stone_bricks", "mossy_cobblestone"], 0.25)
        b.scatter(cx - hx, z, cx + hx, z, FLOOR_Y + 4, ["stone_bricks", "cracked_stone_bricks", "mossy_cobblestone"], 0.25)
    b.scatter(cx - hx + 1, -hz + 1, cx + hx - 1, hz - 1, FLOOR_Y, ["coarse_dirt", "podzol", "moss_block", "rooted_dirt"], 0.12)
    lane = near_spawn_lane(cx, off)
    b.scatter(cx - hx + 1, -hz + 1, cx + hx - 1, hz - 1, FLOOR_Y + 1,
              ["short_grass", "short_grass", "fern", "dandelion", "poppy"], 0.07, avoid=lane)
    for dx, dz, kind in ((-16, -10, "oak"), (-6, 11, "birch"), (5, -12, "oak"), (16, 9, "birch"),
                         (-22, 12, "birch"), (22, -11, "oak"), (0, 0, "oak")):
        tree(b, cx + dx, FLOOR_Y + 1, dz, f"{kind}_log", f"{kind}_leaves", height=5 + (abs(dx) % 2))
    for dx, dz in ((-10, 4), (10, -4), (-26, -6), (26, 6), (-3, -16), (3, 16)):
        b.fill(cx + dx, FLOOR_Y + 1, dz, cx + dx + 1, FLOOR_Y + 1, dz + 1, "oak_leaves[persistent=true]")
    spawn_pads(b, cx, off, "mossy_stone_bricks")
    return b, dict(hx=hx, hz=hz, off=off)


def inferno(cx):
    b = Build("inferno", ARENAS, seed=13)
    hx, hz, off = 35, 20, 28
    arena_shell(b, cx, hx, hz, "polished_blackstone", "blackstone", "nether_bricks")
    b.fill(cx - hx, FLOOR_Y - 2, -hz, cx + hx, FLOOR_Y - 2, hz, "blackstone")
    b.scatter(cx - hx + 1, -hz + 1, cx + hx - 1, hz - 1, FLOOR_Y, ["blackstone", "netherrack", "crimson_nylium", "gilded_blackstone"], 0.14)
    for z in (-hz, hz):
        b.fill(cx - hx, FLOOR_Y + 3, z, cx + hx, FLOOR_Y + 3, z, "red_nether_bricks")
    for x in range(cx - hx, cx + hx + 1, 7):
        for z in (-hz, hz):
            b.fill(x, FLOOR_Y + 1, z, x, FLOOR_Y + 8, z, "polished_basalt")
            b.set(x, FLOOR_Y + 9, z, "shroomlight")
    # lava under glass strips
    for dz in (-12, 12):
        b.fill(cx - 12, FLOOR_Y - 1, dz, cx + 12, FLOOR_Y - 1, dz, "lava")
        b.fill(cx - 12, FLOOR_Y, dz, cx + 12, FLOOR_Y, dz, "glass")
    # basalt columns
    for dx, dz, h in ((-15, -6, 3), (15, 6, 3), (-8, 8, 4), (8, -8, 4), (-22, 0, 2), (22, 0, 2)):
        if abs(dz) <= 2:
            dz = 5
        b.fill(cx + dx, FLOOR_Y + 1, dz, cx + dx + 1, FLOOR_Y + h, dz + 1, "basalt")
        b.set(cx + dx, FLOOR_Y + h + 1, dz, "crying_obsidian")
    spawn_pads(b, cx, off, "crying_obsidian")
    return b, dict(hx=hx, hz=hz, off=off)


def glacier(cx):
    b = Build("glacier", ARENAS, seed=14)
    hx, hz, off = 35, 20, 28
    arena_shell(b, cx, hx, hz, "snow_block", "packed_ice", "packed_ice")
    b.scatter(cx - hx + 1, -hz + 1, cx + hx - 1, hz - 1, FLOOR_Y, ["packed_ice", "white_concrete_powder"], 0.08)
    for x in range(cx - hx, cx + hx + 1, 7):
        for z in (-hz, hz):
            b.fill(x, FLOOR_Y + 1, z, x, FLOOR_Y + 8, z, "blue_ice")
            b.set(x, FLOOR_Y + 9, z, "sea_lantern")
    for z in (-hz, hz):
        b.fill(cx - hx, FLOOR_Y + 7, z, cx + hx, FLOOR_Y + 7, z, "snow_block")
    # ice spikes
    for dx, dz, h in ((-18, -9, 6), (18, 9, 6), (-6, 12, 4), (6, -12, 4), (-26, 10, 3), (26, -10, 3), (0, -6, 3), (0, 7, 3)):
        b.fill(cx + dx - 1, FLOOR_Y + 1, dz - 1, cx + dx + 1, FLOOR_Y + 2, dz + 1, "packed_ice")
        b.fill(cx + dx, FLOOR_Y + 1, dz, cx + dx, FLOOR_Y + h, dz, "packed_ice")
    spawn_pads(b, cx, off, "blue_ice")
    return b, dict(hx=hx, hz=hz, off=off)


def ruins(cx):
    b = Build("ruins", ARENAS, seed=15)
    hx, hz, off = 35, 20, 28
    arena_shell(b, cx, hx, hz, "stone_bricks", "stone", "stone_bricks")
    b.scatter(cx - hx + 1, -hz + 1, cx + hx - 1, hz - 1, FLOOR_Y,
              ["cracked_stone_bricks", "mossy_stone_bricks", "cobblestone", "andesite", "gravel"], 0.25)
    # crumbled wall tops
    for x in range(cx - hx, cx + hx + 1):
        for z in (-hz, hz):
            drop = b.rng.choice((0, 0, 0, 1, 2, 3))
            if drop:
                b.fill(x, FLOOR_Y + 8 - drop, z, x, FLOOR_Y + 7, z, "air")
    for z in range(-hz, hz + 1):
        for x in (cx - hx, cx + hx):
            drop = b.rng.choice((0, 0, 1, 2))
            if drop:
                b.fill(x, FLOOR_Y + 8 - drop, z, x, FLOOR_Y + 7, z, "air")
    for z in (-hz, hz):
        b.scatter(cx - hx, z, cx + hx, z, FLOOR_Y + 2, ["mossy_stone_bricks", "cracked_stone_bricks"], 0.3)
    # broken pillars and low walls
    for dx, dz, h in ((-20, -10, 5), (-20, 10, 2), (20, -10, 2), (20, 10, 5), (-8, -14, 3), (8, 14, 3), (0, 9, 1), (0, -9, 1)):
        b.fill(cx + dx, FLOOR_Y + 1, dz, cx + dx, FLOOR_Y + h, dz, "chiseled_stone_bricks" if h > 3 else "mossy_stone_bricks")
    for dx, dz in ((-12, 5), (12, -5)):
        b.fill(cx + dx, FLOOR_Y + 1, dz, cx + dx + 4, FLOOR_Y + 1, dz, "mossy_cobblestone")
        b.set(cx + dx + 2, FLOOR_Y + 2, dz, "mossy_stone_brick_wall")
    spawn_pads(b, cx, off, "chiseled_stone_bricks")
    return b, dict(hx=hx, hz=hz, off=off)


def sumo(cx):
    b = Build("sumo", ARENAS, seed=16)
    r, off = 7, 3
    pool = 16
    wy = FLOOR_Y - 3  # water surface
    b.fill(cx - pool, wy - 1, -pool, cx + pool, wy - 1, pool, "smooth_quartz")
    b.fill(cx - pool, wy, -pool, cx + pool, wy, pool, "water")
    for z in (-pool - 1, pool + 1):
        b.fill(cx - pool - 1, wy - 1, z, cx + pool + 1, wy + 1, z, "quartz_bricks")
    for x in (cx - pool - 1, cx + pool + 1):
        b.fill(x, wy - 1, -pool - 1, x, wy + 1, pool + 1, "quartz_bricks")
    for y in range(wy, FLOOR_Y):
        b.disc(cx, y, 0, r, "smooth_quartz")
    b.disc(cx, FLOOR_Y, 0, r, "white_concrete")
    b.disc(cx, FLOOR_Y, 0, r, "red_concrete", r_inner=r - 1)
    b.fill(cx, FLOOR_Y, -r + 1, cx, FLOOR_Y, r - 1, "light_gray_concrete")
    # keep pearls and jumpers inside the pool area
    top = FLOOR_Y + 25
    for z in (-pool - 1, pool + 1):
        b.fill(cx - pool - 1, wy + 2, z, cx + pool + 1, top, z, "barrier")
    for x in (cx - pool - 1, cx + pool + 1):
        b.fill(x, wy + 2, -pool - 1, x, top, pool + 1, "barrier")
    b.fill(cx - pool - 1, top, -pool - 1, cx + pool + 1, top, pool + 1, "barrier")
    return b, dict(hx=pool + 1, hz=pool + 1, off=off, sumo=True)


ARENA_BUILDERS = [colosseum, grove, inferno, glacier, ruins, sumo]

# ---------------------------------------------------------------- output

def write(path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main():
    if FUNC.exists():
        shutil.rmtree(FUNC)

    builds = [lobby()]
    arena_info = []
    for i, fn in enumerate(ARENA_BUILDERS):
        cx = i * ARENA_SPACING
        b, info = fn(cx)
        builds.append(b)
        arena_info.append((b.name, cx, info))

    write(PACK / "pack.mcmeta", [
        "{",
        '  "pack": {',
        '    "description": "practice-server-template: builds the lobby and arenas on first boot",',
        '    "min_format": 121,',
        '    "max_format": 999',
        "  }",
        "}",
    ])
    write(PACK / "data/minecraft/tags/function/load.json", ['{', '  "values": ["practice:load"]', '}'])

    write(FUNC / "load.mcfunction", [
        "# Runs on every start, but only does anything the first time.",
        "# Change gamerules in-game afterwards and they'll stick.",
        "scoreboard objectives add practice.setup dummy",
        "execute unless score #done practice.setup matches 1 run function practice:first_boot/start",
    ])

    rules = [
        "advance_time false", "advance_weather false", "spawn_mobs false", "spawn_phantoms false",
        "spawn_patrols false", "spawn_wandering_traders false", "raids false", "mob_griefing false",
        "show_advancement_messages false", "immediate_respawn true", "respawn_radius 0",
    ]
    write(FUNC / "first_boot/start.mcfunction", [
        *[f"gamerule {r}" for r in rules],
        "time set 6000",
        "weather clear",
        f"function practice:maps/{builds[0].name}/start",
    ])
    write(FUNC / "first_boot/finish.mcfunction", [
        "setworldspawn 0 64 0 180 0",
        "scoreboard players set #done practice.setup 1",
        "say [practice] lobby and arenas are built",
    ])

    for i, b in enumerate(builds):
        nxt = f"function practice:maps/{builds[i + 1].name}/start" if i + 1 < len(builds) else "function practice:first_boot/finish"
        x1, z1, x2, z2 = b.min_x, b.min_z, b.max_x, b.max_z
        ns = f"practice:maps/{b.name}"
        corners = " ".join(f"if loaded {x} 0 {z}" for x, z in ((x1, z1), (x2, z1), (x1, z2), (x2, z2)))
        write(FUNC / f"maps/{b.name}/start.mcfunction", [
            f"schedule function {ns}/wait 10t",
        ])
        # the arenas world only exists once ZonePractice has started, so keep retrying until it does
        write(FUNC / f"maps/{b.name}/wait.mcfunction", [
            f"schedule function {ns}/wait 10t",
            f"execute in {b.dim} run forceload add {x1} {z1} {x2} {z2}",
            f"execute in {b.dim} {corners} run function {ns}/build",
        ])
        extra = []
        if b.dim == ARENAS:
            extra = [f"execute in {b.dim} run gamerule {r}" for r in rules if not r.startswith("respawn")]
        write(FUNC / f"maps/{b.name}/build.mcfunction", [
            f"schedule clear {ns}/wait",
            f"execute in {b.dim} run function {ns}/blocks",
            f"execute in {b.dim} run forceload remove {x1} {z1} {x2} {z2}",
            *extra,
            nxt,
        ])
        write(FUNC / f"maps/{b.name}/blocks.mcfunction", [f"# {b.name}, generated by tools/generate_maps.py", *b.cmds])
        print(f"{b.name:10s} {len(b.cmds):5d} commands  x {x1}..{x2}  z {z1}..{z2}")

    # coordinates for arena setup
    lines = ["# arena name, world, spawn1, spawn2, corner1, corner2 (generated)"]
    for name, cx, info in arena_info:
        off, hx, hz = info["off"], info["hx"], info["hz"]
        ez = info.get("extra_z", hz)
        s1 = f"{cx - off + 0.5} {FLOOR_Y + 1} 0.5 -90"
        s2 = f"{cx + off + 0.5} {FLOOR_Y + 1} 0.5 90"
        c1 = f"{cx - hx} {FLOOR_Y - 10} {-ez}"
        c2 = f"{cx + hx} {FLOOR_Y + 30} {ez}"
        lines.append(f"{name}\tarenas\t{s1}\t{s2}\t{c1}\t{c2}")
    write(ROOT / "tools/arenas.tsv", lines)


if __name__ == "__main__":
    main()
