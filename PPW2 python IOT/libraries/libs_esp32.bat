@echo off

rem if %1.==. goto missing
rem     choice /N /M "Create libs directory on ESP32 using port %1 (y)es or (n)o? "
rem     if %errorlevel% == 1 goto cont1
rem     goto abort

:cont1
    echo Creating libs directory on ESP32 using port %1, please wait ...
    ampy -p %1 mkdir ./libs
    if %errorlevel% == 0 goto cont2
    echo Creating libs directory on ESP32 using port %1 failed
    goto abort
    
:cont2
    ampy -p %1 ls -r
    if %errorlevel% == 0 goto cont3
    echo Creating libs directory on ESP32 using port %1 failed
    goto abort
    
:cont3
    echo Successfully created libs directory on ESP32 using port %1
    goto end
    
:missing
    echo No COM port provided

:abort
    echo Aborted!
    
:end
