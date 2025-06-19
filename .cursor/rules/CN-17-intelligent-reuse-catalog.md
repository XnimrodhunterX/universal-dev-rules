---
description: "Intelligent Function & Service Reuse Catalog: AI-assisted code reuse, service discovery, dependency analysis. Comprehensive reuse prevention and optimization."
globs: ["**/*"]
alwaysApply: true
---

# 🧠 Intelligent Function & Service Reuse Catalog

## 1. Service & Function Registry

### Core Requirements
- **MUST** maintain live, queryable catalog of all services and public functions
- **MUST** generate service registry automatically at build/deploy time
- **MUST** include dependency graph capturing function calls across services
- **MUST** integrate with IDE/AI coding assistants to prevent redundant implementations

### Purpose & Benefits
Enable intelligent development environments and AI coding assistants to:
- Recognize existing, working service functions
- Suggest reuse instead of reimplementation
- Reduce code bloat and maintenance burden
- Prevent reinvention of existing functionality
- Improve consistency across services

### Registry Schema
```typescript
// src/catalog/service-registry.ts
export interface ServiceCatalogEntry {
  service: {
    name: string;
    version: string;
    description: string;
    repository: string;
    endpoints: ServiceEndpoint[];
    dependencies: ServiceDependency[];
    tags: string[];
    maintainers: string[];
    lastUpdated: Date;
  };
  functions: FunctionCatalogEntry[];
  apis: APICatalogEntry[];
  events: EventCatalogEntry[];
}

export interface FunctionCatalogEntry {
  name: string;
  signature: string;
  description: string;
  parameters: ParameterSpec[];
  returnType: TypeSpec;
  examples: CodeExample[];
  complexity: 'low' | 'medium' | 'high';
  stability: 'experimental' | 'stable' | 'deprecated';
  reusabilityScore: number; // 0-100
  usageCount: number;
  lastModified: Date;
  sourceLocation: {
    file: string;
    line: number;
    repository: string;
  };
  annotations: {
    reusable: boolean;
    stateless: boolean;
    idempotent: boolean;
    cached: boolean;
    authenticated: boolean;
  };
}

export interface APICatalogEntry {
  endpoint: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  description: string;
  parameters: ParameterSpec[];
  responses: ResponseSpec[];
  authentication: AuthSpec;
  rateLimit: RateLimitSpec;
  examples: APIExample[];
  openApiRef: string;
}

export interface ServiceDependency {
  service: string;
  type: 'synchronous' | 'asynchronous' | 'event-driven';
  functions: string[];
  criticality: 'critical' | 'important' | 'optional';
}
```

## 2. Automatic Registry Generation

