---
description: "Universal database operations: backup/restore, monitoring, maintenance, performance tuning. Database operational excellence and reliability standards."
globs: ["**/*"]
alwaysApply: true
---

# 🔧 Universal Database Operations

## 1. Backup & Recovery

### Backup Requirements
- **IMPLEMENT:** Automated daily full backups with point-in-time recovery capability
- **MAINTAIN:** Multiple backup retention policies (daily, weekly, monthly)
- **TEST:** Regular backup restoration testing and validation
- **MONITOR:** Backup success/failure rates and recovery time objectives (RTO)

### Backup Strategy Implementation
```bash
#!/bin/bash
# backup-database.sh - Automated PostgreSQL backup script

set -euo pipefail

# Configuration
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME}"
DB_USER="${DB_USER}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/postgresql}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
S3_BUCKET="${S3_BUCKET}"

# Create timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql.gz"

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Perform backup with compression
echo "Starting backup of ${DB_NAME} at $(date)"
pg_dump \
  --host="${DB_HOST}" \
  --port="${DB_PORT}" \
  --username="${DB_USER}" \
  --no-password \
  --format=custom \
  --compress=9 \
  --verbose \
  --file="${BACKUP_FILE}" \
  "${DB_NAME}"

# Verify backup
if pg_restore --list "${BACKUP_FILE}" > /dev/null 2>&1; then
  echo "Backup verification successful"
else
  echo "Backup verification failed"
  exit 1
fi

# Upload to S3
if [ -n "${S3_BUCKET}" ]; then
  aws s3 cp "${BACKUP_FILE}" "s3://${S3_BUCKET}/postgresql/${DB_NAME}/"
  echo "Backup uploaded to S3"
fi

# Clean up old backups
find "${BACKUP_DIR}" -name "${DB_NAME}_*.sql.gz" -mtime +${RETENTION_DAYS} -delete

echo "Backup completed successfully: ${BACKUP_FILE}"

# Send notification
curl -X POST "${SLACK_WEBHOOK_URL}" \
  -H 'Content-type: application/json' \
  --data "{\"text\":\"Database backup completed: ${DB_NAME} - $(date)\"}"
```

### Recovery Procedures
```typescript
// recovery-manager.ts
export interface RecoveryOptions {
  targetTime?: Date;
  targetLSN?: string;
  targetTransactionId?: string;
  recoveryMode: 'immediate' | 'point-in-time' | 'standby';
}

export class DatabaseRecoveryManager {
  async performRecovery(
    backupPath: string,
    options: RecoveryOptions
  ): Promise<void> {
    console.log('Starting database recovery...');
    
    // 1. Stop database service
    await this.stopDatabase();
    
    // 2. Restore base backup
    await this.restoreBaseBackup(backupPath);
    
    // 3. Configure recovery
    await this.configureRecovery(options);
    
    // 4. Start database in recovery mode
    await this.startRecovery();
    
    // 5. Validate recovery
    await this.validateRecovery();
    
    console.log('Database recovery completed successfully');
  }
  
  private async restoreBaseBackup(backupPath: string): Promise<void> {
    // Extract backup to data directory
    await exec(`pg_restore --clean --create -d postgres ${backupPath}`);
  }
  
  private async configureRecovery(options: RecoveryOptions): Promise<void> {
    const recoveryConf = `
restore_command = 'aws s3 cp s3://backup-bucket/wal/%f %p'
recovery_target_time = '${options.targetTime?.toISOString()}'
recovery_target_action = 'promote'
    `;
    
    await fs.writeFile('/var/lib/postgresql/data/recovery.conf', recoveryConf);
  }
}
```

## 2. Database Monitoring

### Monitoring Requirements
- **TRACK:** Connection counts, query performance, and resource utilization
- **ALERT:** On performance degradation, connection limits, or error rates
- **COLLECT:** Comprehensive metrics for capacity planning and optimization
- **REPORT:** Regular performance and health reports

