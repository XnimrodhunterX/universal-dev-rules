# Rule 15A: Machine Learning Operations (MLOps) Standards

<!-- CURSOR: highlight: End-to-end MLOps with model lifecycle management, training pipelines, deployment patterns, monitoring, and ML infrastructure -->

## Purpose & Scope

MLOps standards ensure reliable, scalable, and maintainable machine learning systems through standardized model development lifecycles, automated training pipelines, deployment patterns, and comprehensive monitoring. This rule establishes standards for ML model management, feature engineering, training automation, model serving, performance monitoring, and ML infrastructure to enable robust production ML systems.

<!-- CURSOR: complexity: Advanced -->

## Core Standards

### Model Development Lifecycle

#### 1. Model Registry and Versioning

**MLflow Model Management:**
```python
# src/ml/model_registry.py
import mlflow
import mlflow.pytorch
import mlflow.sklearn
from mlflow.models import infer_signature
from mlflow.tracking import MlflowClient
import torch
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ModelRegistry:
    """
    Centralized model registry for versioning, metadata management, and lifecycle tracking
    """
    
    def __init__(self, tracking_uri: str, registry_uri: Optional[str] = None):
        mlflow.set_tracking_uri(tracking_uri)
        if registry_uri:
            mlflow.set_registry_uri(registry_uri)
        self.client = MlflowClient()
    
    def register_model(
        self,
        model,
        model_name: str,
        run_id: str,
        artifact_path: str = "model",
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Register a trained model with versioning and metadata
        
        Args:
            model: Trained model object (PyTorch, sklearn, etc.)
            model_name: Name for the registered model
            run_id: MLflow run ID where model was trained
            artifact_path: Path within the run to store the model
            description: Model description
            tags: Key-value tags for the model
            metadata: Additional metadata (architecture, hyperparameters, etc.)
        
        Returns:
            Model version string
        """
        try:
            # Log model with signature inference
            with mlflow.start_run(run_id=run_id):
                if hasattr(model, 'predict'):
                    # For sklearn-like models, infer signature from training data
                    signature = None  # Will be inferred during logging
                elif hasattr(model, 'forward'):
                    # For PyTorch models
                    signature = None  # Will be set manually if needed
                
                # Log model based on type
                if hasattr(model, 'state_dict'):  # PyTorch
                    mlflow.pytorch.log_model(
                        model,
                        artifact_path,
                        signature=signature,
                        registered_model_name=model_name,
                        metadata=metadata
                    )
                else:  # sklearn or similar
                    mlflow.sklearn.log_model(
                        model,
                        artifact_path,
                        signature=signature,
                        registered_model_name=model_name,
                        metadata=metadata
                    )
            
            # Get the latest version of the registered model
            latest_version = self.client.get_latest_versions(
                model_name, 
                stages=["None"]
            )[0].version
            
            # Update model version with description and tags
            if description:
                self.client.update_model_version(
                    name=model_name,
                    version=latest_version,
                    description=description
                )
            
            if tags:
                for key, value in tags.items():
                    self.client.set_model_version_tag(
                        name=model_name,
                        version=latest_version,
                        key=key,
                        value=value
                    )
            
            logger.info(f"Model {model_name} version {latest_version} registered successfully")
            return latest_version
            
        except Exception as e:
            logger.error(f"Failed to register model {model_name}: {str(e)}")
            raise
    
    def transition_model_stage(
        self,
        model_name: str,
        version: str,
        stage: str,
        archive_existing: bool = True
    ) -> None:
        """
        Transition model version to a new stage (Staging, Production, Archived)
        
        Args:
            model_name: Name of the registered model
            version: Model version to transition
            stage: Target stage (Staging, Production, Archived)
            archive_existing: Whether to archive existing models in target stage
        """
        try:
            self.client.transition_model_version_stage(
                name=model_name,
                version=version,
                stage=stage,
                archive_existing_versions=archive_existing
            )
            
            logger.info(f"Model {model_name} version {version} transitioned to {stage}")
            
        except Exception as e:
            logger.error(f"Failed to transition model {model_name} version {version}: {str(e)}")
            raise
    
    def get_model_versions(
        self,
        model_name: str,
        stages: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get model versions filtered by stages
        
        Args:
            model_name: Name of the registered model
            stages: List of stages to filter by (e.g., ["Production", "Staging"])
        
        Returns:
            List of model version information
        """
        try:
            versions = self.client.get_latest_versions(
                model_name, 
                stages=stages or ["None", "Staging", "Production", "Archived"]
            )
            
            return [
                {
                    "name": v.name,
                    "version": v.version,
                    "stage": v.current_stage,
                    "creation_timestamp": v.creation_timestamp,
                    "last_updated_timestamp": v.last_updated_timestamp,
                    "description": v.description,
                    "run_id": v.run_id,
                    "source": v.source,
                    "tags": dict(v.tags) if v.tags else {}
                }
                for v in versions
            ]
            
        except Exception as e:
            logger.error(f"Failed to get model versions for {model_name}: {str(e)}")
            raise
    
    def load_model(
        self,
        model_name: str,
        version: Optional[str] = None,
        stage: Optional[str] = None
    ):
        """
        Load a registered model by name and version/stage
        
        Args:
            model_name: Name of the registered model
            version: Specific version to load
            stage: Stage to load from (if version not specified)
        
        Returns:
            Loaded model object
        """
        try:
            if version:
                model_uri = f"models:/{model_name}/{version}"
            elif stage:
                model_uri = f"models:/{model_name}/{stage}"
            else:
                # Load latest version
                latest_version = self.client.get_latest_versions(model_name, stages=["Production"])
                if not latest_version:
                    latest_version = self.client.get_latest_versions(model_name, stages=["None"])
                
                if not latest_version:
                    raise ValueError(f"No versions found for model {model_name}")
                
                model_uri = f"models:/{model_name}/{latest_version[0].version}"
            
            # Load model using appropriate flavor
            try:
                return mlflow.pytorch.load_model(model_uri)
            except:
                try:
                    return mlflow.sklearn.load_model(model_uri)
                except:
                    return mlflow.pyfunc.load_model(model_uri)
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {str(e)}")
            raise

# Example usage and integration
class ModelTrainingPipeline:
    """
    Example training pipeline with model registry integration
    """
    
    def __init__(self, registry: ModelRegistry):
        self.registry = registry
    
    def train_and_register_model(
        self,
        model_name: str,
        model_class,
        train_data,
        val_data,
        hyperparameters: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Train model and register it with proper versioning
        """
        with mlflow.start_run() as run:
            # Log hyperparameters
            mlflow.log_params(hyperparameters)
            
            # Log metadata
            if metadata:
                for key, value in metadata.items():
                    mlflow.log_param(f"metadata_{key}", value)
            
            # Initialize and train model
            model = model_class(**hyperparameters)
            
            # Training loop (simplified)
            train_metrics = self._train_model(model, train_data, val_data)
            
            # Log metrics
            for metric_name, value in train_metrics.items():
                mlflow.log_metric(metric_name, value)
            
            # Register model
            version = self.registry.register_model(
                model=model,
                model_name=model_name,
                run_id=run.info.run_id,
                description=f"Model trained on {datetime.now().isoformat()}",
                tags={
                    "framework": "pytorch" if hasattr(model, "state_dict") else "sklearn",
                    "dataset_version": metadata.get("dataset_version", "unknown"),
                    "algorithm": model.__class__.__name__
                },
                metadata=metadata
            )
            
            return version
    
    def _train_model(self, model, train_data, val_data) -> Dict[str, float]:
        """
        Simplified training logic
        Returns training metrics
        """
        # Implementation depends on model type and framework
        # This is a placeholder for actual training logic
        return {
            "train_accuracy": 0.95,
            "val_accuracy": 0.92,
            "train_loss": 0.05,
            "val_loss": 0.08
        }
```

