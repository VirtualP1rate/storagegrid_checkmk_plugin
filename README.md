# CheckMK Plugin for NetApp StorageGRID

Monitor NetApp StorageGRID systems using **CheckMK Raw Edition 2.4.0p18**. This plugin uses the StorageGRID REST API v4 to collect comprehensive monitoring data.

**✅ Built using the official CheckMK 2.4.0 Plugin API**

## Features

### Monitoring Capabilities

- **Node Health**: Monitor all grid nodes (Admin, Storage, Gateway, API Gateway) with state and severity tracking
- **Site Health**: Track site-level connectivity and node aggregation across multiple sites
- **Data Capacity**: Monitor data storage utilization separately with configurable thresholds
- **Metadata Capacity**: Monitor metadata storage utilization separately with configurable thresholds
- **Active Alerts**: Track StorageGRID alerts (critical, major, minor) with detailed information
- **S3 Performance**: Monitor S3 request rates and error rates
- **Node Resources**: Track CPU utilization per node
- **Tenant Usage**: Monitor storage usage and object counts for each tenant account
- **ILM Metrics**: Track Information Lifecycle Management scan progress and queue depth

### Check Plugins

The plugin provides the following CheckMK services:

1. **StorageGRID Node {site}/{node}** - Individual node health status
2. **StorageGRID Site {site}** - Site-level health aggregation
3. **StorageGRID Data Capacity** - Data storage capacity monitoring (separate alerting)
4. **StorageGRID Metadata Capacity** - Metadata storage capacity monitoring (separate alerting)
5. **StorageGRID Alerts Summary** - Active alerts count by severity
6. **StorageGRID S3 Performance** - S3 request metrics and error rates
7. **StorageGRID Node Resources {node}** - Per-node CPU utilization
8. **StorageGRID Tenant {tenant}** - Per-tenant storage usage with object counts
9. **StorageGRID ILM** - ILM scan period and queue metrics

## Requirements

- CheckMK Raw Edition 2.4.0p18 or later
- NetApp StorageGRID 11.8+ with API v4 support
- Python 3 with `requests` library
- Grid administrator credentials with read access

## Installation

### Quick Install

```bash
cd storagegrid_checkmk_plugin
sudo ./INSTALL.sh <your_site_name>
```

Replace `<your_site_name>` with your actual CheckMK site name.

### Manual Installation

```bash
# Set your site name
SITE_NAME="<your_site_name>"
PLUGIN_DIR="/omd/sites/${SITE_NAME}/local/lib/python3/cmk_addons/plugins/storagegrid"

# Create directories
sudo mkdir -p ${PLUGIN_DIR}/{libexec,rulesets,server_side_calls,agent_based}

# Copy files
sudo cp cmk_addons/plugins/storagegrid/libexec/agent_storagegrid ${PLUGIN_DIR}/libexec/
sudo cp cmk_addons/plugins/storagegrid/rulesets/special_agent.py ${PLUGIN_DIR}/rulesets/
sudo cp cmk_addons/plugins/storagegrid/server_side_calls/special_agent.py ${PLUGIN_DIR}/server_side_calls/
sudo cp cmk_addons/plugins/storagegrid/agent_based/*.py ${PLUGIN_DIR}/agent_based/

# Make agent executable
sudo chmod +x ${PLUGIN_DIR}/libexec/agent_storagegrid

# Set ownership
sudo chown -R ${SITE_NAME}:${SITE_NAME} /omd/sites/${SITE_NAME}/local/
```

### Post-Installation

```bash
# Switch to site user
su - <your_site_name>

# Install Python dependencies
pip3 install requests

# Restart web server
omd restart apache
```

## Configuration

### 1. Configure Special Agent Rule in Web UI

1. Navigate to **Setup → Agents → Other integrations**
2. Find and click **NetApp StorageGRID**
3. Click **Add rule**
4. Configure:
   - **Grid Admin Username**: Your StorageGRID admin username (e.g., `root`)
   - **Grid Admin Password**: Your StorageGRID admin password
   - **Disable SSL certificate verification**: Enable for self-signed certificates (not recommended for production)
   - **Request Timeout**: API request timeout in seconds (default: 30)
5. Under **Conditions**, specify which hosts this rule applies to:
   - **Explicit hosts**: Enter your StorageGRID hostname or IP address
   - Or use **Host tags** if you've tagged your StorageGRID systems
6. Save the rule

### 2. Add StorageGRID Host

1. Navigate to **Setup → Hosts → Hosts**
2. Click **Add host**
3. Configure:
   - **Hostname**: Your StorageGRID hostname or IP address (must match the condition in the special agent rule)
   - **IP address family**: IPv4
   - **IPv4 address**: Your StorageGRID management IP or hostname
