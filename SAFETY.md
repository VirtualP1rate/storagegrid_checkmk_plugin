# Safety and Rollback Guide

## Is This Plugin Safe to Install?

**YES** - This plugin is completely safe and reversible. Here's why:

### ✅ No Core Modifications
- All files installed in `/local/` directory only
- No changes to CheckMK core files
- No system-wide configuration changes
- Other CheckMK functionality unaffected

### ✅ Isolated Operation
- Plugin only runs for configured StorageGRID hosts
- Other hosts and services continue normally
- Can be disabled without removing files

### ✅ Easy Removal
- Simple uninstall script provided
- No residual configuration after removal
- Clean rollback possible

---

## Rollback Options (Least to Most Invasive)

### Option 1: Disable Without Removing (Quickest)

**Disable for specific host:**
1. Go to the StorageGRID host in WATO
2. Run service discovery → "Remove vanished services"
3. Activate changes
4. Delete the host if no longer needed

**Result**: Plugin stays installed but inactive for that host

---

### Option 2: Disable Special Agent Rule

**Disable data collection:**
1. Navigate to: Setup → Hosts → Host monitoring rules
2. Search for "NetApp StorageGRID"
3. Delete or disable the rule
4. Run service discovery on affected hosts
5. Activate changes

**Result**: Plugin installed but not collecting data

---

### Option 3: Complete Removal (Use Uninstall Script)

```bash
# Run the uninstall script
sudo ./UNINSTALL.sh mysite

# Restart CheckMK
su - mysite
omd restart
```

**Result**: Plugin completely removed from system

---

## Emergency Rollback (If Something Breaks)

If the plugin causes issues immediately after installation:

### Quick Fix (2 minutes)

```bash
# Stop CheckMK
omd stop

# Remove plugin files
rm -f ~/local/share/check_mk/agents/special/agent_storagegrid
rm -f ~/local/lib/check_mk/base/plugins/agent_based/storagegrid_*.py
rm -f ~/local/share/check_mk/web/plugins/wato/*storagegrid*.py

# Start CheckMK
omd start
```

### Alternative: Restore from Backup

If you create a backup before installation:

```bash
# Before installing, backup the local directory
tar -czf checkmk_local_backup.tar.gz /omd/sites/mysite/local/

# To restore if needed
omd stop
tar -xzf checkmk_local_backup.tar.gz -C /
omd start
```

---

## What Could Go Wrong? (Unlikely Scenarios)

### Scenario 1: Plugin Causes CheckMK Web UI Issues

**Symptoms**: Web UI won't load or shows errors

**Cause**: Syntax error in WATO plugin files

**Fix**:
```bash
# Remove WATO files
rm -f ~/local/share/check_mk/web/plugins/wato/*storagegrid*.py
omd restart
```

### Scenario 2: Service Discovery Hangs

**Symptoms**: Discovery takes too long or times out

**Cause**: StorageGRID API timeout or network issue

**Fix**:
```bash
# Increase timeout in special agent rule (WATO)
# Or remove the special agent rule temporarily
# Or disable SSL verification if certificate issue
```

### Scenario 3: High Load on CheckMK Server

**Symptoms**: CPU spike during checks

**Cause**: Too many API calls or large tenant count

**Fix**:
- Increase check intervals for services
- Disable individual alert detail services
- Reduce tenant monitoring frequency

---

## Testing Strategy (Recommended)

### Test Before Production

1. **Install on Test Site First**
   ```bash
   # Create test site
   omd create test_site
   
   # Install plugin on test site
   sudo ./INSTALL.sh test_site
   ```

2. **Add One Test Host**
   - Configure minimal StorageGRID host
   - Run service discovery
   - Monitor for 24 hours

3. **Verify No Issues**
   - Check CheckMK logs: `~/var/log/web.log`
   - Monitor system resources
   - Test service outputs

4. **Then Deploy to Production**

### Gradual Rollout

1. Install plugin (doesn't activate automatically)
2. Create special agent rule for one host only
3. Monitor for issues
4. Expand to more hosts if successful

---

## Pre-Installation Checklist

Before installing, verify:

- [ ] CheckMK site is running: `omd status`
- [ ] You have root access for installation
- [ ] You can access StorageGRID API
- [ ] You have valid credentials
- [ ] (Optional) Backup created: `tar -czf backup.tar.gz ~/local/`

---

## Post-Installation Verification

After installing, check:

- [ ] CheckMK site still running: `omd status`
- [ ] Web UI accessible
- [ ] Other hosts/services still working
- [ ] Agent script executable: `ls -l ~/local/share/check_mk/agents/special/`
- [ ] No errors in logs: `tail -f ~/var/log/web.log`

---

## Support and Troubleshooting

### Check Logs

```bash
# Web UI errors
tail -f ~/var/log/web.log

# CheckMK core errors
tail -f ~/var/log/cmc.log

# Apache errors (if web UI broken)
tail -f ~/var/log/apache/error_log
```

### Manual Test

```bash
# Test special agent manually
~/local/lib/python3/cmk_addons/plugins/storagegrid/libexec/agent_storagegrid \
  --hostname your-storagegrid-host \
  --username root \
  --password 'your-password' \
  --no-cert-check

# Should output JSON sections, not errors
```

### Get Help

1. Review README.md troubleshooting section
2. Check CheckMK logs for specific errors
3. Run manual agent test to isolate issue
4. Use uninstall script if unrecoverable

---

## Key Takeaway

**This plugin is completely safe and reversible.** 

- Worst case: Remove files and restart CheckMK
- Best practice: Test on non-production site first
- Rollback time: < 5 minutes with uninstall script

You have full control and can remove it anytime without affecting your CheckMK installation.
