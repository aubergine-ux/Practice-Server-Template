schedule clear practice:maps/glacier/wait
execute in minecraft:arenas run function practice:maps/glacier/blocks
execute in minecraft:arenas run forceload remove 565 -20 635 20
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
function practice:maps/ruins/start