4. Save the host

### 3. Run Service Discovery

1. Go to the host's detail page
2. Click **Run service discovery**
3. You should see services discovered for:
   - Individual nodes (all nodes across all sites)
   - Sites (all sites in your grid)
   - Data and metadata capacity
   - Alerts summary
   - S3 performance
   - Node resources (CPU for each node)
   - Tenant usage (for each tenant)
   - ILM metrics
4. Click **Accept all**
5. **Activate changes**

## Directory Structure

```
~/local/lib/python3/cmk_addons/plugins/storagegrid/
├── libexec/
│   └── agent_storagegrid           # Special agent executable
├── rulesets/
│   └── special_agent.py            # GUI configuration for WATO
├── server_side_calls/
│   └── special_agent.py            # Agent invocation logic
└── agent_based/
    ├── storagegrid_health.py       # Node/site health checks
    ├── storagegrid_capacity.py     # Data and metadata capacity checks (split)
    ├── storagegrid_alerts.py       # Alert monitoring
    ├── storagegrid_s3.py           # S3 performance checks
    ├── storagegrid_resources.py    # Node CPU monitoring
    ├── storagegrid_tenants.py      # Tenant usage with object counts
    └── storagegrid_ilm.py          # ILM metrics
```

## Service Configuration

### Adjusting Thresholds

You can customize alert thresholds for various metrics in **Setup → Services → Service monitoring rules**:

#### Data Capacity Thresholds

**Rule:** StorageGRID Data Capacity

- **Default**: WARN at 80%, CRIT at 90%
- Monitors overall data storage utilization

#### Metadata Capacity Thresholds

**Rule:** StorageGRID Metadata Capacity

- **Default**: WARN at 70%, CRIT at 80%
- Monitors metadata storage utilization (more critical than data)

#### S3 Performance Thresholds

**Rule:** StorageGRID S3 Performance

- **Error Rate**: Default WARN at 1%, CRIT at 5%

#### Node Resources Thresholds

**Rule:** StorageGRID Node Resources

- **CPU Utilization**: Default WARN at 80%, CRIT at 90%

#### Tenant Quota Thresholds

**Rule:** StorageGRID Tenant Usage

- **Quota Utilization**: Default WARN at 80%, CRIT at 90%
- Only applies if tenant has a quota set

#### ILM Thresholds

**Rule:** StorageGRID ILM

- **Scan Period**: Default WARN at 3 days, CRIT at 7 days
- **Awaiting Objects**: Default WARN at 100,000, CRIT at 1,000,000

## Testing

### Test Special Agent Manually

```bash
su - <your_site_name>
cd ~/local/lib/python3/cmk_addons/plugins/storagegrid/libexec

./agent_storagegrid \
  --hostname <your_storagegrid_ip> \
  --username root \
  --password '<your_password>' \
  --no-cert-check
```

Expected output: JSON sections prefixed with `<<<storagegrid_*>>>`

### Verify in CheckMK

```bash
# Dump agent output for a host
cmk -d <your_hostname_or_ip>

# Verbose check mode
cmk -vv <your_hostname_or_ip>
```

## Troubleshooting

### Plugin Not Showing in GUI

**Possible causes:**
- Files not in correct location
- Apache not restarted after installation
- Syntax errors in plugin files

**Solutions:**
1. Verify files exist: `ls -la ~/local/lib/python3/cmk_addons/plugins/storagegrid/`
2. Check for Python errors: `python3 ~/local/lib/python3/cmk_addons/plugins/storagegrid/rulesets/special_agent.py`
3. Restart Apache: `omd restart apache`
4. Clear browser cache (Ctrl+F5)

### Authentication Errors

**Possible causes:**
- Invalid credentials
- User lacks permissions
- Account locked

**Solutions:**
- Verify credentials work in StorageGRID Grid Manager web UI
- Ensure user has Grid Administrator or Monitor & Topology permissions
- Check for account lockout in StorageGRID

### SSL Certificate Errors

**For self-signed certificates:**
- Enable "Disable SSL certificate verification" in the special agent rule

**For production (recommended):**
- Add StorageGRID CA certificate to system trust store
- Do not disable SSL verification

### No Services Discovered

**Check:**
1. Special agent runs successfully: `cmk -d <hostname>`
2. Host has special agent rule applied: `cmk -D <hostname> | grep storagegrid`
3. Network connectivity to StorageGRID
4. Firewall rules allow HTTPS (port 443)

### Services Show UNKNOWN

**Possible causes:**
- API endpoint not available in your StorageGRID version
- Network timeout
- API permissions issue