#### 2. Feature Engineering Pipeline

**Feature Store Implementation:**
```python
# src/ml/feature_store.py
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Callable
import sqlite3
import json
import logging
from datetime import datetime, timedelta
import hashlib
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

@dataclass
class FeatureDefinition:
    """Definition of a feature including metadata and transformation logic"""
    name: str
    description: str
    data_type: str
    source_table: str
    transformation: Optional[str] = None
    dependencies: Optional[List[str]] = None
    version: str = "1.0"
    created_at: Optional[datetime] = None
    tags: Optional[Dict[str, str]] = None

class FeatureTransformer(ABC):
    """Abstract base class for feature transformations"""
    
    @abstractmethod
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        pass

class FeatureStore:
    """
    Feature store for managing feature engineering, storage, and serving
    """
    
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.conn = sqlite3.connect(storage_path, check_same_thread=False)
        self.transformers: Dict[str, FeatureTransformer] = {}
        self._init_schema()
    
    def _init_schema(self):
        """Initialize feature store database schema"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS feature_definitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                data_type TEXT,
                source_table TEXT,
                transformation TEXT,
                dependencies TEXT,
                version TEXT,
                created_at TIMESTAMP,
                tags TEXT
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS feature_values (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature_name TEXT,
                entity_id TEXT,
                value TEXT,
                timestamp TIMESTAMP,
                version TEXT,
                FOREIGN KEY (feature_name) REFERENCES feature_definitions (name)
            )
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_feature_entity 
            ON feature_values (feature_name, entity_id, timestamp)
        """)
        
        self.conn.commit()
    
    def register_feature(self, feature_def: FeatureDefinition) -> None:
        """Register a new feature definition"""
        try:
            # Set creation timestamp if not provided
            if feature_def.created_at is None:
                feature_def.created_at = datetime.now()
            
            # Serialize complex fields
            dependencies_json = json.dumps(feature_def.dependencies) if feature_def.dependencies else None
            tags_json = json.dumps(feature_def.tags) if feature_def.tags else None
            
            self.conn.execute("""
                INSERT OR REPLACE INTO feature_definitions
                (name, description, data_type, source_table, transformation, 
                 dependencies, version, created_at, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                feature_def.name,
                feature_def.description,
                feature_def.data_type,
                feature_def.source_table,
                feature_def.transformation,
                dependencies_json,
                feature_def.version,
                feature_def.created_at,
                tags_json
            ))
            
            self.conn.commit()
            logger.info(f"Feature {feature_def.name} registered successfully")
            
        except Exception as e:
            logger.error(f"Failed to register feature {feature_def.name}: {str(e)}")
            raise
    
    def register_transformer(self, name: str, transformer: FeatureTransformer) -> None:
        """Register a feature transformer"""
        self.transformers[name] = transformer
        logger.info(f"Transformer {name} registered")
    
    def compute_features(
        self,
        feature_names: List[str],
        entity_ids: List[str],
        data_source: pd.DataFrame,
        timestamp: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Compute features for given entities using registered transformers
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Get feature definitions
        feature_defs = self._get_feature_definitions(feature_names)
        
        # Build dependency graph and execution order
        execution_order = self._resolve_dependencies(feature_defs)
        
        # Initialize result DataFrame
        result = pd.DataFrame({'entity_id': entity_ids})
        
        # Compute features in dependency order
        for feature_name in execution_order:
            if feature_name in feature_names:
                feature_def = feature_defs[feature_name]
                
                # Get transformer if available
                if feature_def.transformation and feature_def.transformation in self.transformers:
                    transformer = self.transformers[feature_def.transformation]
                    
                    # Prepare input data (include previously computed features)
                    input_data = data_source.copy()
                    if len(result.columns) > 1:  # If we have computed features
                        input_data = input_data.merge(result, on='entity_id', how='left')
                    
                    # Apply transformation
                    feature_values = transformer.transform(input_data)
                    
                    # Add to result
                    if feature_name in feature_values.columns:
                        result[feature_name] = feature_values[feature_name]
                    else:
                        logger.warning(f"Feature {feature_name} not found in transformer output")
                        result[feature_name] = None
                else:
                    # Direct column mapping or simple computation
                    if feature_def.source_table in data_source.columns:
                        result[feature_name] = data_source[feature_def.source_table]
                    else:
                        logger.warning(f"Source column {feature_def.source_table} not found")
                        result[feature_name] = None
                
                # Store computed values
                self._store_feature_values(feature_name, result, timestamp)
        
        return result
    
    def get_features(
        self,
        feature_names: List[str],
        entity_ids: List[str],
        timestamp: Optional[datetime] = None,
        point_in_time: bool = True
    ) -> pd.DataFrame:
        """
        Retrieve feature values for given entities
        
        Args:
            feature_names: List of feature names to retrieve
            entity_ids: List of entity IDs
            timestamp: Point-in-time timestamp for feature retrieval
            point_in_time: Whether to enforce point-in-time correctness
        
        Returns:
            DataFrame with feature values
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Build query based on point-in-time requirements
        if point_in_time:
            # Get latest values before timestamp
            query = """
                SELECT fv.feature_name, fv.entity_id, fv.value, fv.timestamp
                FROM feature_values fv
                INNER JOIN (
                    SELECT feature_name, entity_id, MAX(timestamp) as max_timestamp
                    FROM feature_values 
                    WHERE timestamp <= ? AND feature_name IN ({})
                    GROUP BY feature_name, entity_id
                ) latest ON fv.feature_name = latest.feature_name 
                    AND fv.entity_id = latest.entity_id 
                    AND fv.timestamp = latest.max_timestamp
                WHERE fv.entity_id IN ({})
            """.format(
                ','.join(['?' for _ in feature_names]),
                ','.join(['?' for _ in entity_ids])
            )
            params = [timestamp] + feature_names + entity_ids
        else:
            # Get latest values regardless of timestamp
            query = """
                SELECT fv.feature_name, fv.entity_id, fv.value, fv.timestamp
                FROM feature_values fv
                INNER JOIN (
                    SELECT feature_name, entity_id, MAX(timestamp) as max_timestamp
                    FROM feature_values 
                    WHERE feature_name IN ({})
                    GROUP BY feature_name, entity_id
                ) latest ON fv.feature_name = latest.feature_name 
                    AND fv.entity_id = latest.entity_id 
                    AND fv.timestamp = latest.max_timestamp
                WHERE fv.entity_id IN ({})
            """.format(
                ','.join(['?' for _ in feature_names]),
                ','.join(['?' for _ in entity_ids])
            )
            params = feature_names + entity_ids
        
        # Execute query and build result DataFrame
        cursor = self.conn.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert to DataFrame and pivot
        if rows:
            df = pd.DataFrame(rows, columns=['feature_name', 'entity_id', 'value', 'timestamp'])
            
            # Parse values based on feature data types
            feature_defs = self._get_feature_definitions(feature_names)
            for _, row in df.iterrows():
                feature_name = row['feature_name']
                if feature_name in feature_defs:
                    data_type = feature_defs[feature_name].data_type
                    if data_type == 'float':
                        df.loc[df['feature_name'] == feature_name, 'value'] = pd.to_numeric(
                            df.loc[df['feature_name'] == feature_name, 'value']
                        )
                    elif data_type == 'int':
                        df.loc[df['feature_name'] == feature_name, 'value'] = pd.to_numeric(
                            df.loc[df['feature_name'] == feature_name, 'value'], downcast='integer'
                        )
            
            # Pivot to get features as columns
            result = df.pivot(index='entity_id', columns='feature_name', values='value').reset_index()
            
            # Ensure all requested entity_ids and features are present
            all_entities = pd.DataFrame({'entity_id': entity_ids})
            result = all_entities.merge(result, on='entity_id', how='left')
            
            # Add missing feature columns
            for feature_name in feature_names:
                if feature_name not in result.columns:
                    result[feature_name] = None
        else:
            # No data found, return empty DataFrame with correct structure
            result = pd.DataFrame({'entity_id': entity_ids})
            for feature_name in feature_names:
                result[feature_name] = None
        
        return result
    
    def _get_feature_definitions(self, feature_names: List[str]) -> Dict[str, FeatureDefinition]:
        """Get feature definitions by names"""
        placeholders = ','.join(['?' for _ in feature_names])
        query = f"SELECT * FROM feature_definitions WHERE name IN ({placeholders})"
        
        cursor = self.conn.execute(query, feature_names)
        rows = cursor.fetchall()
        
        feature_defs = {}
        for row in rows:
            dependencies = json.loads(row[5]) if row[5] else None
            tags = json.loads(row[8]) if row[8] else None
            
            feature_defs[row[1]] = FeatureDefinition(
                name=row[1],
                description=row[2],
                data_type=row[3],
                source_table=row[4],
                transformation=row[5],
                dependencies=dependencies,
                version=row[7],
                created_at=datetime.fromisoformat(row[7]) if row[7] else None,
                tags=tags
            )
        
        return feature_defs
    
    def _resolve_dependencies(self, feature_defs: Dict[str, FeatureDefinition]) -> List[str]:
        """Resolve feature dependencies and return execution order"""
        # Simple topological sort for dependency resolution
        visited = set()
        temp_visited = set()
        result = []
        
        def visit(feature_name: str):
            if feature_name in temp_visited:
                raise ValueError(f"Circular dependency detected involving {feature_name}")
            if feature_name in visited:
                return
            
            temp_visited.add(feature_name)
            
            feature_def = feature_defs.get(feature_name)
            if feature_def and feature_def.dependencies:
                for dep in feature_def.dependencies:
                    visit(dep)
            
            temp_visited.remove(feature_name)
            visited.add(feature_name)
            result.append(feature_name)
        
        for feature_name in feature_defs:
            if feature_name not in visited:
                visit(feature_name)
        
        return result
    
    def _store_feature_values(
        self,
        feature_name: str,
        data: pd.DataFrame,
        timestamp: datetime
    ) -> None:
        """Store computed feature values"""
        for _, row in data.iterrows():
            entity_id = row['entity_id']
            value = row[feature_name]
            
            # Convert value to string for storage
            if pd.isna(value):
                value_str = None
            else:
                value_str = str(value)
            
            self.conn.execute("""
                INSERT INTO feature_values (feature_name, entity_id, value, timestamp, version)
                VALUES (?, ?, ?, ?, ?)
            """, (feature_name, entity_id, value_str, timestamp, "1.0"))
        
        self.conn.commit()

# Example feature transformers
class UserEngagementTransformer(FeatureTransformer):
    """Transformer for user engagement features"""
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        result = data.copy()
        
        # Calculate engagement score
        if all(col in data.columns for col in ['page_views', 'session_duration', 'clicks']):
            result['engagement_score'] = (
                data['page_views'] * 0.3 +
                data['session_duration'] / 60 * 0.4 +  # Convert to minutes
                data['clicks'] * 0.3
            )
        
        # Calculate activity frequency
        if 'last_activity_date' in data.columns:
            result['days_since_last_activity'] = (
                datetime.now() - pd.to_datetime(data['last_activity_date'])
            ).dt.days
        
        return result
    
    def get_dependencies(self) -> List[str]:
        return ['page_views', 'session_duration', 'clicks', 'last_activity_date']

class ProductAffinityTransformer(FeatureTransformer):
    """Transformer for product affinity features"""
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        result = data.copy()
        
        # Calculate category preferences
        if 'purchase_history' in data.columns:
            # Simplified: count purchases by category
            result['electronics_affinity'] = data['purchase_history'].str.count('electronics')
            result['clothing_affinity'] = data['purchase_history'].str.count('clothing')
            result['books_affinity'] = data['purchase_history'].str.count('books')
        
        # Calculate price sensitivity
        if all(col in data.columns for col in ['avg_order_value', 'discount_usage']):
            result['price_sensitivity'] = data['discount_usage'] / (data['avg_order_value'] + 1)
        
        return result
    
    def get_dependencies(self) -> List[str]:
        return ['purchase_history', 'avg_order_value', 'discount_usage']
```

