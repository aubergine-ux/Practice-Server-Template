schedule clear practice:maps/colosseum/wait
execute in minecraft:arenas run function practice:maps/colosseum/blocks
execute in minecraft:arenas run forceload remove -35 -25 35 25
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
function practice:maps/grove/start
