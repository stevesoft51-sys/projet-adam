@echo off
title Restaurant ADAM - Installation Windows

echo.
echo ============================================
echo    RESTAURANT ADAM - Installation Windows
echo ============================================
echo.
echo  Ce programme installe Restaurant ADAM sur
echo  votre ordinateur.
echo.

set "INSTALL_DIR=%USERPROFILE%\RestaurantADAM"
set "SRC_DIR=%~dp0"
set "PYTHON_DIR=%LOCALAPPDATA%\Programs\Python\Python312"
set "SCRIPTS=%PYTHON_DIR%\Scripts"

echo [1/4] Installation de Python 3.12...
echo.

"%SRC_DIR%python-3.12.7-amd64.exe" /passive InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_test=0 Include_launcher=0

set "PATH=%PYTHON_DIR%;%SCRIPTS%;%PATH%"

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas accessible.
    pause
    exit /b 1
)
echo [OK] Python installe.
echo.

echo [2/4] Installation des dependances...
echo.

python -m pip install --no-index --find-links="%SRC_DIR%wheels" setuptools
python -m pip install --no-index --find-links="%SRC_DIR%wheels" packaging
python -m pip install --no-index --find-links="%SRC_DIR%wheels" psutil
python -m pip install --no-index --find-links="%SRC_DIR%wheels" altgraph
python -m pip install --no-index --find-links="%SRC_DIR%wheels" fonttools
python -m pip install --no-index --find-links="%SRC_DIR%wheels" defusedxml
python -m pip install --no-index --find-links="%SRC_DIR%wheels" fpdf2
python -m pip install --no-index --find-links="%SRC_DIR%wheels" pillow
python -m pip install --no-index --find-links="%SRC_DIR%wheels" pyinstaller-hooks-contrib
python -m pip install --no-index --find-links="%SRC_DIR%wheels" pefile
python -m pip install --no-index --find-links="%SRC_DIR%wheels" pywin32-ctypes
python -m pip install --no-index --find-links="%SRC_DIR%wheels" pyinstaller

echo [OK] Dependances installees.
echo.

echo [3/4] Construction de l'executable...
echo       (Cela peut prendre 2-3 minutes)
echo.

cd /d "%SRC_DIR%"
"%SCRIPTS%\pyinstaller.exe" --clean --noconfirm RestaurantADAM.spec

if not exist "%SRC_DIR%dist\RestaurantADAM.exe" (
    echo [ERREUR] Echec de la compilation.
    pause
    exit /b 1
)

echo [OK] Executable cree.
echo.

echo [4/4] Installation et raccourci Bureau...
echo.

rem Purge d'une ancienne installation pour eviter les residus
if exist "%INSTALL_DIR%" (
    rmdir /S /Q "%INSTALL_DIR%" 2>nul
)
mkdir "%INSTALL_DIR%" 2>nul
copy /Y "%SRC_DIR%dist\RestaurantADAM.exe" "%INSTALL_DIR%\" >nul
xcopy /E /I /Y "%SRC_DIR%data" "%INSTALL_DIR%\data" >nul

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([System.IO.Path]::Combine([System.Environment]::GetFolderPath('Desktop'), 'Restaurant ADAM.lnk')); $s.TargetPath = '%INSTALL_DIR%\RestaurantADAM.exe'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.Save()"

echo ============================================
echo    INSTALLATION TERMINEE !
echo ============================================
echo.
echo  Raccourci : "Restaurant ADAM" sur le Bureau
echo  Dossier   : %INSTALL_DIR%
echo.
echo  CLE D'ACTIVATION : ADAM-2024-POS-UNIVERSAL
echo  Login : adam / adam
echo ============================================
echo.
pause
