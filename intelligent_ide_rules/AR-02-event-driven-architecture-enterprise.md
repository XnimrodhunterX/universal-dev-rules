# Rule 16B: Event-Driven Architecture Standards

<!-- CURSOR: highlight: Event sourcing, CQRS patterns, message brokers, event streaming, and distributed event processing with consistency patterns -->

## Purpose & Scope

Event-driven architecture standards establish guidelines for designing and implementing systems that respond to and process events through asynchronous communication, event sourcing, and command-query responsibility segregation (CQRS). This rule provides standards for event design, message brokers, event streaming, consistency patterns, and operational considerations to enable scalable and resilient event-driven systems.

<!-- CURSOR: complexity: Advanced -->

## Core Standards

### Event Design Patterns

#### 1. Event Sourcing Implementation

**Event Store and Aggregate Patterns:**
```typescript
// src/event-sourcing/event-store.ts
import { v4 as uuidv4 } from 'uuid';

export interface Event {
  eventId: string;
  aggregateId: string;
  eventType: string;
  eventData: any;
  metadata: EventMetadata;
  version: number;
  timestamp: Date;
}

export interface EventMetadata {
  correlationId?: string;
  causationId?: string;
  userId?: string;
  userAgent?: string;
  ipAddress?: string;
  source: string;
}

export interface Snapshot {
  aggregateId: string;
  aggregateType: string;
  data: any;
  version: number;
  timestamp: Date;
}

export interface EventStoreConfig {
  snapshotFrequency: number; // Create snapshot every N events
  maxEventsToLoad: number;   // Maximum events to load without snapshot
}

export class EventStore {
  private events: Map<string, Event[]> = new Map();
  private snapshots: Map<string, Snapshot> = new Map();
  private config: EventStoreConfig;
  
  constructor(config: EventStoreConfig = { snapshotFrequency: 10, maxEventsToLoad: 100 }) {
    this.config = config;
  }
  
  async saveEvents(
    aggregateId: string,
    events: Event[],
    expectedVersion: number
  ): Promise<void> {
    const existingEvents = this.events.get(aggregateId) || [];
    
    // Optimistic concurrency check
    if (existingEvents.length !== expectedVersion) {
      throw new Error(
        `Concurrency conflict: Expected version ${expectedVersion}, actual version ${existingEvents.length}`
      );
    }
    
    // Validate event versions
    let currentVersion = expectedVersion;
    for (const event of events) {
      currentVersion++;
      if (event.version !== currentVersion) {
        throw new Error(
          `Invalid event version: Expected ${currentVersion}, got ${event.version}`
        );
      }
    }
    
    // Save events
    const allEvents = [...existingEvents, ...events];
    this.events.set(aggregateId, allEvents);
    
    // Create snapshot if needed
    if (allEvents.length % this.config.snapshotFrequency === 0) {
      // This would typically trigger snapshot creation
      console.log(`Snapshot opportunity for aggregate ${aggregateId} at version ${allEvents.length}`);
    }
    
    // Publish events to event bus
    await this.publishEvents(events);
  }
  
  async getEvents(
    aggregateId: string,
    fromVersion: number = 0
  ): Promise<Event[]> {
    const allEvents = this.events.get(aggregateId) || [];
    return allEvents.filter(event => event.version > fromVersion);
  }
  
  async loadAggregate<T>(
    aggregateId: string,
    aggregateClass: new () => T
  ): Promise<{ aggregate: T; version: number }> {
    // Try to load from snapshot first
    const snapshot = this.snapshots.get(aggregateId);
    let aggregate = new aggregateClass();
    let fromVersion = 0;
    
    if (snapshot) {
      (aggregate as any).loadFromSnapshot(snapshot.data);
      fromVersion = snapshot.version;
    }
    
    // Load events since snapshot
    const events = await this.getEvents(aggregateId, fromVersion);
    
    if (events.length > this.config.maxEventsToLoad) {
      throw new Error(
        `Too many events to load (${events.length}). Consider creating a snapshot.`
      );
    }
    
    // Apply events to aggregate
    for (const event of events) {
      (aggregate as any).applyEvent(event);
    }
    
    const currentVersion = fromVersion + events.length;
    return { aggregate, version: currentVersion };
  }
  
  async saveSnapshot(snapshot: Snapshot): Promise<void> {
    this.snapshots.set(snapshot.aggregateId, snapshot);
  }
  
  async getSnapshot(aggregateId: string): Promise<Snapshot | null> {
    return this.snapshots.get(aggregateId) || null;
  }
  
  private async publishEvents(events: Event[]): Promise<void> {
    // This would integrate with your event bus/message broker
    for (const event of events) {
      console.log(`Publishing event: ${event.eventType} for aggregate ${event.aggregateId}`);
      // await this.eventBus.publish(event);
    }
  }
}

// Base Aggregate Root
export abstract class AggregateRoot {
  protected id: string;
  protected version: number = 0;
  private uncommittedEvents: Event[] = [];
  
  constructor(id?: string) {
    this.id = id || uuidv4();
  }
  
  getId(): string {
    return this.id;
  }
  
  getVersion(): number {
    return this.version;
  }
  
  getUncommittedEvents(): Event[] {
    return [...this.uncommittedEvents];
  }
  
  markEventsAsCommitted(): void {
    this.uncommittedEvents = [];
  }
  
  protected addEvent(eventType: string, eventData: any, metadata: EventMetadata): void {
    const event: Event = {
      eventId: uuidv4(),
      aggregateId: this.id,
      eventType,
      eventData,
      metadata,
      version: this.version + 1,
      timestamp: new Date()
    };
    
    this.uncommittedEvents.push(event);
    this.applyEvent(event);
  }
  
  abstract applyEvent(event: Event): void;
  
  loadFromHistory(events: Event[]): void {
    for (const event of events) {
      this.applyEvent(event);
    }
  }
  
  abstract loadFromSnapshot(snapshotData: any): void;
  abstract createSnapshot(): any;
}

// Example Order Aggregate
export class OrderAggregate extends AggregateRoot {
  private customerId: string;
  private items: OrderItem[] = [];
  private status: OrderStatus = OrderStatus.PENDING;
  private totalAmount: number = 0;
  private createdAt: Date;
  private updatedAt: Date;
  
  constructor(id?: string) {
    super(id);
    this.createdAt = new Date();
    this.updatedAt = new Date();
  }
  
  static create(
    customerId: string,
    items: Array<{ productId: string; quantity: number; price: number }>,
    metadata: EventMetadata
  ): OrderAggregate {
    const order = new OrderAggregate();
    
    const orderCreatedData = {
      customerId,
      items: items.map(item => ({
        productId: item.productId,
        quantity: item.quantity,
        price: item.price,
        lineTotal: item.quantity * item.price
      })),
      totalAmount: items.reduce((sum, item) => sum + (item.quantity * item.price), 0),
      createdAt: new Date()
    };
    
    order.addEvent('OrderCreated', orderCreatedData, metadata);
    return order;
  }
  
  addItem(
    productId: string,
    quantity: number,
    price: number,
    metadata: EventMetadata
  ): void {
    if (this.status !== OrderStatus.PENDING) {
      throw new Error('Cannot add items to a non-pending order');
    }
    
    const itemAddedData = {
      productId,
      quantity,
      price,
      lineTotal: quantity * price
    };
    
    this.addEvent('OrderItemAdded', itemAddedData, metadata);
  }
  
  removeItem(productId: string, metadata: EventMetadata): void {
    if (this.status !== OrderStatus.PENDING) {
      throw new Error('Cannot remove items from a non-pending order');
    }
    
    const existingItem = this.items.find(item => item.productId === productId);
    if (!existingItem) {
      throw new Error('Item not found in order');
    }
    
    this.addEvent('OrderItemRemoved', { productId }, metadata);
  }
  
  confirm(metadata: EventMetadata): void {
    if (this.status !== OrderStatus.PENDING) {
      throw new Error('Order is not in pending status');
    }
    
    if (this.items.length === 0) {
      throw new Error('Cannot confirm order with no items');
    }
    
    this.addEvent('OrderConfirmed', { confirmedAt: new Date() }, metadata);
  }
  
  cancel(reason: string, metadata: EventMetadata): void {
    if (this.status === OrderStatus.CANCELLED || this.status === OrderStatus.DELIVERED) {
      throw new Error('Cannot cancel order in current status');
    }
    
    this.addEvent('OrderCancelled', { reason, cancelledAt: new Date() }, metadata);
  }
  
  ship(trackingNumber: string, metadata: EventMetadata): void {
    if (this.status !== OrderStatus.CONFIRMED) {
      throw new Error('Order must be confirmed before shipping');
    }
    
    this.addEvent('OrderShipped', { trackingNumber, shippedAt: new Date() }, metadata);
  }
  
  deliver(metadata: EventMetadata): void {
    if (this.status !== OrderStatus.SHIPPED) {
      throw new Error('Order must be shipped before delivery');
    }
    
    this.addEvent('OrderDelivered', { deliveredAt: new Date() }, metadata);
  }
  
  applyEvent(event: Event): void {
    this.version = event.version;
    this.updatedAt = event.timestamp;
    
    switch (event.eventType) {
      case 'OrderCreated':
        this.customerId = event.eventData.customerId;
        this.items = event.eventData.items;
        this.totalAmount = event.eventData.totalAmount;
        this.status = OrderStatus.PENDING;
        this.createdAt = event.eventData.createdAt;
        break;
        
      case 'OrderItemAdded':
        this.items.push({
          productId: event.eventData.productId,
          quantity: event.eventData.quantity,
          price: event.eventData.price,
          lineTotal: event.eventData.lineTotal
        });
        this.recalculateTotal();
        break;
        
      case 'OrderItemRemoved':
        this.items = this.items.filter(item => item.productId !== event.eventData.productId);
        this.recalculateTotal();
        break;
        
      case 'OrderConfirmed':
        this.status = OrderStatus.CONFIRMED;
        break;
        
      case 'OrderCancelled':
        this.status = OrderStatus.CANCELLED;
        break;
        
      case 'OrderShipped':
        this.status = OrderStatus.SHIPPED;
        break;
        
      case 'OrderDelivered':
        this.status = OrderStatus.DELIVERED;
        break;
        
      default:
        console.warn(`Unknown event type: ${event.eventType}`);
    }
  }
  
  loadFromSnapshot(snapshotData: any): void {
    this.customerId = snapshotData.customerId;
    this.items = snapshotData.items;
    this.status = snapshotData.status;
    this.totalAmount = snapshotData.totalAmount;
    this.createdAt = new Date(snapshotData.createdAt);
    this.updatedAt = new Date(snapshotData.updatedAt);
    this.version = snapshotData.version;
  }
  
  createSnapshot(): any {
    return {
      customerId: this.customerId,
      items: this.items,
      status: this.status,
      totalAmount: this.totalAmount,
      createdAt: this.createdAt.toISOString(),
      updatedAt: this.updatedAt.toISOString(),
      version: this.version
    };
  }
  
  private recalculateTotal(): void {
    this.totalAmount = this.items.reduce((sum, item) => sum + item.lineTotal, 0);
  }
  
  // Getters for read operations
  getCustomerId(): string { return this.customerId; }
  getItems(): OrderItem[] { return [...this.items]; }
  getStatus(): OrderStatus { return this.status; }
  getTotalAmount(): number { return this.totalAmount; }
  getCreatedAt(): Date { return this.createdAt; }
  getUpdatedAt(): Date { return this.updatedAt; }
}

export interface OrderItem {
  productId: string;
  quantity: number;
  price: number;
  lineTotal: number;
}

export enum OrderStatus {
  PENDING = 'PENDING',
  CONFIRMED = 'CONFIRMED',
  SHIPPED = 'SHIPPED',
  DELIVERED = 'DELIVERED',
  CANCELLED = 'CANCELLED'
}
```