### Training Pipeline Automation

#### 1. Automated Training with Kubeflow

**Kubeflow Pipeline for Model Training:**
```python
# pipelines/training_pipeline.py
import kfp
from kfp import dsl, components
from kfp.v2 import compiler
from kfp.v2.dsl import component, pipeline, Input, Output, Dataset, Model, Metrics
from typing import NamedTuple
import os

# Component for data preprocessing
@component(
    base_image="python:3.9",
    packages_to_install=["pandas", "scikit-learn", "numpy"]
)
def preprocess_data(
    raw_data: Input[Dataset],
    processed_data: Output[Dataset],
    test_size: float = 0.2,
    random_state: int = 42
) -> NamedTuple('Outputs', [('train_size', int), ('test_size', int)]):
    """Preprocess raw data for training"""
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    import pickle
    
    # Load raw data
    df = pd.read_csv(raw_data.path)
    
    # Feature engineering
    X = df.drop(['target'], axis=1)
    y = df['target']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Save processed data
    processed_data_dict = {
        'X_train': X_train_scaled,
        'X_test': X_test_scaled,
        'y_train': y_train.values,
        'y_test': y_test.values,
        'scaler': scaler,
        'feature_names': X.columns.tolist()
    }
    
    with open(processed_data.path, 'wb') as f:
        pickle.dump(processed_data_dict, f)
    
    from collections import namedtuple
    Outputs = namedtuple('Outputs', ['train_size', 'test_size'])
    return Outputs(len(X_train), len(X_test))

# Main training pipeline
@pipeline(
    name="ml-training-pipeline",
    description="Automated ML training pipeline with preprocessing, training, and validation"
)
def training_pipeline(
    dataset_path: str,
    model_type: str = "random_forest",
    test_size: float = 0.2,
    hyperparameter_tuning: bool = True,
    n_trials: int = 50,
    accuracy_threshold: float = 0.8,
    mlflow_tracking_uri: str = "http://mlflow-server:5000"
):
    """
    Complete training pipeline from raw data to validated model
    """
    
    # Create dataset input
    raw_data = dsl.InputUri(dataset_path)
    
    # Step 1: Preprocess data
    preprocess_task = preprocess_data(
        raw_data=raw_data,
        test_size=test_size
    )
    
    # Step 2: Train model
    train_task = train_model(
        processed_data=preprocess_task.outputs['processed_data'],
        model_type=model_type,
        hyperparameter_tuning=hyperparameter_tuning,
        n_trials=n_trials,
        mlflow_tracking_uri=mlflow_tracking_uri
    )
    
    # Step 3: Validate model
    validate_task = validate_model(
        model_input=train_task.outputs['model_output'],
        processed_data=preprocess_task.outputs['processed_data'],
        accuracy_threshold=accuracy_threshold,
        mlflow_tracking_uri=mlflow_tracking_uri
    )
    
    # Only proceed to deployment if validation passes
    validate_task.after(train_task)

# Pipeline compilation and execution
def compile_and_run_pipeline():
    """Compile and submit the training pipeline"""
    
    # Compile pipeline
    compiler.Compiler().compile(
        pipeline_func=training_pipeline,
        package_path='training_pipeline.json'
    )
    
    # Submit to Kubeflow
    import kfp
    client = kfp.Client()
    
    experiment = client.create_experiment('ml-training-experiments')
    
    run = client.run_pipeline(
        experiment_id=experiment.id,
        job_name='ml-training-run',
        pipeline_package_path='training_pipeline.json',
        params={
            'dataset_path': 'gs://ml-data-bucket/training_data.csv',
            'model_type': 'random_forest',
            'hyperparameter_tuning': True,
            'n_trials': 100,
            'accuracy_threshold': 0.85
        }
    )
    
    return run
```

