---
description: "Release Management: Release planning, feature flags, version management, release coordination. Comprehensive release governance and automation."
globs: ["**/*"]
alwaysApply: true
---

# 📦 Release Management Standards

<!-- CURSOR: highlight: release:management -->
<!-- CURSOR: context: versioning, feature-flags, release-planning, coordination -->
<!-- CURSOR: complexity: intermediate -->
<!-- CURSOR: priority: high -->

## 1. Release Planning & Coordination

### Core Requirements
- **MUST** follow semantic versioning (SemVer) for all releases
- **MUST** maintain release notes with breaking changes, new features, and bug fixes
- **MUST** implement feature flags for gradual feature rollouts
- **MUST** coordinate releases across dependent services

### Release Types & Cadence
```yaml
# release-strategy.yaml
release_strategy:
  types:
    hotfix:
      description: "Critical bug fixes requiring immediate deployment"
      cadence: "as_needed"
      approval_required: "engineering_lead"
      testing_requirements: ["smoke_tests"]
      rollback_plan: "automatic"
      
    patch:
      description: "Bug fixes and minor improvements"
      cadence: "weekly"
      approval_required: "team_lead"
      testing_requirements: ["unit_tests", "integration_tests", "smoke_tests"]
      rollback_plan: "automatic"
      
    minor:
      description: "New features and non-breaking changes"
      cadence: "bi_weekly"
      approval_required: "product_manager"
      testing_requirements: ["full_test_suite", "performance_tests", "security_scans"]
      rollback_plan: "manual_approval"
      
    major:
      description: "Breaking changes and major feature releases"
      cadence: "quarterly"
      approval_required: "architecture_committee"
      testing_requirements: ["full_test_suite", "performance_tests", "security_scans", "user_acceptance_tests"]
      rollback_plan: "manual_approval"

  coordination:
    dependency_check: true
    cross_team_notification: true
    release_train_alignment: true
    maintenance_window_scheduling: true
```

### Release Planning Template
```markdown
# Release Plan: [Service Name] v[Version]

## 📋 Release Information
- **Release Type**: [Major/Minor/Patch/Hotfix]
- **Target Date**: [YYYY-MM-DD]
- **Release Manager**: [@username]
- **Engineering Lead**: [@username]

## 🎯 Release Goals
- [ ] Goal 1: Description
- [ ] Goal 2: Description
- [ ] Goal 3: Description

## 🚀 Features & Changes
### New Features
- [ ] Feature 1: Description (Issue #123)
- [ ] Feature 2: Description (Issue #456)

### Bug Fixes
- [ ] Fix 1: Description (Issue #789)
- [ ] Fix 2: Description (Issue #101)

### Breaking Changes
- [ ] Breaking Change 1: Description and migration guide
- [ ] Breaking Change 2: Description and migration guide

## 🔗 Dependencies
### Upstream Dependencies
- [ ] Service A v1.2.0 (required)
- [ ] Service B v2.1.0 (recommended)

### Downstream Impact
- [ ] Service C (requires update)
- [ ] Service D (compatibility check needed)

## 🧪 Testing Plan
- [ ] Unit tests (>90% coverage)
- [ ] Integration tests
- [ ] Performance tests
- [ ] Security scans
- [ ] Load testing
- [ ] User acceptance testing

## 📊 Feature Flags
- [ ] `new_payment_flow` - Gradual rollout (0% → 5% → 25% → 100%)
- [ ] `enhanced_search` - A/B testing (50/50 split)
- [ ] `legacy_api_deprecation` - Sunset timeline (6 months)

## 🚨 Rollback Plan
- **Automated Rollback Triggers**: Error rate >2%, P99 latency >3s
- **Manual Rollback**: Available within 2 minutes
- **Data Migration Rollback**: [Describe if applicable]

## 📅 Timeline
- **Code Freeze**: [Date]
- **QA Testing**: [Date Range]
- **Staging Deployment**: [Date]
- **Production Deployment**: [Date]
- **Go-Live**: [Date]

## 🔔 Communication Plan
- [ ] Engineering team notification (1 week prior)
- [ ] Stakeholder notification (3 days prior)
- [ ] Customer communication (if user-facing changes)
- [ ] Post-release summary

## ✅ Release Checklist
- [ ] All tests passing
- [ ] Security scans completed
- [ ] Documentation updated
- [ ] Release notes prepared
- [ ] Rollback plan tested
- [ ] Feature flags configured
- [ ] Monitoring dashboards updated
```

