# QC-01: Comprehensive Testing Standards & Automation

## Purpose & Scope

Comprehensive testing standards covering the complete testing lifecycle from strategy through implementation to automation. This rule establishes unified standards for test pyramid strategy, test-driven development, implementation patterns for unit/integration/e2e tests, and full CI/CD automation to ensure high-quality, reliable software delivery.

## Core Standards

### 1. Testing Strategy & Architecture

#### Test Pyramid Framework

**Optimal Test Distribution:**
```typescript
// testing/test-pyramid-strategy.ts
export interface TestPyramid {
  unit: UnitTestStrategy;
  integration: IntegrationTestStrategy;
  e2e: E2ETestStrategy;
  performance: PerformanceTestStrategy;
  security: SecurityTestStrategy;
}

export interface TestDistribution {
  unit: { target: number; minimum: number; description: string };
  integration: { target: number; minimum: number; description: string };
  e2e: { target: number; minimum: number; description: string };
}

export class TestStrategy {
  private config: TestConfig;
  
  constructor(config: TestConfig) {
    this.config = config;
  }
  
  getTestDistribution(): TestDistribution {
    return {
      unit: {
        target: 70,
        minimum: 60,
        description: 'Fast, isolated tests for individual functions/classes'
      },
      integration: {
        target: 20,
        minimum: 15,
        description: 'Tests for component interactions and API contracts'
      },
      e2e: {
        target: 10,
        minimum: 5,
        description: 'Full user journey tests through the UI'
      }
    };
  }
  
  validateTestBalance(results: TestResults): ValidationResult {
    const distribution = this.getTestDistribution();
    const total = results.unit + results.integration + results.e2e;
    
    const actual = {
      unit: (results.unit / total) * 100,
      integration: (results.integration / total) * 100,
      e2e: (results.e2e / total) * 100
    };
    
    const violations: string[] = [];
    
    if (actual.unit < distribution.unit.minimum) {
      violations.push(`Unit test coverage too low: ${actual.unit}% (minimum: ${distribution.unit.minimum}%)`);
    }
    
    if (actual.e2e > 15) {
      violations.push(`Too many E2E tests: ${actual.e2e}% (maximum: 15%)`);
    }
    
    return {
      valid: violations.length === 0,
      violations,
      recommendations: this.generateRecommendations(actual, distribution)
    };
  }
}
```

#### Test Framework Configuration

**Comprehensive Framework Setup:**
```typescript
// testing/framework-configuration.ts
export interface TestFrameworkConfig {
  unit: {
    framework: 'jest' | 'vitest' | 'mocha';
    runner: string;
    coverage: CoverageConfig;
    mocking: MockConfig;
  };
  integration: {
    framework: 'jest' | 'supertest' | 'testcontainers';
    database: DatabaseTestConfig;
    external: ExternalServiceConfig;
  };
  e2e: {
    framework: 'playwright' | 'cypress' | 'puppeteer';
    browsers: string[];
    environment: E2EEnvironmentConfig;
  };
}

export const ENTERPRISE_TEST_CONFIG: TestFrameworkConfig = {
  unit: {
    framework: 'jest',
    runner: 'jest',
    coverage: {
      threshold: {
        global: {
          branches: 90,
          functions: 90,
          lines: 90,
          statements: 90
        }
      },
      reporters: ['text', 'lcov', 'html', 'json-summary'],
      collectCoverageFrom: [
        'src/**/*.{ts,js}',
        '!src/**/*.d.ts',
        '!src/**/*.test.{ts,js}',
        '!src/**/__tests__/**',
        '!src/test-utils/**'
      ]
    },
    mocking: {
      mockImplementation: 'jest',
      autoMock: false,
      clearMocks: true,
      resetMocks: true
    }
  },
  integration: {
    framework: 'supertest',
    database: {
      strategy: 'testcontainers',
      cleanup: 'after-each',
      isolation: 'transaction'
    },
    external: {
      strategy: 'wiremock',
      contracts: true,
      fallback: 'real-service'
    }
  },
  e2e: {
    framework: 'playwright',
    browsers: ['chromium', 'firefox', 'webkit'],
    environment: {
      baseUrl: 'http://localhost:3000',
      parallel: true,
      retries: 2,
      timeout: 30000
    }
  }
};
```

