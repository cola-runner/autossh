#!/bin/bash

set -e

echo "🔧 Installing autossh..."

INSTALL_DIR="/usr/local/bin"
BINARY_URL="https://github.com/Cola-Rex/autossh/releases/latest/download/autossh"
TARGET="$INSTALL_DIR/autossh"

if ! command -v curl &> /dev/null; then
  echo "❌ curl is required but not installed."
  exit 1
fi

echo "⬇️  Downloading autossh from: $BINARY_URL"
sudo curl -fsSL "$BINARY_URL" -o "$TARGET"
sudo chmod +x "$TARGET"

echo "✅ autossh installed at: $TARGET"
echo ""
echo "📦 Example usage:"
echo "  autossh -L 5433:remote-db:5432 user@remote-host"
echo ""
echo "🎉 All done!"
