#!/bin/bash
# Restaurant ADAM — Script de build
set -e
cd "$(dirname "$0")"

echo "=== Restaurant ADAM — Build ==="
echo ""

# Nettoyer les anciens builds
rm -rf build dist RestaurantADAM.spec

echo "[1/3] Construction de l'executable..."
pyinstaller --onefile \
    --name RestaurantADAM \
    --noconsole \
    --add-data "app:app" \
    --add-data "data:data" \
    --add-data "fonts:fonts" \
    --hidden-import app.activation \
    --hidden-import app.bootstrap \
    --hidden-import app.pdf_generator \
    --hidden-import app.security \
    --hidden-import app.services \
    --hidden-import app.state \
    --hidden-import app.storage \
    --hidden-import app.ui.activation_window \
    --hidden-import app.ui.login_window \
    --hidden-import app.ui.main_window \
    --hidden-import app.ui.product_images \
    --hidden-import app.ui.theme \
    --hidden-import app.ui.widgets \
    --hidden-import app.ui.views.cash_view \
    --hidden-import app.ui.views.floor_view \
    --hidden-import app.ui.views.menu_view \
    --hidden-import app.ui.views.pos_view \
    --hidden-import app.ui.views.reports_helpers \
    --hidden-import app.ui.views.reports_view \
    --hidden-import app.ui.views.staff_view \
    --hidden-import app.ui.views.stock_view \
    --hidden-import app.ui.views.suppliers_view \
    --hidden-import fpdf \
    main.py

echo "[2/3] Preparation de l'installeur..."
mkdir -p dist/installateur
cp dist/RestaurantADAM dist/installateur/
cp -r data dist/installateur/
cp LICENCE dist/installateur/ 2>/dev/null || true

# Cle universelle
CLE="ADAM-2024-POS-UNIVERSAL"
echo "    Cle d'activation : $CLE"

# Creer le script d'installation
cat > dist/installateur/installer.sh << INSTALLER
#!/bin/bash
set -e
echo ""
echo "==========================================="
echo "   Restaurant ADAM — Installation"
echo "==========================================="
echo ""
echo "Cle d'activation : $CLE"
echo ""
INSTALL_DIR="\$HOME/RestaurantADAM"
echo "Installation dans : \$INSTALL_DIR"
mkdir -p "\$INSTALL_DIR"
cp -r "\$(dirname "\$0")/"* "\$INSTALL_DIR/"
chmod +x "\$INSTALL_DIR/RestaurantADAM"

# Creer le raccourci bureau
cat > "\$HOME/Bureau/RestaurantADAM.desktop" << DESKTOP
[Desktop Entry]
Name=Restaurant ADAM
Comment=Point de Vente & Gestion
Exec=\$INSTALL_DIR/RestaurantADAM
Icon=\$INSTALL_DIR/RestaurantADAM
Terminal=false
Type=Application
Categories=Restaurant;POS;
DESKTOP
chmod +x "\$HOME/Bureau/RestaurantADAM.desktop"

echo ""
echo "Installation terminee !"
echo "L'application est accessible depuis le Bureau."
echo ""
read -p "Appuyez sur Entree pour terminer..."
INSTALLER
chmod +x dist/installateur/installer.sh

# Creer l'archive auto-extractible
cd dist
tar czf RestaurantADAM-installer.tar.gz installateur/

echo ""
echo "[3/3] Build termine !"
echo ""
echo "  Executable : dist/RestaurantADAM"
echo "  Installeur : dist/RestaurantADAM-installer.tar.gz"
echo "  Cle        : $CLE"
echo ""
