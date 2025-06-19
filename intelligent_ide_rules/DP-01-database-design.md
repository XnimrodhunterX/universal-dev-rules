---
description: "Universal database design: schema patterns, migrations, indexing, performance optimization. Database architecture standards and best practices."
globs: ["**/*"]
alwaysApply: true
---

# 🗃️ Universal Database Design

## 1. Schema Design Standards

### Database Schema Requirements
- **USE:** Consistent naming conventions across all database objects
- **IMPLEMENT:** Proper data types and constraints for data integrity
- **DESIGN:** Normalized schemas with appropriate denormalization for performance
- **ENFORCE:** Foreign key constraints and referential integrity

### Naming Conventions
```sql
-- Table naming: plural, snake_case
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Column naming: snake_case, descriptive
CREATE TABLE user_profiles (
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  first_name VARCHAR(255) NOT NULL,
  last_name VARCHAR(255) NOT NULL,
  date_of_birth DATE,
  email_address VARCHAR(320) UNIQUE NOT NULL,
  phone_number VARCHAR(20),
  is_email_verified BOOLEAN DEFAULT FALSE,
  profile_image_url TEXT
);

-- Index naming: idx_<table>_<columns>
CREATE INDEX idx_users_email_address ON users(email_address);
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);

-- Constraint naming: <type>_<table>_<columns>
ALTER TABLE user_profiles 
ADD CONSTRAINT chk_user_profiles_email_format 
CHECK (email_address ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');
```

### Data Type Standards
```sql
-- Use appropriate data types
CREATE TABLE orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_number VARCHAR(50) UNIQUE NOT NULL,          -- Business identifier
  user_id UUID NOT NULL REFERENCES users(id),
  order_status VARCHAR(20) NOT NULL DEFAULT 'pending',
  total_amount DECIMAL(10,2) NOT NULL,               -- Monetary values
  currency_code CHAR(3) NOT NULL DEFAULT 'USD',     -- ISO currency codes
  order_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(), -- Always use timezone
  shipped_date TIMESTAMP WITH TIME ZONE,
  tracking_number VARCHAR(100),
  notes TEXT,                                        -- Variable length text
  metadata JSONB,                                    -- Structured data
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enum types for controlled vocabularies
CREATE TYPE order_status_enum AS ENUM (
  'pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled'
);

ALTER TABLE orders ALTER COLUMN order_status TYPE order_status_enum 
USING order_status::order_status_enum;
```

### Audit and Soft Delete Patterns
```sql
-- Audit columns (required on all tables)
CREATE TABLE base_entity (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  created_by UUID REFERENCES users(id),
  updated_by UUID REFERENCES users(id),
  version INTEGER DEFAULT 1 NOT NULL  -- Optimistic locking
);

-- Soft delete pattern
CREATE TABLE products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  price DECIMAL(10,2) NOT NULL,
  is_deleted BOOLEAN DEFAULT FALSE NOT NULL,
  deleted_at TIMESTAMP WITH TIME ZONE,
  deleted_by UUID REFERENCES users(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  NEW.version = OLD.version + 1;
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_products_updated_at 
  BEFORE UPDATE ON products 
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

## 2. Migration Management

### Migration Standards
- **VERSION:** All database changes through versioned migration scripts
- **REVERSIBLE:** Provide rollback scripts for all schema changes
- **ATOMIC:** Each migration should be atomic and independent
- **TEST:** Validate migrations on staging before production deployment

### Migration Template
```sql
-- migrations/001_create_users_table.up.sql
-- Description: Create users table with basic profile information
-- Author: team@example.com
-- Date: 2024-01-15

BEGIN;

-- Create users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(320) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  is_active BOOLEAN DEFAULT TRUE NOT NULL,
  last_login_at TIMESTAMP WITH TIME ZONE,
  failed_login_attempts INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Add constraints
ALTER TABLE users ADD CONSTRAINT chk_users_email_format 
  CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

ALTER TABLE users ADD CONSTRAINT chk_users_failed_attempts 
  CHECK (failed_login_attempts >= 0 AND failed_login_attempts <= 10);