### 2. Test-Driven Development (TDD)

#### TDD Implementation Framework

**Red-Green-Refactor Cycle:**
```typescript
// testing/tdd-workflow.ts
export class TDDWorkflow {
  private testRunner: TestRunner;
  private coverage: CoverageTracker;
  
  constructor(testRunner: TestRunner, coverage: CoverageTracker) {
    this.testRunner = testRunner;
    this.coverage = coverage;
  }
  
  async executeRedGreenRefactorCycle(
    feature: FeatureSpec
  ): Promise<TDDCycleResult> {
    const cycle: TDDCycleResult = {
      steps: [],
      finalState: 'unknown',
      coverage: 0,
      duration: 0
    };
    
    const startTime = Date.now();
    
    try {
      // RED: Write failing test first
      const redStep = await this.redPhase(feature);
      cycle.steps.push(redStep);
      
      if (!redStep.success) {
        throw new Error('Red phase failed - test should fail initially');
      }
      
      // GREEN: Write minimal code to pass
      const greenStep = await this.greenPhase(feature);
      cycle.steps.push(greenStep);
      
      if (!greenStep.success) {
        throw new Error('Green phase failed - cannot make test pass');
      }
      
      // REFACTOR: Improve code while keeping tests green
      const refactorStep = await this.refactorPhase(feature);
      cycle.steps.push(refactorStep);
      
      cycle.finalState = 'completed';
      cycle.coverage = await this.coverage.getCoverage();
      
    } catch (error) {
      cycle.finalState = 'failed';
      cycle.errorMessage = error.message;
    }
    
    cycle.duration = Date.now() - startTime;
    return cycle;
  }
  
  private async redPhase(feature: FeatureSpec): Promise<TDDStep> {
    const testCode = this.generateFailingTest(feature);
    await this.writeTestFile(feature.testPath, testCode);
    
    const result = await this.testRunner.run({
      testPath: feature.testPath,
      expectFailure: true
    });
    
    return {
      phase: 'red',
      success: result.failed && result.failureReason === 'expected',
      duration: result.duration,
      output: result.output
    };
  }
  
  private async greenPhase(feature: FeatureSpec): Promise<TDDStep> {
    const implementationCode = this.generateMinimalImplementation(feature);
    await this.writeImplementationFile(feature.implementationPath, implementationCode);
    
    const result = await this.testRunner.run({
      testPath: feature.testPath,
      expectSuccess: true
    });
    
    return {
      phase: 'green',
      success: result.passed,
      duration: result.duration,
      output: result.output
    };
  }
  
  private async refactorPhase(feature: FeatureSpec): Promise<TDDStep> {
    const refactoredCode = await this.improveImplementation(feature);
    await this.writeImplementationFile(feature.implementationPath, refactoredCode);
    
    const result = await this.testRunner.run({
      testPath: feature.testPath,
      expectSuccess: true
    });
    
    return {
      phase: 'refactor',
      success: result.passed,
      duration: result.duration,
      output: result.output,
      improvements: await this.analyzeImprovements(feature)
    };
  }
}
```

### 3. Unit Test Implementation Patterns

#### Comprehensive Unit Test Standards