## 2. Semantic Versioning Standards

### Version Number Format
- **MUST** use format: `MAJOR.MINOR.PATCH` (e.g., `2.1.3`)
- **MUST** increment MAJOR for breaking changes
- **MUST** increment MINOR for new features (backward compatible)
- **MUST** increment PATCH for bug fixes (backward compatible)

### Automated Version Management
```typescript
// scripts/version-manager.ts
export class VersionManager {
  private readonly packageJsonPath: string;
  private readonly changelogPath: string;
  
  constructor(projectRoot: string) {
    this.packageJsonPath = path.join(projectRoot, 'package.json');
    this.changelogPath = path.join(projectRoot, 'CHANGELOG.md');
  }

  async determineNextVersion(currentVersion: string, changes: ChangeSet): Promise<string> {
    const current = semver.parse(currentVersion);
    if (!current) {
      throw new Error(`Invalid current version: ${currentVersion}`);
    }

    // Determine version bump based on changes
    if (changes.hasBreakingChanges()) {
      return semver.inc(currentVersion, 'major')!;
    } else if (changes.hasNewFeatures()) {
      return semver.inc(currentVersion, 'minor')!;
    } else if (changes.hasBugFixes()) {
      return semver.inc(currentVersion, 'patch')!;
    } else {
      throw new Error('No changes detected that warrant a version bump');
    }
  }

  async analyzeCommitsSinceLastRelease(): Promise<ChangeSet> {
    const lastTag = await this.getLastReleaseTag();
    const commits = await this.getCommitsSince(lastTag);
    
    const changes = new ChangeSet();
    
    for (const commit of commits) {
      if (this.isBreakingChange(commit)) {
        changes.addBreakingChange(commit);
      } else if (this.isFeature(commit)) {
        changes.addFeature(commit);
      } else if (this.isBugFix(commit)) {
        changes.addBugFix(commit);
      }
    }
    
    return changes;
  }

  private isBreakingChange(commit: GitCommit): boolean {
    return commit.message.includes('BREAKING CHANGE:') ||
           commit.message.includes('!:') ||
           commit.footer?.includes('BREAKING CHANGE:');
  }

  private isFeature(commit: GitCommit): boolean {
    return commit.type === 'feat';
  }

  private isBugFix(commit: GitCommit): boolean {
    return commit.type === 'fix';
  }

  async createRelease(version: string, changes: ChangeSet): Promise<Release> {
    // Update package.json
    await this.updatePackageVersion(version);
    
    // Generate changelog
    await this.updateChangelog(version, changes);
    
    // Create git tag
    await this.createGitTag(version);
    
    // Generate release notes
    const releaseNotes = await this.generateReleaseNotes(version, changes);
    
    return {
      version,
      releaseNotes,
      timestamp: new Date(),
      changes
    };
  }

  private async generateReleaseNotes(version: string, changes: ChangeSet): Promise<string> {
    let notes = `# Release ${version}\n\n`;
    
    if (changes.breakingChanges.length > 0) {
      notes += '## 🚨 Breaking Changes\n\n';
      for (const change of changes.breakingChanges) {
        notes += `- ${change.description}\n`;
        if (change.migrationGuide) {
          notes += `  - **Migration**: ${change.migrationGuide}\n`;
        }
      }
      notes += '\n';
    }

    if (changes.features.length > 0) {
      notes += '## ✨ New Features\n\n';
      for (const feature of changes.features) {
        notes += `- ${feature.description}\n`;
      }
      notes += '\n';
    }

    if (changes.bugFixes.length > 0) {
      notes += '## 🐛 Bug Fixes\n\n';
      for (const fix of changes.bugFixes) {
        notes += `- ${fix.description}\n`;
      }
      notes += '\n';
    }

    return notes;
  }
}

