# Small platform so the first people to join don't drop into the void.
# Build your lobby around it and move spawn with /setworldspawn.
fill -4 63 -4 4 63 4 minecraft:smooth_stone keep
setblock 0 63 0 minecraft:sea_lantern
setworldspawn 0 64 0
forceload remove -8 -8 8 8
scoreboard players set #done duels.setup 1
say [duels-template] First-boot setup done
