schedule clear practice:maps/lobby/wait
execute if score #lobby practice.setup matches 1 run return fail
scoreboard players set #lobby practice.setup 1
execute in minecraft:overworld run function practice:maps/lobby/blocks
execute in minecraft:overworld run forceload remove -26 -26 26 26
function practice:maps/colosseum/start
