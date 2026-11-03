# Runs on every start, but only does anything the first time.
# Change gamerules in-game afterwards and they'll stick.
scoreboard objectives add duels.setup dummy
execute unless score #done duels.setup matches 1 run function duels:first_boot/start
