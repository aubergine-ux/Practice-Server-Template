schedule function practice:maps/grove/wait 10t
execute in minecraft:arenas run forceload add 165 -20 235 20
execute in minecraft:arenas if loaded 165 0 -20 if loaded 235 0 -20 if loaded 165 0 20 if loaded 235 0 20 run function practice:maps/grove/build
