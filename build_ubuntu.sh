#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
DIST_DIR="$PROJECT_DIR/dist"
DEB_DIR="$DIST_DIR/vibemusic_1.0.0_amd64.tmp"

echo "============================================"
echo "  VibeMusic - Ubuntu deb Build Script"
echo "============================================"
echo ""

echo "[1/5] Checking dependencies..."
pip install pyinstaller pycryptodome PyExecJS --quiet 2>/dev/null || pip3 install pyinstaller pycryptodome PyExecJS --quiet 2>/dev/null || { echo "[ERROR] Cannot install dependencies"; exit 1; }

echo "[2/5] Cleaning previous build..."
rm -rf "$DIST_DIR" "$PROJECT_DIR/build"

echo "[3/5] Running PyInstaller..."
cd "$PROJECT_DIR"
pyinstaller VibeMusic.linux.spec --noconfirm || pyinstaller3 VibeMusic.linux.spec --noconfirm || { echo "[ERROR] PyInstaller failed"; exit 1; }

echo "[4/5] Creating deb package structure..."
mkdir -p "$DEB_DIR/DEBIAN"
mkdir -p "$DEB_DIR/opt/vibemusic"
mkdir -p "$DEB_DIR/usr/bin"
mkdir -p "$DEB_DIR/usr/share/applications"

cat > "$DEB_DIR/DEBIAN/control" << 'EOF'
Package: vibemusic
Version: 1.0.0
Section: sound
Priority: optional
Architecture: amd64
Depends: libwebkit2gtk-4.1-0 (>= 2.40) | libwebkit2gtk-4.0-37, nodejs (>= 18)
Maintainer: VibeMusic <vibemusic@local>
Description: VibeMusic - Retro-futuristic terminal music player
 A cyberpunk-styled desktop music player with multi-platform
 music source (Kugou/Kuwo/Netease/QQ), AI agent integration,
 real-time spectrum visualization, and danmaku overlay.
EOF

cat > "$DEB_DIR/usr/share/applications/vibemusic.desktop" << 'DESKTOP'
[Desktop Entry]
Name=VibeMusic
Comment=Retro-futuristic terminal music player
Exec=/opt/vibemusic/VibeMusic
Icon=vibemusic
Terminal=false
Type=Application
Categories=AudioVideo;Audio;Player;
Keywords=music;player;cyberpunk;terminal;
DESKTOP

cp -r "$DIST_DIR/VibeMusic/"* "$DEB_DIR/opt/vibemusic/"

cat > "$DEB_DIR/usr/bin/vibemusic" << 'BINSH'
#!/bin/bash
exec /opt/vibemusic/VibeMusic "$@"
BINSH
chmod 755 "$DEB_DIR/usr/bin/vibemusic"

echo "[5/5] Building deb package..."
dpkg-deb --build "$DEB_DIR" "$DIST_DIR/vibemusic_1.0.0_amd64.deb"

rm -rf "$DEB_DIR"

echo ""
echo "============================================"
echo "  Build complete!"
echo "  Output: $DIST_DIR/vibemusic_1.0.0_amd64.deb"
echo "  Install: sudo dpkg -i vibemusic_1.0.0_amd64.deb"
echo "============================================"
echo ""
echo "NOTE: Requires Node.js >= 18 for QQ/Kuwo music sign."
echo "      sudo apt install nodejs"