### Build-Time Registration
```typescript
// scripts/generate-catalog.ts
import { execSync } from 'child_process';
import { ServiceCatalogGenerator } from './catalog-generator';

export class AutomaticRegistryBuilder {
  private generator: ServiceCatalogGenerator;
  
  constructor(config: CatalogConfig) {
    this.generator = new ServiceCatalogGenerator(config);
  }

  async buildCatalog(projectRoot: string): Promise<ServiceCatalogEntry> {
    const serviceInfo = await this.extractServiceMetadata(projectRoot);
    const functions = await this.scanFunctions(projectRoot);
    const apis = await this.extractAPIs(projectRoot);
    const dependencies = await this.analyzeDependencies(projectRoot);
    
    return {
      service: serviceInfo,
      functions,
      apis,
      events: await this.extractEvents(projectRoot)
    };
  }

  private async scanFunctions(projectRoot: string): Promise<FunctionCatalogEntry[]> {
    const functions: FunctionCatalogEntry[] = [];
    
    // Scan TypeScript/JavaScript files
    const tsFiles = await this.glob(`${projectRoot}/**/*.{ts,js}`, {
      ignore: ['node_modules', 'dist', 'build', '**/*.test.*', '**/*.spec.*']
    });
    
    for (const file of tsFiles) {
      const ast = await this.parseFile(file);
      const extractedFunctions = this.extractFunctions(ast, file);
      functions.push(...extractedFunctions);
    }
    
    return functions;
  }

  private extractFunctions(ast: any, filePath: string): FunctionCatalogEntry[] {
    const functions: FunctionCatalogEntry[] = [];
    
    // AST traversal logic to extract function signatures
    ast.body.forEach((node: any) => {
      if (node.type === 'FunctionDeclaration' || node.type === 'ArrowFunctionExpression') {
        const funcEntry = this.createFunctionEntry(node, filePath);
        if (this.isReusableFunction(funcEntry)) {
          functions.push(funcEntry);
        }
      }
      
      // Extract class methods
      if (node.type === 'ClassDeclaration') {
        node.body.body.forEach((method: any) => {
          if (method.type === 'MethodDefinition' && method.accessibility === 'public') {
            const methodEntry = this.createMethodEntry(method, filePath, node.id.name);
            if (this.isReusableFunction(methodEntry)) {
              functions.push(methodEntry);
            }
          }
        });
      }
    });
    
    return functions;
  }

  private createFunctionEntry(node: any, filePath: string): FunctionCatalogEntry {
    return {
      name: node.id?.name || 'anonymous',
      signature: this.generateSignature(node),
      description: this.extractDocComment(node),
      parameters: this.extractParameters(node.params),
      returnType: this.inferReturnType(node),
      examples: this.extractExamples(node),
      complexity: this.calculateComplexity(node),
      stability: this.determineStability(node),
      reusabilityScore: this.calculateReusabilityScore(node),
      usageCount: 0, // Updated during usage analysis
      lastModified: new Date(),
      sourceLocation: {
        file: filePath,
        line: node.loc.start.line,
        repository: this.getRepositoryInfo()
      },
      annotations: this.extractAnnotations(node)
    };
  }

  private isReusableFunction(func: FunctionCatalogEntry): boolean {
    // Logic to determine if function should be in reuse catalog
    return func.annotations.reusable ||
           func.reusabilityScore > 70 ||
           func.annotations.stateless ||
           func.complexity === 'medium' || func.complexity === 'high';
  }

  private calculateReusabilityScore(node: any): number {
    let score = 50; // Base score
    
    // Increase score for pure functions
    if (this.isPureFunction(node)) score += 20;
    
    // Increase score for well-documented functions
    if (this.hasGoodDocumentation(node)) score += 15;
    
    // Increase score for functions with examples
    if (this.hasExamples(node)) score += 10;
    
    // Decrease score for highly coupled functions
    if (this.isHighlyCoupled(node)) score -= 20;
    
    // Increase score for generic/configurable functions
    if (this.isGeneric(node)) score += 15;
    
    return Math.max(0, Math.min(100, score));
  }
}
```

### Deployment Integration
```yaml
# .github/workflows/catalog-update.yml
name: Update Service Catalog

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  update-catalog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Generate service catalog
        run: |
          npm run generate:catalog
          
      - name: Upload catalog to registry
        run: |
          curl -X POST "${{ secrets.CATALOG_REGISTRY_URL }}/services" \
            -H "Authorization: Bearer ${{ secrets.CATALOG_TOKEN }}" \
            -H "Content-Type: application/json" \
            -d @service-catalog.json
      
      - name: Update dependency graph
        run: |
          npm run analyze:dependencies
          curl -X PUT "${{ secrets.CATALOG_REGISTRY_URL }}/dependencies" \
            -H "Authorization: Bearer ${{ secrets.CATALOG_TOKEN }}" \
            -H "Content-Type: application/json" \
            -d @dependency-graph.json
```

## 3. IDE Integration & AI Assistant Support

