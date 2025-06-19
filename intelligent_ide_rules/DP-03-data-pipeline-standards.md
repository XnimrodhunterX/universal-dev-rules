# Rule 13B: Data Pipeline Standards

## Purpose & Scope

Data pipeline standards ensure reliable, scalable, and maintainable data processing systems through standardized architectures, quality controls, and orchestration patterns. This rule establishes standards for batch and streaming data pipelines, data quality frameworks, pipeline monitoring, and governance to enable robust data-driven applications.

## Core Standards

### Data Pipeline Architecture

#### 1. Pipeline Design Patterns

**Event-Driven Data Architecture:**
```yaml
# data-pipeline-architecture.yaml
pipeline_architecture:
  streaming_patterns:
    event_sourcing:
      description: "Immutable event logs as source of truth"
      use_cases: ["audit_trails", "real_time_analytics", "system_integration"]
      technologies: ["Apache Kafka", "AWS Kinesis", "Azure Event Hubs"]
      guarantees: "at_least_once_delivery"
      
    cqrs_pattern:
      description: "Command Query Responsibility Segregation"
      use_cases: ["read_write_optimization", "complex_business_logic", "scaling"]
      technologies: ["Event Store", "Redis", "Elasticsearch"]
      consistency: "eventual_consistency"
      
    lambda_architecture:
      description: "Batch and speed layers for comprehensive processing"
      components:
        batch_layer: "Hadoop/Spark for historical data"
        speed_layer: "Storm/Flink for real-time processing"
        serving_layer: "NoSQL databases for query serving"
      use_cases: ["large_scale_analytics", "complex_aggregations"]
      
    kappa_architecture:
      description: "Stream-only processing architecture"
      components:
        streaming_layer: "Kafka Streams/Apache Flink"
        serving_layer: "Materialized views in databases"
      use_cases: ["real_time_processing", "simplified_architecture"]
      
  batch_patterns:
    etl_pipeline:
      description: "Extract, Transform, Load traditional pattern"
      stages: ["extract", "transform", "load"]
      scheduling: "cron_based_or_workflow_orchestrated"
      use_cases: ["data_warehousing", "reporting", "analytics"]
      
    elt_pipeline:
      description: "Extract, Load, Transform modern pattern"
      stages: ["extract", "load", "transform"]
      advantages: ["cloud_native", "scalable_compute", "flexible_transformations"]
      use_cases: ["data_lakes", "cloud_analytics", "big_data"]

data_flow_patterns:
  producer_consumer:
    pattern: "Decoupled message-based communication"
    benefits: ["scalability", "fault_tolerance", "flexibility"]
    implementation: "message_queues_and_event_streams"
    
  publish_subscribe:
    pattern: "One-to-many event distribution"
    benefits: ["loose_coupling", "event_broadcasting", "system_integration"]
    implementation: "event_buses_and_message_brokers"
    
  request_response:
    pattern: "Synchronous API-based communication"
    benefits: ["immediate_feedback", "simple_implementation", "transactional"]
    implementation: "rest_apis_and_graphql"
```

#### 2. Data Processing Framework Standards

**Apache Kafka Streaming Architecture:**
```yaml
# kafka-streaming-config.yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: production-cluster
  namespace: data-platform
spec:
  kafka:
    version: 3.5.0
    replicas: 3
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
        authentication:
          type: tls
      - name: external
        port: 9094
        type: route
        tls: true
        authentication:
          type: scram-sha-512
    authorization:
      type: simple
      superUsers:
        - CN=kafka-admin
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
      default.replication.factor: 3
      min.insync.replicas: 2
      inter.broker.protocol.version: "3.5"
      log.message.format.version: "3.5"
      log.retention.hours: 168
      log.segment.bytes: 1073741824
      log.cleanup.policy: delete
      num.partitions: 12
      compression.type: lz4
    storage:
      type: jbod
      volumes:
      - id: 0
        type: persistent-claim
        size: 500Gi
        storageClass: fast-ssd
        deleteClaim: false
  zookeeper:
    replicas: 3
    storage:
      type: persistent-claim
      size: 100Gi
      storageClass: fast-ssd
      deleteClaim: false
  entityOperator:
    topicOperator: {}
    userOperator: {}

---
# Kafka Connect for data integration
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaConnect
metadata:
  name: data-connect-cluster
  namespace: data-platform
  annotations:
    strimzi.io/use-connector-resources: "true"
spec:
  version: 3.5.0
  replicas: 3
  bootstrapServers: production-cluster-kafka-bootstrap:9093
  tls:
    trustedCertificates:
      - secretName: production-cluster-cluster-ca-cert
        certificate: ca.crt
  authentication:
    type: tls
    certificateAndKey:
      secretName: kafka-connect-tls
      certificate: user.crt
      key: user.key
  config:
    group.id: connect-cluster
    offset.storage.topic: connect-cluster-offsets
    offset.storage.replication.factor: 3
    config.storage.topic: connect-cluster-configs
    config.storage.replication.factor: 3
    status.storage.topic: connect-cluster-status
    status.storage.replication.factor: 3
    key.converter: org.apache.kafka.connect.json.JsonConverter
    value.converter: org.apache.kafka.connect.json.JsonConverter
    key.converter.schemas.enable: false
    value.converter.schemas.enable: false
  resources:
    requests:
      memory: 2Gi
      cpu: 1
    limits:
      memory: 4Gi
      cpu: 2
  logging:
    type: inline
    loggers:
      log4j.logger.org.apache.kafka.connect: INFO
  readinessProbe:
    initialDelaySeconds: 15
    timeoutSeconds: 5
  livenessProbe:
    initialDelaySeconds: 15
    timeoutSeconds: 5
```

