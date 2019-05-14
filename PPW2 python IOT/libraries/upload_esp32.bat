@echo off

rem if %1.==. goto missing
rem     choice /N /M "Upload files to ESP32 using port %1 (y)es or (n)o? "
rem     if %errorlevel% == 1 goto cont1
rem     goto abort

:cont1
    echo Uploading MicroPython files to ESP32 using port %1, please wait ...
    for %%f in (libs/*.*) do (
        ampy -p %1 put libs/%%~f /libs/%%~f
        echo Uploaded MicroPython file %%~f
    )
    echo MicroPython files successfully uploaded to ESP32 using port %1  
    goto end
    
:missing
    echo No COM port provided

:abort
    echo Aborted!
    
:end