export class ChangeSet {
  public breakingChanges: Change[] = [];
  public features: Change[] = [];
  public bugFixes: Change[] = [];

  addBreakingChange(commit: GitCommit): void {
    this.breakingChanges.push(this.parseChange(commit));
  }

  addFeature(commit: GitCommit): void {
    this.features.push(this.parseChange(commit));
  }

  addBugFix(commit: GitCommit): void {
    this.bugFixes.push(this.parseChange(commit));
  }

  hasBreakingChanges(): boolean {
    return this.breakingChanges.length > 0;
  }

  hasNewFeatures(): boolean {
    return this.features.length > 0;
  }

  hasBugFixes(): boolean {
    return this.bugFixes.length > 0;
  }

  private parseChange(commit: GitCommit): Change {
    return {
      description: commit.subject,
      commit: commit.hash,
      author: commit.author,
      timestamp: commit.timestamp,
      issueNumbers: this.extractIssueNumbers(commit.message),
      migrationGuide: this.extractMigrationGuide(commit.body)
    };
  }

  private extractIssueNumbers(message: string): string[] {
    const matches = message.match(/#(\d+)/g);
    return matches ? matches.map(match => match.slice(1)) : [];
  }

  private extractMigrationGuide(body: string): string | undefined {
    const match = body.match(/Migration:\s*(.+)/i);
    return match ? match[1].trim() : undefined;
  }
}
```

## 3. Feature Flag Management

### Feature Flag Standards
- **MUST** use feature flags for all new features and experimental changes
- **MUST** implement gradual rollout capabilities (0% → 5% → 25% → 50% → 100%)
- **MUST** provide instant toggle capability for emergency rollbacks
- **MUST** clean up deprecated feature flags within 2 release cycles

### LaunchDarkly Integration
```typescript
// src/feature-flags/feature-flag-service.ts
import { LDClient, LDUser } from 'launchdarkly-node-server-sdk';

export class FeatureFlagService {
  private client: LDClient;
  private readonly defaultValues: Map<string, any> = new Map();

  constructor(sdkKey: string) {
    this.client = LDClient.init(sdkKey);
    this.setupDefaultValues();
  }

  async isFeatureEnabled(
    flagKey: string, 
    user: LDUser, 
    defaultValue: boolean = false
  ): Promise<boolean> {
    try {
      return await this.client.variation(flagKey, user, defaultValue);
    } catch (error) {
      console.error(`Error evaluating feature flag ${flagKey}:`, error);
      return this.getDefaultValue(flagKey, defaultValue);
    }
  }

  async getFeatureVariation<T>(
    flagKey: string,
    user: LDUser,
    defaultValue: T
  ): Promise<T> {
    try {
      return await this.client.variation(flagKey, user, defaultValue);
    } catch (error) {
      console.error(`Error getting feature variation ${flagKey}:`, error);
      return this.getDefaultValue(flagKey, defaultValue);
    }
  }

  async evaluateAllFlags(user: LDUser): Promise<Record<string, any>> {
    try {
      return await this.client.allFlagsState(user);
    } catch (error) {
      console.error('Error evaluating all flags:', error);
      return {};
    }
  }

  private setupDefaultValues(): void {
    // Critical feature flags with safe defaults
    this.defaultValues.set('new_payment_flow', false);
    this.defaultValues.set('enhanced_search', false);
    this.defaultValues.set('beta_dashboard', false);
    this.defaultValues.set('legacy_api_enabled', true);
    this.defaultValues.set('maintenance_mode', false);
  }

  private getDefaultValue<T>(flagKey: string, fallback: T): T {
    return this.defaultValues.get(flagKey) ?? fallback;
  }