-- Update migration tracking
INSERT INTO schema_migrations (version, applied_at) 
VALUES ('001', NOW());

COMMIT;
```

```sql
-- migrations/001_create_users_table.down.sql
-- Rollback script for users table creation

BEGIN;

-- Remove from migration tracking
DELETE FROM schema_migrations WHERE version = '001';

-- Drop table (cascades to indexes and constraints)
DROP TABLE IF EXISTS users CASCADE;

COMMIT;
```

### Migration Management System
```typescript
// migration-manager.ts
export interface Migration {
  version: string;
  description: string;
  upSql: string;
  downSql: string;
  appliedAt?: Date;
}

export class MigrationManager {
  private db: DatabaseClient;
  
  constructor(db: DatabaseClient) {
    this.db = db;
  }
  
  async initializeMigrationTracking(): Promise<void> {
    await this.db.query(`
      CREATE TABLE IF NOT EXISTS schema_migrations (
        version VARCHAR(255) PRIMARY KEY,
        description TEXT NOT NULL,
        applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        rollback_sql TEXT,
        checksum VARCHAR(64) NOT NULL
      );
    `);
  }
  
  async getPendingMigrations(): Promise<Migration[]> {
    const appliedVersions = await this.db.query(`
      SELECT version FROM schema_migrations ORDER BY version
    `);
    
    const allMigrations = await this.loadMigrationFiles();
    return allMigrations.filter(m => 
      !appliedVersions.rows.some(r => r.version === m.version)
    );
  }
  
  async applyMigration(migration: Migration): Promise<void> {
    const transaction = await this.db.begin();
    
    try {
      // Apply the migration
      await transaction.query(migration.upSql);
      
      // Record the migration
      await transaction.query(`
        INSERT INTO schema_migrations (version, description, rollback_sql, checksum)
        VALUES ($1, $2, $3, $4)
      `, [
        migration.version,
        migration.description,
        migration.downSql,
        this.calculateChecksum(migration.upSql)
      ]);
      
      await transaction.commit();
      console.log(`Applied migration ${migration.version}: ${migration.description}`);
    } catch (error) {
      await transaction.rollback();
      throw error;
    }
  }
  
  async rollbackMigration(version: string): Promise<void> {
    const migration = await this.db.query(`
      SELECT * FROM schema_migrations WHERE version = $1
    `, [version]);
    
    if (migration.rows.length === 0) {
      throw new Error(`Migration ${version} not found`);
    }
    
    const transaction = await this.db.begin();
    
    try {
      // Apply rollback
      await transaction.query(migration.rows[0].rollback_sql);
      
      // Remove migration record
      await transaction.query(`
        DELETE FROM schema_migrations WHERE version = $1
      `, [version]);
      
      await transaction.commit();
      console.log(`Rolled back migration ${version}`);
    } catch (error) {
      await transaction.rollback();
      throw error;
    }
  }
  
  private calculateChecksum(sql: string): string {
    return crypto.createHash('sha256').update(sql).digest('hex');
  }
  
  private async loadMigrationFiles(): Promise<Migration[]> {
    // Load migration files from filesystem
    // Implementation depends on your migration file structure
    return [];
  }
}
```

## 3. Indexing Strategy

### Index Design Principles
- **CREATE:** Indexes for all foreign keys and frequently queried columns
- **OPTIMIZE:** Composite indexes for multi-column queries
- **MONITOR:** Index usage and performance impact
- **MAINTAIN:** Regular index maintenance and analysis

### Index Types and Usage
```sql
-- B-tree indexes (default) - for equality and range queries
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_order_date ON orders(order_date);

-- Partial indexes - for filtered queries
CREATE INDEX idx_orders_active ON orders(user_id) 
WHERE order_status IN ('pending', 'confirmed', 'processing');

-- Composite indexes - for multi-column queries
CREATE INDEX idx_orders_user_status_date ON orders(user_id, order_status, order_date);

-- Expression indexes - for computed values
CREATE INDEX idx_users_lower_email ON users(LOWER(email));