### Model Deployment Patterns

#### 1. Kubernetes Model Serving

**Seldon Core Deployment:**
```yaml
# deployments/model-serving.yaml
apiVersion: machinelearning.seldon.io/v1
kind: SeldonDeployment
metadata:
  name: ml-model-classifier
  namespace: ml-serving
  labels:
    app: ml-model
    version: v1.0.0
spec:
  name: ml-model-classifier
  predictors:
  - componentSpecs:
    - spec:
        containers:
        - name: classifier
          image: ml-models/classifier:v1.0.0
          env:
          - name: MODEL_URI
            value: "gs://ml-models-bucket/classifier/v1.0.0"
          - name: MLFLOW_TRACKING_URI
            value: "http://mlflow-server:5000"
          resources:
            requests:
              cpu: 100m
              memory: 512Mi
            limits:
              cpu: 1000m
              memory: 2Gi
          readinessProbe:
            httpGet:
              path: /health/ping
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health/status
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 30
    graph:
      children: []
      implementation: MLFLOW_SERVER
      modelUri: gs://ml-models-bucket/classifier/v1.0.0
      name: classifier
      parameters:
      - name: model_name
        type: STRING
        value: "random_forest_classifier"
      - name: model_version
        type: STRING
        value: "1"
    name: default
    replicas: 3
    traffic: 100
    engineResources:
      requests:
        cpu: 100m
        memory: 256Mi
      limits:
        cpu: 500m
        memory: 1Gi

---
apiVersion: v1
kind: Service
metadata:
  name: ml-model-classifier-service
  namespace: ml-serving
  labels:
    app: ml-model
spec:
  selector:
    app.kubernetes.io/name: ml-model-classifier
  ports:
  - port: 8080
    targetPort: 8080
    protocol: TCP
    name: http
  type: ClusterIP

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ml-model-classifier-ingress
  namespace: ml-serving
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - ml-api.example.com
    secretName: ml-api-tls
  rules:
  - host: ml-api.example.com
    http:
      paths:
      - path: /predict
        pathType: Prefix
        backend:
          service:
            name: ml-model-classifier-service
            port:
              number: 8080
```