### Monitoring Setup
```typescript
// monitoring/database-metrics.ts
export class DatabaseMonitoringService {
  private db: DatabaseClient;
  private metricsCollector: MetricsCollector;
  
  constructor(db: DatabaseClient, metrics: MetricsCollector) {
    this.db = db;
    this.metricsCollector = metrics;
  }
  
  async collectMetrics(): Promise<void> {
    // Connection metrics
    const connections = await this.getConnectionMetrics();
    this.metricsCollector.gauge('db_connections_active', connections.active);
    this.metricsCollector.gauge('db_connections_idle', connections.idle);
    this.metricsCollector.gauge('db_connections_max', connections.max);
    
    // Query performance metrics
    const queryStats = await this.getQueryPerformanceStats();
    this.metricsCollector.histogram('db_query_duration', queryStats.avgDuration);
    this.metricsCollector.counter('db_queries_total', queryStats.totalQueries);
    this.metricsCollector.counter('db_slow_queries_total', queryStats.slowQueries);
    
    // Resource utilization
    const resources = await this.getResourceUtilization();
    this.metricsCollector.gauge('db_cpu_usage_percent', resources.cpu);
    this.metricsCollector.gauge('db_memory_usage_percent', resources.memory);
    this.metricsCollector.gauge('db_disk_usage_percent', resources.disk);
    
    // Database size metrics
    const sizes = await this.getDatabaseSizes();
    sizes.forEach(size => {
      this.metricsCollector.gauge('db_size_bytes', size.bytes, {
        database: size.name
      });
    });
  }
  
  private async getConnectionMetrics(): Promise<{
    active: number;
    idle: number;
    max: number;
  }> {
    const result = await this.db.query(`
      SELECT 
        COUNT(*) FILTER (WHERE state = 'active') as active,
        COUNT(*) FILTER (WHERE state = 'idle') as idle,
        (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') as max
      FROM pg_stat_activity
      WHERE datname = current_database()
    `);
    
    return result.rows[0];
  }
  
  async checkHealth(): Promise<HealthStatus> {
    try {
      // Basic connectivity check
      await this.db.query('SELECT 1');
      
      // Check replication lag (if applicable)
      const replicationLag = await this.getReplicationLag();
      
      // Check for long-running transactions
      const longTransactions = await this.getLongRunningTransactions();
      
      // Check disk space
      const diskSpace = await this.getDiskSpace();
      
      return {
        status: 'healthy',
        timestamp: new Date(),
        checks: {
          connectivity: true,
          replicationLag: replicationLag < 1000, // < 1 second
          longTransactions: longTransactions.length === 0,
          diskSpace: diskSpace > 20 // > 20% free
        }
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        timestamp: new Date(),
        error: error.message
      };
    }
  }
}
```

## 3. Database Maintenance

### Maintenance Requirements
- **SCHEDULE:** Regular VACUUM and ANALYZE operations
- **MONITOR:** Table and index bloat with automated cleanup
- **MAINTAIN:** Statistics and query planner optimization
- **UPGRADE:** Database version management and compatibility

### Automated Maintenance Tasks
```sql
-- automated-maintenance.sql
-- Run daily maintenance tasks

-- Update table statistics
DO $$
DECLARE
  rec RECORD;
BEGIN
  FOR rec IN
    SELECT schemaname, tablename
    FROM pg_tables
    WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
  LOOP
    EXECUTE format('ANALYZE %I.%I', rec.schemaname, rec.tablename);
  END LOOP;
END $$;

-- Vacuum tables with high bloat
WITH bloated_tables AS (
  SELECT 
    schemaname,
    tablename,
    ROUND((CASE WHEN otta=0 THEN 0.0 ELSE sml.relpages/otta::numeric END)::numeric,1) AS bloat_ratio
  FROM (
    SELECT 
      schemaname, tablename, cc.reltuples, cc.relpages, bs,
      CEIL((cc.reltuples*((datahdr+ma-
        (CASE WHEN datahdr%ma=0 THEN ma ELSE datahdr%ma END))+nullhdr2+4))/(bs-20::float)) AS otta
    FROM (
      SELECT 
        ma,bs,schemaname,tablename,
        (datawidth+(hdr+ma-(case when hdr%ma=0 THEN ma ELSE hdr%ma END)))::numeric AS datahdr,
        (maxfracsum*(nullhdr+ma-(case when nullhdr%ma=0 THEN ma ELSE nullhdr%ma END))) AS nullhdr2
      FROM (
        SELECT
          schemaname, tablename, hdr, ma, bs,
          SUM((1-null_frac)*avg_width) AS datawidth,
          MAX(null_frac) AS maxfracsum,
          hdr+(
            SELECT 1+count(*)/8
            FROM pg_stats s2
            WHERE null_frac<>0 AND s2.schemaname = s.schemaname AND s2.tablename = s.tablename
          ) AS nullhdr
        FROM pg_stats s, (
          SELECT
            (SELECT current_setting('block_size')::numeric) AS bs,
            CASE WHEN substring(SPLIT_PART(v, ' ', 2) FROM '#"[0-9]+.[0-9]+#"%' for '#')
              IN ('8.0','8.1','8.2') THEN 27 ELSE 23 END AS hdr,
            CASE WHEN v ~ 'mingw32' OR v ~ '64-bit|x86_64|ppc64|ia64|amd64' THEN 8 ELSE 4 END AS ma
          FROM (SELECT version() AS v) AS foo
        ) AS constants
        GROUP BY 1,2,3,4,5
      ) AS foo
    ) AS rs
    JOIN pg_class cc ON cc.relname = rs.tablename
    JOIN pg_namespace nn ON cc.relnamespace = nn.oid AND nn.nspname = rs.schemaname AND nn.nspname <> 'information_schema'
  ) AS sml
  WHERE sml.relpages > 0
)
SELECT schemaname, tablename, bloat_ratio
FROM bloated_tables
WHERE bloat_ratio > 2.0;
```

---

## 🛠️ Enforcement & Tooling

### Required CI Checks
- [ ] Backup script validation and testing
- [ ] Monitoring configuration verification
- [ ] Maintenance task scheduling validation
- [ ] Performance benchmark testing
- [ ] Recovery procedure documentation and testing

### Repository Requirements
- [ ] `/scripts/backup/` directory with backup automation scripts
- [ ] `/monitoring/` directory with metrics collection and alerting
- [ ] `/maintenance/` directory with automated maintenance tasks
- [ ] Database performance benchmarks and SLA definitions
- [ ] Recovery runbooks and disaster recovery procedures

### Recommended Tools
- **Backup & Recovery:** pgBackRest, Barman, AWS RDS snapshots, pg_dump/pg_restore
- **Monitoring:** Prometheus + Grafana, DataDog, pganalyze, New Relic
- **Maintenance:** pg_cron, automated vacuum, pgAgent
- **Performance:** pg_stat_statements, EXPLAIN visualization, pgBadger
- **Alerting:** Alertmanager, PagerDuty, Slack integrations

### Database Operations Metrics & KPIs
- **Backup Success Rate:** 100% successful automated backups
- **Recovery Time Objective (RTO):** < 1 hour for critical systems
- **Recovery Point Objective (RPO):** < 15 minutes data loss maximum
- **Uptime:** 99.95% availability target
- **Query Performance:** 95th percentile response time < 500ms
- **Maintenance Window:** < 2 hours for scheduled maintenance

---

*This rule focuses on database operations and maintenance. See also: DP-01-database-design.md for schema design and 10A-monitoring-setup.md for comprehensive monitoring strategies.* 