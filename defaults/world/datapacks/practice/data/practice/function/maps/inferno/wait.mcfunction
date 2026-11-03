execute if score #inferno practice.setup matches 1 run return fail
schedule function practice:maps/inferno/wait 10t
execute in minecraft:arenas run forceload add 365 -20 435 20
execute in minecraft:arenas if loaded 365 0 -20 if loaded 435 0 -20 if loaded 365 0 20 if loaded 435 0 20 run function practice:maps/inferno/build
