schedule clear practice:maps/inferno/wait
execute if score #inferno practice.setup matches 1 run return fail
scoreboard players set #inferno practice.setup 1
execute in minecraft:arenas run function practice:maps/inferno/blocks
execute in minecraft:arenas run forceload remove 365 -20 435 20
execute in minecraft:arenas run gamerule advance_time false
execute in minecraft:arenas run gamerule advance_weather false
execute in minecraft:arenas run gamerule spawn_mobs false
execute in minecraft:arenas run gamerule spawn_phantoms false
execute in minecraft:arenas run gamerule spawn_patrols false
execute in minecraft:arenas run gamerule spawn_wandering_traders false
execute in minecraft:arenas run gamerule raids false
execute in minecraft:arenas run gamerule mob_griefing false
execute in minecraft:arenas run gamerule show_advancement_messages false
execute in minecraft:arenas run gamerule immediate_respawn true
function practice:maps/glacier/start
