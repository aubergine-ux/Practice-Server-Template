schedule function practice:maps/ruins/wait 10t
execute in minecraft:arenas run forceload add 765 -20 835 20
execute in minecraft:arenas if loaded 765 0 -20 if loaded 835 0 -20 if loaded 765 0 20 if loaded 835 0 20 run function practice:maps/ruins/build
