# Contributing to Universal Development Rules

## 🤝 Welcome Contributors!

Thank you for your interest in improving the Universal Development Rules Framework! This guide will help you contribute effectively to our [GitHub repository](https://github.com/XnimrodhunterX/universal-dev-rules).

## 🔄 Development Workflow

### Branch Strategy
- **`main`**: Production releases (v2.1, v2.2, v2.3...)
- **`universal-dev-rules-v2.x`**: Development branches for next version
- **`feature/rule-name`**: Feature development branches
- **`bugfix/issue-description`**: Bug fix branches

### Getting Started
1. **Fork** the repository on GitHub: [https://github.com/XnimrodhunterX/universal-dev-rules](https://github.com/XnimrodhunterX/universal-dev-rules)
2. **Clone** your fork locally
   ```bash
   git clone https://github.com/YOUR_USERNAME/universal-dev-rules.git
   cd universal-dev-rules
   ```
3. **Add** the upstream remote
   ```bash
   git remote add upstream https://github.com/XnimrodhunterX/universal-dev-rules.git
   ```

### Making Changes
1. **Check** the current development branch
   ```bash
   git fetch upstream
   git checkout upstream/universal-dev-rules-v2.2  # or latest dev branch
   ```
2. **Create** your feature branch
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make** your changes with proper testing
4. **Commit** with conventional commit format
   ```bash
   git commit -m "feat(rules): add new security rule for API authentication"
   ```

### Submitting Changes
1. **Push** to your fork
   ```bash
   git push origin feature/your-feature-name
   ```
2. **Create** a Pull Request to the **next development branch**
   - Target: `universal-dev-rules-v2.x` (not main)
   - Include: Description, testing, documentation updates
   - Use our [PR template](https://github.com/XnimrodhunterX/universal-dev-rules/blob/main/.github/pull_request_template.md)

## 📋 **Table of Contents**

- [Getting Started](#getting-started)
- [Rule Structure & Standards](#rule-structure--standards)
- [Contribution Types](#contribution-types)
- [Review Process](#review-process)
- [AI Assistant Integration](#ai-assistant-integration)
- [Testing & Validation](#testing--validation)

---

## 🚀 **Getting Started**

### Prerequisites
- Understanding of software development best practices
- Familiarity with markdown formatting
- Experience with the specific technology domain (if contributing domain-specific rules)

### Setup
1. Fork this repository
2. Clone your fork locally
3. Install the rule testing framework: `pip install -r scripts/requirements.txt`
4. Run existing tests: `python scripts/rule_test_runner.py`

---

## 📐 **Rule Structure & Standards**

### Rule File Format
All rules must follow this exact structure:

```markdown
---
description: "Brief description of the rule (1-2 lines)"
globs: ["**/*"]
alwaysApply: true
---

# 🔧 Rule Title

## 1. Section Title

### Core Requirements
- **MUST** do X (RFC 2119 keywords required)
- **SHOULD** do Y
- **MAY** do Z (optional)

### Implementation Example
```typescript
// Real, working code examples required
export class ExampleImplementation {
  // ...
}
```

### Tooling Requirements
- **Tool Name** for specific purpose
- **Alternative Tool** for same purpose

---

## 🛠️ **Enforcement & Tooling**

### Required CI Checks
- [ ] Specific check with command
- [ ] Another check

### Quality Gates
```yaml
quality_gates:
  metric_name:
    description: "What this measures"
    threshold: 95
    blocking: true
```

---

## 📋 **Implementation Checklist**
- [ ] Specific implementation task
- [ ] Another task

---

## 🎯 **Success Metrics**
- **Metric Name:** Target value and description
```

### Rule Naming Convention
- Format: `##X-descriptive-name.md`
- `##` = Two-digit rule number (01, 02, etc.)
- `X` = Sub-rule letter (A, B, C)
- Use kebab-case for descriptive names

### Rule Categories (by Number Range)
- **01-03**: Foundation (Architecture, Service Design, Security)
- **04-06**: Core Development (Database, Config, APIs)
- **07-09**: Quality & Deployment (Testing, Observability, CI/CD)
- **10-12**: Infrastructure (IaC, Platforms, Performance)
- **13-22**: Specialized (Domain-specific, Advanced)

---

## 🔄 **Contribution Types**

### 1. New Rule Submission

**When to create a new rule:**
- Addresses a gap in current coverage
- Represents a distinct, enforceable standard
- Applies to multiple teams/projects
- Has measurable success criteria

**Process:**
1. Check existing rules for overlap
2. Propose rule outline in GitHub Discussion
3. Get community feedback
4. Submit pull request with complete rule

### 2. Rule Enhancement

**Types of enhancements:**
- Adding new sections or requirements
- Improving code examples
- Adding tool recommendations
- Updating for new technology versions
- Enhancing enforcement mechanisms

**Process:**
1. Identify specific improvement
2. Ensure backward compatibility
3. Update related templates if needed
4. Submit pull request with detailed explanation

### 3. Template Contributions

**Template requirements:**
- Must be referenced by at least one rule
- Include comprehensive examples
- Provide validation schemas where applicable
- Include documentation/comments

**Process:**
1. Create template in `templates/` directory
2. Reference from relevant rule(s)
3. Add validation to rule testing framework
4. Submit pull request

### 4. Tooling Improvements

**Types of tooling contributions:**
- Rule testing framework enhancements
- New validation checks
- CI/CD integrations
- Monitoring/metrics improvements

---

## 👥 **Review Process**

### Review Criteria

**Technical Quality:**
- [ ] Follows rule structure standards
- [ ] Includes working code examples
- [ ] Has enforceable requirements (MUST/SHOULD/MAY)
- [ ] Provides specific tooling recommendations
- [ ] Includes measurable success criteria

**Content Quality:**
- [ ] Addresses real development challenges
- [ ] Avoids overlap with existing rules
- [ ] Provides clear implementation guidance
- [ ] Includes comprehensive examples
- [ ] Has proper enforcement mechanisms

**Documentation Quality:**
- [ ] Clear, unambiguous language
- [ ] Proper markdown formatting
- [ ] Consistent with project style
- [ ] Includes all required sections
- [ ] Has proper rule metadata

### Review Roles

**Subject Matter Experts (SMEs):**
- Review domain-specific accuracy
- Validate technical implementations
- Ensure best practices alignment

**Rule Maintainers:**
- Ensure structural compliance
- Check for overlap/conflicts
- Validate enforcement mechanisms
- Approve final integration

**Community Reviewers:**
- Provide usability feedback
- Test implementation examples
- Suggest improvements

### Approval Requirements
- ✅ At least 2 SME approvals for domain accuracy
- ✅ 1 Rule Maintainer approval for structure
- ✅ All automated tests passing
- ✅ No blocking feedback unresolved

---

## 🤖 **AI Assistant Integration**

### Cursor-Specific Enhancements

**Rule Anchors:**
Add Cursor-friendly anchors for quick navigation:
```markdown
<!-- CURSOR: highlight: api:design -->
<!-- CURSOR: highlight: testing:strategy -->
<!-- CURSOR: highlight: security:auth -->
```

**Context Tags:**
Include context hints for AI assistants:
```markdown
<!-- CURSOR: context: microservices, rest-api, nodejs -->
<!-- CURSOR: complexity: intermediate -->
<!-- CURSOR: priority: high -->
```

**Code Snippets:**
Mark reusable code snippets:
```markdown
<!-- CURSOR: snippet: error-handler -->
```typescript
export class ErrorHandler {
  // Reusable implementation
}
```
<!-- CURSOR: /snippet -->
```

### AI Assistant Guidelines

**When writing rules:**
1. Include clear, unambiguous language
2. Provide multiple implementation examples
3. Use consistent terminology
4. Include troubleshooting guidance
5. Add context tags for better AI understanding

**Code examples should:**
- Be complete and runnable
- Include necessary imports
- Show both basic and advanced usage
- Include error handling
- Be well-commented

---

## 🧪 **Testing & Validation**

### Automated Testing

**Rule Structure Tests:**
```bash
# Run structure validation
python scripts/validate_rule_structure.py .cursor/rules/
```

**Content Tests:**
```bash
# Run rule compliance tests
python scripts/rule_test_runner.py . compliance_report.md
```

**Template Validation:**
```bash
# Validate template references
python scripts/validate_templates.py
```

### Manual Testing

**Implementation Testing:**
1. Create test project using the rule
2. Verify all code examples work
3. Test enforcement mechanisms
4. Validate tooling recommendations

**Usability Testing:**
1. Follow rule from scratch
2. Time implementation effort
3. Note any confusion points
4. Test with different skill levels

---

## 📊 **Quality Standards**

### Content Standards

**Code Examples:**
- ✅ Must be syntactically correct
- ✅ Must include necessary dependencies
- ✅ Must be production-ready
- ✅ Must include error handling
- ✅ Must be well-documented

**Requirements:**
- ✅ Use RFC 2119 keywords (MUST/SHOULD/MAY)
- ✅ Be specific and measurable
- ✅ Include success criteria
- ✅ Be enforceable via tooling
- ✅ Address real-world scenarios

**Documentation:**
- ✅ Clear implementation steps
- ✅ Comprehensive examples
- ✅ Troubleshooting guidance
- ✅ Tool recommendations
- ✅ Reference materials

### Metrics & KPIs

**Rule Effectiveness:**
- Implementation time reduction
- Error rate reduction
- Consistency improvement
- Developer satisfaction
- Automation coverage

**Community Engagement:**
- Usage across projects
- Community feedback
- Contribution frequency
- Issue resolution time

---

## 🏷️ **Tagging & Organization**

### Semantic Tags
```yaml
tags:
  technology: [nodejs, python, kubernetes, docker]
  domain: [security, performance, testing, deployment]
  complexity: [beginner, intermediate, advanced]
  priority: [critical, high, medium, low]
  enforcement: [automated, manual, hybrid]
```

### Rule Dependencies
```yaml
dependencies:
  requires: [01A, 02A]  # Rules that must be implemented first
  enhances: [03A, 05B]  # Rules that work better together
  conflicts: []         # Rules that conflict
```

---

## 🎯 **Success Criteria**

### For New Rules
- [ ] Addresses identified gap or need
- [ ] Has clear success metrics
- [ ] Is adopted by at least 3 teams
- [ ] Reduces implementation time by >20%
- [ ] Has >90% automated enforcement

### For Enhancements
- [ ] Improves existing metric by >10%
- [ ] Maintains backward compatibility
- [ ] Gets positive community feedback
- [ ] Increases automation coverage

### For Templates
- [ ] Is used by multiple rules
- [ ] Reduces setup time significantly
- [ ] Has validation mechanisms
- [ ] Gets adopted across projects

---

## 📞 **Getting Help**

### Community Resources
- **GitHub Discussions**: General questions and proposals
- **Issues**: Bug reports and specific problems
- **Wiki**: Additional documentation and examples
- **Slack/Discord**: Real-time community chat

### Mentorship
New contributors can request mentorship for:
- Understanding rule structure
- Technical implementation guidance
- Review process navigation
- Best practices learning

---

## 📜 **Code of Conduct**

### Collaboration Principles
- **Respectful**: Value diverse perspectives and experiences
- **Constructive**: Provide helpful, actionable feedback
- **Inclusive**: Welcome contributors of all backgrounds
- **Quality-focused**: Maintain high standards while being supportive
- **Transparent**: Communicate openly about decisions and changes

### Review Standards
- Focus on content, not contributor
- Provide specific, actionable suggestions
- Explain reasoning behind feedback
- Recognize good work and improvements
- Help contributors learn and grow

---

**Thank you for contributing to Universal Rules! 🎉**

Your contributions help create better software development standards for everyone. 