**Unit Testing Patterns:**
```typescript
// tests/unit/user-service.test.ts
import { UserService } from '../../src/services/user-service';
import { UserRepository } from '../../src/repositories/user-repository';
import { EmailService } from '../../src/services/email-service';
import { ValidationError, NotFoundError } from '../../src/errors';

// Mock dependencies
jest.mock('../../src/repositories/user-repository');
jest.mock('../../src/services/email-service');

describe('UserService', () => {
  let userService: UserService;
  let mockUserRepository: jest.Mocked<UserRepository>;
  let mockEmailService: jest.Mocked<EmailService>;

  beforeEach(() => {
    // Create fresh mocks for each test
    mockUserRepository = new UserRepository() as jest.Mocked<UserRepository>;
    mockEmailService = new EmailService() as jest.Mocked<EmailService>;
    
    userService = new UserService(mockUserRepository, mockEmailService);
    
    // Reset all mocks
    jest.clearAllMocks();
  });

  describe('createUser', () => {
    const validUserData = {
      email: 'test@example.com',
      name: 'Test User',
      password: 'SecurePass123!'
    };

    it('should create user with valid data', async () => {
      // Arrange
      const expectedUser = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        ...validUserData,
        password: undefined, // Password should be omitted from response
        createdAt: new Date('2024-01-20T10:00:00Z'),
        updatedAt: new Date('2024-01-20T10:00:00Z')
      };
      
      mockUserRepository.findByEmail.mockResolvedValue(null);
      mockUserRepository.create.mockResolvedValue(expectedUser);
      mockEmailService.sendWelcomeEmail.mockResolvedValue(undefined);

      // Act
      const result = await userService.createUser(validUserData);

      // Assert
      expect(result).toEqual(expectedUser);
      expect(mockUserRepository.findByEmail).toHaveBeenCalledWith(validUserData.email);
      expect(mockUserRepository.create).toHaveBeenCalledWith({
        ...validUserData,
        password: expect.any(String) // Hashed password
      });
      expect(mockEmailService.sendWelcomeEmail).toHaveBeenCalledWith(
        expectedUser.email,
        expectedUser.name
      );
    });

    it('should throw ValidationError for invalid email', async () => {
      // Arrange
      const invalidUserData = {
        ...validUserData,
        email: 'invalid-email'
      };

      // Act & Assert
      await expect(userService.createUser(invalidUserData))
        .rejects
        .toThrow(ValidationError);
      
      expect(mockUserRepository.findByEmail).not.toHaveBeenCalled();
      expect(mockUserRepository.create).not.toHaveBeenCalled();
    });

    // Parameterized tests for validation scenarios
    test.each([
      ['empty email', { email: '', name: 'Test', password: 'Pass123!' }, 'Email is required'],
      ['invalid email format', { email: 'invalid', name: 'Test', password: 'Pass123!' }, 'Invalid email format'],
      ['empty name', { email: 'test@example.com', name: '', password: 'Pass123!' }, 'Name is required'],
      ['short password', { email: 'test@example.com', name: 'Test', password: '123' }, 'Password too weak'],
      ['weak password', { email: 'test@example.com', name: 'Test', password: 'password' }, 'Password too weak']
    ])('should reject %s', async (scenario, userData, expectedError) => {
      await expect(userService.createUser(userData))
        .rejects
        .toThrow(expectedError);
    });
  });
});
```

#### Test Utilities & Helpers

**Reusable Test Components:**
```typescript
// tests/utils/test-helpers.ts
export class TestDataBuilder {
  static createUser(overrides: Partial<User> = {}): User {
    return {
      id: '123e4567-e89b-12d3-a456-426614174000',
      email: 'test@example.com',
      name: 'Test User',
      status: 'active',
      role: 'user',
      createdAt: new Date('2024-01-20T10:00:00Z'),
      updatedAt: new Date('2024-01-20T10:00:00Z'),
      ...overrides
    };
  }

  static createCreateUserRequest(overrides: Partial<CreateUserRequest> = {}): CreateUserRequest {
    return {
      email: 'test@example.com',
      name: 'Test User',
      password: 'SecurePass123!',
      ...overrides
    };
  }

  static createApiResponse<T>(data: T, overrides: Partial<ApiResponse<T>> = {}): ApiResponse<T> {
    return {
      data,
      meta: {
        timestamp: '2024-01-20T10:00:00Z',
        version: 'v2',
        requestId: 'req-123'
      },
      ...overrides
    };
  }
}

export class MockFactory {
  static createUserRepository(): jest.Mocked<UserRepository> {
    return {
      findById: jest.fn(),
      findByEmail: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
      delete: jest.fn(),
      findMany: jest.fn(),
      count: jest.fn()
    };
  }

  static createEmailService(): jest.Mocked<EmailService> {
    return {
      sendWelcomeEmail: jest.fn(),
      sendPasswordResetEmail: jest.fn(),
      sendNotificationEmail: jest.fn()
    };
  }
}
```

### 4. Integration Test Implementation

#### Database Integration Testing