-- GIN indexes - for JSONB and full-text search
CREATE INDEX idx_orders_metadata ON orders USING GIN(metadata);
CREATE INDEX idx_products_search ON products USING GIN(to_tsvector('english', name || ' ' || description));

-- Covering indexes - include additional columns
CREATE INDEX idx_orders_user_covering ON orders(user_id) INCLUDE (total_amount, order_date);
```

### Index Monitoring
```sql
-- Check index usage
SELECT 
  schemaname,
  tablename,
  indexname,
  idx_tup_read,
  idx_tup_fetch,
  idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Find unused indexes
SELECT 
  schemaname,
  tablename,
  indexname,
  pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE idx_scan = 0 AND idx_tup_read = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- Check index bloat
SELECT
  schemaname,
  tablename,
  indexname,
  ROUND((CASE WHEN avg_leaf_density = 'NaN' THEN 0 ELSE avg_leaf_density END)::numeric, 2) AS avg_leaf_density,
  est_pages,
  est_pages_inc_bloat,
  ROUND((est_pages_inc_bloat - est_pages)::numeric / est_pages::numeric * 100, 2) AS bloat_pct
FROM pgstattuple_approx('index_name');
```

## 4. Performance Optimization

### Query Performance Standards
- **TARGET:** < 100ms for simple queries, < 500ms for complex analytics
- **IMPLEMENT:** Connection pooling and prepared statements
- **MONITOR:** Query performance and slow query logging
- **OPTIMIZE:** Regular query plan analysis and optimization

### Query Optimization Patterns
```sql
-- Use EXPLAIN ANALYZE for query optimization
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT 
  o.id,
  o.order_number,
  u.email,
  o.total_amount
FROM orders o
JOIN users u ON o.user_id = u.id
WHERE o.order_date >= '2024-01-01'
  AND o.order_status = 'completed'
ORDER BY o.order_date DESC
LIMIT 100;

-- Optimize with proper indexing
CREATE INDEX idx_orders_status_date ON orders(order_status, order_date) 
WHERE order_status = 'completed';

-- Use materialized views for complex aggregations
CREATE MATERIALIZED VIEW daily_order_summary AS
SELECT 
  DATE(order_date) as order_date,
  COUNT(*) as total_orders,
  SUM(total_amount) as total_revenue,
  AVG(total_amount) as avg_order_value
FROM orders 
WHERE order_status = 'completed'
GROUP BY DATE(order_date);

-- Refresh materialized view periodically
CREATE OR REPLACE FUNCTION refresh_daily_order_summary()
RETURNS void AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY daily_order_summary;
END;
$$ LANGUAGE plpgsql;
```

### Connection Management
```typescript
// connection-pool.ts
import { Pool } from 'pg';

export class DatabaseConnectionPool {
  private pool: Pool;
  
  constructor() {
    this.pool = new Pool({
      host: process.env.DB_HOST,
      port: parseInt(process.env.DB_PORT || '5432'),
      database: process.env.DB_NAME,
      user: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      
      // Connection pool settings
      max: 20,                    // Maximum connections
      min: 2,                     // Minimum connections
      idleTimeoutMillis: 30000,   // Close idle connections after 30s
      connectionTimeoutMillis: 2000, // Fail after 2s if no connection available
      
      // Performance settings
      statement_timeout: 30000,   // Kill queries after 30s
      query_timeout: 30000,       // Application-level timeout
      
      // SSL settings
      ssl: process.env.NODE_ENV === 'production' ? {
        rejectUnauthorized: false
      } : false
    });
    
    // Handle pool errors
    this.pool.on('error', (err) => {
      console.error('Database pool error:', err);
    });
  }
  
  async query(text: string, params?: any[]): Promise<any> {
    const start = Date.now();
    const client = await this.pool.connect();
    
    try {
      const result = await client.query(text, params);
      const duration = Date.now() - start;
      
      // Log slow queries
      if (duration > 1000) {
        console.warn(`Slow query (${duration}ms):`, text);
      }
      
      return result;
    } finally {
      client.release();
    }
  }
  