  // Metrics and monitoring
  async trackFeatureFlagMetrics(): Promise<void> {
    const allFlags = await this.client.allFlagsState({
      key: 'system',
      anonymous: true
    });

    // Track flag usage metrics
    for (const [flagKey, value] of Object.entries(allFlags.allValues())) {
      await this.recordMetric('feature_flag_value', {
        flag: flagKey,
        value: value.toString(),
        timestamp: Date.now()
      });
    }
  }

  private async recordMetric(metricName: string, data: any): Promise<void> {
    // Implementation depends on your metrics system
    // Example: Prometheus, DataDog, CloudWatch, etc.
  }
}

// Feature flag middleware for Express.js
export function featureFlagMiddleware(featureFlagService: FeatureFlagService) {
  return async (req: any, res: any, next: any) => {
    const user: LDUser = {
      key: req.user?.id || req.sessionID,
      email: req.user?.email,
      name: req.user?.name,
      custom: {
        userAgent: req.headers['user-agent'],
        ipAddress: req.ip,
        environment: process.env.NODE_ENV
      }
    };

    // Add feature flag evaluation helper to request
    req.featureFlags = {
      isEnabled: (flagKey: string, defaultValue: boolean = false) =>
        featureFlagService.isFeatureEnabled(flagKey, user, defaultValue),
      
      getVariation: <T>(flagKey: string, defaultValue: T) =>
        featureFlagService.getFeatureVariation(flagKey, user, defaultValue),
      
      user
    };

    next();
  };
}
```

### Feature Flag Configuration
```yaml
# feature-flags.yaml
feature_flags:
  new_payment_flow:
    description: "New checkout flow with enhanced UX"
    type: "boolean"
    default_value: false
    rollout_strategy:
      type: "gradual"
      stages:
        - percentage: 5
          duration: "24h"
          criteria: "internal_users"
        - percentage: 25
          duration: "48h"
          criteria: "beta_users"
        - percentage: 50
          duration: "72h"
          criteria: "all_users"
        - percentage: 100
          duration: "permanent"
    monitoring:
      metrics:
        - "payment_success_rate"
        - "checkout_completion_time"
        - "user_satisfaction_score"
      alerts:
        - condition: "payment_success_rate < 0.95"
          action: "rollback"
        - condition: "checkout_completion_time > 30s"
          action: "alert_team"

  enhanced_search:
    description: "AI-powered search with personalization"
    type: "variant"
    variants:
      control: "legacy_search"
      treatment_a: "ai_search_v1"
      treatment_b: "ai_search_v2"
    default_variant: "control"
    rollout_strategy:
      type: "ab_test"
      traffic_split:
        control: 50
        treatment_a: 25
        treatment_b: 25
      duration: "2 weeks"
    success_metrics:
      primary: "search_click_through_rate"
      secondary: ["search_result_relevance", "user_engagement_time"]

  legacy_api_deprecation:
    description: "Gradual sunset of legacy API endpoints"
    type: "boolean"
    default_value: true
    sunset_plan:
      warning_phase:
        start_date: "2024-01-01"
        duration: "3 months"
        actions: ["deprecation_headers", "warning_logs"]
      
      restricted_phase:
        start_date: "2024-04-01"
        duration: "2 months"
        actions: ["rate_limiting", "forced_migration_notices"]
      
