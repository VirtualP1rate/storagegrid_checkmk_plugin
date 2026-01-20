# Changelog

All notable changes to the StorageGRID CheckMK Plugin will be documented in this file.

## [2.0.0] - 2026-01-20

### Added
- Complete rebuild for CheckMK 2.4.0 Plugin API
- New `cmk_addons` plugin structure
- Agent-based v2 API implementation
- Ruleset v1 API for web UI configuration
- Server-side calls v1 API for agent invocation
- Split data and metadata capacity monitoring for independent alerting
- Object count tracking for tenant usage
- Comprehensive monitoring capabilities:
  - Node health monitoring (Admin, Storage, Gateway nodes)
  - Site health aggregation across multiple sites
  - Data capacity monitoring with configurable thresholds
  - Metadata capacity monitoring with separate alerting
  - Active alerts tracking by severity (critical, major, minor)
  - S3 performance metrics (request rates, error rates)
  - Node resource monitoring (CPU utilization)
  - Tenant storage quota and object count tracking
  - ILM (Information Lifecycle Management) metrics
- Web UI configuration interface in CheckMK
- SSL certificate verification support
- Configurable API timeouts
- Automated installation and uninstall scripts
- Comprehensive documentation suite

### Changed
- Updated to StorageGRID API v4.2
- Removed IP address display (not consistently available in API)
- Improved error handling and reporting
- Enhanced metric collection reliability

### Documentation
- Complete installation guide with examples
- API reference documentation
- Safety and rollback procedures
- Troubleshooting guide
- Security best practices

### Supported Versions
- CheckMK Raw Edition 2.4.0p18 or later
- NetApp StorageGRID 11.8+
- NetApp StorageGRID 12.0+
- StorageGRID REST API v4

### Requirements
- Python 3 with `requests` library
- Grid administrator credentials with read access
- Network access to StorageGRID management interface

### Security
- No hardcoded credentials, IPs, or hostnames
- All configuration via CheckMK web interface
- Support for SSL certificate verification
- Password storage in CheckMK password store
