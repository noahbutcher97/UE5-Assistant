# UE5 AI Assistant - Automation Suite

Comprehensive automation suite for project cleanup and standard operations.

## 📁 Structure

```
automation/
├── cleanup/                    # Cleanup automation
│   ├── cleanup_rules.py       # Cleanup rules and patterns
│   ├── file_scanner.py        # File scanning and analysis
│   └── project_cleaner.py     # Main cleanup orchestrator
├── standard_ops/               # Standard operations
│   ├── ops_manager.py         # Operations manager
│   ├── deployment.py          # Deployment operations
│   ├── testing.py             # Testing operations
│   └── maintenance.py         # Maintenance operations
├── utils/                      # Utility functions
│   ├── logger.py              # Centralized logging
│   └── file_utils.py          # File utilities
├── logs/                       # Automation logs (auto-created)
├── run_automation.py          # CLI tool
└── README.md                  # This file
```

## 🚀 Quick Start

### Analyze Project for Cleanup

```bash
python automation/run_automation.py cleanup --analyze
```

### Run Automatic Cleanup (Dry Run)

```bash
python automation/run_automation.py cleanup --auto
```

### Run Automatic Cleanup (Execute)

```bash
python automation/run_automation.py cleanup --auto --force
```

### Clean Attached Assets

```bash
python automation/run_automation.py cleanup --attached-assets --force
```

### Run Tests

```bash
python automation/run_automation.py ops test
```

### Health Check

```bash
python automation/run_automation.py ops health_check
```

### List All Operations

```bash
python automation/run_automation.py list
```

## 🧹 Cleanup Operations

### Cleanup Categories

The cleanup system identifies and categorizes files:

1. **Temporary Files**
   - Pasted logs (`Pasted-*.txt`)
   - Temporary files (`*.tmp`, `*.log.old`)
   - Safe auto-delete: ❌ (requires review)

2. **Build Artifacts**
   - Python cache (`*.pyc`, `__pycache__`)
   - Test cache (`.pytest_cache`)
   - OS cache (`.DS_Store`, `Thumbs.db`)
   - Safe auto-delete: ✅

3. **Backup Files**
   - Editor backups (`*.bak`, `*~`, `*.swp`)
   - Safe auto-delete: ✅

4. **Archive Files**
   - Old documentation (`*_SUMMARY.md`)
   - Archived items in `archive/` directory
   - Safe auto-delete: ❌ (requires review)

### Protected Paths

These paths are never deleted:
- `.git` - Version control
- `.pythonlibs` - External dependencies
- `venv`, `.venv` - Virtual environments
- `requirements.txt` - Dependencies
- `main.py` - Entry point
- `README.md` - Documentation

### Cleanup Analysis Report

Run analysis to get detailed report:

```bash
python automation/run_automation.py cleanup --analyze
```

**Report includes:**
- Files categorized by type
- Duplicate files detection
- Large files (>5MB)
- Empty directories
- Old files (>90 days)
- Total space to be cleaned

### Safe Auto-Delete

These categories are safe for automatic deletion:
- Python cache files
- Test cache files
- OS cache files
- Editor backup files
- Build artifacts

```bash
# Dry run (preview)
python automation/run_automation.py cleanup --auto

# Execute
python automation/run_automation.py cleanup --auto --force
```

## 🔧 Standard Operations

### Testing Operations

**Run All Tests:**
```bash
python automation/run_automation.py ops test
```

**Run Unit Tests Only:**
```bash
python automation/run_automation.py ops test_unit
```

**Run Integration Tests Only:**
```bash
python automation/run_automation.py ops test_integration
```

### Deployment Operations

**Prepare Deployment:**
```bash
python automation/run_automation.py ops deploy_prepare
```

**Validate Deployment:**
```bash
python automation/run_automation.py ops deploy_validate
```

### Maintenance Operations

**Health Check:**
```bash
python automation/run_automation.py ops health_check
```

Checks:
- ✅ Project structure integrity
- ✅ Dependencies health
- ✅ Configuration validity
- ✅ API endpoints
- ✅ UE5 client modules

