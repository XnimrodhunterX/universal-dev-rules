#!/bin/bash

# Universal Development Rules - Cursor Setup Script
# This script sets up Cursor rules in your project

set -e

PROJECT_DIR="${1:-$(pwd)}"

# Auto-detect the framework location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRAMEWORK_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RULES_SOURCE_DIR="$FRAMEWORK_ROOT/.cursor/rules"

echo "🚀 Setting up Universal Development Rules for Cursor IDE..."
echo "Framework location: $FRAMEWORK_ROOT"
echo "Target project: $PROJECT_DIR"

# Validate framework structure
if [ ! -d "$RULES_SOURCE_DIR" ]; then
    echo "❌ Error: Cursor rules not found at $RULES_SOURCE_DIR"
    echo ""
    echo "🔍 Searching for rules in common locations..."
    
    # Try alternative locations
    ALT_LOCATIONS=(
        "$SCRIPT_DIR/.cursor/rules"
        "$PWD/.cursor/rules"
        "$(dirname "$SCRIPT_DIR")/.cursor/rules"
        "$HOME/.cursor/universal-dev-rules"
    )
    
    for location in "${ALT_LOCATIONS[@]}"; do
        if [ -d "$location" ]; then
            echo "✅ Found rules at: $location"
            RULES_SOURCE_DIR="$location"
            break
        fi
    done
    
    if [ ! -d "$RULES_SOURCE_DIR" ]; then
        echo ""
        echo "❌ Could not locate Universal Development Rules framework."
        echo ""
        echo "📋 Please ensure you have:"
        echo "   1. Downloaded/cloned the Universal Development Rules framework"
        echo "   2. Are running this script from the framework directory"
        echo "   3. The .cursor/rules directory exists in the framework"
        echo ""
        echo "💡 Try:"
        echo "   cd /path/to/universal-dev-rules-v2.1"
        echo "   ./scripts/setup-cursor-rules.sh /path/to/your/project"
        echo ""
        exit 1
    fi
fi

# Validate target project directory
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Error: Target project directory does not exist: $PROJECT_DIR"
    echo ""
    echo "💡 Usage: $0 [target-project-directory]"
    echo "   Example: $0 /path/to/your/project"
    echo "   Example: $0 (uses current directory)"
    echo ""
    exit 1
fi

# Create Cursor rules directory structure
echo "📁 Creating .cursor/rules directory structure..."
mkdir -p "$PROJECT_DIR/.cursor/rules/always"
mkdir -p "$PROJECT_DIR/.cursor/rules/auto-attached"
mkdir -p "$PROJECT_DIR/.cursor/rules/agent-requested"
mkdir -p "$PROJECT_DIR/.cursor/rules/manual"

# Copy framework rules
echo "📋 Copying framework rules..."
echo "   Source: $RULES_SOURCE_DIR"
echo "   Target: $PROJECT_DIR/.cursor/rules/"

