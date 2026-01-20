#!/bin/bash
# Uninstall script for StorageGRID CheckMK Plugin
# Usage: sudo ./UNINSTALL.sh <site_name>

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

if [ ! -d "${OMD_ROOT}" ]; then
  echo "ERROR: CheckMK site '${SITE_NAME}' not found at ${OMD_ROOT}"
  exit 1
fi

echo "Uninstalling StorageGRID CheckMK Plugin from site: ${SITE_NAME}"
echo "================================================================"
echo ""
read -p "Are you sure you want to remove the plugin? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
  echo "Uninstall cancelled."
  exit 0
fi

# Remove special agent
echo "Removing special agent..."
rm -fv "${OMD_ROOT}/local/share/check_mk/agents/special/agent_storagegrid"

# Remove check plugins
echo "Removing check plugins..."
rm -fv "${OMD_ROOT}/local/lib/check_mk/base/plugins/agent_based/storagegrid_health.py"
rm -fv "${OMD_ROOT}/local/lib/check_mk/base/plugins/agent_based/storagegrid_capacity.py"
rm -fv "${OMD_ROOT}/local/lib/check_mk/base/plugins/agent_based/storagegrid_alerts.py"
rm -fv "${OMD_ROOT}/local/lib/check_mk/base/plugins/agent_based/storagegrid_s3.py"
rm -fv "${OMD_ROOT}/local/lib/check_mk/base/plugins/agent_based/storagegrid_resources.py"
rm -fv "${OMD_ROOT}/local/lib/check_mk/base/plugins/agent_based/storagegrid_tenants.py"
rm -fv "${OMD_ROOT}/local/lib/check_mk/base/plugins/agent_based/storagegrid_ilm.py"
rm -fv "${OMD_ROOT}/local/lib/check_mk/base/plugins/agent_based/storagegrid_storage_state.py"

# Remove WATO configuration
echo "Removing WATO configuration..."
rm -fv "${OMD_ROOT}/local/share/check_mk/web/plugins/wato/agent_storagegrid.py"
rm -fv "${OMD_ROOT}/local/share/check_mk/web/plugins/wato/check_parameters_storagegrid.py"

# Remove Python cache files if they exist
echo "Cleaning up cache files..."
find "${OMD_ROOT}/local/lib/check_mk/base/plugins/agent_based/" -name "*storagegrid*.pyc" -delete 2>/dev/null || true
find "${OMD_ROOT}/local/lib/check_mk/base/plugins/agent_based/" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "${OMD_ROOT}/local/share/check_mk/web/plugins/wato/" -name "*storagegrid*.pyc" -delete 2>/dev/null || true
find "${OMD_ROOT}/local/share/check_mk/web/plugins/wato/" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo ""
echo "Plugin files removed successfully!"
echo ""
echo "IMPORTANT: Manual cleanup required:"
echo "1. Restart CheckMK to unload the plugin:"
echo "   omd restart"
echo ""
echo "2. Remove StorageGRID hosts or delete services in WATO:"
echo "   - Navigate to affected hosts"
echo "   - Run 'Remove vanished services' discovery"
echo "   - Activate changes"
echo ""
echo "3. Delete special agent rule in WATO (if configured):"
echo "   Setup → Hosts → Host monitoring rules → Search 'StorageGRID'"
echo "   Delete the rule and activate changes"
echo ""
echo "4. (Optional) Uninstall Python dependencies if not needed:"
echo "   su - ${SITE_NAME}"
echo "   pip3 uninstall requests"
echo ""