      shutdown_phase:
        start_date: "2024-06-01"
        actions: ["api_disabled", "redirect_to_new_endpoints"]
```

## 4. Release Automation

### Automated Release Pipeline
```yaml
# .github/workflows/release.yml
name: Automated Release

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      release_type:
        description: 'Release type'
        required: true
        default: 'auto'
        type: choice
        options: ['auto', 'patch', 'minor', 'major']

jobs:
  analyze-changes:
    runs-on: ubuntu-latest
    outputs:
      should-release: ${{ steps.analysis.outputs.should-release }}
      next-version: ${{ steps.analysis.outputs.next-version }}
      changelog: ${{ steps.analysis.outputs.changelog }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Analyze commits for release
        id: analysis
        run: |
          npm ci
          npm run release:analyze
          
          # Output results for next job
          echo "should-release=$(cat .release-analysis/should-release)" >> $GITHUB_OUTPUT
          echo "next-version=$(cat .release-analysis/next-version)" >> $GITHUB_OUTPUT
          echo "changelog<<EOF" >> $GITHUB_OUTPUT
          cat .release-analysis/changelog.md >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT

  create-release:
    needs: analyze-changes
    if: needs.analyze-changes.outputs.should-release == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.RELEASE_TOKEN }}

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Configure Git
        run: |
          git config user.name "Release Bot"
          git config user.email "release-bot@example.com"

      - name: Create release
        env:
          NEXT_VERSION: ${{ needs.analyze-changes.outputs.next-version }}
          CHANGELOG: ${{ needs.analyze-changes.outputs.changelog }}
        run: |
          npm ci
          
          # Update version in package.json
          npm version $NEXT_VERSION --no-git-tag-version
          
          # Update CHANGELOG.md
          echo "$CHANGELOG" | cat - CHANGELOG.md > temp && mv temp CHANGELOG.md
          
          # Commit changes
          git add package.json CHANGELOG.md
          git commit -m "chore(release): version $NEXT_VERSION"
          
          # Create and push tag
          git tag "v$NEXT_VERSION"
          git push origin main --tags

      - name: Build and publish
        env:
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
        run: |
          npm run build
          npm run test
          npm publish

      - name: Create GitHub Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: v${{ needs.analyze-changes.outputs.next-version }}
          release_name: Release ${{ needs.analyze-changes.outputs.next-version }}
          body: ${{ needs.analyze-changes.outputs.changelog }}
          draft: false
          prerelease: false

      - name: Deploy to staging
        run: |
          curl -X POST "${{ secrets.STAGING_DEPLOY_WEBHOOK }}" \
            -H "Authorization: Bearer ${{ secrets.DEPLOY_TOKEN }}" \
            -H "Content-Type: application/json" \
            -d '{"version": "${{ needs.analyze-changes.outputs.next-version }}", "environment": "staging"}'

  notify-stakeholders:
    needs: [analyze-changes, create-release]
    runs-on: ubuntu-latest
    steps:
      - name: Notify Slack
        uses: 8398a7/action-slack@v3
        with:
          status: success
          text: |
            🚀 **New Release Created**: v${{ needs.analyze-changes.outputs.next-version }}
            
            **Changes:**
            ${{ needs.analyze-changes.outputs.changelog }}
            
            **Next Steps:**
            - Staging deployment in progress
            - Production deployment requires approval
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}

      - name: Update project tracking
        run: |
          curl -X POST "${{ secrets.PROJECT_TRACKING_API }}" \
            -H "Authorization: Bearer ${{ secrets.PROJECT_TOKEN }}" \
            -H "Content-Type: application/json" \
            -d '{
              "event": "release_created",
              "version": "${{ needs.analyze-changes.outputs.next-version }}",
              "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
              "changes": ${{ toJson(needs.analyze-changes.outputs.changelog) }}
            }'
```

## 5. Release Coordination

### Cross-Service Release Coordination
```typescript
// src/release/release-coordinator.ts
export class ReleaseCoordinator {
  private readonly serviceRegistry: ServiceRegistry;
  private readonly notificationService: NotificationService;
  private readonly dependencyAnalyzer: DependencyAnalyzer;

  constructor(
    serviceRegistry: ServiceRegistry,
    notificationService: NotificationService,
    dependencyAnalyzer: DependencyAnalyzer
  ) {
    this.serviceRegistry = serviceRegistry;
    this.notificationService = notificationService;
    this.dependencyAnalyzer = dependencyAnalyzer;
  }