if [ -d "$RULES_SOURCE_DIR" ]; then
    # Copy all rule categories
    for category in always auto-attached agent-requested manual; do
        if [ -d "$RULES_SOURCE_DIR/$category" ]; then
            cp -r "$RULES_SOURCE_DIR/$category"/* "$PROJECT_DIR/.cursor/rules/$category/" 2>/dev/null || true
            echo "   ✅ Copied $category rules"
        fi
    done
    echo "✅ Framework rules copied successfully!"
else
    echo "❌ Framework rules not found at $RULES_SOURCE_DIR"
    exit 1
fi

# Fix path references in copied rules
echo "🔧 Fixing rule path references..."
find "$PROJECT_DIR/.cursor/rules" -name "*.mdc" -type f -exec sed -i '' 's/@intelligent_ide_rules\///g' {} \; 2>/dev/null || true
echo "   ✅ Fixed @intelligent_ide_rules/ references to match copied file locations"

# Ensure project-specific rule exists (create if missing)
PROJECT_RULE_FILE="$PROJECT_DIR/.cursor/rules/manual/project-standards.mdc"
if [ ! -f "$PROJECT_RULE_FILE" ]; then
    echo "🔧 Creating project-specific rule template..."
    cat > "$PROJECT_RULE_FILE" << 'EOF'
---
description: Project-specific development standards
alwaysApply: false
---

# Project Development Standards

Customize this rule for your specific project needs:

## Technology Stack
- Backend: [Your backend framework - e.g., FastAPI, Spring Boot, Express]
- Frontend: [Your frontend framework - e.g., React, Vue, Angular]
- Database: [Your database - e.g., PostgreSQL, MongoDB, MySQL]
- Infrastructure: [Your infrastructure - e.g., AWS, GCP, Azure]

## Project-Specific Patterns
- [Add your specific error handling patterns]
- [Add your naming conventions]
- [Add your logging standards]
- [Add your testing approaches]

## File Organization
- [Describe your project structure]
- [Add your module organization]
- [Add your import patterns]
- [Add your component organization]

## Code Style & Standards
- [Add your linting rules]
- [Add your formatting standards]
- [Add your comment guidelines]
- [Add your documentation requirements]

## Deployment & Operations
- [Add your deployment process]
- [Add your monitoring requirements]
- [Add your alerting standards]
- [Add your backup procedures]

## Team Conventions
- [Add your branch naming]
- [Add your commit message format]
- [Add your PR/MR process]
- [Add your code review guidelines]

Usage: Type @project-standards in Cursor chat to invoke this rule.
EOF
    echo "✅ Created project-specific rule template"
else
    echo "ℹ️  Project-specific rule already exists, skipping creation"
fi

# Create .gitignore entry if it doesn't exist
if [ -f "$PROJECT_DIR/.gitignore" ]; then
    if ! grep -q ".cursor/rules" "$PROJECT_DIR/.gitignore"; then
        echo "" >> "$PROJECT_DIR/.gitignore"
        echo "# Cursor IDE rules (optional - include if you want to version control them)" >> "$PROJECT_DIR/.gitignore"
        echo "# .cursor/rules/" >> "$PROJECT_DIR/.gitignore"
        echo "📝 Added .cursor/rules to .gitignore (commented out - uncomment if you don't want to version control rules)"
    fi
fi

# Count installed rules
RULE_COUNT=$(find "$PROJECT_DIR/.cursor/rules" -name "*.mdc" | wc -l | tr -d ' ')

echo ""
echo "🎉 Cursor rules setup complete!"
echo ""
echo "📊 Installation Summary:"
echo "   📁 Framework location: $FRAMEWORK_ROOT"
echo "   🎯 Target project: $PROJECT_DIR"
echo "   📋 Rules installed: $RULE_COUNT files"
echo ""
echo "📋 What's been set up:"
echo "   ✅ Core architecture rules (always applied)"
echo "   ✅ Security standards (always applied)"
echo "   ✅ Documentation standards (always applied)"
echo "   ✅ Project management practices (always applied)"
echo "   ✅ API development patterns (auto-attached)"
echo "   ✅ Database operation patterns (auto-attached)"
echo "   ✅ Testing strategies (auto-attached)"
echo "   ✅ Frontend component patterns (auto-attached)"
echo "   ✅ Microservices governance (agent-requested)"
echo "   ✅ Project-specific rule template (manual)"
echo ""
echo "🚀 Next steps:"
echo "   1. Open your project in Cursor IDE"
echo "   2. Go to Cursor Settings > Rules to see all available rules"
echo "   3. Customize the project-specific rule in .cursor/rules/manual/project-standards.mdc"
echo "   4. Use @project-standards in Cursor chat to invoke your custom rule"
echo "   5. Use Cmd/Ctrl + Shift + P > 'New Cursor Rule' to create additional rules"
echo ""
echo "📚 Documentation:"
echo "   - Cursor Rules: https://docs.cursor.com/context/rules"
echo "   - Framework Guide: $FRAMEWORK_ROOT/docs/CURSOR_INTEGRATION.md"
echo "   - Full Rule Library: $FRAMEWORK_ROOT/intelligent_ide_rules/"
echo ""
echo "🔧 Troubleshooting:"
echo "   - If rules don't appear in Cursor, restart the IDE"
echo "   - Check Cursor Settings > Rules for rule status"
echo "   - Verify file permissions on .cursor/rules/ directory"
echo ""
echo "Happy coding with intelligent assistance! 🤖✨" 