# Rule 17A: Event-Driven Architecture

## Overview
Event-driven architecture patterns enabling loose coupling, scalability, and resilience through asynchronous communication, event sourcing, CQRS, and distributed event streaming.

## Core Principles

### Event-First Design
- Events as first-class citizens in system design
- Immutable event logs as source of truth
- Eventual consistency over strong consistency
- Decoupled services through event contracts

### Event Architecture
```yaml
# event-architecture.yaml
event_driven_design:
  patterns:
    event_sourcing: "Store events, not state"
    cqrs: "Separate command and query models"
    saga: "Distributed transaction coordination"
    event_streaming: "Real-time event processing"
  
  messaging:
    broker: "apache_kafka"
    serialization: "avro"
    delivery_guarantees: "at_least_once"
    ordering: "per_partition"
  
  consistency:
    model: "eventual_consistency"
    timeout: "30s"
    retry_policy: "exponential_backoff"
    dead_letter_queue: true
```

## Implementation Standards

### 1. Event Store Implementation

#### Event Store Schema
```sql
-- events/schema.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Events table for event sourcing
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    aggregate_id UUID NOT NULL,
    aggregate_type VARCHAR(100) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_version INTEGER NOT NULL DEFAULT 1,
    event_data JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    sequence_number BIGSERIAL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT events_aggregate_sequence UNIQUE (aggregate_id, sequence_number)
);

-- Snapshots table for performance optimization
CREATE TABLE snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    aggregate_id UUID NOT NULL UNIQUE,
    aggregate_type VARCHAR(100) NOT NULL,
    sequence_number BIGINT NOT NULL,
    snapshot_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Event subscriptions for tracking consumers
CREATE TABLE event_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subscription_name VARCHAR(255) NOT NULL UNIQUE,
    last_processed_sequence BIGINT DEFAULT 0,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance indexes
CREATE INDEX idx_events_aggregate_id ON events (aggregate_id);
CREATE INDEX idx_events_aggregate_type ON events (aggregate_type);
CREATE INDEX idx_events_event_type ON events (event_type);
CREATE INDEX idx_events_sequence_number ON events (sequence_number);
CREATE INDEX idx_events_created_at ON events (created_at);
```