**Database Test Patterns:**
```typescript
// tests/integration/user-repository.test.ts
import { UserRepository } from '../../src/repositories/user-repository';
import { TestDatabase } from '../utils/test-database';
import { TestDataBuilder } from '../utils/test-helpers';

describe('UserRepository Integration', () => {
  let testDb: TestDatabase;
  let userRepository: UserRepository;

  beforeAll(async () => {
    testDb = new TestDatabase();
    await testDb.initialize();
    userRepository = new UserRepository(testDb.getConnection());
  });

  afterAll(async () => {
    await testDb.cleanup();
  });

  beforeEach(async () => {
    await testDb.clearTables(['users']);
  });

  describe('create', () => {
    it('should create user in database', async () => {
      // Arrange
      const userData = TestDataBuilder.createCreateUserRequest();

      // Act
      const createdUser = await userRepository.create(userData);

      // Assert
      expect(createdUser).toMatchObject({
        email: userData.email,
        name: userData.name,
        status: 'active'
      });
      expect(createdUser.id).toBeDefined();
      expect(createdUser.createdAt).toBeInstanceOf(Date);

      // Verify in database
      const dbUser = await testDb.query('SELECT * FROM users WHERE id = ?', [createdUser.id]);
      expect(dbUser).toHaveLength(1);
      expect(dbUser[0].email).toBe(userData.email);
    });
  });
});
```

#### API Integration Testing

**API Contract Testing:**
```typescript
// tests/integration/user-api.test.ts
import request from 'supertest';
import { createTestApp } from '../utils/test-app';
import { TestDatabase } from '../utils/test-database';
import { TestDataBuilder } from '../utils/test-helpers';

describe('User API Integration', () => {
  let app: Express.Application;
  let testDb: TestDatabase;

  beforeAll(async () => {
    testDb = new TestDatabase();
    await testDb.initialize();
    app = await createTestApp(testDb.getConnection());
  });

  afterAll(async () => {
    await testDb.cleanup();
  });

  beforeEach(async () => {
    await testDb.clearTables(['users']);
  });

  describe('POST /api/v2/users', () => {
    it('should create user successfully', async () => {
      // Arrange
      const userData = TestDataBuilder.createCreateUserRequest();

      // Act
      const response = await request(app)
        .post('/api/v2/users')
        .send(userData)
        .expect(201);

      // Assert
      expect(response.body).toMatchObject({
        data: {
          email: userData.email,
          name: userData.name,
          status: 'active'
        },
        meta: {
          version: 'v2'
        }
      });
      expect(response.headers.location).toMatch(/\/api\/v2\/users\/[a-f0-9-]+/);
    });

    it('should return 409 for duplicate email', async () => {
      // Arrange
      const userData = TestDataBuilder.createCreateUserRequest();
      await testDb.insertUser(userData);

      // Act
      const response = await request(app)
        .post('/api/v2/users')
        .send(userData)
        .expect(409);

      // Assert
      expect(response.body).toMatchObject({
        type: 'https://api.example.com/problems/conflict',
        title: 'Conflict',
        status: 409,
        detail: expect.stringContaining('already exists')
      });
    });
  });
});
```

### 5. End-to-End Testing

#### E2E Test Implementation

**User Journey Testing:**
```typescript
// tests/e2e/user-registration.spec.ts
import { test, expect, Page } from '@playwright/test';
import { TestDataBuilder } from '../utils/test-helpers';

test.describe('User Registration Flow', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;
    await page.goto('/register');
  });

  test('should complete user registration successfully', async () => {
    // Arrange
    const userData = TestDataBuilder.createCreateUserRequest();

    // Act - Fill registration form
    await page.fill('[data-testid="email-input"]', userData.email);
    await page.fill('[data-testid="name-input"]', userData.name);
    await page.fill('[data-testid="password-input"]', userData.password);
    await page.fill('[data-testid="confirm-password-input"]', userData.password);
    
    // Submit form
    await page.click('[data-testid="register-button"]');

    // Assert - Check success state
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="success-message"]')).toContainText(
      'Registration successful! Please check your email for verification.'
    );

    // Verify redirect to login
    await expect(page).toHaveURL('/login?registered=true');
  });

  test('should show validation errors for invalid input', async () => {
    // Act - Submit empty form
    await page.click('[data-testid="register-button"]');

    // Assert - Check validation errors
    await expect(page.locator('[data-testid="email-error"]')).toContainText('Email is required');
    await expect(page.locator('[data-testid="name-error"]')).toContainText('Name is required');
    await expect(page.locator('[data-testid="password-error"]')).toContainText('Password is required');

    // Form should not be submitted
    await expect(page).toHaveURL('/register');
  });

  test('should handle server error gracefully', async () => {
    // Arrange - Mock server error
    await page.route('/api/v2/users', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          type: 'https://api.example.com/problems/internal-server-error',
          title: 'Internal Server Error',
          status: 500
        })
      });
    });

    const userData = TestDataBuilder.createCreateUserRequest();

    // Act
    await page.fill('[data-testid="email-input"]', userData.email);
    await page.fill('[data-testid="name-input"]', userData.name);
    await page.fill('[data-testid="password-input"]', userData.password);
    await page.fill('[data-testid="confirm-password-input"]', userData.password);
    await page.click('[data-testid="register-button"]');

    // Assert - Check error handling
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toContainText(
      'Registration failed. Please try again later.'
    );
  });
});
```