  async planRelease(releaseRequest: ReleaseRequest): Promise<ReleasePlan> {
    console.log(`📋 Planning release for ${releaseRequest.serviceName} v${releaseRequest.version}`);

    // Analyze dependencies
    const dependencies = await this.dependencyAnalyzer.analyzeDependencies(
      releaseRequest.serviceName,
      releaseRequest.version
    );

    // Check for conflicts
    const conflicts = await this.checkReleaseConflicts(releaseRequest, dependencies);
    
    if (conflicts.length > 0) {
      throw new ReleaseConflictError(`Release conflicts detected: ${conflicts.join(', ')}`);
    }

    // Create release plan
    const plan: ReleasePlan = {
      primaryRelease: releaseRequest,
      dependentReleases: await this.planDependentReleases(dependencies),
      timeline: await this.createReleaseTimeline(releaseRequest, dependencies),
      approvals: await this.determineRequiredApprovals(releaseRequest),
      rollbackPlan: await this.createRollbackPlan(releaseRequest, dependencies),
      communicationPlan: await this.createCommunicationPlan(releaseRequest)
    };

    return plan;
  }

  async executeRelease(plan: ReleasePlan): Promise<ReleaseExecution> {
    console.log(`🚀 Executing release plan for ${plan.primaryRelease.serviceName}`);

    const execution: ReleaseExecution = {
      plan,
      startTime: new Date(),
      status: 'in_progress',
      completedSteps: [],
      failedSteps: [],
      rollbackExecuted: false
    };

    try {
      // Execute pre-release tasks
      await this.executePreReleaseTasks(plan, execution);

      // Execute main release
      await this.executeMainRelease(plan, execution);

      // Execute post-release tasks
      await this.executePostReleaseTasks(plan, execution);

      execution.status = 'completed';
      execution.endTime = new Date();

      await this.notificationService.notifyReleaseSuccess(execution);
      
      return execution;
    } catch (error) {
      console.error('Release execution failed:', error);
      
      execution.status = 'failed';
      execution.error = error.message;

      // Execute rollback if configured
      if (plan.rollbackPlan.automaticRollback) {
        await this.executeRollback(execution);
      }

      await this.notificationService.notifyReleaseFailure(execution);
      throw error;
    }
  }

  private async executePreReleaseTasks(
    plan: ReleasePlan,
    execution: ReleaseExecution
  ): Promise<void> {
    const tasks = [
      () => this.validateDependencies(plan),
      () => this.runPreReleaseTests(plan),
      () => this.notifyStakeholders(plan),
      () => this.prepareRollbackResources(plan)
    ];

    for (const task of tasks) {
      try {
        await task();
        execution.completedSteps.push(`pre_release_${task.name}`);
      } catch (error) {
        execution.failedSteps.push(`pre_release_${task.name}: ${error.message}`);
        throw error;
      }
    }
  }

  private async executeMainRelease(
    plan: ReleasePlan,
    execution: ReleaseExecution
  ): Promise<void> {
    // Execute dependent releases first
    for (const dependentRelease of plan.dependentReleases) {
      try {
        await this.deployService(dependentRelease);
        execution.completedSteps.push(`deploy_${dependentRelease.serviceName}`);
      } catch (error) {
        execution.failedSteps.push(`deploy_${dependentRelease.serviceName}: ${error.message}`);
        throw error;
      }
    }

    // Execute primary release
    try {
      await this.deployService(plan.primaryRelease);
      execution.completedSteps.push(`deploy_${plan.primaryRelease.serviceName}`);
    } catch (error) {
      execution.failedSteps.push(`deploy_${plan.primaryRelease.serviceName}: ${error.message}`);
      throw error;
    }
  }

  private async deployService(release: ReleaseRequest): Promise<void> {
    console.log(`🚢 Deploying ${release.serviceName} v${release.version}`);

    const deploymentStrategy = await this.determineDeploymentStrategy(release);
    
    switch (deploymentStrategy) {
      case 'blue-green':
        await this.executeBlueGreenDeployment(release);
        break;
      case 'canary':
        await this.executeCanaryDeployment(release);
        break;
      case 'rolling':
        await this.executeRollingDeployment(release);
        break;
      default:
        throw new Error(`Unknown deployment strategy: ${deploymentStrategy}`);
    }

    // Verify deployment
    await this.verifyDeployment(release);
  }

