#!/bin/bash
# Installation script for StorageGRID CheckMK Plugin (CheckMK 2.4.0)
# Usage: sudo ./INSTALL.sh <site_name>

set -e

if [ "$EUID" -ne 0 ]; then
  echo "ERROR: This script must be run as root"
  exit 1
fi

if [ -z "$1" ]; then
  echo "Usage: $0 <site_name>"
  echo "Example: $0 mysite"
  exit 1
fi

SITE_NAME="$1"
OMD_ROOT="/omd/sites/${SITE_NAME}"
PLUGIN_DIR="${OMD_ROOT}/local/lib/python3/cmk_addons/plugins/storagegrid"

if [ ! -d "${OMD_ROOT}" ]; then
  echo "ERROR: CheckMK site '${SITE_NAME}' not found at ${OMD_ROOT}"
  exit 1
fi

echo "Installing StorageGRID CheckMK Plugin for site: ${SITE_NAME}"
echo "================================================================"
echo ""

# Remove old incorrectly placed files if they exist
echo "Cleaning up any old plugin files..."
rm -rf "${OMD_ROOT}/local/share/check_mk/web/plugins/wato/special_agents" 2>/dev/null || true
rm -f "${OMD_ROOT}/local/share/check_mk/web/plugins/wato/agent_storagegrid.py" 2>/dev/null || true
rm -f "${OMD_ROOT}/local/share/check_mk/web/plugins/wato/check_parameters_storagegrid.py" 2>/dev/null || true
rm -rf "${OMD_ROOT}/local/share/check_mk/agents/special/agent_storagegrid" 2>/dev/null || true
rm -rf "${OMD_ROOT}/local/lib/check_mk/base/plugins/agent_based/storagegrid_*.py" 2>/dev/null || true

# Create plugin directory structure
echo "Creating plugin directory structure..."
mkdir -p "${PLUGIN_DIR}/libexec"
mkdir -p "${PLUGIN_DIR}/rulesets"
mkdir -p "${PLUGIN_DIR}/server_side_calls"
mkdir -p "${PLUGIN_DIR}/agent_based"

# Copy files
echo "Installing plugin files..."

# Special agent executable
cp -v cmk_addons/plugins/storagegrid/libexec/agent_storagegrid "${PLUGIN_DIR}/libexec/"
chmod +x "${PLUGIN_DIR}/libexec/agent_storagegrid"

# Rulesets (GUI configuration)
cp -v cmk_addons/plugins/storagegrid/rulesets/special_agent.py "${PLUGIN_DIR}/rulesets/"

# Server-side calls (agent invocation)
cp -v cmk_addons/plugins/storagegrid/server_side_calls/special_agent.py "${PLUGIN_DIR}/server_side_calls/"

# Agent-based check plugins
cp -v cmk_addons/plugins/storagegrid/agent_based/*.py "${PLUGIN_DIR}/agent_based/"

# Python package __init__.py files (required for module discovery)
echo "Installing Python package files..."
cp -v cmk_addons/__init__.py "${OMD_ROOT}/local/lib/python3/cmk_addons/"
mkdir -p "${OMD_ROOT}/local/lib/python3/cmk_addons/plugins"
cp -v cmk_addons/plugins/__init__.py "${OMD_ROOT}/local/lib/python3/cmk_addons/plugins/"
cp -v cmk_addons/plugins/storagegrid/__init__.py "${PLUGIN_DIR}/"

# Set ownership
echo "Setting file ownership..."
chown -R "${SITE_NAME}:${SITE_NAME}" "${OMD_ROOT}/local/"

echo ""
echo "Installation completed successfully!"
echo ""
echo "Next steps:"
echo "1. Install Python dependencies as the site user:"
echo "   su - ${SITE_NAME}"
echo "   pip3 install requests"
echo ""
echo "2. Restart the web server:"
echo "   omd restart apache"
echo ""
echo "3. Configure the special agent in the web UI:"
echo "   Setup → Agents → Other integrations → NetApp StorageGRID"
echo ""
echo "4. Add your StorageGRID host and run service discovery"
echo ""
