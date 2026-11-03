execute if score #lobby practice.setup matches 1 run return fail
schedule function practice:maps/lobby/wait 10t
execute in minecraft:overworld run forceload add -26 -26 26 26
execute in minecraft:overworld if loaded -26 0 -26 if loaded 26 0 -26 if loaded -26 0 26 if loaded 26 0 26 run function practice:maps/lobby/build
