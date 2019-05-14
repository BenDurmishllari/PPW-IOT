@echo off

if %1.==. goto missing
    choice /N /M "Erase and flash ESP32 firmware using port %1 (y)es or (n)o? "
    if %errorlevel% == 1 goto cont1
    goto abort

:cont1
    echo Erasing current firmware from ESP32 using port %1, please wait ...
    esptool --chip esp32 --port %1 erase_flash > nul 2> nul
    if %errorlevel% == 0 goto cont2
    echo Erase of current firmware from ESP32 using port %1 failed
    goto abort
    
:cont2
    echo Current firmware successfully erased from ESP32 using port %1
    echo Flashing MicroPython firmware to ESP32 using port %1, please wait ...
    esptool --chip esp32 --port %1 --baud 921600 write_flash -z 0x1000 esp32mp.bin > nul 2> nul
    if %errorlevel% == 0 goto cont3
    echo Flash of MicroPython firmware to ESP32 using port %1 failed
    goto abort

:cont3
    ampy -p %1 ls -r
    if %errorlevel% == 0 goto cont4
    echo Flash of MicroPython firmware to ESP32 using port %1 failed
    goto abort

:cont4
    echo MicroPython firmware successfully flashed to ESP32 using port %1
    goto end
    
:missing
    echo No COM port provided

:abort
    echo Aborted!
    
:end
