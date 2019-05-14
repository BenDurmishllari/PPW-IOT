@echo off

if %1.==. goto missing
    call flash_esp32 %1
    if %errorlevel% == 0 goto cont1
    goto end

:cont1
    call libs_esp32 %1
    if %errorlevel% == 0 goto cont2
    goto end

:cont2
    call upload_esp32 %1
    if %errorlevel% == 0 goto end
    goto end
    
:missing
    echo No COM port provided
    echo Aborted!
    
:end