### Cursor Integration
```typescript
// .cursor/service-catalog.js
export class CursorServiceCatalog {
  async suggestReusableFunction(context: CodeContext): Promise<ReuseSuggestion[]> {
    const intent = await this.analyzeCodeIntent(context);
    const similarFunctions = await this.searchCatalog(intent);
    
    return similarFunctions.map(func => ({
      function: func,
      similarity: this.calculateSimilarity(intent, func),
      suggestion: this.generateUsageSuggestion(func),
      codeExample: this.generateCodeExample(func, context)
    }));
  }

  private async analyzeCodeIntent(context: CodeContext): Promise<CodeIntent> {
    // Analyze what the developer is trying to accomplish
    return {
      domain: this.extractDomain(context.currentCode),
      operation: this.extractOperation(context.currentCode),
      inputTypes: this.extractInputTypes(context.currentCode),
      expectedOutput: this.extractExpectedOutput(context.currentCode),
      keywords: this.extractKeywords(context.currentCode)
    };
  }

  private async searchCatalog(intent: CodeIntent): Promise<FunctionCatalogEntry[]> {
    const query = {
      domain: intent.domain,
      operation: intent.operation,
      inputTypes: intent.inputTypes,
      minReusabilityScore: 70
    };
    
    return await this.catalogService.search(query);
  }

  generateUsageSuggestion(func: FunctionCatalogEntry): string {
    return `
💡 **Reuse Suggestion**: Instead of implementing this functionality, consider using:

**Function**: \`${func.name}\`
**Service**: ${func.sourceLocation.repository}
**Description**: ${func.description}
**Reusability Score**: ${func.reusabilityScore}/100

**Usage Example**:
\`\`\`typescript
${func.examples[0]?.code || 'No example available'}
\`\`\`

**To use this function**:
1. Add service dependency: \`npm install ${func.sourceLocation.repository}\`
2. Import: \`import { ${func.name} } from '${func.sourceLocation.repository}'\`
3. Call: \`${func.signature}\`

**Benefits**: Reduces code duplication, leverages tested implementation, improves maintainability.
`;
  }
}
```

### VS Code Extension
```typescript
// extensions/service-catalog/src/extension.ts
import * as vscode from 'vscode';

export class ServiceCatalogExtension {
  private catalogProvider: ServiceCatalogProvider;
  
  constructor() {
    this.catalogProvider = new ServiceCatalogProvider();
  }

  activate(context: vscode.ExtensionContext) {
    // Register code action provider for reuse suggestions
    const reuseProvider = vscode.languages.registerCodeActionsProvider(
      ['typescript', 'javascript', 'python'],
      new ReuseSuggestionProvider(this.catalogProvider)
    );
    
    // Register hover provider for function information
    const hoverProvider = vscode.languages.registerHoverProvider(
      ['typescript', 'javascript'],
      new FunctionHoverProvider(this.catalogProvider)
    );
    
    // Register completion provider for function suggestions
    const completionProvider = vscode.languages.registerCompletionItemProvider(
      ['typescript', 'javascript'],
      new FunctionCompletionProvider(this.catalogProvider),
      '.' // Trigger on dot notation
    );
    
    context.subscriptions.push(reuseProvider, hoverProvider, completionProvider);
  }
}

class ReuseSuggestionProvider implements vscode.CodeActionProvider {
  constructor(private catalogProvider: ServiceCatalogProvider) {}

  async provideCodeActions(
    document: vscode.TextDocument,
    range: vscode.Range | vscode.Selection,
    context: vscode.CodeActionContext
  ): Promise<vscode.CodeAction[]> {
    const selectedText = document.getText(range);
    const suggestions = await this.catalogProvider.findSimilarFunctions(selectedText);
    
    return suggestions.map(suggestion => {
      const action = new vscode.CodeAction(
        `💡 Reuse: ${suggestion.function.name}`,
        vscode.CodeActionKind.Refactor
      );
      
      action.edit = new vscode.WorkspaceEdit();
      action.edit.replace(document.uri, range, suggestion.codeExample);
      
      return action;
    });
  }
}
```

## 4. Linting Integration & Redundancy Prevention

### ESLint Plugin for Redundancy Detection
```typescript
// eslint-plugin-reuse-catalog/src/rules/no-redundant-implementation.ts
import { Rule } from 'eslint';