#### 3. Stream Processing Applications

**Kafka Streams Application:**
```java
// StreamProcessingApplication.java
package com.example.dataplatform.streams;

import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.kstream.*;
import org.apache.kafka.streams.state.Stores;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;
import java.util.Properties;
import java.util.concurrent.CountDownLatch;

/**
 * Real-time stream processing application for user behavior analytics
 * Processes user events and generates real-time metrics and alerts
 */
public class UserBehaviorStreamProcessor {
    private static final Logger logger = LoggerFactory.getLogger(UserBehaviorStreamProcessor.class);
    
    private static final String USER_EVENTS_TOPIC = "user-events";
    private static final String USER_METRICS_TOPIC = "user-metrics";
    private static final String FRAUD_ALERTS_TOPIC = "fraud-alerts";
    
    public static void main(String[] args) {
        Properties props = createStreamConfig();
        
        StreamsBuilder builder = new StreamsBuilder();
        buildTopology(builder);
        
        KafkaStreams streams = new KafkaStreams(builder.build(), props);
        
        // Graceful shutdown
        CountDownLatch latch = new CountDownLatch(1);
        Runtime.getRuntime().addShutdownHook(new Thread("streams-shutdown-hook") {
            @Override
            public void run() {
                logger.info("Shutting down stream processor...");
                streams.close(Duration.ofSeconds(30));
                latch.countDown();
            }
        });
        
        try {
            streams.start();
            latch.await();
        } catch (Throwable e) {
            logger.error("Stream processing failed", e);
            System.exit(1);
        }
        System.exit(0);
    }
    
    private static Properties createStreamConfig() {
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "user-behavior-processor");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "production-cluster-kafka-bootstrap:9093");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, StreamsConfig.EXACTLY_ONCE_V2);
        props.put(StreamsConfig.COMMIT_INTERVAL_MS_CONFIG, 1000);
        props.put(StreamsConfig.CACHE_MAX_BYTES_BUFFERING_CONFIG, 10 * 1024 * 1024L);
        props.put(StreamsConfig.STATE_DIR_CONFIG, "/tmp/kafka-streams");
        props.put(StreamsConfig.REPLICATION_FACTOR_CONFIG, 3);
        
        // Security configuration
        props.put("security.protocol", "SSL");
        props.put("ssl.truststore.location", "/etc/ssl/certs/kafka.client.truststore.jks");
        props.put("ssl.truststore.password", System.getenv("KAFKA_TRUSTSTORE_PASSWORD"));
        props.put("ssl.keystore.location", "/etc/ssl/certs/kafka.client.keystore.jks");
        props.put("ssl.keystore.password", System.getenv("KAFKA_KEYSTORE_PASSWORD"));
        props.put("ssl.key.password", System.getenv("KAFKA_KEY_PASSWORD"));
        
        return props;
    }
    
    private static void buildTopology(StreamsBuilder builder) {
        // Define JSON Serde for user events
        JsonSerde<UserEvent> userEventSerde = new JsonSerde<>(UserEvent.class);
        JsonSerde<UserMetrics> userMetricsSerde = new JsonSerde<>(UserMetrics.class);
        JsonSerde<FraudAlert> fraudAlertSerde = new JsonSerde<>(FraudAlert.class);
        
        // Create state store for user session tracking
        builder.addStateStore(
            Stores.keyValueStoreBuilder(
                Stores.persistentKeyValueStore("user-sessions"),
                Serdes.String(),
                userEventSerde
            )
        );
        
        KStream<String, UserEvent> userEvents = builder
            .stream(USER_EVENTS_TOPIC, Consumed.with(Serdes.String(), userEventSerde))
            .filter((key, event) -> event != null && event.getUserId() != null)
            .selectKey((key, event) -> event.getUserId());
        
        // Real-time user metrics calculation
        KTable<String, UserMetrics> userMetrics = userEvents
            .groupByKey(Grouped.with(Serdes.String(), userEventSerde))
            .windowedBy(TimeWindows.of(Duration.ofMinutes(5)).advanceBy(Duration.ofMinutes(1)))
            .aggregate(
                UserMetrics::new,
                (userId, event, metrics) -> metrics.addEvent(event),
                Materialized.<String, UserMetrics, WindowStore<Bytes, byte[]>>as("user-metrics-store")
                    .withKeySerde(Serdes.String())
                    .withValueSerde(userMetricsSerde)
                    .withRetention(Duration.ofHours(24))
            )
            .toStream()
            .map((windowedKey, metrics) -> KeyValue.pair(windowedKey.key(), metrics));
        
        // Publish metrics to topic
        userMetrics.to(USER_METRICS_TOPIC, Produced.with(Serdes.String(), userMetricsSerde));
        
        // Fraud detection stream
        KStream<String, FraudAlert> fraudAlerts = userEvents
            .filter((userId, event) -> isSuspiciousActivity(event))
            .groupByKey(Grouped.with(Serdes.String(), userEventSerde))
            .windowedBy(TimeWindows.of(Duration.ofMinutes(10)))
            .aggregate(
                () -> new FraudDetectionState(),
                (userId, event, state) -> state.addEvent(event),
                Materialized.with(Serdes.String(), new JsonSerde<>(FraudDetectionState.class))
            )
            .toStream()
            .filter((windowedKey, state) -> state.isFraudulent())
            .map((windowedKey, state) -> KeyValue.pair(
                windowedKey.key(),
                new FraudAlert(windowedKey.key(), state.getRiskScore(), state.getReasons())
            ));
        
        // Publish fraud alerts
        fraudAlerts.to(FRAUD_ALERTS_TOPIC, Produced.with(Serdes.String(), fraudAlertSerde));
        
        // Join user events with session data for enrichment
        KStream<String, EnrichedUserEvent> enrichedEvents = userEvents
            .transform(() -> new UserSessionEnricher(), "user-sessions");
        
        // Branch processing based on event type
        Map<String, KStream<String, EnrichedUserEvent>> branches = enrichedEvents
            .split(Named.as("event-type-"))
            .branch((key, event) -> "purchase".equals(event.getEventType()), Branched.as("purchase"))
            .branch((key, event) -> "login".equals(event.getEventType()), Branched.as("login"))
            .branch((key, event) -> "page_view".equals(event.getEventType()), Branched.as("pageview"))
            .defaultBranch(Branched.as("other"));
        
        // Process purchase events
        branches.get("event-type-purchase")
            .mapValues(event -> processPurchaseEvent(event))
            .to("purchase-processed", Produced.with(Serdes.String(), new JsonSerde<>(ProcessedPurchase.class)));
        
        // Process login events
        branches.get("event-type-login")
            .mapValues(event -> processLoginEvent(event))
            .to("login-processed", Produced.with(Serdes.String(), new JsonSerde<>(ProcessedLogin.class)));
    }
    
    private static boolean isSuspiciousActivity(UserEvent event) {
        // Implement fraud detection logic
        return event.getAmount() != null && event.getAmount() > 10000.0 ||
               event.getLocation() != null && isHighRiskLocation(event.getLocation()) ||
               event.getDeviceFingerprint() != null && isKnownFraudulentDevice(event.getDeviceFingerprint());
    }
    
    private static ProcessedPurchase processPurchaseEvent(EnrichedUserEvent event) {
        // Implement purchase processing logic
        return new ProcessedPurchase(
            event.getUserId(),
            event.getAmount(),
            event.getTimestamp(),
            event.getSessionData()
        );
    }
    
    private static ProcessedLogin processLoginEvent(EnrichedUserEvent event) {
        // Implement login processing logic
        return new ProcessedLogin(
            event.getUserId(),
            event.getTimestamp(),
            event.getLocation(),
            event.getDeviceFingerprint()
        );
    }
}

// Supporting data classes
class UserEvent {
    private String userId;
    private String eventType;
    private Double amount;
    private String location;
    private String deviceFingerprint;
    private long timestamp;
    
    // Constructors, getters, setters
    public UserEvent() {}
    
    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }
    
    public String getEventType() { return eventType; }
    public void setEventType(String eventType) { this.eventType = eventType; }
    
    public Double getAmount() { return amount; }
    public void setAmount(Double amount) { this.amount = amount; }
    
    public String getLocation() { return location; }
    public void setLocation(String location) { this.location = location; }
    
    public String getDeviceFingerprint() { return deviceFingerprint; }
    public void setDeviceFingerprint(String deviceFingerprint) { this.deviceFingerprint = deviceFingerprint; }
    
    public long getTimestamp() { return timestamp; }
    public void setTimestamp(long timestamp) { this.timestamp = timestamp; }
}

class UserMetrics {
    private String userId;
    private long eventCount;
    private double totalAmount;
    private long windowStart;
    private long windowEnd;
    
    public UserMetrics() {
        this.eventCount = 0;
        this.totalAmount = 0.0;
    }
    
    public UserMetrics addEvent(UserEvent event) {
        this.eventCount++;
        if (event.getAmount() != null) {
            this.totalAmount += event.getAmount();
        }
        return this;
    }
    
    // Getters and setters
    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }
    
    public long getEventCount() { return eventCount; }
    public void setEventCount(long eventCount) { this.eventCount = eventCount; }
    
    public double getTotalAmount() { return totalAmount; }
    public void setTotalAmount(double totalAmount) { this.totalAmount = totalAmount; }
}
```