#### Event Store Implementation
```typescript
// event-store/EventStore.ts
import { Pool } from 'pg';

export interface Event {
  id?: string;
  aggregateId: string;
  aggregateType: string;
  eventType: string;
  eventVersion: number;
  eventData: any;
  metadata?: any;
  sequenceNumber?: number;
  createdAt?: Date;
}

export class EventStore {
  constructor(private pool: Pool) {}

  /**
   * Append events with optimistic concurrency control
   */
  async appendEvents(
    aggregateId: string, 
    expectedVersion: number, 
    events: Omit<Event, 'aggregateId' | 'sequenceNumber' | 'createdAt'>[]
  ): Promise<Event[]> {
    const client = await this.pool.connect();
    
    try {
      await client.query('BEGIN');

      // Check current version for optimistic concurrency control
      const { rows: currentEvents } = await client.query(
        'SELECT sequence_number FROM events WHERE aggregate_id = $1 ORDER BY sequence_number DESC LIMIT 1',
        [aggregateId]
      );

      const currentVersion = currentEvents.length > 0 ? currentEvents[0].sequence_number : 0;
      
      if (currentVersion !== expectedVersion) {
        throw new Error(`Concurrency conflict: expected version ${expectedVersion}, but current version is ${currentVersion}`);
      }

      const savedEvents: Event[] = [];

      for (let i = 0; i < events.length; i++) {
        const event = events[i];
        const { rows } = await client.query(`
          INSERT INTO events (aggregate_id, aggregate_type, event_type, event_version, event_data, metadata)
          VALUES ($1, $2, $3, $4, $5, $6)
          RETURNING *
        `, [
          aggregateId,
          event.aggregateType,
          event.eventType,
          event.eventVersion,
          JSON.stringify(event.eventData),
          JSON.stringify(event.metadata || {})
        ]);

        savedEvents.push({
          ...rows[0],
          eventData: rows[0].event_data,
          metadata: rows[0].metadata
        });
      }

      await client.query('COMMIT');
      return savedEvents;
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }

  /**
   * Get events for an aggregate
   */
  async getEvents(aggregateId: string, fromVersion?: number): Promise<Event[]> {
    const query = fromVersion
      ? 'SELECT * FROM events WHERE aggregate_id = $1 AND sequence_number > $2 ORDER BY sequence_number'
      : 'SELECT * FROM events WHERE aggregate_id = $1 ORDER BY sequence_number';
    
    const params = fromVersion ? [aggregateId, fromVersion] : [aggregateId];
    
    const { rows } = await this.pool.query(query, params);
    
    return rows.map(row => ({
      ...row,
      eventData: row.event_data,
      metadata: row.metadata,
      sequenceNumber: row.sequence_number,
      createdAt: row.created_at
    }));
  }

  /**
   * Save snapshot for performance optimization
   */
  async saveSnapshot(aggregateId: string, aggregateType: string, sequenceNumber: number, snapshotData: any): Promise<void> {
    await this.pool.query(`
      INSERT INTO snapshots (aggregate_id, aggregate_type, sequence_number, snapshot_data)
      VALUES ($1, $2, $3, $4)
      ON CONFLICT (aggregate_id) 
      DO UPDATE SET 
        sequence_number = EXCLUDED.sequence_number,
        snapshot_data = EXCLUDED.snapshot_data,
        created_at = NOW()
    `, [aggregateId, aggregateType, sequenceNumber, JSON.stringify(snapshotData)]);
  }

  /**
   * Get events from sequence for subscriptions
   */
  async getEventsFromSequence(fromSequence: number, batchSize: number = 100): Promise<Event[]> {
    const { rows } = await this.pool.query(`
      SELECT * FROM events 
      WHERE sequence_number > $1 
      ORDER BY sequence_number 
      LIMIT $2
    `, [fromSequence, batchSize]);

    return rows.map(row => ({
      ...row,
      eventData: row.event_data,
      metadata: row.metadata,
      sequenceNumber: row.sequence_number,
      createdAt: row.created_at
    }));
  }
}
```

### 2. Aggregate Root Pattern

#### Base Aggregate Root
```typescript
// domain/AggregateRoot.ts
import { Event } from '../event-store/EventStore';

export abstract class AggregateRoot {
  protected id: string;
  protected version: number = 0;
  private uncommittedEvents: Event[] = [];

  constructor(id: string) {
    this.id = id;
  }

  getId(): string {
    return this.id;
  }

  getVersion(): number {
    return this.version;
  }

  getUncommittedEvents(): Event[] {
    return this.uncommittedEvents;
  }

  markEventsAsCommitted(): void {
    this.uncommittedEvents = [];
  }

  /**
   * Apply event to aggregate
   */
  protected applyEvent(event: Omit<Event, 'aggregateId' | 'sequenceNumber' | 'createdAt'>): void {
    const fullEvent: Event = {
      ...event,
      aggregateId: this.id
    };

    this.apply(fullEvent);
    this.uncommittedEvents.push(fullEvent);
    this.version++;
  }

  /**
   * Rebuild aggregate from events
   */
  loadFromHistory(events: Event[]): void {
    events.forEach(event => {
      this.apply(event);
      this.version = event.sequenceNumber || this.version + 1;
    });
  }

  protected abstract apply(event: Event): void;
}
```

