# 📖 setup-cursor-rules.sh Usage Guide

Complete reference for the Universal Development Rules Cursor IDE setup script.

## 📋 Quick Reference

```bash
./scripts/setup-cursor-rules.sh [target-directory]
```

## 🎯 Synopsis

The `setup-cursor-rules.sh` script automatically installs Universal Development Rules into your project's Cursor IDE configuration. It copies rule files, creates directory structures, and sets up project-specific templates.

## 📝 Parameters

### Positional Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `target-directory` | No | Current directory (`pwd`) | Path to the project where rules should be installed |

### Examples

```bash
# Install to current directory
./scripts/setup-cursor-rules.sh

# Install to current directory (explicit)
./scripts/setup-cursor-rules.sh .

# Install to specific project
./scripts/setup-cursor-rules.sh /path/to/my-project

# Install to relative path
./scripts/setup-cursor-rules.sh ../my-other-project

# Install with spaces in path (use quotes)
./scripts/setup-cursor-rules.sh "/path/to/my project with spaces"
```

## 🚀 Behavior & Features

### Automatic Framework Detection

The script automatically detects the Universal Development Rules framework location using multiple strategies:

1. **Primary**: Relative to script location (`../` from script directory)
2. **Fallback locations** (searched in order):
   - `$SCRIPT_DIR/.cursor/rules`
   - `$PWD/.cursor/rules`
   - `$(dirname "$SCRIPT_DIR")/.cursor/rules`
   - `$HOME/.cursor/universal-dev-rules`

### Directory Structure Creation

Creates the following structure in your project:

```
your-project/
└── .cursor/
    └── rules/
        ├── always/           # Core rules (always applied)
        ├── auto-attached/    # Context-sensitive rules
        ├── agent-requested/  # AI-driven rules
        └── manual/          # Manually invoked rules
```

### Rule Categories Installed

| Category | Count | Trigger | Description |
|----------|-------|---------|-------------|
| **Always** | 4 | Automatic | Core architecture, security, documentation, project management |
| **Auto-Attached** | 4 | File patterns | API development, database ops, frontend, testing |
| **Agent-Requested** | 1 | AI decision | Advanced microservices governance |
| **Manual** | 1 | `@rule-name` | Project-specific customizable template |

## 🛠️ Script Operations

### 1. Validation Phase
- ✅ Verifies framework rules exist
- ✅ Validates target directory exists
- ✅ Checks write permissions

### 2. Installation Phase
- 📁 Creates `.cursor/rules/` directory structure
- 📋 Copies all rule files from framework
- 🔧 Creates project-specific rule template
- 📝 Updates `.gitignore` (optional entry)

### 3. Reporting Phase
- 📊 Counts installed rules
- 📋 Lists what was installed
- 🚀 Provides next steps
- 🔧 Includes troubleshooting tips

## 📂 File Operations

### Files Created

```bash
# Rule files (10 total)
.cursor/rules/always/architecture.mdc
.cursor/rules/always/security.mdc
.cursor/rules/always/documentation.mdc
.cursor/rules/always/project-management.mdc
.cursor/rules/auto-attached/api-development.mdc
.cursor/rules/auto-attached/database-operations.mdc
.cursor/rules/auto-attached/frontend-components.mdc
.cursor/rules/auto-attached/testing-patterns.mdc
.cursor/rules/agent-requested/microservices-governance.mdc
.cursor/rules/manual/project-standards.mdc

# Optional .gitignore entry
# .cursor/rules/ (commented by default)
```

### File Permissions

- **Directories**: `755` (rwxr-xr-x)
- **Rule files**: `644` (rw-r--r--)
- **Preserves**: Existing file permissions

## ⚠️ Error Handling

### Common Errors & Solutions

#### Framework Not Found
```bash
❌ Error: Cursor rules not found at /path/to/framework/.cursor/rules
```

**Solutions:**
1. Ensure you're running from the framework directory
2. Check that `.cursor/rules/` exists in framework
3. Re-download/clone the framework

#### Target Directory Not Found
```bash
❌ Error: Target project directory does not exist: /path/to/project
```

**Solutions:**
1. Create the target directory first: `mkdir -p /path/to/project`
2. Check path spelling and permissions
3. Use absolute paths to avoid confusion

#### Permission Denied
```bash
❌ Error: Permission denied when creating .cursor/rules/
```