### 6. Test Automation & CI/CD Integration

#### Comprehensive CI/CD Pipeline

**Multi-Stage Test Pipeline:**
```yaml
# .github/workflows/comprehensive-test.yml
name: Comprehensive Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  NODE_VERSION: '18'
  PNPM_VERSION: '8.15.0'

jobs:
  test-unit:
    name: Unit Tests
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}

      - name: Setup pnpm
        uses: pnpm/action-setup@v2
        with:
          version: ${{ env.PNPM_VERSION }}

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Run unit tests
        run: pnpm test:unit --coverage --reporter=ci-pipeline
        env:
          CI: true

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          file: ./coverage/lcov.info
          flags: unit
          name: unit-tests

      - name: Quality Gate - Coverage Check
        run: |
          coverage=$(node -e "console.log(JSON.parse(require('fs').readFileSync('./coverage/coverage-summary.json')).total.lines.pct)")
          if (( $(echo "$coverage < 90" | bc -l) )); then
            echo "Coverage $coverage% is below 90% threshold"
            exit 1
          fi

  test-integration:
    name: Integration Tests
    runs-on: ubuntu-latest
    timeout-minutes: 15

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: testdb
          POSTGRES_USER: testuser
          POSTGRES_PASSWORD: testpass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Run database migrations
        run: pnpm db:migrate
        env:
          DATABASE_URL: postgresql://testuser:testpass@localhost:5432/testdb

      - name: Run integration tests
        run: pnpm test:integration --coverage --reporter=ci-pipeline
        env:
          CI: true
          DATABASE_URL: postgresql://testuser:testpass@localhost:5432/testdb
          REDIS_URL: redis://localhost:6379

  test-e2e:
    name: E2E Tests
    runs-on: ubuntu-latest
    timeout-minutes: 30
    needs: [test-unit, test-integration]

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: e2edb
          POSTGRES_USER: e2euser
          POSTGRES_PASSWORD: e2epass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    strategy:
      matrix:
        browser: [chromium, firefox, webkit]
        shard: [1, 2, 3, 4]

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Install Playwright browsers
        run: pnpm playwright install ${{ matrix.browser }} --with-deps

      - name: Build application
        run: pnpm build

      - name: Start application
        run: |
          pnpm start &
          npx wait-on http://localhost:3000 --timeout 60000
        env:
          DATABASE_URL: postgresql://e2euser:e2epass@localhost:5432/e2edb

      - name: Run E2E tests
        run: pnpm test:e2e --project=${{ matrix.browser }} --shard=${{ matrix.shard }}/4
        env:
          CI: true

      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: e2e-results-${{ matrix.browser }}-${{ matrix.shard }}
          path: |
            test-results/
            playwright-report/
          retention-days: 30

  quality-gate:
    name: Quality Gate
    runs-on: ubuntu-latest
    needs: [test-unit, test-integration, test-e2e]
    if: always()

    steps:
      - name: Check test results
        run: |
          if [[ "${{ needs.test-unit.result }}" != "success" ]]; then
            echo "Unit tests failed"
            exit 1
          fi
          if [[ "${{ needs.test-integration.result }}" != "success" ]]; then
            echo "Integration tests failed"
            exit 1
          fi
          if [[ "${{ needs.test-e2e.result }}" != "success" ]]; then
            echo "E2E tests failed"
            exit 1
          fi
          echo "All tests passed - Quality gate satisfied"
```