### Data Quality Framework

#### 1. Data Quality Validation

**Comprehensive Data Quality Pipeline:**
```python
# data_quality_framework.py
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import great_expectations as ge
from pydantic import BaseModel, validator
from apache_beam import Pipeline, DoFn, ParDo, Map
from apache_beam.options.pipeline_options import PipelineOptions

class DataQualityLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class DataQualityRule:
    name: str
    description: str
    severity: DataQualityLevel
    rule_type: str  # "completeness", "validity", "accuracy", "consistency", "timeliness"
    validation_function: callable
    threshold: float
    metadata: Dict[str, Any]

class DataQualityFramework:
    def __init__(self, config_path: str = None):
        self.rules = []
        self.execution_history = []
        self.quality_metrics = {}
        self.alert_thresholds = {
            DataQualityLevel.CRITICAL: 0.99,
            DataQualityLevel.HIGH: 0.95,
            DataQualityLevel.MEDIUM: 0.90,
            DataQualityLevel.LOW: 0.80
        }
        
    def register_rule(self, rule: DataQualityRule):
        """Register a data quality rule"""
        self.rules.append(rule)
        logging.info(f"Registered data quality rule: {rule.name}")
    
    def validate_dataset(self, dataset: pd.DataFrame, dataset_name: str) -> Dict[str, Any]:
        """Validate dataset against all registered rules"""
        validation_results = {
            'dataset_name': dataset_name,
            'timestamp': datetime.now().isoformat(),
            'total_rules': len(self.rules),
            'passed_rules': 0,
            'failed_rules': 0,
            'rule_results': [],
            'overall_score': 0.0,
            'quality_level': None
        }
        
        for rule in self.rules:
            try:
                result = self._execute_rule(rule, dataset)
                validation_results['rule_results'].append(result)
                
                if result['passed']:
                    validation_results['passed_rules'] += 1
                else:
                    validation_results['failed_rules'] += 1
                    
            except Exception as e:
                logging.error(f"Rule execution failed: {rule.name} - {str(e)}")
                validation_results['rule_results'].append({
                    'rule_name': rule.name,
                    'passed': False,
                    'score': 0.0,
                    'error': str(e)
                })
                validation_results['failed_rules'] += 1
        
        # Calculate overall quality score
        if validation_results['total_rules'] > 0:
            validation_results['overall_score'] = validation_results['passed_rules'] / validation_results['total_rules']
        
        # Determine quality level
        validation_results['quality_level'] = self._determine_quality_level(validation_results['overall_score'])
        
        # Store execution history
        self.execution_history.append(validation_results)
        
        return validation_results
    
    def _execute_rule(self, rule: DataQualityRule, dataset: pd.DataFrame) -> Dict[str, Any]:
        """Execute a single data quality rule"""
        start_time = datetime.now()
        
        try:
            # Execute validation function
            score = rule.validation_function(dataset)
            passed = score >= rule.threshold
            
            result = {
                'rule_name': rule.name,
                'rule_type': rule.rule_type,
                'severity': rule.severity.value,
                'score': score,
                'threshold': rule.threshold,
                'passed': passed,
                'execution_time_ms': (datetime.now() - start_time).total_seconds() * 1000,
                'metadata': rule.metadata
            }
            
            if not passed:
                result['violation_details'] = self._get_violation_details(rule, dataset, score)
            
            return result
            
        except Exception as e:
            return {
                'rule_name': rule.name,
                'rule_type': rule.rule_type,
                'severity': rule.severity.value,
                'score': 0.0,
                'threshold': rule.threshold,
                'passed': False,
                'error': str(e),
                'execution_time_ms': (datetime.now() - start_time).total_seconds() * 1000
            }
    
    def _determine_quality_level(self, score: float) -> str:
        """Determine quality level based on score"""
        if score >= self.alert_thresholds[DataQualityLevel.CRITICAL]:
            return "EXCELLENT"
        elif score >= self.alert_thresholds[DataQualityLevel.HIGH]:
            return "GOOD"
        elif score >= self.alert_thresholds[DataQualityLevel.MEDIUM]:
            return "FAIR"
        else:
            return "POOR"
    
    def create_completeness_rule(self, column: str, threshold: float = 0.95) -> DataQualityRule:
        """Create completeness validation rule"""
        def validate_completeness(df: pd.DataFrame) -> float:
            if column not in df.columns:
                return 0.0
            return (df[column].notna().sum() / len(df))
        
        return DataQualityRule(
            name=f"completeness_{column}",
            description=f"Completeness check for column {column}",
            severity=DataQualityLevel.HIGH,
            rule_type="completeness",
            validation_function=validate_completeness,
            threshold=threshold,
            metadata={"column": column}
        )
    
    def create_uniqueness_rule(self, column: str, threshold: float = 0.99) -> DataQualityRule:
        """Create uniqueness validation rule"""
        def validate_uniqueness(df: pd.DataFrame) -> float:
            if column not in df.columns or len(df) == 0:
                return 0.0
            unique_count = df[column].nunique()
            total_count = len(df)
            return unique_count / total_count
        
        return DataQualityRule(
            name=f"uniqueness_{column}",
            description=f"Uniqueness check for column {column}",
            severity=DataQualityLevel.MEDIUM,
            rule_type="validity",
            validation_function=validate_uniqueness,
            threshold=threshold,
            metadata={"column": column}
        )
    
    def create_range_rule(self, column: str, min_val: float, max_val: float, threshold: float = 0.95) -> DataQualityRule:
        """Create range validation rule"""
        def validate_range(df: pd.DataFrame) -> float:
            if column not in df.columns or len(df) == 0:
                return 0.0
            valid_count = df[(df[column] >= min_val) & (df[column] <= max_val)].shape[0]
            return valid_count / len(df)
        
        return DataQualityRule(
            name=f"range_{column}",
            description=f"Range validation for column {column} ({min_val} - {max_val})",
            severity=DataQualityLevel.HIGH,
            rule_type="validity",
            validation_function=validate_range,
            threshold=threshold,
            metadata={"column": column, "min_val": min_val, "max_val": max_val}
        )
    
    def create_pattern_rule(self, column: str, pattern: str, threshold: float = 0.90) -> DataQualityRule:
        """Create pattern validation rule"""
        import re
        compiled_pattern = re.compile(pattern)
        
        def validate_pattern(df: pd.DataFrame) -> float:
            if column not in df.columns or len(df) == 0:
                return 0.0
            valid_count = df[column].astype(str).str.match(compiled_pattern).sum()
            return valid_count / len(df)
        
        return DataQualityRule(
            name=f"pattern_{column}",
            description=f"Pattern validation for column {column}",
            severity=DataQualityLevel.MEDIUM,
            rule_type="validity",
            validation_function=validate_pattern,
            threshold=threshold,
            metadata={"column": column, "pattern": pattern}
        )
    
    def create_timeliness_rule(self, column: str, max_age_hours: int, threshold: float = 0.95) -> DataQualityRule:
        """Create timeliness validation rule"""
        def validate_timeliness(df: pd.DataFrame) -> float:
            if column not in df.columns or len(df) == 0:
                return 0.0
            
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            df[column] = pd.to_datetime(df[column])
            recent_count = (df[column] >= cutoff_time).sum()
            return recent_count / len(df)
        
        return DataQualityRule(
            name=f"timeliness_{column}",
            description=f"Timeliness check for column {column} (max {max_age_hours} hours)",
            severity=DataQualityLevel.HIGH,
            rule_type="timeliness",
            validation_function=validate_timeliness,
            threshold=threshold,
            metadata={"column": column, "max_age_hours": max_age_hours}
        )

class GreatExpectationsIntegration:
    """Integration with Great Expectations for advanced data validation"""
    
    def __init__(self, context_root_dir: str = "/opt/data_quality"):
        import great_expectations as ge
        self.context = ge.get_context(context_root_dir=context_root_dir)
        
    def create_expectation_suite(self, suite_name: str, dataset: pd.DataFrame) -> str:
        """Create expectation suite from dataset"""
        # Convert to Great Expectations dataset
        ge_dataset = ge.from_pandas(dataset)
        
        # Create basic expectations
        expectations = []
        
        for column in dataset.columns:
            # Completeness expectations
            null_percentage = dataset[column].isnull().mean()
            if null_percentage < 0.05:  # Less than 5% nulls
                expectations.append(f"expect_column_values_to_not_be_null('{column}')")
            
            # Type expectations
            if dataset[column].dtype in ['int64', 'float64']:
                expectations.append(f"expect_column_values_to_be_of_type('{column}', '{dataset[column].dtype}')")
            
            # Uniqueness for potential ID columns
            if 'id' in column.lower() and dataset[column].nunique() / len(dataset) > 0.95:
                expectations.append(f"expect_column_values_to_be_unique('{column}')")
        
        # Create and save suite
        suite = self.context.create_expectation_suite(suite_name, overwrite_existing=True)
        
        for expectation in expectations:
            eval(f"ge_dataset.{expectation}")
        
        suite = ge_dataset.get_expectation_suite()
        self.context.save_expectation_suite(suite)
        
        return suite_name
    
    def validate_with_expectations(self, dataset: pd.DataFrame, suite_name: str) -> Dict[str, Any]:
        """Validate dataset using existing expectation suite"""
        ge_dataset = ge.from_pandas(dataset)
        
        # Get the expectation suite
        suite = self.context.get_expectation_suite(suite_name)
        
        # Run validation
        validation_result = ge_dataset.validate(expectation_suite=suite)
        
        return {
            'success': validation_result.success,
            'statistics': validation_result.statistics,
            'results': [
                {
                    'expectation_type': result.expectation_config.expectation_type,
                    'success': result.success,
                    'result': result.result
                }
                for result in validation_result.results
            ]
        }

# Example usage and configuration
if __name__ == "__main__":
    # Initialize data quality framework
    dq_framework = DataQualityFramework()
    
    # Register standard data quality rules
    dq_framework.register_rule(
        dq_framework.create_completeness_rule("user_id", threshold=0.99)
    )
    dq_framework.register_rule(
        dq_framework.create_uniqueness_rule("transaction_id", threshold=1.0)
    )
    dq_framework.register_rule(
        dq_framework.create_range_rule("amount", 0, 100000, threshold=0.95)
    )
    dq_framework.register_rule(
        dq_framework.create_pattern_rule("email", r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    )
    dq_framework.register_rule(
        dq_framework.create_timeliness_rule("created_at", max_age_hours=24)
    )
    
    # Example dataset validation
    sample_data = pd.DataFrame({
        'user_id': ['user1', 'user2', 'user3'],
        'transaction_id': ['txn1', 'txn2', 'txn3'],
        'amount': [100.0, 250.0, 75.0],
        'email': ['user1@example.com', 'user2@example.com', 'invalid-email'],
        'created_at': [datetime.now(), datetime.now(), datetime.now() - timedelta(hours=25)]
    })
    
    # Run validation
    results = dq_framework.validate_dataset(sample_data, "sample_transactions")
    
    print(f"Data Quality Results:")
    print(f"Overall Score: {results['overall_score']:.2%}")
    print(f"Quality Level: {results['quality_level']}")
    print(f"Passed Rules: {results['passed_rules']}/{results['total_rules']}")
```

This rule establishes comprehensive data pipeline standards ensuring reliable, scalable, and maintainable data processing systems through standardized architectures, quality controls, and orchestration patterns.