**Validate Project Structure:**
```bash
python automation/run_automation.py ops validate_structure
```

**Update Dependencies:**
```bash
# Dry run (check outdated)
python automation/run_automation.py ops update_dependencies

# Execute update
python automation/run_automation.py ops update_dependencies --force
```

## 📊 Logs

All automation operations are logged:

- **Cleanup logs:** `automation/logs/cleanup_YYYYMMDD_HHMMSS.json`
- **Operations logs:** `automation/logs/ops_YYYYMMDD_HHMMSS.json`
- **Daily logs:** `automation/logs/automation_YYYYMMDD.log`

## 🔌 Programmatic Usage

### Python API

```python
from automation.cleanup.project_cleaner import ProjectCleaner
from automation.standard_ops.ops_manager import OpsManager

# Cleanup
cleaner = ProjectCleaner(dry_run=True)
report = cleaner.analyze_project()
result = cleaner.auto_cleanup(force=True)

# Operations
manager = OpsManager()
result = manager.run_operation('health_check')
ops_list = manager.get_available_operations()
```

### Cleanup Rules

```python
from automation.cleanup.cleanup_rules import CleanupRules, FileCategory

# Get all rules
rules = CleanupRules.get_all_rules()

# Get safe auto-delete rules
safe_rules = CleanupRules.get_safe_auto_delete_rules()

# Check if path is protected
is_protected = CleanupRules.is_protected_path(some_path)

# Categorize file
category_info = CleanupRules.categorize_file(file_path)
```

### File Scanner

```python
from automation.cleanup.file_scanner import FileScanner

scanner = FileScanner()

# Scan project
categorized = scanner.scan_project()

# Find duplicates
duplicates = scanner.find_duplicates()

# Find large files
large_files = scanner.find_large_files(min_size_mb=10)

# Find empty directories
empty_dirs = scanner.find_empty_directories()

# Find old files
old_files = scanner.find_old_files(days=90)
```

## 🎯 Best Practices

### Regular Maintenance

1. **Weekly:** Run cleanup analysis
   ```bash
   python automation/run_automation.py cleanup --analyze
   ```

2. **Monthly:** Clean attached assets
   ```bash
   python automation/run_automation.py cleanup --attached-assets --force
   ```

3. **Before Deployment:** Run health check
   ```bash
   python automation/run_automation.py ops health_check
   python automation/run_automation.py ops deploy_validate
   ```

4. **After Major Changes:** Validate structure
   ```bash
   python automation/run_automation.py ops validate_structure
   ```

### Safe Workflow

1. Always run in dry-run mode first
2. Review the analysis report
3. Execute cleanup with `--force` flag
4. Check logs for any issues
5. Run health check after cleanup

### Integration with Development

Add to your workflow:

```bash
# Pre-commit hook
python automation/run_automation.py ops validate_structure

# CI/CD pipeline
python automation/run_automation.py ops test
python automation/run_automation.py ops deploy_validate

# Automated cleanup (cron job)
python automation/run_automation.py cleanup --auto --force
```

## 🔍 Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Ensure you're in project root
cd /path/to/project
python automation/run_automation.py --help
```

**Permission Errors:**
- Check file permissions
- Run with appropriate privileges
- Verify protected paths

**Cleanup Not Working:**
- Verify dry-run mode is disabled with `--force`
- Check cleanup logs for errors
- Ensure paths are not protected

## 📈 Future Enhancements

Planned features:
- [ ] Automated duplicate file resolution
- [ ] Configurable cleanup schedules
- [ ] Integration with CI/CD
- [ ] Performance optimization for large projects
- [ ] Advanced file similarity detection
- [ ] Custom cleanup rules via config file

## 🤝 Contributing

To add new cleanup rules:

1. Edit `automation/cleanup/cleanup_rules.py`
2. Add new `CleanupRule` to `get_all_rules()`
3. Test with dry-run mode
4. Update documentation

To add new operations:

1. Add method to appropriate ops class
2. Register in `OpsManager.run_operation()`
3. Add to `get_available_operations()`
4. Update CLI commands in `run_automation.py`

## 📝 License

Part of UE5 AI Assistant project.
