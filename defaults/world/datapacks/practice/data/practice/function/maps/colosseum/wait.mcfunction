execute if score #colosseum practice.setup matches 1 run return fail
schedule function practice:maps/colosseum/wait 10t
execute in minecraft:arenas run forceload add -35 -25 35 25
execute in minecraft:arenas if loaded -35 0 -25 if loaded 35 0 -25 if loaded -35 0 25 if loaded 35 0 25 run function practice:maps/colosseum/build