**Debug:**
- Check service details for error messages
- Run agent manually to see actual API errors
- Verify StorageGRID version supports API v4

## API Endpoints Used

The plugin queries the following StorageGRID API endpoints:

- `POST /api/v4/authorize` - Authentication
- `GET /api/v4/grid/node-health` - Node health status
- `GET /api/v4/grid/health/topology` - Grid topology (for IP addresses, if available)
- `GET /api/v4/grid/alerts` - Active alerts
- `GET /api/v4/grid/metric-query` - Prometheus metrics
- `GET /api/v4/grid/accounts` - Tenant accounts
- `GET /api/v4/grid/accounts/{id}/usage` - Tenant usage

## Monitored Metrics

### Prometheus Metrics Collected

**Storage Metrics:**
- `storagegrid_storage_utilization_data_bytes`
- `storagegrid_storage_utilization_metadata_bytes`
- `storagegrid_storage_utilization_metadata_allowed_bytes`
- `storagegrid_storage_utilization_usable_space_bytes`
- `storagegrid_storage_utilization_total_space_bytes`

**S3 Metrics:**
- `storagegrid_s3_successful_request_rate`
- `storagegrid_s3_failed_request_rate`

**Node Metrics:**
- `storagegrid_node_cpu_utilization_percentage`

**ILM Metrics:**
- `storagegrid_ilm_scan_period_estimated_minutes`
- `storagegrid_ilm_awaiting_background_objects`

## Node Health States

The plugin monitors node health with the following states:

- **OK (Green)**: `{nodeType} is healthy` - Node connected and operating normally
- **WARN (Yellow)**: `{nodeType} has minor issues` - Node has minor alerts or is administratively down
- **CRIT (Red)**: `{nodeType} state: {state}, severity: {severity}` - Node offline, disconnected, or has critical issues
- **UNKNOWN (Gray)**: `{nodeType} state cannot be determined` - Unable to determine node state

## Security Considerations

### Production Deployment

1. **SSL Certificate Verification**: Always enable in production
   - Add StorageGRID CA to system trust store
   - Never use `--no-cert-check` in production

2. **Credential Management**:
   - Use CheckMK password store
   - Rotate passwords regularly
   - Use dedicated monitoring account with minimal permissions

3. **Network Security**:
   - Restrict API access to monitoring server IPs
   - Use firewall rules
   - Consider dedicated management network

4. **Least Privilege**:
   - Create read-only monitoring user (if your StorageGRID version supports it)
   - Grant only necessary API permissions
   - Avoid using root account if possible

## Performance Tuning

### Check Intervals

Adjust check intervals in **Setup → Services → Service monitoring rules**:

- **Health/Alerts**: 1 minute (default)
- **Capacity**: 5 minutes (recommended for large grids)
- **Performance Metrics**: 1 minute
- **Tenant Usage**: 5-15 minutes (depending on number of tenants)

### Reducing API Load

If monitoring causes high API load:

1. Increase check interval for less critical services
2. Reduce frequency of tenant usage checks for systems with many tenants
3. Increase API timeout if queries are slow

## Uninstallation

```bash
sudo ./UNINSTALL.sh <your_site_name>
```

Then remove:
1. StorageGRID hosts from CheckMK
2. Special agent rule in **Setup → Agents → Other integrations**
3. Activate changes

See [SAFETY.md](SAFETY.md) for detailed rollback options.

## Support and Documentation

### Official Documentation

- **StorageGRID API**: Sign in to Grid Manager → Help → API documentation
- **StorageGRID Docs**: https://docs.netapp.com/us-en/storagegrid/
- **CheckMK Docs**: https://docs.checkmk.com/
- **Plugin API Reference**: [storagegrid-api-documentation.md](storagegrid-api-documentation.md)

### Plugin Documentation

- **[SAFETY.md](SAFETY.md)** - Installation safety and rollback procedures
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes
- **[storagegrid-api-documentation.md](storagegrid-api-documentation.md)** - Complete StorageGRID REST API v4 reference

### Plugin Information

- **CheckMK Version**: 2.4.0p18 or later
- **StorageGRID Versions**: 11.8+, 12.0+
- **API Version**: v4

## Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

- **2.0.0** (2026-01-20) - Complete rebuild for CheckMK 2.4.0 with modern plugin API

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

### Development

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with CheckMK 2.4.0+
5. Submit a pull request

## License

This plugin is released under the MIT License. See the [LICENSE](LICENSE) file for details.

## Disclaimer

This is a community-developed plugin and is not officially supported by NetApp or CheckMK. Use at your own risk.

## Author

Community contribution for NetApp StorageGRID monitoring with CheckMK.
