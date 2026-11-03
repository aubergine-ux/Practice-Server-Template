@echo off
rem Starts the server. Change the heap size with: set MEMORY=6G
cd /d "%~dp0server"
if "%MEMORY%"=="" set MEMORY=4G

if not exist server.jar (
    echo server.jar not found - run setup.bat first
    pause
    exit /b 1
)

findstr /b /c:"eula=true" eula.txt >nul 2>&1
if not errorlevel 1 goto run

echo You must accept the Minecraft EULA to run a server: https://aka.ms/MinecraftEULA
set /p ANSWER=Do you accept it? [y/N]
if /i not "%ANSWER:~0,1%"=="y" exit /b 1
echo eula=true> eula.txt

:run
rem JVM flags recommended by PaperMC for this version (fill.papermc.io)
java -Xms%MEMORY% -Xmx%MEMORY% ^
  -XX:+AlwaysPreTouch -XX:+DisableExplicitGC -XX:+ParallelRefProcEnabled ^
  -XX:+PerfDisableSharedMem -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC ^
  -XX:G1HeapRegionSize=8M -XX:G1HeapWastePercent=5 -XX:G1MaxNewSizePercent=40 ^
  -XX:G1MixedGCCountTarget=4 -XX:G1MixedGCLiveThresholdPercent=90 ^
  -XX:G1NewSizePercent=30 -XX:G1RSetUpdatingPauseTimePercent=5 ^
  -XX:G1ReservePercent=20 -XX:InitiatingHeapOccupancyPercent=15 ^
  -XX:MaxGCPauseMillis=200 -XX:MaxTenuringThreshold=1 -XX:SurvivorRatio=32 ^
  -jar server.jar --nogui
pause
