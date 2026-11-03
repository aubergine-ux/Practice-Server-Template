schedule function practice:maps/glacier/wait 10t
execute in minecraft:arenas run forceload add 565 -20 635 20
execute in minecraft:arenas if loaded 565 0 -20 if loaded 635 0 -20 if loaded 565 0 20 if loaded 635 0 20 run function practice:maps/glacier/build
