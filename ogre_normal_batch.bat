@echo off
setlocal enabledelayedexpansion

echo Ogre Mesh Normal Recalculation - Simple & Working
echo ===================================================

REM Check if Python script exists
if not exist "recalculate_normals.py" (
    echo ERROR: recalculate_normals.py not found
    pause
    exit /b 1
)

REM Create backup directory
if not exist "backup" mkdir backup

echo Found mesh files:
for %%f in (*.mesh) do echo   %%f
echo.

REM Process all .mesh files
set /a total=0
set /a success=0
set /a failed=0

for %%f in (*.mesh) do (
    set /a total+=1
    echo.
    echo [!total!] Processing: %%f
    echo ========================
    
    REM Create backup
    echo Creating backup...
    copy "%%f" "backup\%%f.backup" >nul
    
    REM Step 1: Convert to XML (same as your manual process)
    echo Converting to XML...
    OgreXMLConverter.exe "%%f" "%%f.xml"
    
    if exist "%%f.xml" (
        echo ✓ XML created successfully
        
        REM Step 2: Recalculate normals
        echo Recalculating normals...
        python recalculate_normals.py "%%f.xml"
        
        if !errorlevel! equ 0 (
            echo ✓ Normals recalculated successfully
            
            REM Step 3: Convert back to mesh
            echo Converting back to mesh...
            set original_size=0
            for %%s in ("%%f") do set original_size=%%~zs
            
            OgreXMLConverter.exe "%%f.xml" "%%f"
            
            REM Check if mesh file exists and has reasonable size (better than just exit code)
            if exist "%%f" (
                set new_size=0
                for %%s in ("%%f") do set new_size=%%~zs
                if !new_size! gtr 100 (
                    echo ✓ Successfully processed %%f ^(size: !new_size! bytes^)
                    set /a success+=1
                    
                    REM Clean up XML file
                    del "%%f.xml" 2>nul
                ) else (
                    echo ✗ Mesh file created but appears corrupted ^(size: !new_size! bytes^)
                    set /a failed+=1
                )
            ) else (
                echo ✗ Failed to convert back to mesh - file not created
                set /a failed+=1
            )
        ) else (
            echo ✗ Failed to recalculate normals
            set /a failed+=1
        )
    ) else (
        echo ✗ Failed to create XML file
        set /a failed+=1
    )
)

echo.
echo ===================================================
echo Processing Complete!
echo.
echo Summary:
echo   Total files processed: !total!
echo   Successfully updated: !success!
echo   Failed: !failed!
echo   Original files backed up to: backup\
echo.

if !failed! gtr 0 (
    echo Note: Some files failed processing.
    echo Check the output above for specific error details.
    echo Original files are safe in the backup folder.
) else (
    echo All mesh files have been successfully updated with recalculated normals!
)

echo.
pause