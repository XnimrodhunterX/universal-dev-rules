#!/bin/bash

# Fix Cursor Rule References Script
# Fixes @intelligent_ide_rules/ references to match actual copied file locations

echo "🔧 Fixing Cursor rule references..."

# Find all .mdc files in .cursor/rules and fix the references
find .cursor/rules -name "*.mdc" -type f | while read -r file; do
    if grep -q "@intelligent_ide_rules/" "$file"; then
        echo "   Fixing references in: $file"
        # Remove the @intelligent_ide_rules/ prefix from references
        sed -i '' 's/@intelligent_ide_rules\///g' "$file"
    fi
done

echo "✅ All Cursor rule references fixed!"
echo ""
echo "📋 What was fixed:"
echo "   Changed: @intelligent_ide_rules/DP-01-database-design.md"
echo "   To:      DP-01-database-design.md"
echo ""
echo "   Changed: @intelligent_ide_rules/security/SEC-01-credential-hygiene.md"
echo "   To:      security/SEC-01-credential-hygiene.md"
echo ""
echo "🎯 This ensures Cursor can find the referenced files after they're copied by setup-cursor-rules.sh" 