  async transaction<T>(
    callback: (client: any) => Promise<T>
  ): Promise<T> {
    const client = await this.pool.connect();
    
    try {
      await client.query('BEGIN');
      const result = await callback(client);
      await client.query('COMMIT');
      return result;
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }
  
  async close(): Promise<void> {
    await this.pool.end();
  }
}
```

---

## 🛠️ Enforcement & Tooling

### Required CI Checks
- [ ] Database schema validation and naming convention compliance
- [ ] Migration script validation (up/down pairs, atomic changes)
- [ ] Index analysis and performance validation
- [ ] Connection pool configuration verification
- [ ] Query performance testing against SLA targets

### Repository Requirements
- [ ] `/migrations/` directory with versioned migration scripts
- [ ] Database schema documentation and ER diagrams
- [ ] Connection pool and database configuration
- [ ] Performance monitoring and alerting setup
- [ ] Database backup and recovery procedures

### Recommended Tools
- **Migration Management:** Flyway, Liquibase, golang-migrate, node-pg-migrate
- **Schema Management:** Prisma, TypeORM, Sequelize, Drizzle
- **Performance Monitoring:** pganalyze, DataDog, New Relic, Grafana
- **Query Optimization:** pgBadger, pg_stat_statements, EXPLAIN visualizers
- **Connection Pooling:** PgBouncer, connection pool libraries

### Database Metrics & KPIs
- **Query Performance:** 95th percentile query response time < 500ms
- **Connection Utilization:** Pool utilization < 80% under normal load
- **Index Efficiency:** All tables > 1MB have appropriate indexes
- **Migration Success:** 100% successful migration deployment rate
- **Schema Compliance:** 100% adherence to naming conventions
- **Data Integrity:** Zero foreign key constraint violations

---

*This rule focuses on database design and performance. See also: DP-02-database-operations.md for operational aspects and CN-14-environment-configuration.md for database configuration management.*
        description TEXT,
        applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        checksum VARCHAR(64) NOT NULL
      );
    `);
  }
  
  async applyMigrations(migrations: Migration[]): Promise<void> {
    await this.initializeMigrationTracking();
    
    const appliedMigrations = await this.getAppliedMigrations();
    const pendingMigrations = migrations.filter(
      m => !appliedMigrations.has(m.version)
    );
    
    for (const migration of pendingMigrations) {
      await this.applyMigration(migration);
    }
  }
  
  private async applyMigration(migration: Migration): Promise<void> {
    const checksum = this.calculateChecksum(migration.upSql);
    
    try {
      await this.db.transaction(async (tx) => {
        // Apply the migration
        await tx.query(migration.upSql);
        
        // Record in migration tracking
        await tx.query(`
          INSERT INTO schema_migrations (version, description, checksum) 
          VALUES ($1, $2, $3)
        `, [migration.version, migration.description, checksum]);
      });
      
      console.log(`Migration ${migration.version} applied successfully`);
    } catch (error) {
      console.error(`Migration ${migration.version} failed:`, error);
      throw error;
    }
  }
  
  private async getAppliedMigrations(): Promise<Set<string>> {
    const result = await this.db.query(
      'SELECT version FROM schema_migrations ORDER BY version'
    );
    return new Set(result.rows.map(row => row.version));
  }
  
  private calculateChecksum(sql: string): string {
    return crypto.createHash('sha256').update(sql).digest('hex');
  }
}
```

## 3. Indexing Strategy

### Indexing Standards
- **CREATE:** Indexes on foreign keys, frequently queried columns, and WHERE clauses
- **MONITOR:** Index usage and performance impact
- **AVOID:** Over-indexing that impacts write performance
- **COMPOSITE:** Use composite indexes for multi-column queries

### Index Design Patterns
```sql
-- Single column indexes
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(order_status);
CREATE INDEX idx_orders_date ON orders(order_date);

-- Composite indexes (order matters!)
-- For queries filtering by user_id and status
CREATE INDEX idx_orders_user_status ON orders(user_id, order_status);

-- For queries ordering by date within user
CREATE INDEX idx_orders_user_date ON orders(user_id, order_date DESC);

