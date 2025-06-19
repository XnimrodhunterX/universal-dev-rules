# 🤖 Cursor IDE Integration Guide

This guide provides comprehensive instructions for integrating the Universal Development Rules Framework with [Cursor IDE](https://docs.cursor.com/context/rules) using native `.mdc` rule files.

## 🚀 Quick Setup

### 1. Initialize Cursor Rules

```bash
# In your project root
mkdir -p .cursor/rules
cd .cursor/rules

# Copy framework rules
cp -r /path/to/universal-rules/.cursor/rules/* .
```

### 2. Verify Rule Installation

Open Cursor and check:
- `Cursor Settings > Rules` to see all available rules
- Rules should appear with their descriptions and status
- Use `Cmd/Ctrl + Shift + P > "New Cursor Rule"` to create custom rules

## 📋 Rule Types & Usage

### Always Applied Rules
These rules are **automatically included** in every AI interaction:

```mdc
---
description: Core architectural principles
alwaysApply: true
---

Your rule content here...
```

**Available Always Rules:**
- `always/architecture.mdc` - Core architectural principles
- `always/security.mdc` - Essential security standards

### Auto-Attached Rules
These rules **activate automatically** when working with specific file patterns:

```mdc
---
description: API development standards
globs: ["**/api/**", "**/controllers/**"]
alwaysApply: false
---

Your API-specific guidance...
```

**Available Auto-Attached Rules:**
- `auto-attached/api-development.mdc` - API patterns and standards
- `auto-attached/database-operations.mdc` - Database best practices

### Agent-Requested Rules
The AI **decides when to apply** these rules based on context:

```mdc
---
description: Microservices governance patterns
alwaysApply: false
---

Advanced microservices guidance...
```

**Available Agent-Requested Rules:**
- `agent-requested/microservices-governance.mdc` - Microservices patterns

## 🔧 Creating Custom Project Rules

### 1. Using Cursor Command Palette

```bash
# In Cursor
Cmd/Ctrl + Shift + P > "New Cursor Rule"
```

### 2. Custom Rule Template

```mdc
---
description: Project-specific development standards
globs: ["**/src/**", "**/lib/**"]
alwaysApply: false
themes: ["custom_project"]
---

# Your Project Name - Development Standards

## Technology Stack
- Use [Your Framework] for backend development
- Use [Your Frontend] for user interfaces
- Use [Your Database] for data persistence

@project-templates/error-handler.ts
@project-templates/logger-config.ts
```

### 3. Generate Rules from Conversations

```bash
# In Cursor chat, after a detailed conversation
/Generate Cursor Rules
```

## 📁 Recommended Directory Structure

```
.cursor/rules/
├── always/                          # Always applied
│   ├── architecture.mdc            # Core architecture
│   └── security.mdc                # Security standards
├── auto-attached/                   # Pattern-based activation
│   ├── api-development.mdc         # API-specific
│   └── database-operations.mdc     # Database patterns
├── agent-requested/                 # AI-driven activation
│   └── microservices-governance.mdc
└── manual/                          # Explicit invocation
    └── troubleshooting.mdc         # @troubleshooting
```

## 🎯 Rule Effectiveness Tips

### 1. Keep Rules Focused
```mdc
# Good: Specific, actionable guidance
---
description: API error handling patterns
globs: ["**/api/**"]
---

Use RFC 9457 Problem Details format for all API errors:
- Include type, title, status, detail fields
- Provide actionable error messages
```

### 2. Reference Specific Files
```mdc
# Include relevant templates and examples
@project-templates/api-error-schema.json
@intelligent_ide_rules/MI-05-comprehensive-api-standards.md
```

## 📚 Additional Resources

- [Cursor Rules Documentation](https://docs.cursor.com/context/rules)
- [Universal Development Rules Framework](../README.md)
- [MDC Format Specification](https://docs.cursor.com/context/rules#example-mdc-rule)

---

**Next Steps:**
1. Set up your `.cursor/rules` directory
2. Copy framework rules to your project
3. Create custom project-specific rules
4. Test rule effectiveness with your team 