#### Order Aggregate Example
```typescript
// domain/Order.ts
import { AggregateRoot } from './AggregateRoot';
import { Event } from '../event-store/EventStore';

export interface OrderItem {
  productId: string;
  quantity: number;
  price: number;
}

export enum OrderStatus {
  PENDING = 'pending',
  CONFIRMED = 'confirmed',
  CANCELLED = 'cancelled'
}

export class Order extends AggregateRoot {
  private customerId: string = '';
  private items: OrderItem[] = [];
  private totalAmount: number = 0;
  private status: OrderStatus = OrderStatus.PENDING;

  static create(id: string, customerId: string, items: OrderItem[]): Order {
    const order = new Order(id);
    
    const totalAmount = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    
    order.applyEvent({
      aggregateType: 'Order',
      eventType: 'OrderCreated',
      eventVersion: 1,
      eventData: { customerId, items, totalAmount },
      metadata: { timestamp: new Date().toISOString() }
    });

    return order;
  }

  confirm(): void {
    if (this.status !== OrderStatus.PENDING) {
      throw new Error('Only pending orders can be confirmed');
    }

    this.applyEvent({
      aggregateType: 'Order',
      eventType: 'OrderConfirmed',
      eventVersion: 1,
      eventData: { confirmedAt: new Date() },
      metadata: { timestamp: new Date().toISOString() }
    });
  }

  cancel(reason: string): void {
    if (this.status === OrderStatus.CANCELLED) {
      throw new Error('Order is already cancelled');
    }

    this.applyEvent({
      aggregateType: 'Order',
      eventType: 'OrderCancelled',
      eventVersion: 1,
      eventData: { reason, cancelledAt: new Date() },
      metadata: { timestamp: new Date().toISOString() }
    });
  }

  protected apply(event: Event): void {
    switch (event.eventType) {
      case 'OrderCreated':
        this.customerId = event.eventData.customerId;
        this.items = [...event.eventData.items];
        this.totalAmount = event.eventData.totalAmount;
        this.status = OrderStatus.PENDING;
        break;
      case 'OrderConfirmed':
        this.status = OrderStatus.CONFIRMED;
        break;
      case 'OrderCancelled':
        this.status = OrderStatus.CANCELLED;
        break;
    }
  }

  // Getters
  getCustomerId(): string { return this.customerId; }
  getItems(): OrderItem[] { return [...this.items]; }
  getTotalAmount(): number { return this.totalAmount; }
  getStatus(): OrderStatus { return this.status; }
}
```

### 3. CQRS Implementation

#### Command Bus
```typescript
// cqrs/CommandBus.ts
export interface Command {
  id: string;
  type: string;
  payload: any;
}

export interface CommandHandler<T extends Command> {
  handle(command: T): Promise<void>;
}

export class CommandBus {
  private handlers = new Map<string, CommandHandler<any>>();

  register<T extends Command>(commandType: string, handler: CommandHandler<T>): void {
    this.handlers.set(commandType, handler);
  }

  async send<T extends Command>(command: T): Promise<void> {
    const handler = this.handlers.get(command.type);
    if (!handler) {
      throw new Error(`No handler registered for command type: ${command.type}`);
    }

    await handler.handle(command);
  }
}
```

#### Order Command Handlers
```typescript
// commands/OrderCommandHandlers.ts
import { CommandHandler } from '../cqrs/CommandBus';
import { EventStore } from '../event-store/EventStore';
import { Order } from '../domain/Order';

export interface CreateOrderCommand {
  id: string;
  type: 'CreateOrder';
  payload: {
    orderId: string;
    customerId: string;
    items: Array<{
      productId: string;
      quantity: number;
      price: number;
    }>;
  };
}

export class CreateOrderCommandHandler implements CommandHandler<CreateOrderCommand> {
  constructor(private eventStore: EventStore) {}

  async handle(command: CreateOrderCommand): Promise<void> {
    const { orderId, customerId, items } = command.payload;

    // Check if order already exists
    const existingEvents = await this.eventStore.getEvents(orderId);
    if (existingEvents.length > 0) {
      throw new Error(`Order with ID ${orderId} already exists`);
    }

    // Create new order aggregate
    const order = Order.create(orderId, customerId, items);

    // Save events
    await this.eventStore.appendEvents(
      orderId,
      0,
      order.getUncommittedEvents()
    );

    order.markEventsAsCommitted();
  }
}
```

### 4. Event Streaming with Kafka