export const noRedundantImplementation: Rule.RuleModule = {
  meta: {
    type: 'suggestion',
    docs: {
      description: 'Prevent implementation of functions that already exist in the service catalog',
      category: 'Best Practices',
      recommended: true
    },
    fixable: 'code',
    schema: [
      {
        type: 'object',
        properties: {
          catalogUrl: { type: 'string' },
          minSimilarity: { type: 'number', minimum: 0, maximum: 100 },
          excludePatterns: { type: 'array', items: { type: 'string' } }
        },
        additionalProperties: false
      }
    ]
  },

  create(context) {
    const options = context.options[0] || {};
    const catalogUrl = options.catalogUrl || process.env.SERVICE_CATALOG_URL;
    const minSimilarity = options.minSimilarity || 80;

    if (!catalogUrl) {
      return {}; // Skip if no catalog configured
    }

    return {
      FunctionDeclaration(node) {
        this.checkFunction(node, context, catalogUrl, minSimilarity);
      },
      
      MethodDefinition(node) {
        if (node.accessibility === 'public') {
          this.checkFunction(node, context, catalogUrl, minSimilarity);
        }
      }
    };
  },

  async checkFunction(node: any, context: Rule.RuleContext, catalogUrl: string, minSimilarity: number) {
    const functionSignature = this.extractSignature(node);
    const functionBody = this.extractBody(node);
    
    try {
      const similarFunctions = await this.searchCatalog(catalogUrl, {
        signature: functionSignature,
        body: functionBody,
        minSimilarity
      });

      if (similarFunctions.length > 0) {
        const bestMatch = similarFunctions[0];
        
        context.report({
          node,
          message: `Similar function exists: ${bestMatch.name} (${bestMatch.similarity}% similar). Consider reusing instead of reimplementing.`,
          data: {
            existingFunction: bestMatch.name,
            service: bestMatch.service,
            similarity: bestMatch.similarity
          },
          suggest: [
            {
              desc: `Replace with call to ${bestMatch.name}`,
              fix: (fixer) => {
                return fixer.replaceText(node, this.generateReuseCode(bestMatch));
              }
            }
          ]
        });
      }
    } catch (error) {
      // Catalog service unavailable - skip check
      console.warn('Service catalog unavailable:', error.message);
    }
  }
};
```

### Pre-commit Hook Integration
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "🔍 Checking for redundant implementations..."

# Run catalog-aware linting
npm run lint:catalog

if [ $? -ne 0 ]; then
    echo "❌ Redundant implementations detected. Consider reusing existing functions."
    echo "💡 Run 'npm run catalog:suggest' for reuse suggestions."
    exit 1
fi

echo "✅ No redundant implementations found."
```

## 5. Dependency Analysis & Visualization

### Dependency Graph Generation
```typescript
// src/analysis/dependency-analyzer.ts
export class DependencyAnalyzer {
  async generateGraph(services: ServiceCatalogEntry[]): Promise<DependencyGraph> {
    const graph: DependencyGraph = {
      nodes: [],
      edges: [],
      clusters: []
    };

    // Create nodes for each service
    services.forEach(service => {
      graph.nodes.push({
        id: service.service.name,
        type: 'service',
        label: service.service.name,
        version: service.service.version,
        metadata: {
          functionCount: service.functions.length,
          apiCount: service.apis.length,
          complexity: this.calculateServiceComplexity(service)
        }
      });

      // Create nodes for reusable functions
      service.functions
        .filter(func => func.reusabilityScore > 70)
        .forEach(func => {
          graph.nodes.push({
            id: `${service.service.name}::${func.name}`,
            type: 'function',
            label: func.name,
            parent: service.service.name,
            metadata: {
              reusabilityScore: func.reusabilityScore,
              usageCount: func.usageCount,
              complexity: func.complexity
            }
          });
        });
    });

    // Create edges for dependencies
    services.forEach(service => {
      service.service.dependencies.forEach(dep => {
        graph.edges.push({
          source: service.service.name,
          target: dep.service,
          type: dep.type,
          weight: dep.criticality === 'critical' ? 3 : 
                  dep.criticality === 'important' ? 2 : 1,
          functions: dep.functions
        });
      });
    });

    return graph;
  }

  async detectCircularDependencies(graph: DependencyGraph): Promise<CircularDependency[]> {
    const visited = new Set<string>();
    const recursionStack = new Set<string>();
    const cycles: CircularDependency[] = [];

    const dfs = (nodeId: string, path: string[]): void => {
      visited.add(nodeId);
      recursionStack.add(nodeId);

      const edges = graph.edges.filter(edge => edge.source === nodeId);
      
      for (const edge of edges) {
        if (!visited.has(edge.target)) {
          dfs(edge.target, [...path, edge.target]);
        } else if (recursionStack.has(edge.target)) {
          // Found a cycle
          const cycleStart = path.indexOf(edge.target);
          cycles.push({
            cycle: path.slice(cycleStart),
            severity: this.calculateCycleSeverity(path.slice(cycleStart), graph)
          });
        }
      }

      recursionStack.delete(nodeId);
    };

    graph.nodes
      .filter(node => node.type === 'service')
      .forEach(node => {
        if (!visited.has(node.id)) {
          dfs(node.id, [node.id]);
        }
      });

    return cycles;
  }
}
```

