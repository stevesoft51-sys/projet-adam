@echo off
chcp 65001 >nul
echo.
echo ===========================================
echo    Restaurant ADAM — Build Windows
echo ===========================================
echo.

REM Verifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH.
    echo Telechargez Python depuis https://www.python.org/downloads/
    echo Cochez "Add Python to PATH" lors de l'installation.
    pause
    exit /b 1
)

REM Installer les dependances
echo [0/3] Installation des dependances...
pip install pyinstaller fpdf2 pillow --quiet
if errorlevel 1 (
    echo [ERREUR] Echec de l'installation des dependances.
    pause
    exit /b 1
)

echo.
echo [1/3] Construction de l'executable...
pyinstaller --onefile ^
    --noconsole ^
    --name RestaurantADAM ^
    --add-data "app;app" ^
    --add-data "data;data" ^
    --add-data "fonts;fonts" ^
    --hidden-import app.activation ^
    --hidden-import app.bootstrap ^
    --hidden-import app.pdf_generator ^
    --hidden-import app.security ^
    --hidden-import app.services ^
    --hidden-import app.state ^
    --hidden-import app.storage ^
    --hidden-import app.ui.activation_window ^
    --hidden-import app.ui.login_window ^
    --hidden-import app.ui.main_window ^
    --hidden-import app.ui.product_images ^
    --hidden-import app.ui.theme ^
    --hidden-import app.ui.widgets ^
    --hidden-import app.ui.views.cash_view ^
    --hidden-import app.ui.views.floor_view ^
    --hidden-import app.ui.views.menu_view ^
    --hidden-import app.ui.views.pos_view ^
    --hidden-import app.ui.views.reports_helpers ^
    --hidden-import app.ui.views.reports_view ^
    --hidden-import app.ui.views.staff_view ^
    --hidden-import app.ui.views.stock_view ^
    --hidden-import app.ui.views.suppliers_view ^
    --hidden-import fpdf ^
    main.py

if errorlevel 1 (
    echo [ERREUR] Echec de la compilation.
    pause
    exit /b 1
)

echo.
echo [2/3] Preparation du dossier de distribution...
if not exist dist\installateur mkdir dist\installateur
copy dist\RestaurantADAM.exe dist\installateur\ >nul
xcopy /E /I /Y data dist\installateur\data >nul

REM Generer installer.bat dans le dossier installateur
echo [3/3] Creation de l'installeur...
(
echo @echo off
echo chcp 65001 ^>nul
echo echo.
echo echo ===========================================
echo echo    Restaurant ADAM — Installation
echo echo ===========================================
echo echo.
echo set "INSTALL_DIR=%%USERPROFILE%%\RestaurantADAM"
echo echo Installation dans : %%INSTALL_DIR%%
echo mkdir "%%INSTALL_DIR%%" 2^>nul
echo xcopy /E /I /Y "%%~dp0RestaurantADAM.exe" "%%INSTALL_DIR%%\" ^>nul
echo copy /Y "%%~dp0data" "%%INSTALL_DIR%%\" ^>nul
echo xcopy /E /I /Y "%%~dp0data" "%%INSTALL_DIR%%\data\" ^>nul
echo.
echo REM Creer le raccourci Bureau via PowerShell
echo powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%%USERPROFILE%%\Desktop\Restaurant ADAM.lnk'); $s.TargetPath = '%%INSTALL_DIR%%\RestaurantADAM.exe'; $s.WorkingDirectory = '%%INSTALL_DIR%%'; $s.Save()"
echo.
echo echo.
echo echo Installation terminee !
echo echo Un raccourci "Restaurant ADAM" a ete cree sur le Bureau.
echo echo.
echo echo ===========================================
echo echo    CLE D'ACTIVATION : ADAM-2024-POS-UNIVERSAL
echo echo ===========================================
echo echo.
echo pause
) > dist\installateur\installer.bat

REM Creer l'archive zip
echo.
echo Creation de l'archive ZIP...
cd dist
powershell -Command "Compress-Archive -Path 'installateur\*' -DestinationPath 'RestaurantADAM-Installer-Windows.zip' -Force"
cd ..

echo.
echo ===========================================
echo    BUILD TERMINE !
echo ===========================================
echo.
echo  Executable : dist\RestaurantADAM.exe
echo  Installeur : dist\RestaurantADAM-Installer-Windows.zip
echo  Cle        : ADAM-2024-POS-UNIVERSAL
echo.
pause