#### Kafka Event Publisher
```typescript
// messaging/KafkaEventPublisher.ts
import { Kafka, Producer } from 'kafkajs';

export interface DomainEvent {
  id: string;
  aggregateId: string;
  aggregateType: string;
  eventType: string;
  eventData: any;
  metadata: any;
  version: number;
  occurredAt: Date;
}

export class KafkaEventPublisher {
  private producer: Producer;

  constructor(private kafka: Kafka) {
    this.producer = kafka.producer({
      maxInFlightRequests: 1,
      idempotent: true
    });
  }

  async connect(): Promise<void> {
    await this.producer.connect();
  }

  async publishEvent(event: DomainEvent): Promise<void> {
    const topic = `${event.aggregateType.toLowerCase()}-events`;
    
    await this.producer.send({
      topic,
      messages: [{
        key: event.aggregateId,
        value: JSON.stringify({
          id: event.id,
          aggregateId: event.aggregateId,
          aggregateType: event.aggregateType,
          eventType: event.eventType,
          eventData: event.eventData,
          metadata: {
            ...event.metadata,
            version: event.version,
            occurredAt: event.occurredAt.toISOString(),
            publishedAt: new Date().toISOString()
          }
        })
      }]
    });
  }
}
```

#### Event Consumer
```typescript
// messaging/KafkaEventConsumer.ts
import { Kafka, Consumer } from 'kafkajs';

export interface EventHandler {
  eventType: string;
  handle(event: DomainEvent): Promise<void>;
}

export class KafkaEventConsumer {
  private consumer: Consumer;
  private handlers = new Map<string, EventHandler[]>();

  constructor(kafka: Kafka, groupId: string) {
    this.consumer = kafka.consumer({ groupId });
  }

  async connect(): Promise<void> {
    await this.consumer.connect();
  }

  registerHandler(handler: EventHandler): void {
    if (!this.handlers.has(handler.eventType)) {
      this.handlers.set(handler.eventType, []);
    }
    this.handlers.get(handler.eventType)!.push(handler);
  }

  async subscribe(topics: string[]): Promise<void> {
    await this.consumer.subscribe({ topics });

    await this.consumer.run({
      eachMessage: async ({ message }) => {
        if (!message.value) return;

        const event: DomainEvent = JSON.parse(message.value.toString());
        const handlers = this.handlers.get(event.eventType) || [];
        
        await Promise.all(
          handlers.map(handler => handler.handle(event))
        );
      }
    });
  }
}
```

### 5. Read Model Projections

#### Order Read Model
```typescript
// projections/OrderProjection.ts
import { EventHandler, DomainEvent } from '../messaging/KafkaEventConsumer';
import { Pool } from 'pg';

export class OrderProjectionHandler implements EventHandler {
  eventType = 'OrderCreated';

  constructor(private pool: Pool) {}

  async handle(event: DomainEvent): Promise<void> {
    const { customerId, items, totalAmount } = event.eventData;
    
    await this.pool.query(`
      INSERT INTO order_read_models (
        id, customer_id, status, total_amount, item_count, created_at
      ) VALUES ($1, $2, $3, $4, $5, $6)
    `, [
      event.aggregateId,
      customerId,
      'pending',
      totalAmount,
      items.length,
      new Date()
    ]);
  }
}
```

## CI/CD Integration

### Event Architecture Pipeline
```yaml
# .github/workflows/event-architecture.yml
name: Event Architecture

on:
  push:
    paths:
      - 'event-store/**'
      - 'messaging/**'

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Setup database schema
        run: |
          PGPASSWORD=postgres psql -h localhost -U postgres -d postgres -f event-store/schema.sql
      
      - name: Run tests
        run: npm test
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/postgres

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy event store
        run: |
          kubectl apply -f k8s/event-store.yaml
          kubectl rollout status deployment/event-store
```

## Success Criteria

- ✅ Event store provides ACID transactions and optimistic concurrency
- ✅ Aggregates properly apply events and maintain consistency
- ✅ CQRS separates command and query responsibilities
- ✅ Event streaming enables real-time processing
- ✅ Projections maintain eventually consistent read models
- ✅ Events are immutable and provide complete audit trail
- ✅ System maintains 99.9% availability during event processing
- ✅ Event processing latency < 100ms (P95) 