### Interactive Catalog Dashboard
```typescript
// src/dashboard/catalog-dashboard.tsx
import React, { useState, useEffect } from 'react';
import { ServiceCatalogAPI } from '../api/catalog-api';

export const CatalogDashboard: React.FC = () => {
  const [services, setServices] = useState<ServiceCatalogEntry[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<CatalogFilters>({
    minReusabilityScore: 70,
    complexity: 'all',
    stability: 'all'
  });

  const filteredFunctions = services
    .flatMap(service => service.functions)
    .filter(func => {
      return func.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
             func.reusabilityScore >= filters.minReusabilityScore &&
             (filters.complexity === 'all' || func.complexity === filters.complexity) &&
             (filters.stability === 'all' || func.stability === filters.stability);
    })
    .sort((a, b) => b.reusabilityScore - a.reusabilityScore);

  return (
    <div className="catalog-dashboard">
      <header>
        <h1>🧠 Service Catalog</h1>
        <div className="search-section">
          <input
            type="text"
            placeholder="Search functions, services, or descriptions..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
          />
          <CatalogFilters filters={filters} onChange={setFilters} />
        </div>
      </header>

      <main>
        <div className="catalog-stats">
          <StatCard 
            title="Total Services" 
            value={services.length} 
            icon="🏗️"
          />
          <StatCard 
            title="Reusable Functions" 
            value={filteredFunctions.length} 
            icon="🔧"
          />
          <StatCard 
            title="Average Reusability" 
            value={`${Math.round(filteredFunctions.reduce((sum, f) => sum + f.reusabilityScore, 0) / filteredFunctions.length)}%`}
            icon="📊"
          />
        </div>

        <div className="function-grid">
          {filteredFunctions.map(func => (
            <FunctionCard 
              key={`${func.sourceLocation.repository}::${func.name}`}
              function={func}
              onUse={handleUseFunction}
            />
          ))}
        </div>

        <div className="dependency-visualization">
          <DependencyGraph services={services} />
        </div>
      </main>
    </div>
  );
};

const FunctionCard: React.FC<{ function: FunctionCatalogEntry; onUse: (func: FunctionCatalogEntry) => void }> = ({ function: func, onUse }) => (
  <div className="function-card">
    <header>
      <h3>{func.name}</h3>
      <div className="badges">
        <span className={`complexity ${func.complexity}`}>{func.complexity}</span>
        <span className={`stability ${func.stability}`}>{func.stability}</span>
        <span className="reusability">{func.reusabilityScore}% reusable</span>
      </div>
    </header>
    
    <p className="description">{func.description}</p>
    
    <div className="signature">
      <code>{func.signature}</code>
    </div>
    
    <div className="usage-info">
      <span>Used {func.usageCount} times</span>
      <span>Modified {func.lastModified.toLocaleDateString()}</span>
    </div>
    
    <footer>
      <button onClick={() => onUse(func)}>
        📋 Copy Usage
      </button>
      <a href={`${func.sourceLocation.repository}/blob/main/${func.sourceLocation.file}#L${func.sourceLocation.line}`}>
        📝 View Source
      </a>
    </footer>
  </div>
);
```

## 6. Usage Analytics & Optimization

### Function Usage Tracking
```typescript
// src/analytics/usage-tracker.ts
export class FunctionUsageTracker {
  async trackUsage(functionId: string, context: UsageContext): Promise<void> {
    const usageEvent: UsageEvent = {
      functionId,
      timestamp: new Date(),
      context: {
        service: context.callingService,
        method: context.callingMethod,
        userId: context.userId,
        sessionId: context.sessionId
      },
      metrics: {
        executionTime: context.executionTime,
        memoryUsage: context.memoryUsage,
        success: context.success,
        errorType: context.errorType
      }
    };

    await this.analyticsService.recordEvent(usageEvent);
    await this.updateFunctionMetrics(functionId, usageEvent);
  }