#### Test Reporting & Analytics

**Comprehensive Test Reporting:**
```typescript
// testing/reporting/test-reporter.ts
export class ComprehensiveTestReporter {
  private results: TestResults[] = [];
  
  async generateReport(): Promise<TestReport> {
    const summary = this.calculateSummary();
    const coverage = await this.getCoverageReport();
    const performance = this.getPerformanceMetrics();
    const trends = await this.getTrendAnalysis();
    
    return {
      summary,
      coverage,
      performance,
      trends,
      timestamp: new Date().toISOString(),
      buildInfo: this.getBuildInfo()
    };
  }
  
  private calculateSummary(): TestSummary {
    const total = this.results.length;
    const passed = this.results.filter(r => r.status === 'passed').length;
    const failed = this.results.filter(r => r.status === 'failed').length;
    const skipped = this.results.filter(r => r.status === 'skipped').length;
    
    return {
      total,
      passed,
      failed,
      skipped,
      passRate: (passed / total) * 100,
      duration: this.results.reduce((sum, r) => sum + r.duration, 0)
    };
  }
  
  async getCoverageReport(): Promise<CoverageReport> {
    return {
      lines: await this.getCoverageMetric('lines'),
      branches: await this.getCoverageMetric('branches'),
      functions: await this.getCoverageMetric('functions'),
      statements: await this.getCoverageMetric('statements')
    };
  }
}
```

## Implementation Requirements

### 1. Testing Workflow Integration

```yaml
# testing-workflow-standards.yaml
development_workflow:
  pre_commit:
    - "Run affected unit tests"
    - "Validate test coverage requirements"
    - "Check test naming conventions"
    - "Verify mock configurations"
    
  feature_development:
    - "Write failing tests first (TDD)"
    - "Implement minimal passing code"
    - "Refactor with tests green"
    - "Add integration tests for new APIs"
    
  pull_request:
    - "Run full test suite"
    - "Generate coverage report"
    - "Execute affected E2E tests"
    - "Validate quality gates"
    
  deployment:
    - "Run smoke tests in staging"
    - "Execute critical path E2E tests"
    - "Monitor test results post-deployment"
    - "Rollback on test failures"
```

### 2. Quality Gates & Metrics

```yaml
# testing-quality-standards.yaml
quality_gates:
  unit_tests:
    coverage_threshold: 90
    performance_threshold: "< 5s total runtime"
    flakiness_threshold: "< 1% flaky tests"
    
  integration_tests:
    coverage_threshold: 80
    performance_threshold: "< 2 minutes total runtime"
    isolation_requirement: "no shared state between tests"
    
  e2e_tests:
    critical_path_coverage: 100
    performance_threshold: "< 15 minutes total runtime"
    reliability_threshold: "> 95% success rate"
    
  overall_requirements:
    test_pyramid_compliance: "70% unit, 20% integration, 10% E2E"
    build_time_limit: "< 20 minutes total"
    zero_tolerance: "security tests, accessibility tests"
```

## Testing Checklist & Best Practices

### Unit Testing Standards
- ✅ Fast execution (< 5 seconds total)
- ✅ Isolated and independent tests
- ✅ Comprehensive mocking of dependencies
- ✅ Clear arrange-act-assert structure
- ✅ Parameterized tests for multiple scenarios
- ✅ 90%+ code coverage with meaningful tests

### Integration Testing Standards
- ✅ Database integration with transactions
- ✅ API contract testing
- ✅ External service mocking/stubbing
- ✅ Environment isolation
- ✅ Cleanup after each test
- ✅ Real-world data scenarios

### E2E Testing Standards
- ✅ Critical user journey coverage
- ✅ Cross-browser compatibility
- ✅ Performance validation
- ✅ Error handling verification
- ✅ Accessibility compliance
- ✅ Mobile responsiveness

### Automation Requirements
- ✅ Full CI/CD pipeline integration
- ✅ Parallel test execution
- ✅ Comprehensive reporting
- ✅ Quality gate enforcement
- ✅ Performance monitoring
- ✅ Flaky test detection and remediation

This comprehensive testing standards rule consolidates testing strategy, implementation patterns, and automation into unified guidance for building robust, reliable software with comprehensive quality assurance throughout the development lifecycle. 