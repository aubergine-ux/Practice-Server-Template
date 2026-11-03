gamerule advance_time false
gamerule advance_weather false
gamerule spawn_mobs false
gamerule spawn_phantoms false
gamerule spawn_patrols false
gamerule spawn_wandering_traders false
gamerule raids false
gamerule mob_griefing false
gamerule show_advancement_messages false
gamerule immediate_respawn true
gamerule respawn_radius 0
time set 6000
weather clear

# Spawn chunk isn't loaded yet at this point, so load it and build once it's ready
forceload add -8 -8 8 8
schedule function duels:first_boot/platform 20t