  async generateUsageReport(timeframe: Timeframe): Promise<UsageReport> {
    const usageData = await this.analyticsService.getUsageData(timeframe);
    
    return {
      topReusedFunctions: this.getTopReusedFunctions(usageData),
      underutilizedFunctions: this.getUnderutilizedFunctions(usageData),
      reuseOpportunities: this.identifyReuseOpportunities(usageData),
      costSavings: this.calculateCostSavings(usageData),
      recommendations: this.generateRecommendations(usageData)
    };
  }

  private identifyReuseOpportunities(usageData: UsageData[]): ReuseOpportunity[] {
    const opportunities: ReuseOpportunity[] = [];
    
    // Find patterns of similar function implementations
    const functionGroups = this.groupSimilarFunctions(usageData);
    
    functionGroups.forEach(group => {
      if (group.functions.length > 1) {
        opportunities.push({
          type: 'consolidation',
          description: `${group.functions.length} similar functions can be consolidated`,
          functions: group.functions,
          potentialSavings: group.functions.length * 2, // 2 hours per function
          complexity: group.averageComplexity
        });
      }
    });

    return opportunities;
  }
}
```

## 7. OpenAPI & AsyncAPI Integration

### API Introspection
```typescript
// src/integration/api-introspection.ts
export class APIIntrospectionService {
  async integrateOpenAPISpecs(services: ServiceCatalogEntry[]): Promise<ServiceCatalogEntry[]> {
    for (const service of services) {
      const openApiSpec = await this.loadOpenAPISpec(service.service.repository);
      
      if (openApiSpec) {
        // Enhance service catalog with OpenAPI information
        service.apis = this.extractAPIsFromSpec(openApiSpec);
        service.functions = this.enhanceFunctionsWithAPIInfo(service.functions, openApiSpec);
      }
    }

    return services;
  }

  async integrateAsyncAPISpecs(services: ServiceCatalogEntry[]): Promise<ServiceCatalogEntry[]> {
    for (const service of services) {
      const asyncApiSpec = await this.loadAsyncAPISpec(service.service.repository);
      
      if (asyncApiSpec) {
        // Enhance service catalog with AsyncAPI information
        service.events = this.extractEventsFromSpec(asyncApiSpec);
        service.functions = this.enhanceFunctionsWithEventInfo(service.functions, asyncApiSpec);
      }
    }

    return services;
  }