-- Partial indexes for conditional queries
CREATE INDEX idx_orders_active ON orders(user_id, order_date) 
WHERE order_status NOT IN ('cancelled', 'delivered');

-- Functional indexes
CREATE INDEX idx_users_email_lower ON users(LOWER(email));

-- JSONB indexes for document queries
CREATE INDEX idx_orders_metadata ON orders USING GIN(metadata);
CREATE INDEX idx_orders_metadata_customer ON orders USING GIN((metadata->'customer'));

-- Full-text search indexes
ALTER TABLE products ADD COLUMN search_vector tsvector;
CREATE INDEX idx_products_search ON products USING GIN(search_vector);

-- Update search vector trigger
CREATE OR REPLACE FUNCTION update_product_search_vector()
RETURNS TRIGGER AS $$
BEGIN
  NEW.search_vector := to_tsvector('english', 
    COALESCE(NEW.name, '') || ' ' || COALESCE(NEW.description, '')
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_products_search_vector
  BEFORE INSERT OR UPDATE ON products
  FOR EACH ROW EXECUTE FUNCTION update_product_search_vector();
```

### Index Monitoring
```sql
-- Query to find unused indexes
SELECT 
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY schemaname, tablename, indexname;

-- Query to find missing indexes
SELECT 
  schemaname,
  tablename,
  seq_scan,
  seq_tup_read,
  seq_tup_read / seq_scan AS avg_tuples_per_scan
FROM pg_stat_user_tables
WHERE seq_scan > 0
  AND seq_tup_read / seq_scan > 1000
ORDER BY seq_tup_read DESC;

-- Index size and usage
SELECT 
  i.indexname,
  pg_size_pretty(pg_relation_size(indexrelid)) as size,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes i
JOIN pg_indexes idx ON i.indexname = idx.indexname
WHERE i.schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```

## 4. Performance Optimization

### Query Performance Standards
- **TARGET:** < 100ms for simple queries, < 1s for complex analytics
- **ANALYZE:** Use EXPLAIN ANALYZE for query optimization
- **OPTIMIZE:** Avoid N+1 queries and unnecessary joins
- **CACHE:** Implement query result caching for expensive operations

### Query Optimization Patterns
```sql
-- Use EXPLAIN ANALYZE for performance analysis
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT JSON)
SELECT 
  u.email,
  COUNT(o.id) as order_count,
  SUM(o.total_amount) as total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at >= '2024-01-01'
GROUP BY u.id, u.email
HAVING COUNT(o.id) > 0
ORDER BY total_spent DESC
LIMIT 100;

-- Optimized pagination with cursor-based approach
-- Instead of OFFSET (slow for large offsets)
SELECT * FROM orders 
WHERE order_date < $1  -- cursor value
ORDER BY order_date DESC 
LIMIT 20;

-- Use EXISTS instead of IN for large subqueries
SELECT * FROM users u
WHERE EXISTS (
  SELECT 1 FROM orders o 
  WHERE o.user_id = u.id 
    AND o.order_status = 'completed'
);

-- Use window functions for rankings
SELECT 
  user_id,
  order_date,
  total_amount,
  ROW_NUMBER() OVER (
    PARTITION BY user_id 
    ORDER BY order_date DESC
  ) as order_rank
FROM orders;

-- Efficient bulk operations
-- Bulk insert with COPY
COPY orders(user_id, total_amount, order_status) 
FROM '/path/to/orders.csv' 
WITH (FORMAT csv, HEADER true);

-- Bulk update with JOIN
UPDATE products p
SET category_id = c.id
FROM categories c
WHERE p.category_name = c.name;
```

### Connection Pooling Configuration
```typescript
// database-pool.ts
import { Pool } from 'pg';

export interface PoolConfig {
  host: string;
  port: number;
  database: string;
  user: string;
  password: string;
  min: number;
  max: number;
  idleTimeoutMillis: number;
  connectionTimeoutMillis: number;
}

export class DatabasePool {
  private pool: Pool;
  