**Solutions:**
1. Check write permissions: `ls -la /path/to/project`
2. Run with appropriate permissions
3. Ensure you own the target directory

### Exit Codes

| Code | Meaning | Cause |
|------|---------|-------|
| `0` | Success | Installation completed successfully |
| `1` | Error | Framework not found, target invalid, or permission denied |

## 🔧 Advanced Usage

### Environment Variables

The script uses these environment variables if available:

```bash
# Override framework detection
export CURSOR_RULES_FRAMEWORK="/custom/path/to/framework"

# Override home directory fallback
export HOME="/custom/home"
```

### Integration with CI/CD

```bash
# In CI/CD pipeline
#!/bin/bash
set -e

# Clone framework
git clone https://github.com/XnimrodhunterX/universal-dev-rules.git
cd universal-dev-rules

# Install rules to project
./scripts/setup-cursor-rules.sh "$GITHUB_WORKSPACE"

# Verify installation
if [ -d "$GITHUB_WORKSPACE/.cursor/rules" ]; then
    echo "✅ Cursor rules installed successfully"
else
    echo "❌ Cursor rules installation failed"
    exit 1
fi
```

### Docker Integration

```dockerfile
# Dockerfile
FROM node:18-alpine

# Install Universal Development Rules
RUN git clone https://github.com/XnimrodhunterX/universal-dev-rules.git /tmp/rules
RUN /tmp/rules/scripts/setup-cursor-rules.sh /workspace
RUN rm -rf /tmp/rules

WORKDIR /workspace
```

## 🧪 Testing & Verification

### Verify Installation

```bash
# Check rule files exist
ls -la .cursor/rules/

# Count installed rules
find .cursor/rules -name "*.mdc" | wc -l

# Test project-specific rule
grep -A 5 "Technology Stack" .cursor/rules/manual/project-standards.mdc
```

### Test Script Without Installation

```bash
# Dry run (read-only check)
./scripts/setup-cursor-rules.sh /tmp/nonexistent-dir
# Will show error without modifying anything
```

## 📚 Related Documentation

- **[Cursor Integration Guide](CURSOR_INTEGRATION.md)** - Complete Cursor setup
- **[Contributing Guide](../CONTRIBUTING.md)** - Development workflow
- **[Rule Library](../intelligent_ide_rules/)** - All available rules
- **[Templates](../templates/)** - Configuration templates

## 🆘 Troubleshooting

### Rules Don't Appear in Cursor

1. **Restart Cursor IDE** completely
2. **Check Cursor Settings > Rules** for rule status
3. **Verify file permissions** on `.cursor/rules/`
4. **Check rule syntax** with `cursor --validate-rules`

### Performance Issues

1. **Too many rules**: Disable unused categories
2. **Large projects**: Use `.cursorignore` to exclude files
3. **Slow startup**: Check rule complexity and file patterns

### Rule Conflicts

1. **Duplicate rules**: Check for overlapping file patterns
2. **Conflicting advice**: Prioritize rules by category order
3. **Custom rules**: Ensure they don't override framework rules

## 🔄 Updates & Maintenance

### Updating Rules

```bash
# Update framework
git pull origin main

# Reinstall rules (overwrites existing)
./scripts/setup-cursor-rules.sh /path/to/project

# Preserve custom project-standards.mdc
cp .cursor/rules/manual/project-standards.mdc .cursor/rules/manual/project-standards.mdc.backup
./scripts/setup-cursor-rules.sh .
cp .cursor/rules/manual/project-standards.mdc.backup .cursor/rules/manual/project-standards.mdc
```

### Uninstalling Rules

```bash
# Remove all rules
rm -rf .cursor/rules/

# Remove specific category
rm -rf .cursor/rules/auto-attached/

# Remove from .gitignore
sed -i '/\.cursor\/rules/d' .gitignore
```

---

## 📊 Script Specifications

- **Language**: Bash (POSIX compatible)
- **Dependencies**: None (uses standard Unix tools)
- **Platforms**: macOS, Linux, WSL
- **Size**: ~6KB
- **Execution time**: ~1-3 seconds
- **Memory usage**: Minimal (<1MB)

---

**For support, see [GitHub Issues](https://github.com/XnimrodhunterX/universal-dev-rules/issues) or [Discussions](https://github.com/XnimrodhunterX/universal-dev-rules/discussions)** 