#### 2. Model Monitoring and Observability

**ML Model Monitoring System:**
```python
# src/monitoring/model_monitor.py
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
import logging
from datetime import datetime, timedelta
from prometheus_client import Counter, Histogram, Gauge
from dataclasses import dataclass
import asyncio
import json
from scipy import stats
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import mlflow

logger = logging.getLogger(__name__)

@dataclass
class ModelPerformanceMetrics:
    """Model performance metrics for monitoring"""
    model_name: str
    model_version: str
    timestamp: datetime
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    prediction_count: int = 0
    average_latency_ms: float = 0.0
    error_rate: float = 0.0

@dataclass
class DataDriftMetrics:
    """Data drift detection metrics"""
    feature_name: str
    drift_score: float
    p_value: float
    is_drift_detected: bool
    reference_mean: float
    current_mean: float
    reference_std: float
    current_std: float
    timestamp: datetime

class ModelMonitor:
    """
    Comprehensive model monitoring system for performance and data drift detection
    """
    
    def __init__(self, mlflow_uri: str):
        self.mlflow_uri = mlflow_uri
        mlflow.set_tracking_uri(mlflow_uri)
        
        # Prometheus metrics
        self.prediction_counter = Counter(
            'ml_predictions_total', 
            'Total predictions made', 
            ['model_name', 'model_version']
        )
        self.prediction_latency = Histogram(
            'ml_prediction_duration_seconds', 
            'Prediction latency', 
            ['model_name']
        )
        self.model_accuracy = Gauge(
            'ml_model_accuracy', 
            'Model accuracy', 
            ['model_name', 'model_version']
        )
        self.data_drift_score = Gauge(
            'ml_data_drift_score', 
            'Data drift score', 
            ['model_name', 'feature_name']
        )
        
        # Store reference data for drift detection
        self.reference_data: Dict[str, pd.DataFrame] = {}
        self.performance_history: Dict[str, List[ModelPerformanceMetrics]] = {}
    
    def set_reference_data(self, model_name: str, reference_data: pd.DataFrame) -> None:
        """Set reference data for drift detection"""
        self.reference_data[model_name] = reference_data.copy()
        logger.info(f"Reference data set for model {model_name} with {len(reference_data)} samples")
    
    def log_prediction(
        self,
        model_name: str,
        model_version: str,
        features: Dict[str, Any],
        prediction: Any,
        actual: Optional[Any] = None,
        latency_ms: float = 0.0,
        timestamp: Optional[datetime] = None
    ) -> None:
        """Log individual prediction for monitoring"""
        if timestamp is None:
            timestamp = datetime.now()
        
        # Update Prometheus metrics
        self.prediction_counter.labels(
            model_name=model_name, 
            model_version=model_version
        ).inc()
        
        self.prediction_latency.labels(model_name=model_name).observe(latency_ms / 1000)
        
        # Store prediction data for batch analysis
        prediction_data = {
            'model_name': model_name,
            'model_version': model_version,
            'features': features,
            'prediction': prediction,
            'actual': actual,
            'latency_ms': latency_ms,
            'timestamp': timestamp
        }
        
        # Log to MLflow
        with mlflow.start_run(run_name=f"prediction_log_{timestamp.strftime('%Y%m%d_%H%M%S')}"):
            mlflow.log_params({
                'model_name': model_name,
                'model_version': model_version
            })
            mlflow.log_metrics({
                'latency_ms': latency_ms,
            })
            if actual is not None:
                accuracy = 1.0 if prediction == actual else 0.0
                mlflow.log_metric('prediction_accuracy', accuracy)
    
    def compute_performance_metrics(
        self,
        model_name: str,
        model_version: str,
        predictions: List[Any],
        actuals: List[Any],
        latencies_ms: List[float],
        errors: List[bool],
        timestamp: Optional[datetime] = None
    ) -> ModelPerformanceMetrics:
        """Compute performance metrics for a batch of predictions"""
        if timestamp is None:
            timestamp = datetime.now()
        
        # Convert to numpy arrays for easier computation
        predictions = np.array(predictions)
        actuals = np.array(actuals)
        
        # Compute metrics based on problem type
        if len(np.unique(actuals)) <= 10:  # Classification
            accuracy = accuracy_score(actuals, predictions)
            precision = precision_score(actuals, predictions, average='weighted', zero_division=0)
            recall = recall_score(actuals, predictions, average='weighted', zero_division=0)
            f1 = f1_score(actuals, predictions, average='weighted', zero_division=0)
        else:  # Regression
            from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
            mse = mean_squared_error(actuals, predictions)
            mae = mean_absolute_error(actuals, predictions)
            r2 = r2_score(actuals, predictions)
            
            # Use R² as accuracy proxy for regression
            accuracy = max(0, r2)
            precision = 1.0 / (1.0 + mse)  # Inverse MSE as precision proxy
            recall = 1.0 / (1.0 + mae)     # Inverse MAE as recall proxy
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        metrics = ModelPerformanceMetrics(
            model_name=model_name,
            model_version=model_version,
            timestamp=timestamp,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            prediction_count=len(predictions),
            average_latency_ms=np.mean(latencies_ms),
            error_rate=np.mean(errors)
        )
        
        # Update Prometheus metrics
        self.model_accuracy.labels(
            model_name=model_name, 
            model_version=model_version
        ).set(accuracy)
        
        # Store in history
        if model_name not in self.performance_history:
            self.performance_history[model_name] = []
        self.performance_history[model_name].append(metrics)
        
        # Log to MLflow
        with mlflow.start_run(run_name=f"performance_metrics_{timestamp.strftime('%Y%m%d_%H%M%S')}"):
            mlflow.log_params({
                'model_name': model_name,
                'model_version': model_version,
                'prediction_count': len(predictions)
            })
            mlflow.log_metrics({
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'average_latency_ms': np.mean(latencies_ms),
                'error_rate': np.mean(errors)
            })
        
        return metrics
    
    def detect_data_drift(
        self,
        model_name: str,
        current_data: pd.DataFrame,
        drift_threshold: float = 0.05,
        timestamp: Optional[datetime] = None
    ) -> List[DataDriftMetrics]:
        """
        Detect data drift using statistical tests
        
        Args:
            model_name: Name of the model
            current_data: Current production data
            drift_threshold: P-value threshold for drift detection
            timestamp: Timestamp for drift detection
        
        Returns:
            List of drift metrics for each feature
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        if model_name not in self.reference_data:
            raise ValueError(f"No reference data found for model {model_name}")
        
        reference_data = self.reference_data[model_name]
        drift_metrics = []
        
        # Check each numerical feature
        for feature in current_data.select_dtypes(include=[np.number]).columns:
            if feature in reference_data.columns:
                ref_values = reference_data[feature].dropna()
                current_values = current_data[feature].dropna()
                
                if len(ref_values) > 0 and len(current_values) > 0:
                    # Kolmogorov-Smirnov test for distribution drift
                    ks_statistic, p_value = stats.ks_2samp(ref_values, current_values)
                    
                    is_drift = p_value < drift_threshold
                    
                    metrics = DataDriftMetrics(
                        feature_name=feature,
                        drift_score=ks_statistic,
                        p_value=p_value,
                        is_drift_detected=is_drift,
                        reference_mean=float(ref_values.mean()),
                        current_mean=float(current_values.mean()),
                        reference_std=float(ref_values.std()),
                        current_std=float(current_values.std()),
                        timestamp=timestamp
                    )
                    
                    drift_metrics.append(metrics)
                    
                    # Update Prometheus metrics
                    self.data_drift_score.labels(
                        model_name=model_name,
                        feature_name=feature
                    ).set(ks_statistic)
                    
                    # Log drift detection
                    if is_drift:
                        logger.warning(
                            f"Data drift detected for feature {feature} in model {model_name}: "
                            f"KS statistic={ks_statistic:.4f}, p-value={p_value:.4f}"
                        )
                    
                    # Log to MLflow
                    with mlflow.start_run(run_name=f"drift_detection_{feature}_{timestamp.strftime('%Y%m%d_%H%M%S')}"):
                        mlflow.log_params({
                            'model_name': model_name,
                            'feature_name': feature,
                            'drift_threshold': drift_threshold
                        })
                        mlflow.log_metrics({
                            'ks_statistic': ks_statistic,
                            'p_value': p_value,
                            'reference_mean': float(ref_values.mean()),
                            'current_mean': float(current_values.mean()),
                            'reference_std': float(ref_values.std()),
                            'current_std': float(current_values.std())
                        })
                        mlflow.log_metric('drift_detected', float(is_drift))
        
        return drift_metrics
    
    def generate_monitoring_report(
        self,
        model_name: str,
        days_back: int = 7
    ) -> Dict[str, Any]:
        """Generate comprehensive monitoring report"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)
        
        # Get performance history
        if model_name in self.performance_history:
            recent_metrics = [
                m for m in self.performance_history[model_name]
                if start_time <= m.timestamp <= end_time
            ]
        else:
            recent_metrics = []
        
        if recent_metrics:
            avg_accuracy = np.mean([m.accuracy for m in recent_metrics if m.accuracy is not None])
            avg_latency = np.mean([m.average_latency_ms for m in recent_metrics])
            total_predictions = sum([m.prediction_count for m in recent_metrics])
            avg_error_rate = np.mean([m.error_rate for m in recent_metrics])
        else:
            avg_accuracy = 0.0
            avg_latency = 0.0
            total_predictions = 0
            avg_error_rate = 0.0
        
        report = {
            'model_name': model_name,
            'report_period': {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'days': days_back
            },
            'performance_summary': {
                'average_accuracy': avg_accuracy,
                'average_latency_ms': avg_latency,
                'total_predictions': total_predictions,
                'average_error_rate': avg_error_rate,
                'metrics_count': len(recent_metrics)
            },
            'alerts': []
        }
        
        # Check for performance degradation
        if avg_accuracy < 0.8:
            report['alerts'].append({
                'type': 'performance_degradation',
                'severity': 'high',
                'message': f"Model accuracy ({avg_accuracy:.3f}) is below threshold (0.8)"
            })
        
        if avg_latency > 1000:  # 1 second
            report['alerts'].append({
                'type': 'high_latency',
                'severity': 'medium',
                'message': f"Average latency ({avg_latency:.1f}ms) is high"
            })
        
        if avg_error_rate > 0.05:  # 5%
            report['alerts'].append({
                'type': 'high_error_rate',
                'severity': 'high',
                'message': f"Error rate ({avg_error_rate:.3f}) is above threshold (0.05)"
            })
        
        return report

# Example usage
async def monitoring_example():
    """Example of using the model monitoring system"""
    monitor = ModelMonitor(mlflow_uri="http://mlflow-server:5000")
    
    # Set reference data for drift detection
    reference_data = pd.DataFrame({
        'feature1': np.random.normal(0, 1, 1000),
        'feature2': np.random.normal(5, 2, 1000),
        'feature3': np.random.uniform(0, 10, 1000)
    })
    monitor.set_reference_data('my_model', reference_data)
    
    # Simulate some predictions
    for i in range(100):
        features = {
            'feature1': np.random.normal(0, 1),
            'feature2': np.random.normal(5, 2),
            'feature3': np.random.uniform(0, 10)
        }
        prediction = np.random.randint(0, 2)  # Binary classification
        actual = np.random.randint(0, 2)
        latency = np.random.uniform(50, 200)  # ms
        
        monitor.log_prediction(
            model_name='my_model',
            model_version='1.0',
            features=features,
            prediction=prediction,
            actual=actual,
            latency_ms=latency
        )
    
    # Simulate data drift with slightly different distribution
    current_data = pd.DataFrame({
        'feature1': np.random.normal(0.5, 1.2, 500),  # Shifted mean and variance
        'feature2': np.random.normal(5, 2, 500),
        'feature3': np.random.uniform(0, 10, 500)
    })
    
    # Detect drift
    drift_metrics = monitor.detect_data_drift('my_model', current_data)
    
    for metric in drift_metrics:
        print(f"Feature {metric.feature_name}: drift_score={metric.drift_score:.4f}, "
              f"p_value={metric.p_value:.4f}, drift_detected={metric.is_drift_detected}")
    
    # Generate monitoring report
    report = monitor.generate_monitoring_report('my_model', days_back=1)
    print(json.dumps(report, indent=2))
```

This completes Rule 15A with comprehensive MLOps standards covering model lifecycle management, automated training pipelines, deployment patterns, and advanced monitoring capabilities for production ML systems.