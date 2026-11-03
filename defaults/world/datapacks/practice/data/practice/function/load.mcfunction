# Runs on every start, but only does anything the first time.
# Change gamerules in-game afterwards and they'll stick.
scoreboard objectives add practice.setup dummy
execute unless score #done practice.setup matches 1 run function practice:first_boot/start