  constructor(config: PoolConfig) {
    this.pool = new Pool({
      host: config.host,
      port: config.port,
      database: config.database,
      user: config.user,
      password: config.password,
      min: config.min,                    // Minimum connections
      max: config.max,                    // Maximum connections
      idleTimeoutMillis: config.idleTimeoutMillis,  // Close idle connections
      connectionTimeoutMillis: config.connectionTimeoutMillis,
      
      // Performance settings
      statement_timeout: 30000,           // 30 second query timeout
      idle_in_transaction_session_timeout: 60000,  // 1 minute idle in transaction
      
      // SSL configuration for production
      ssl: process.env.NODE_ENV === 'production' ? {
        rejectUnauthorized: false
      } : false
    });
    
    this.setupEventListeners();
  }
  
  private setupEventListeners(): void {
    this.pool.on('connect', (client) => {
      console.log('Database client connected');
    });
    
    this.pool.on('error', (err, client) => {
      console.error('Database pool error:', err);
    });
    
    this.pool.on('acquire', (client) => {
      console.log('Database client acquired from pool');
    });
    
    this.pool.on('release', (client) => {
      console.log('Database client released back to pool');
    });
  }
  
  async query(text: string, params?: any[]): Promise<any> {
    const start = Date.now();
    
    try {
      const result = await this.pool.query(text, params);
      const duration = Date.now() - start;
      
      // Log slow queries
      if (duration > 1000) {
        console.warn(`Slow query (${duration}ms): ${text}`);
      }
      
      return result;
    } catch (error) {
      console.error('Database query error:', { text, params, error });
      throw error;
    }
  }
  
  async transaction<T>(callback: (client: any) => Promise<T>): Promise<T> {
    const client = await this.pool.connect();
    
    try {
      await client.query('BEGIN');
      const result = await callback(client);
      await client.query('COMMIT');
      return result;
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }
  
  async getPoolStats(): Promise<any> {
    return {
      totalCount: this.pool.totalCount,
      idleCount: this.pool.idleCount,
      waitingCount: this.pool.waitingCount
    };
  }
  
  async close(): Promise<void> {
    await this.pool.end();
  }
}

// Connection pool configuration by environment
export const poolConfigs = {
  production: {
    host: process.env.DB_HOST!,
    port: parseInt(process.env.DB_PORT!),
    database: process.env.DB_NAME!,
    user: process.env.DB_USER!,
    password: process.env.DB_PASSWORD!,
    min: 10,                    // Maintain minimum connections
    max: 30,                    // Scale up to 30 connections
    idleTimeoutMillis: 30000,   // 30 seconds
    connectionTimeoutMillis: 10000  // 10 seconds
  },
  
  development: {
    host: 'localhost',
    port: 5432,
    database: 'app_development',
    user: 'developer',
    password: 'password',
    min: 2,
    max: 10,
    idleTimeoutMillis: 10000,
    connectionTimeoutMillis: 5000
  }
};
```

---

## 🛠️ Enforcement & Tooling

### Required CI Checks
- [ ] Database schema validation and linting
- [ ] Migration script testing (up and down)
- [ ] Index usage analysis and optimization
- [ ] Query performance testing with EXPLAIN ANALYZE
- [ ] Database connection pooling configuration validation

### Repository Requirements
- [ ] `migrations/` directory with versioned migration scripts
- [ ] Database schema documentation and ERD
- [ ] Index strategy documentation
- [ ] Connection pooling configuration
- [ ] Query performance monitoring setup

### Recommended Tools
- **Migration Management:** Flyway, Liquibase, golang-migrate, Alembic
- **Schema Design:** dbdiagram.io, ERDPlus, Lucidchart
- **Performance Monitoring:** pg_stat_statements, pgBadger, DataDog, New Relic
- **Query Analysis:** pgMustard, EXPLAIN.DEPESZ.COM

### Database Metrics
- **Query Performance:** Average query time, slow query count, query throughput
- **Connection Health:** Pool utilization, connection errors, timeout rates
- **Index Efficiency:** Index hit ratio, unused indexes, missing indexes
- **Schema Quality:** Foreign key violations, constraint failures, data type usage

---

*This rule focuses on database design and schema management. See also: DP-02-database-operations.md for operational procedures and monitoring.* 