  private async checkReleaseConflicts(
    request: ReleaseRequest,
    dependencies: ServiceDependency[]
  ): Promise<string[]> {
    const conflicts: string[] = [];

    // Check for concurrent releases
    const ongoingReleases = await this.serviceRegistry.getOngoingReleases();
    for (const ongoing of ongoingReleases) {
      if (dependencies.some(dep => dep.serviceName === ongoing.serviceName)) {
        conflicts.push(`Concurrent release of dependency ${ongoing.serviceName}`);
      }
    }

    // Check for maintenance windows
    const maintenanceWindows = await this.serviceRegistry.getMaintenanceWindows();
    for (const window of maintenanceWindows) {
      if (this.isTimeConflict(request.scheduledTime, window)) {
        conflicts.push(`Maintenance window conflict: ${window.description}`);
      }
    }

    // Check for version compatibility
    for (const dependency of dependencies) {
      const compatibility = await this.checkVersionCompatibility(
        request.serviceName,
        request.version,
        dependency
      );
      
      if (!compatibility.compatible) {
        conflicts.push(`Version incompatibility with ${dependency.serviceName}: ${compatibility.reason}`);
      }
    }

    return conflicts;
  }
}

export interface ReleaseRequest {
  serviceName: string;
  version: string;
  releaseType: 'major' | 'minor' | 'patch' | 'hotfix';
  scheduledTime: Date;
  approver: string;
  description: string;
  breakingChanges: BreakingChange[];
  featureFlags: FeatureFlag[];
}

export interface ReleasePlan {
  primaryRelease: ReleaseRequest;
  dependentReleases: ReleaseRequest[];
  timeline: ReleaseTimeline;
  approvals: ApprovalRequirement[];
  rollbackPlan: RollbackPlan;
  communicationPlan: CommunicationPlan;
}
```

## 6. Quality Gates & Metrics

### Release Quality Gates
```yaml
# Quality gates for release management
release_quality_gates:
  release_success_rate:
    description: "Percentage of releases that complete without rollback"
    metric: "successful_releases / total_releases * 100"
    threshold: 95
    blocking: true

  release_lead_time:
    description: "Time from code merge to production deployment"
    metric: "production_deployment_time - code_merge_time"
    threshold: 24  # hours
    blocking: false

  feature_flag_cleanup:
    description: "Feature flags removed within 2 release cycles"
    metric: "cleaned_feature_flags / total_deprecated_flags * 100"
    threshold: 90
    blocking: false

  release_frequency:
    description: "Number of releases per week"
    metric: "releases_per_week"
    threshold: 2
    blocking: false

  rollback_frequency:
    description: "Percentage of releases requiring rollback"
    metric: "rollbacks / total_releases * 100"
    threshold: 5
    blocking: true
```

---

## 📋 **Implementation Checklist**

### Release Planning
- [ ] Implement semantic versioning across all services
- [ ] Create release planning templates and processes
- [ ] Set up cross-service dependency tracking
- [ ] Establish release approval workflows

### Feature Flag Management
- [ ] Integrate feature flag service (LaunchDarkly/Split/Custom)
- [ ] Implement gradual rollout capabilities
- [ ] Set up feature flag monitoring and alerting
- [ ] Create feature flag cleanup automation

### Version Management
- [ ] Automate version determination from commits
- [ ] Set up automated changelog generation
- [ ] Implement git tagging and release creation
- [ ] Create version compatibility checking

### Release Coordination
- [ ] Build release coordination system
- [ ] Implement conflict detection and resolution
- [ ] Set up cross-team notification systems
- [ ] Create release timeline management

### Automation
- [ ] Set up automated release pipelines
- [ ] Implement release quality gates
- [ ] Create rollback automation
- [ ] Set up release metrics and monitoring

---

## 🎯 **Success Metrics**

- **Release Frequency:** 2+ releases per week with high confidence
- **Release Success Rate:** 95% of releases complete without rollback
- **Lead Time:** <24 hours from code merge to production
- **Feature Flag Coverage:** 100% of new features behind flags
- **Release Coordination:** Zero conflicts due to improved planning and communication 