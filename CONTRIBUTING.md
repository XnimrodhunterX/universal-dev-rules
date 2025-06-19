# Contributing to Universal Development Rules

## 🤝 Welcome Contributors!

Thank you for your interest in improving the Universal Development Rules Framework! This guide will help you contribute effectively.

## 🔄 Development Workflow

### Branch Strategy
- **`main`**: Production releases (v2.1, v2.2, v2.3...)
- **`universal-dev-rules-v2.x`**: Development branches for next version
- **`feature/rule-name`**: Feature development branches
- **`bugfix/issue-description`**: Bug fix branches

### Getting Started
1. **Fork** the repository on GitHub
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

## 📋 Contribution Types

### 🐛 Bug Reports
- Use the bug report template
- Include steps to reproduce
- Provide environment details
- Add screenshots if applicable

### 💡 Rule Improvements
- Identify specific rule (e.g., AR-05, CN-04)
- Explain current limitations
- Propose specific improvements
- Include use cases and impact

### 🆕 New Rules
- Follow existing rule structure
- Include comprehensive examples
- Add to appropriate theme/domain
- Update documentation

### 📚 Documentation
- Fix typos and improve clarity
- Add examples and use cases
- Update setup instructions
- Translate content

## 🎯 Quality Standards

### Rule Development
- **Structure**: Follow existing rule format
- **Examples**: Include practical, tested examples
- **References**: Link to authoritative sources
- **Testing**: Validate with real projects

### Code Quality
- **Linting**: Follow project linting rules
- **Testing**: Include tests for new functionality
- **Documentation**: Update relevant docs
- **Compatibility**: Ensure Cursor IDE compatibility

### Commit Standards
Use [Conventional Commits](https://www.conventionalcommits.org/):
- `feat(scope): description` - New features
- `fix(scope): description` - Bug fixes
- `docs(scope): description` - Documentation
- `style(scope): description` - Formatting
- `refactor(scope): description` - Code refactoring
- `test(scope): description` - Testing
- `chore(scope): description` - Maintenance

## 🔢 Version Management

### Semantic Versioning
We follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (v3.0.0): Breaking changes
- **MINOR** (v2.1.0): New features, backward compatible
- **PATCH** (v2.1.1): Bug fixes, backward compatible

### Release Process
1. **Development**: Work on `universal-dev-rules-v2.x` branch
2. **Testing**: Validate changes with real projects
3. **Review**: Code review and approval process
4. **Merge**: Merge to `main` when ready for release
5. **Tag**: Create release tag with changelog
6. **Next**: Create new development branch for next version

### Contribution Targeting
- **Current main version**: v2.1
- **Next development branch**: `universal-dev-rules-v2.2`
- **Your PR target**: Always target the **next development branch**
- **Never** submit PRs directly to `main`

## 🧪 Testing Guidelines

### Rule Testing
- Test rules with real projects
- Verify Cursor IDE integration
- Check cross-platform compatibility
- Validate documentation accuracy

### Integration Testing
- Test setup scripts on different systems
- Verify template functionality
- Check automation scripts
- Validate distribution process

## 📝 Documentation Requirements

### Rule Documentation
- Clear, actionable guidance
- Practical examples with code
- Technology-specific considerations
- Links to authoritative sources

### Setup Documentation
- Step-by-step instructions
- Common troubleshooting issues
- Platform-specific notes
- Version compatibility matrix

## 🎁 Recognition

### Contributor Recognition
- **Contributors** listed in release notes
- **Major contributors** featured in README
- **Hall of Fame** for significant contributions
- **Early access** to new features

### Feedback Loop
- **Response time**: < 48 hours for all contributions
- **Review process**: Transparent and constructive
- **Implementation tracking**: Progress updates
- **Follow-up**: Post-implementation feedback

## 📞 Getting Help

### Community Support
- **GitHub Discussions**: General questions and ideas
- **GitHub Issues**: Bug reports and feature requests
- **Documentation**: Comprehensive guides and examples

### Maintainer Contact
- **Code reviews**: Automated assignment
- **Complex changes**: Tag maintainers for guidance
- **Process questions**: Use discussions for clarification

---

**Thank you for helping make development better for everyone!** 🚀

Your contributions drive the evolution of this framework and help developers worldwide build better software with intelligent assistance.