#### 2. CQRS Pattern Implementation

**Command and Query Separation:**
```typescript
// src/cqrs/command-bus.ts
export interface Command {
  commandId: string;
  timestamp: Date;
  metadata: CommandMetadata;
}

export interface CommandMetadata {
  userId?: string;
  correlationId?: string;
  source: string;
}

export interface CommandHandler<T extends Command> {
  handle(command: T): Promise<void>;
}

export interface CommandResult {
  success: boolean;
  aggregateId?: string;
  version?: number;
  errors?: string[];
}

export class CommandBus {
  private handlers: Map<string, CommandHandler<any>> = new Map();
  private middlewares: CommandMiddleware[] = [];
  
  registerHandler<T extends Command>(
    commandType: string,
    handler: CommandHandler<T>
  ): void {
    if (this.handlers.has(commandType)) {
      throw new Error(`Handler already registered for command type: ${commandType}`);
    }
    
    this.handlers.set(commandType, handler);
  }
  
  addMiddleware(middleware: CommandMiddleware): void {
    this.middlewares.push(middleware);
  }
  
  async dispatch<T extends Command>(command: T): Promise<CommandResult> {
    const commandType = command.constructor.name;
    const handler = this.handlers.get(commandType);
    
    if (!handler) {
      throw new Error(`No handler registered for command type: ${commandType}`);
    }
    
    // Build middleware chain
    const chain = [...this.middlewares].reverse();
    
    let next = async () => {
      try {
        await handler.handle(command);
        return { success: true };
      } catch (error) {
        return {
          success: false,
          errors: [error instanceof Error ? error.message : 'Unknown error']
        };
      }
    };
    
    for (const middleware of chain) {
      const currentNext = next;
      next = async () => middleware.execute(command, currentNext);
    }
    
    return next();
  }
}

export interface CommandMiddleware {
  execute<T extends Command>(
    command: T,
    next: () => Promise<CommandResult>
  ): Promise<CommandResult>;
}

// Validation Middleware
export class ValidationMiddleware implements CommandMiddleware {
  async execute<T extends Command>(
    command: T,
    next: () => Promise<CommandResult>
  ): Promise<CommandResult> {
    // Validate command structure
    if (!command.commandId || !command.timestamp) {
      return {
        success: false,
        errors: ['Invalid command structure: missing commandId or timestamp']
      };
    }
    
    // Validate metadata
    if (!command.metadata || !command.metadata.source) {
      return {
        success: false,
        errors: ['Invalid command metadata: missing source']
      };
    }
    
    return next();
  }
}

// Logging Middleware
export class LoggingMiddleware implements CommandMiddleware {
  async execute<T extends Command>(
    command: T,
    next: () => Promise<CommandResult>
  ): Promise<CommandResult> {
    const commandType = command.constructor.name;
    const startTime = Date.now();
    
    console.log(`Executing command: ${commandType}`, {
      commandId: command.commandId,
      timestamp: command.timestamp,
      metadata: command.metadata
    });
    
    try {
      const result = await next();
      const duration = Date.now() - startTime;
      
      console.log(`Command completed: ${commandType}`, {
        commandId: command.commandId,
        success: result.success,
        duration: `${duration}ms`
      });
      
      return result;
    } catch (error) {
      const duration = Date.now() - startTime;
      
      console.error(`Command failed: ${commandType}`, {
        commandId: command.commandId,
        error: error instanceof Error ? error.message : 'Unknown error',
        duration: `${duration}ms`
      });
      
      throw error;
    }
  }
}

// Order Commands
export class CreateOrderCommand implements Command {
  commandId: string;
  timestamp: Date;
  metadata: CommandMetadata;
  
  constructor(
    public readonly customerId: string,
    public readonly items: Array<{
      productId: string;
      quantity: number;
      price: number;
    }>,
    metadata: CommandMetadata
  ) {
    this.commandId = uuidv4();
    this.timestamp = new Date();
    this.metadata = metadata;
  }
}

export class AddOrderItemCommand implements Command {
  commandId: string;
  timestamp: Date;
  metadata: CommandMetadata;
  
  constructor(
    public readonly orderId: string,
    public readonly productId: string,
    public readonly quantity: number,
    public readonly price: number,
    metadata: CommandMetadata
  ) {
    this.commandId = uuidv4();
    this.timestamp = new Date();
    this.metadata = metadata;
  }
}

export class ConfirmOrderCommand implements Command {
  commandId: string;
  timestamp: Date;
  metadata: CommandMetadata;
  
  constructor(
    public readonly orderId: string,
    metadata: CommandMetadata
  ) {
    this.commandId = uuidv4();
    this.timestamp = new Date();
    this.metadata = metadata;
  }
}

// Command Handlers
export class CreateOrderCommandHandler implements CommandHandler<CreateOrderCommand> {
  constructor(
    private readonly eventStore: EventStore
  ) {}
  
  async handle(command: CreateOrderCommand): Promise<void> {
    const eventMetadata: EventMetadata = {
      correlationId: command.metadata.correlationId,
      causationId: command.commandId,
      userId: command.metadata.userId,
      source: command.metadata.source
    };
    
    const order = OrderAggregate.create(
      command.customerId,
      command.items,
      eventMetadata
    );
    
    const events = order.getUncommittedEvents();
    await this.eventStore.saveEvents(order.getId(), events, 0);
    order.markEventsAsCommitted();
  }
}

export class AddOrderItemCommandHandler implements CommandHandler<AddOrderItemCommand> {
  constructor(
    private readonly eventStore: EventStore
  ) {}
  
  async handle(command: AddOrderItemCommand): Promise<void> {
    const { aggregate: order, version } = await this.eventStore.loadAggregate(
      command.orderId,
      OrderAggregate
    );
    
    const eventMetadata: EventMetadata = {
      correlationId: command.metadata.correlationId,
      causationId: command.commandId,
      userId: command.metadata.userId,
      source: command.metadata.source
    };
    
    order.addItem(
      command.productId,
      command.quantity,
      command.price,
      eventMetadata
    );
    
    const events = order.getUncommittedEvents();
    await this.eventStore.saveEvents(order.getId(), events, version);
    order.markEventsAsCommitted();
  }
}

// Query Side
export interface QueryHandler<TQuery, TResult> {
  handle(query: TQuery): Promise<TResult>;
}

export class QueryBus {
  private handlers: Map<string, QueryHandler<any, any>> = new Map();
  
  registerHandler<TQuery, TResult>(
    queryType: string,
    handler: QueryHandler<TQuery, TResult>
  ): void {
    this.handlers.set(queryType, handler);
  }
  
  async execute<TQuery, TResult>(query: TQuery): Promise<TResult> {
    const queryType = (query as any).constructor.name;
    const handler = this.handlers.get(queryType);
    
    if (!handler) {
      throw new Error(`No handler registered for query type: ${queryType}`);
    }
    
    return handler.handle(query);
  }
}

// Read Models
export interface OrderReadModel {
  id: string;
  customerId: string;
  customerName: string;
  items: Array<{
    productId: string;
    productName: string;
    quantity: number;
    price: number;
    lineTotal: number;
  }>;
  status: string;
  totalAmount: number;
  createdAt: Date;
  updatedAt: Date;
  version: number;
}

export class GetOrderByIdQuery {
  constructor(public readonly orderId: string) {}
}

export class GetOrdersByCustomerQuery {
  constructor(
    public readonly customerId: string,
    public readonly page: number = 1,
    public readonly pageSize: number = 20
  ) {}
}

export class GetOrdersByStatusQuery {
  constructor(
    public readonly status: string,
    public readonly page: number = 1,
    public readonly pageSize: number = 20
  ) {}
}

// Query Handlers
export class GetOrderByIdQueryHandler implements QueryHandler<GetOrderByIdQuery, OrderReadModel | null> {
  constructor(
    private readonly readModelRepository: OrderReadModelRepository
  ) {}
  
  async handle(query: GetOrderByIdQuery): Promise<OrderReadModel | null> {
    return this.readModelRepository.findById(query.orderId);
  }
}

export class GetOrdersByCustomerQueryHandler implements QueryHandler<GetOrdersByCustomerQuery, {
  orders: OrderReadModel[];
  totalCount: number;
  page: number;
  pageSize: number;
}> {
  constructor(
    private readonly readModelRepository: OrderReadModelRepository
  ) {}
  
  async handle(query: GetOrdersByCustomerQuery) {
    const { orders, totalCount } = await this.readModelRepository.findByCustomerId(
      query.customerId,
      query.page,
      query.pageSize
    );
    
    return {
      orders,
      totalCount,
      page: query.page,
      pageSize: query.pageSize
    };
  }
}

// Read Model Repository
export interface OrderReadModelRepository {
  findById(orderId: string): Promise<OrderReadModel | null>;
  findByCustomerId(customerId: string, page: number, pageSize: number): Promise<{
    orders: OrderReadModel[];
    totalCount: number;
  }>;
  findByStatus(status: string, page: number, pageSize: number): Promise<{
    orders: OrderReadModel[];
    totalCount: number;
  }>;
  save(order: OrderReadModel): Promise<void>;
  update(order: OrderReadModel): Promise<void>;
  delete(orderId: string): Promise<void>;
}
```

This represents the first part of Rule 16B covering event sourcing and CQRS patterns. The implementation continues with message brokers, event streaming, and distributed event processing patterns. 