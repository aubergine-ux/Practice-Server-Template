schedule function practice:maps/sumo/wait 10t
execute in minecraft:arenas run forceload add 983 -17 1017 17
execute in minecraft:arenas if loaded 983 0 -17 if loaded 1017 0 -17 if loaded 983 0 17 if loaded 1017 0 17 run function practice:maps/sumo/build