  private extractAPIsFromSpec(spec: OpenAPISpec): APICatalogEntry[] {
    const apis: APICatalogEntry[] = [];

    Object.entries(spec.paths).forEach(([path, pathItem]) => {
      Object.entries(pathItem).forEach(([method, operation]) => {
        if (operation && typeof operation === 'object') {
          apis.push({
            endpoint: path,
            method: method.toUpperCase() as any,
            description: operation.summary || operation.description || '',
            parameters: this.extractParameters(operation.parameters || []),
            responses: this.extractResponses(operation.responses || {}),
            authentication: this.extractAuthInfo(operation.security || []),
            rateLimit: this.extractRateLimits(operation),
            examples: this.extractAPIExamples(operation),
            openApiRef: `${spec.info.title}#${path}:${method}`
          });
        }
      });
    });

    return apis;
  }
}
```

## 8. Quality Gates & Enforcement

### Reuse Metrics & KPIs
```yaml
# Quality gates for intelligent reuse
reuse_quality_gates:
  function_reuse_rate:
    description: "Percentage of functions marked as reusable that are actually reused"
    metric: "reused_functions / total_reusable_functions * 100"
    threshold: 60
    blocking: false

  redundancy_detection:
    description: "Percentage of new functions flagged for potential redundancy"
    metric: "flagged_redundant_functions / new_functions * 100"
    threshold: 5
    blocking: true

  catalog_coverage:
    description: "Percentage of services registered in catalog"
    metric: "cataloged_services / total_services * 100"
    threshold: 95
    blocking: true

  dependency_health:
    description: "Services with circular dependencies"
    metric: "services_with_circular_deps"
    threshold: 0
    blocking: true

  reusability_score:
    description: "Average reusability score of cataloged functions"
    metric: "avg_reusability_score"
    threshold: 70
    blocking: false
```

### Automated Enforcement
```typescript
// src/enforcement/reuse-enforcer.ts
export class ReuseEnforcer {
  async enforceReusePolicy(project: ProjectContext): Promise<EnforcementResult> {
    const violations: PolicyViolation[] = [];

    // Check for service catalog registration
    const isRegistered = await this.checkServiceRegistration(project);
    if (!isRegistered) {
      violations.push({
        type: 'missing_registration',
        severity: 'error',
        message: 'Service not registered in catalog',
        fix: 'Run npm run register:service'
      });
    }

    // Check for redundant implementations
    const redundancies = await this.detectRedundancies(project);
    violations.push(...redundancies);

    // Check catalog integration
    const catalogIntegration = await this.checkCatalogIntegration(project);
    if (!catalogIntegration.hasLinting) {
      violations.push({
        type: 'missing_linting',
        severity: 'warning', 
        message: 'ESLint catalog integration not configured',
        fix: 'Add eslint-plugin-reuse-catalog to ESLint config'
      });
    }

    return {
      passed: violations.filter(v => v.severity === 'error').length === 0,
      violations,
      recommendations: this.generateRecommendations(violations)
    };
  }
}
```

---

## 📋 **Implementation Checklist**

### Catalog Infrastructure
- [ ] Set up service registry schema and database
- [ ] Implement automatic catalog generation at build time
- [ ] Create dependency analysis and circular dependency detection
- [ ] Set up catalog API and search functionality

### IDE Integration
- [ ] Create Cursor extension for reuse suggestions
- [ ] Implement VS Code extension with code actions
- [ ] Add hover providers for function information
- [ ] Create completion providers for intelligent suggestions

### Linting & Prevention
- [ ] Develop ESLint plugin for redundancy detection
- [ ] Set up pre-commit hooks for reuse checking
- [ ] Create automated similarity analysis
- [ ] Implement reuse suggestion notifications

### Analytics & Optimization
- [ ] Implement usage tracking and analytics
- [ ] Create reuse opportunity identification
- [ ] Build cost savings calculations
- [ ] Set up performance monitoring for catalog

### Dashboard & Visualization
- [ ] Build interactive catalog dashboard
- [ ] Create dependency graph visualization
- [ ] Implement search and filtering capabilities
- [ ] Add usage analytics and reporting

---

## 🎯 **Success Metrics**

- **Function Reuse Rate:** 60% of cataloged functions are reused across services
- **Redundancy Reduction:** 80% reduction in duplicate function implementations
- **Development Speed:** 25% faster development through function reuse
- **Code Quality:** 90% of reused functions have high reusability scores
- **Catalog Coverage:** 95% of services registered and actively maintained in catalog 