# Changelog

All notable changes to the Universal Development Rules Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v2.2.0] - 2025-06-19

### 🚨 BREAKING CHANGES
- **Rule Consolidation**: All rule files moved from `intelligent_ide_rules/` to `.cursor/rules/`
- **Directory Structure**: Eliminated dual directory structure for cleaner organization
- **Migration Required**: Users must re-run `setup-cursor-rules.sh` to get new structure

### Added
- **Unified Rule Location**: All 56 development rules now consolidated in `.cursor/rules/`
- **Flat Structure**: Simplified organization with all rules in single directory
- **Enhanced Setup Script**: Updated to handle both `.mdc` and `.md` files correctly
- **Improved Cursor Integration**: Better native Cursor IDE support with consolidated structure

### Changed
- **File Paths**: All rule references updated from `intelligent_ide_rules/` to `.cursor/rules/`
- **Documentation**: Updated README.md with 75+ corrected file path references
- **Contributing Guide**: Updated validation commands for new structure
- **Security Rules**: Moved from `intelligent_ide_rules/security/` to `.cursor/rules/`
- **Metadata Files**: `domains.yaml` and `themes.yaml` moved to `.cursor/rules/`

### Fixed
- **Rule References**: All `.mdc` files now reference correct local file paths
- **Setup Script**: Enhanced path handling and file copying logic
- **Project Management**: Fixed `project-management.mdc` with proper content and rule references
- **Documentation Links**: All internal links updated to new structure

### Removed
- **Dual Directory**: Eliminated `intelligent_ide_rules/` directory completely
- **Path Confusion**: No more confusion between rule locations

### Technical Details
- 56 rule files successfully migrated
- All rule content preserved (only locations changed)
- Backward compatibility maintained through setup script
- Enhanced Cursor IDE native integration

## [v2.1.1] - 2025-06-19

### Added
- **Setup Script Documentation**: Comprehensive usage guide for `setup-cursor-rules.sh`
  - Complete parameter reference with examples
  - Error handling and troubleshooting guide
  - CI/CD and Docker integration examples
  - Advanced usage scenarios and environment variables
- **Quick Reference Guide**: Essential commands and examples for setup script
- **README Updates**: Added links to new documentation resources

### Documentation
- Enhanced setup script usability with detailed guides
- Improved developer onboarding experience
- Added verification steps and maintenance procedures

## [v2.1.0] - 2025-06-18

### Added
- Complete Universal Development Rules Framework
- 52+ comprehensive development rules across 9 categories
- Cursor IDE integration with native `.mdc` files
- Production-ready templates and automation
- Theme-based organization with cross-rule navigation
- Support for 6 technology domains
- Enterprise-grade compliance (SOC 2, ISO 27001, GDPR)
- Comprehensive testing and validation framework

### Features
- **Architecture & Design**: Event-driven, scalability, performance optimization
- **Cloud Native**: Infrastructure, containers, monitoring, SRE practices
- **Security**: Comprehensive security and compliance standards
- **Quality Control**: Testing, CI/CD, code review standards
- **Data Platform**: Database design, data governance, pipeline standards
- **Frontend**: Development standards, mobile, accessibility
- **Microservices**: Service architecture, API standards, governance
- **Machine Learning**: MLOps standards, AI ethics, responsible ML
- **Sustainability**: Green ops, supply chain security

### Infrastructure
- Automated setup scripts with path detection
- Rule testing framework with compliance validation
- GitHub integration templates and workflows
- Distribution system for clean deployments 