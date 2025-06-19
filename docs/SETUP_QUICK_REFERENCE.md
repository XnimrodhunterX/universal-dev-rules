# 🚀 Quick Reference: setup-cursor-rules.sh

## Basic Usage

```bash
# Install to current directory
./scripts/setup-cursor-rules.sh

# Install to specific project
./scripts/setup-cursor-rules.sh /path/to/project

# Install with spaces in path
./scripts/setup-cursor-rules.sh "/path/to/my project"
```

## What Gets Installed

| Category | Files | Trigger | Description |
|----------|-------|---------|-------------|
| **Always** | 4 | Automatic | Core rules always active |
| **Auto-Attached** | 4 | File patterns | Context-sensitive rules |
| **Agent-Requested** | 1 | AI decision | Advanced governance |
| **Manual** | 1 | `@rule-name` | Custom project rules |

## Common Errors

```bash
# Target doesn't exist
❌ Error: Target project directory does not exist: /path
✅ Solution: mkdir -p /path/to/project

# Framework not found  
❌ Error: Cursor rules not found at /path/.cursor/rules
✅ Solution: Run from framework directory

# Permission denied
❌ Error: Permission denied when creating .cursor/rules/
✅ Solution: Check directory permissions
```

## Verification

```bash
# Check installation
ls -la .cursor/rules/

# Count rules
find .cursor/rules -name "*.mdc" | wc -l

# Should output: 10
```

## Next Steps

1. **Open Cursor IDE** in your project
2. **Check Settings > Rules** to see active rules
3. **Customize** `.cursor/rules/manual/project-standards.mdc`
4. **Use** `@project-standards` in Cursor chat

## Help & Support

- **Full Documentation**: [SETUP_SCRIPT_USAGE.md](SETUP_SCRIPT_USAGE.md)
- **Cursor Integration**: [CURSOR_INTEGRATION.md](CURSOR_INTEGRATION.md)
- **Issues**: [GitHub Issues](https://github.com/XnimrodhunterX/universal-dev-rules/issues) 