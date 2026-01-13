#!/bin/bash
# Automated installer for Google Cloud SDK
# This script downloads and installs gcloud CLI on Linux

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Google Cloud SDK Installer${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if gcloud is already installed
if command -v gcloud &> /dev/null; then
    echo -e "${GREEN}✅ gcloud is already installed!${NC}"
    gcloud --version
    echo ""
    echo -e "${YELLOW}To update gcloud, run: gcloud components update${NC}"
    exit 0
fi

# Download location
INSTALL_DIR="$HOME"
SDK_DIR="$INSTALL_DIR/google-cloud-sdk"

echo -e "${YELLOW}Installing Google Cloud SDK to: $SDK_DIR${NC}"
echo ""

# Download the latest SDK
echo -e "${BLUE}Step 1/5: Downloading Google Cloud SDK...${NC}"
cd "$INSTALL_DIR"
wget -q https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz

echo -e "${GREEN}✅ Downloaded${NC}"
echo ""

# Extract
echo -e "${BLUE}Step 2/5: Extracting...${NC}"
tar -xf google-cloud-cli-linux-x86_64.tar.gz

echo -e "${GREEN}✅ Extracted${NC}"
echo ""

# Install
echo -e "${BLUE}Step 3/5: Installing...${NC}"
"$SDK_DIR/install.sh" \
    --quiet \
    --usage-reporting false \
    --path-update true \
    --command-completion true

echo -e "${GREEN}✅ Installed${NC}"
echo ""

# Add to PATH for current session
export PATH="$SDK_DIR/bin:$PATH"

# Detect shell and update config
echo -e "${BLUE}Step 4/5: Updating shell configuration...${NC}"

if [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
elif [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
else
    SHELL_RC="$HOME/.profile"
fi

# Add to shell config if not already present
if ! grep -q "google-cloud-sdk" "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "# Google Cloud SDK" >> "$SHELL_RC"
    echo "export PATH=\"\$HOME/google-cloud-sdk/bin:\$PATH\"" >> "$SHELL_RC"
    echo -e "${GREEN}✅ Added to $SHELL_RC${NC}"
else
    echo -e "${YELLOW}Already in $SHELL_RC${NC}"
fi

echo ""

# Clean up
echo -e "${BLUE}Step 5/5: Cleaning up...${NC}"
rm google-cloud-cli-linux-x86_64.tar.gz
echo -e "${GREEN}✅ Done${NC}"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo ""
echo "1. Reload your shell:"
echo -e "   ${BLUE}source $SHELL_RC${NC}"
echo ""
echo "2. Verify installation:"
echo -e "   ${BLUE}gcloud --version${NC}"
echo ""
echo "3. Initialize gcloud:"
echo -e "   ${BLUE}gcloud init${NC}"
echo ""
echo "4. Authenticate:"
echo -e "   ${BLUE}gcloud auth login${NC}"
echo -e "   ${BLUE}gcloud auth application-default login${NC}"
echo ""
echo "5. Enable Vertex AI:"
echo -e "   ${BLUE}gcloud services enable aiplatform.googleapis.com${NC}"
echo ""
echo -e "${YELLOW}Or continue with the GCLOUD_SETUP_GUIDE.md for full setup!${NC}"
echo ""
