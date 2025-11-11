#!/usr/bin/env python3
"""
Real Data Content Library for Learning Companion
===============================================

Comprehensive, real-world programming content library with authentic examples,
industry-standard practices, and practical learning scenarios.
"""

from .content_models import ContentModule, ContentType, DifficultyLevel, Emotion
import json

class RealDataContentLibrary:
    """Real-world content library with authentic programming examples and scenarios."""

    def __init__(self):
        self.content_modules = self._load_real_content()

    def _load_real_content(self) -> dict:
        """Load real programming content from various domains."""

        return {
            "python_programming": self._get_python_modules(),
            "web_development": self._get_web_dev_modules(),
            "data_science": self._get_data_science_modules(),
            "algorithms": self._get_algorithm_modules(),
            "system_administration": self._get_system_admin_modules(),
            "machine_learning": self._get_ml_modules(),
            "devops": self._get_devops_modules()
        }

    def _get_python_modules(self) -> list:
        """Real Python programming content with industry examples."""

        return [
            ContentModule(
                content_id="python_oop_design",
                title="Object-Oriented Design Patterns",
                content_type=ContentType.CONCEPT_EXPLANATION,
                difficulty=DifficultyLevel.INTERMEDIATE,
                emotional_alignment=[Emotion.ANALYTICAL, Emotion.CALM],
                estimated_duration=25,
                prerequisites=["python_basics", "functions"],
                learning_objectives=[
                    "Understand SOLID principles",
                    "Implement Factory and Observer patterns",
                    "Apply design patterns to real problems"
                ],
                content_data={
                    "concept_breakdown": {
                        "solid_principles": {
                            "SRP": "Single Responsibility Principle",
                            "OCP": "Open/Closed Principle",
                            "LSP": "Liskov Substitution Principle",
                            "ISP": "Interface Segregation Principle",
                            "DIP": "Dependency Inversion Principle"
                        },
                        "common_patterns": {
                            "factory": "Creates objects without specifying exact classes",
                            "observer": "Defines one-to-many dependency",
                            "singleton": "Ensures single instance",
                            "strategy": "Encapsulates algorithms"
                        }
                    },
                    "real_world_examples": [
                        {
                            "domain": "E-commerce",
                            "pattern": "Factory",
                            "code": """
class PaymentProcessor:
    @staticmethod
    def create_processor(payment_type):
        if payment_type == 'credit_card':
            return CreditCardProcessor()
        elif payment_type == 'paypal':
            return PayPalProcessor()
        elif payment_type == 'crypto':
            return CryptoProcessor()
        else:
            raise ValueError(f"Unknown payment type: {payment_type}")
                            """,
                            "explanation": "Payment processor factory handles different payment methods"
                        }
                    ]
                },
                success_criteria={
                    "solid_understanding": True,
                    "pattern_implementation": True,
                    "real_world_application": True
                }
            ),

            ContentModule(
                content_id="python_async_programming",
                title="Asynchronous Programming with asyncio",
                content_type=ContentType.PRACTICAL_PROJECT,
                difficulty=DifficultyLevel.ADVANCED,
                emotional_alignment=[Emotion.ENGAGED, Emotion.CREATIVE],
                estimated_duration=35,
                prerequisites=["python_basics", "networking"],
                learning_objectives=[
                    "Master async/await syntax",
                    "Build concurrent web scrapers",
                    "Implement async database operations"
                ],
                content_data={
                    "project_prompt": "Build an async web scraper for GitHub repositories",
                    "requirements": [
                        "Use aiohttp for HTTP requests",
                        "Implement concurrent API calls",
                        "Handle rate limiting gracefully",
                        "Store results in async database"
                    ],
                    "starter_code": """
import asyncio
import aiohttp
from typing import List, Dict
import json

class GitHubScraper:
    def __init__(self, token: str):
        self.token = token
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={'Authorization': f'token {self.token}'}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_repo_data(self, repo_url: str) -> Dict:
        \"\"\"Fetch repository data asynchronously.\"\"\"
        async with self.session.get(repo_url) as response:
            return await response.json()

    async def scrape_repositories(self, usernames: List[str]) -> List[Dict]:
        \"\"\"Scrape multiple repositories concurrently.\"\"\"
        # Implementation here
        pass
                    """,
                    "advanced_challenges": [
                        "Implement exponential backoff for rate limits",
                        "Add database persistence with async SQLAlchemy",
                        "Create progress tracking with tqdm"
                    ]
                },
                success_criteria={
                    "async_syntax_mastery": True,
                    "concurrent_operations": True,
                    "error_handling": True,
                    "production_ready": True
                }
            )
        ]

    def _get_web_dev_modules(self) -> list:
        """Real web development content with modern frameworks."""

        return [
            ContentModule(
                content_id="react_hooks_patterns",
                title="Advanced React Hooks Patterns",
                content_type=ContentType.INTERACTIVE_EXERCISE,
                difficulty=DifficultyLevel.ADVANCED,
                emotional_alignment=[Emotion.CREATIVE, Emotion.ENGAGED],
                estimated_duration=30,
                prerequisites=["javascript", "react_basics"],
                learning_objectives=[
                    "Master custom hooks",
                    "Implement compound component patterns",
                    "Use hooks for data fetching and caching"
                ],
                content_data={
                    "exercise_prompt": "Build a data table component with sorting, filtering, and pagination using custom hooks",
                    "requirements": [
                        "Create useDataTable hook for state management",
                        "Implement useLocalStorage for persistence",
                        "Add useDebounce for search optimization",
                        "Support generic data types"
                    ],
                    "starter_code": """
import { useState, useEffect, useCallback, useMemo } from 'react';

function useDataTable(initialData, initialSort = {}) {
    const [data, setData] = useState(initialData);
    const [sortConfig, setSortConfig] = useState(initialSort);
    const [filters, setFilters] = useState({});
    const [page, setPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);

    // Sorting logic
    const sortedData = useMemo(() => {
        // Implementation here
    }, [data, sortConfig]);

    // Filtering logic
    const filteredData = useMemo(() => {
        // Implementation here
    }, [sortedData, filters]);

    // Pagination logic
    const paginatedData = useMemo(() => {
        // Implementation here
    }, [filteredData, page, pageSize]);

    const handleSort = useCallback((key) => {
        // Implementation here
    }, []);

    const handleFilter = useCallback((key, value) => {
        // Implementation here
    }, []);

    return {
        data: paginatedData,
        totalCount: filteredData.length,
        sortConfig,
        filters,
        page,
        pageSize,
        handleSort,
        handleFilter,
        setPage,
        setPageSize
    };
}

export default useDataTable;
                    """,
                    "real_world_scenarios": [
                        "Building admin dashboards",
                        "E-commerce product listings",
                        "User management interfaces",
                        "Analytics data tables"
                    ]
                },
                success_criteria={
                    "custom_hooks_created": True,
                    "reusable_components": True,
                    "performance_optimized": True,
                    "typescript_integration": True
                }
            )
        ]

    def _get_data_science_modules(self) -> list:
        """Real data science content with industry applications."""

        return [
            ContentModule(
                content_id="pandas_advanced_techniques",
                title="Advanced Pandas for Big Data Processing",
                content_type=ContentType.PRACTICAL_PROJECT,
                difficulty=DifficultyLevel.ADVANCED,
                emotional_alignment=[Emotion.ANALYTICAL, Emotion.CALM],
                estimated_duration=45,
                prerequisites=["python", "pandas_basics", "numpy"],
                learning_objectives=[
                    "Master vectorized operations",
                    "Implement efficient data pipelines",
                    "Handle large datasets with chunking",
                    "Optimize memory usage"
                ],
                content_data={
                    "project_prompt": "Process a 10GB+ dataset of NYC taxi trips to find insights about traffic patterns",
                    "dataset_info": {
                        "source": "NYC Taxi & Limousine Commission",
                        "size": "~10GB compressed",
                        "columns": ["pickup_datetime", "dropoff_datetime", "passenger_count", "trip_distance", "fare_amount", "tip_amount", "total_amount"],
                        "time_range": "2019-2020"
                    },
                    "technical_requirements": [
                        "Process data in chunks to manage memory",
                        "Use categorical data types for optimization",
                        "Implement parallel processing where possible",
                        "Create efficient aggregations"
                    ],
                    "analysis_tasks": [
                        "Calculate hourly pickup patterns",
                        "Find most profitable routes",
                        "Analyze tip percentages by time/location",
                        "Identify surge pricing patterns"
                    ],
                    "starter_code": """
import pandas as pd
import numpy as np
from typing import Iterator, Dict, Any
import dask.dataframe as dd

def process_taxi_data_chunked(file_path: str, chunk_size: int = 100000):
    \"\"\"Process large taxi dataset in chunks.\"\"\"
    results = []

    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        # Memory optimization
        chunk['pickup_datetime'] = pd.to_datetime(chunk['pickup_datetime'])
        chunk['dropoff_datetime'] = pd.to_datetime(chunk['dropoff_datetime'])

        # Calculate derived columns
        chunk['trip_duration'] = (chunk['dropoff_datetime'] - chunk['pickup_datetime']).dt.total_seconds() / 60
        chunk['hour'] = chunk['pickup_datetime'].dt.hour
        chunk['day_of_week'] = chunk['pickup_datetime'].dt.dayofweek

        # Filter outliers
        chunk = chunk[
            (chunk['trip_distance'] > 0) &
            (chunk['trip_distance'] < 100) &
            (chunk['fare_amount'] > 0) &
            (chunk['fare_amount'] < 500)
        ]

        results.append(process_chunk(chunk))

    return pd.concat(results, ignore_index=True)

def process_chunk(chunk: pd.DataFrame) -> pd.DataFrame:
    \"\"\"Process individual chunk.\"\"\"
    # Implementation for aggregations and insights
    return chunk
                    """,
                    "performance_optimizations": [
                        "Use appropriate dtypes (category, int32, float32)",
                        "Leverage pandas eval() for complex operations",
                        "Implement proper indexing strategies",
                        "Use swifter or dask for parallel processing"
                    ]
                },
                success_criteria={
                    "memory_efficient": True,
                    "processing_performance": True,
                    "insightful_analysis": True,
                    "scalable_solution": True
                }
            )
        ]

    def _get_algorithm_modules(self) -> list:
        """Real algorithm and data structures content."""

        return [
            ContentModule(
                content_id="graph_algorithms_real_world",
                title="Graph Algorithms for Social Network Analysis",
                content_type=ContentType.PRACTICAL_PROJECT,
                difficulty=DifficultyLevel.ADVANCED,
                emotional_alignment=[Emotion.ANALYTICAL, Emotion.ENGAGED],
                estimated_duration=40,
                prerequisites=["data_structures", "python_basics"],
                learning_objectives=[
                    "Implement graph traversal algorithms",
                    "Apply centrality measures",
                    "Find communities and clusters",
                    "Analyze network properties"
                ],
                content_data={
                    "project_prompt": "Analyze GitHub collaboration networks to find key contributors and project clusters",
                    "real_data_source": "GitHub API or local repository analysis",
                    "algorithms_to_implement": [
                        "Breadth-First Search (BFS)",
                        "Depth-First Search (DFS)",
                        "PageRank algorithm",
                        "Community detection (Louvain method)",
                        "Betweenness centrality"
                    ],
                    "analysis_goals": [
                        "Identify most influential contributors",
                        "Find collaboration clusters",
                        "Detect bridge maintainers",
                        "Analyze project ecosystem structure"
                    ],
                    "starter_code": """
from collections import defaultdict, deque
import heapq
from typing import List, Dict, Set, Tuple
import networkx as nx

class GitHubCollaborationGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.contributors = {}
        self.repositories = {}

    def add_collaboration(self, contributor: str, repo: str, contribution_type: str):
        \"\"\"Add collaboration edge between contributor and repository.\"\"\"
        # Implementation here

    def calculate_centrality_measures(self) -> Dict[str, float]:
        \"\"\"Calculate various centrality measures.\"\"\"
        # PageRank
        pagerank = nx.pagerank(self.graph)

        # Betweenness centrality
        betweenness = nx.betweenness_centrality(self.graph)

        # Degree centrality
        degree = nx.degree_centrality(self.graph)

        return {
            'pagerank': pagerank,
            'betweenness': betweenness,
            'degree': degree
        }

    def find_communities(self) -> List[List[str]]:
        \"\"\"Find communities using Louvain method.\"\"\"
        try:
            from community import community_louvain
            partition = community_louvain.best_partition(self.graph.to_undirected())
            communities = defaultdict(list)

            for node, community_id in partition.items():
                communities[community_id].append(node)

            return list(communities.values())
        except ImportError:
            # Fallback to connected components
            return [list(component) for component in nx.connected_components(self.graph.to_undirected())]

    def analyze_collaboration_patterns(self) -> Dict[str, Any]:
        \"\"\"Analyze collaboration patterns and insights.\"\"\"
        # Implementation here
        pass
                    """,
                    "real_world_insights": [
                        "Identifying key maintainers",
                        "Finding collaboration bottlenecks",
                        "Discovering project ecosystems",
                        "Measuring contributor influence"
                    ]
                },
                success_criteria={
                    "algorithms_implemented": True,
                    "graph_analysis": True,
                    "performance_optimized": True,
                    "actionable_insights": True
                }
            )
        ]

    def _get_system_admin_modules(self) -> list:
        """Real system administration content."""

        return [
            ContentModule(
                content_id="linux_system_monitoring",
                title="Advanced Linux System Monitoring and Alerting",
                content_type=ContentType.PRACTICAL_PROJECT,
                difficulty=DifficultyLevel.INTERMEDIATE,
                emotional_alignment=[Emotion.ANALYTICAL, Emotion.URGENT],
                estimated_duration=35,
                prerequisites=["linux_basics", "bash_scripting"],
                learning_objectives=[
                    "Implement comprehensive system monitoring",
                    "Create alerting mechanisms",
                    "Build dashboard visualizations",
                    "Automate incident response"
                ],
                content_data={
                    "project_prompt": "Build a production-ready monitoring system for a Linux server with alerting and dashboards",
                    "monitoring_components": [
                        "CPU usage and load averages",
                        "Memory utilization and swap",
                        "Disk I/O and space usage",
                        "Network traffic and connections",
                        "System logs and error patterns",
                        "Process monitoring and resource usage"
                    ],
                    "alerting_system": {
                        "cpu_threshold": "80%",
                        "memory_threshold": "85%",
                        "disk_threshold": "90%",
                        "notification_channels": ["email", "slack", "pagerduty"]
                    },
                    "starter_code": """
#!/bin/bash

# Advanced System Monitor
# =======================

MONITOR_CONFIG="/etc/monitor/config.json"

# Load configuration
if [ -f "$MONITOR_CONFIG" ]; then
    ALERT_EMAIL=$(jq -r '.alert_email' "$MONITOR_CONFIG")
    SLACK_WEBHOOK=$(jq -r '.slack_webhook' "$MONITOR_CONFIG")
    THRESHOLDS=$(jq -r '.thresholds' "$MONITOR_CONFIG")
fi

# System metrics collection
collect_system_metrics() {
    echo "{
        \"timestamp\": \"$(date -Iseconds)\",
        \"cpu_usage\": $(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}'),
        \"memory_usage\": $(free | grep Mem | awk '{printf "%.2f", $3/$2 * 100.0}'),
        \"disk_usage\": $(df / | tail -1 | awk '{print $5}' | sed 's/%//'),
        \"load_average\": $(uptime | awk -F'load average:' '{ print $2 }' | cut -d, -f1 | xargs),
        \"network_connections\": $(netstat -tun | grep ESTABLISHED | wc -l)
    }"
}

# Alert checking logic
check_alerts() {
    local metrics=$1
    local alerts=()

    # CPU alert
    cpu_usage=$(echo "$metrics" | jq -r '.cpu_usage')
    if (( $(echo "$cpu_usage > 80" | bc -l) )); then
        alerts+=("HIGH_CPU:$cpu_usage%")
    fi

    # Memory alert
    mem_usage=$(echo "$metrics" | jq -r '.memory_usage')
    if (( $(echo "$mem_usage > 85" | bc -l) )); then
        alerts+=("HIGH_MEMORY:$mem_usage%")
    fi

    # Disk alert
    disk_usage=$(echo "$metrics" | jq -r '.disk_usage')
    if (( disk_usage > 90 )); then
        alerts+=("HIGH_DISK:$disk_usage%")
    fi

    echo "${alerts[@]}"
}

# Send alerts
send_alert() {
    local alert_message=$1

    # Email alert
    if [ -n "$ALERT_EMAIL" ]; then
        echo "System Alert: $alert_message" | mail -s "System Monitor Alert" "$ALERT_EMAIL"
    fi

    # Slack alert
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -X POST -H 'Content-type: application/json' \
             --data "{\"text\":\"🚨 System Alert: $alert_message\"}" \
             "$SLACK_WEBHOOK"
    fi
}

# Main monitoring loop
main() {
    echo "🖥️  Advanced System Monitor Started"
    echo "=================================="

    while true; do
        metrics=$(collect_system_metrics)
        alerts=$(check_alerts "$metrics")

        if [ ${#alerts} -gt 0 ]; then
            for alert in $alerts; do
                echo "🚨 Alert: $alert"
                send_alert "$alert"
            done
        fi

        # Log metrics
        echo "$metrics" >> /var/log/system_monitor.json

        sleep 60  # Check every minute
    done
}

# Run main function
main "$@"
                    """,
                    "production_considerations": [
                        "Implement proper logging and rotation",
                        "Add configuration management",
                        "Create systemd service",
                        "Implement health checks",
                        "Add metric storage and graphing"
                    ]
                },
                success_criteria={
                    "monitoring_implemented": True,
                    "alerting_system": True,
                    "production_ready": True,
                    "comprehensive_coverage": True
                }
            )
        ]

    def _get_ml_modules(self) -> list:
        """Real machine learning content."""

        return [
            ContentModule(
                content_id="computer_vision_pipeline",
                title="End-to-End Computer Vision Pipeline",
                content_type=ContentType.PRACTICAL_PROJECT,
                difficulty=DifficultyLevel.ADVANCED,
                emotional_alignment=[Emotion.ANALYTICAL, Emotion.CREATIVE],
                estimated_duration=60,
                prerequisites=["python", "machine_learning_basics", "opencv"],
                learning_objectives=[
                    "Build complete CV pipeline",
                    "Implement model training and deployment",
                    "Handle real-world image processing challenges",
                    "Optimize for production performance"
                ],
                content_data={
                    "project_prompt": "Build an intelligent document scanner that can classify and extract information from various document types",
                    "pipeline_components": [
                        "Data collection and preprocessing",
                        "Model architecture design",
                        "Training pipeline with augmentation",
                        "Model evaluation and optimization",
                        "API deployment and serving",
                        "Performance monitoring"
                    ],
                    "real_world_challenges": [
                        "Handle various lighting conditions",
                        "Process different document formats",
                        "Extract text from complex layouts",
                        "Classify document types accurately",
                        "Handle image quality variations"
                    ],
                    "technologies": [
                        "PyTorch for model development",
                        "OpenCV for image processing",
                        "FastAPI for serving",
                        "Docker for containerization",
                        "MLflow for experiment tracking"
                    ],
                    "starter_code": """
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import resnet50
import cv2
import numpy as np
from typing import Dict, List, Tuple
import logging

class DocumentScanner(nn.Module):
    def __init__(self, num_classes: int):
        super().__init__()
        # Use ResNet50 as backbone
        self.backbone = resnet50(pretrained=True)
        self.backbone.fc = nn.Identity()  # Remove classification head

        # Custom classification head
        self.classifier = nn.Sequential(
            nn.Linear(2048, 1024),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(1024, num_classes)
        )

        # Text detection head
        self.text_detector = nn.Sequential(
            nn.Conv2d(2048, 512, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(512, 256, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(256, 1, 1)  # Binary text/non-text segmentation
        )

    def forward(self, x):
        features = self.backbone(x)

        # Classification
        class_logits = self.classifier(features)

        # Text detection (reshape features back to spatial)
        # This is a simplified version - real implementation would be more complex
        batch_size = x.size(0)
        text_mask = torch.randn(batch_size, 1, 28, 28)  # Placeholder

        return {
            'class_logits': class_logits,
            'text_mask': text_mask
        }

class DocumentProcessingPipeline:
    def __init__(self, model_path: str):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = DocumentScanner(num_classes=5)  # 5 document types
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def preprocess_image(self, image: np.ndarray) -> torch.Tensor:
        \"\"\"Preprocess image for model input.\"\"\"
        if isinstance(image, np.ndarray):
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return self.transform(image).unsqueeze(0).to(self.device)

    def predict(self, image: np.ndarray) -> Dict[str, any]:
        \"\"\"Make prediction on document image.\"\"\"
        with torch.no_grad():
            input_tensor = self.preprocess_image(image)
            outputs = self.model(input_tensor)

            # Get predictions
            class_probs = torch.softmax(outputs['class_logits'], dim=1)
            predicted_class = torch.argmax(class_probs, dim=1).item()
            confidence = class_probs[0][predicted_class].item()

            return {
                'document_type': self._class_id_to_name(predicted_class),
                'confidence': confidence,
                'text_regions': self._process_text_mask(outputs['text_mask'])
            }

    def _class_id_to_name(self, class_id: int) -> str:
        \"\"\"Convert class ID to document type name.\"\"\"
        classes = ['invoice', 'receipt', 'contract', 'passport', 'driver_license']
        return classes[class_id] if class_id < len(classes) else 'unknown'

    def _process_text_mask(self, text_mask: torch.Tensor) -> List[Dict]:
        \"\"\"Process text detection mask to extract text regions.\"\"\"
        # Simplified text region extraction
        # Real implementation would use connected components, OCR, etc.
        return [{'bbox': [0, 0, 100, 50], 'confidence': 0.8}]  # Placeholder
                    """,
                    "production_requirements": [
                        "Implement proper data augmentation",
                        "Add model quantization for mobile deployment",
                        "Create comprehensive evaluation metrics",
                        "Implement model versioning and rollback",
                        "Add GPU optimization and batch processing"
                    ]
                },
                success_criteria={
                    "complete_pipeline": True,
                    "production_ready": True,
                    "performance_optimized": True,
                    "comprehensive_evaluation": True
                }
            )
        ]

    def _get_devops_modules(self) -> list:
        """Real DevOps content."""

        return [
            ContentModule(
                content_id="kubernetes_microservices",
                title="Microservices Deployment on Kubernetes",
                content_type=ContentType.PRACTICAL_PROJECT,
                difficulty=DifficultyLevel.ADVANCED,
                emotional_alignment=[Emotion.ANALYTICAL, Emotion.ENGAGED],
                estimated_duration=50,
                prerequisites=["docker", "kubernetes_basics", "microservices"],
                learning_objectives=[
                    "Design microservices architecture",
                    "Implement Kubernetes deployments",
                    "Set up service mesh and observability",
                    "Implement CI/CD pipelines"
                ],
                content_data={
                    "project_prompt": "Build and deploy a complete e-commerce microservices platform on Kubernetes",
                    "architecture_components": [
                        "API Gateway (Kong/Traefik)",
                        "User Service (authentication & profiles)",
                        "Product Catalog Service",
                        "Order Management Service",
                        "Payment Processing Service",
                        "Notification Service"
                    ],
                    "kubernetes_resources": [
                        "Deployments and StatefulSets",
                        "Services and Ingress",
                        "ConfigMaps and Secrets",
                        "Persistent Volumes",
                        "Network Policies",
                        "Horizontal Pod Autoscalers"
                    ],
                    "observability_stack": [
                        "Prometheus for metrics",
                        "Grafana for dashboards",
                        "ELK stack for logging",
                        "Jaeger for tracing",
                        "AlertManager for alerts"
                    ],
                    "starter_code": """
# E-commerce Microservices - Kubernetes Manifests
# ===============================================

# api-gateway/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: ecommerce
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: kong
        image: kong:3.4
        ports:
        - containerPort: 8000
          name: proxy
        - containerPort: 8443
          name: proxy-ssl
        env:
        - name: KONG_DATABASE
          value: "off"
        - name: KONG_DECLARATIVE_CONFIG
          value: "/etc/kong/kong.yml"
        volumeMounts:
        - name: kong-config
          mountPath: /etc/kong
      volumes:
      - name: kong-config
        configMap:
          name: kong-config

---
# user-service/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  namespace: ecommerce
spec:
  replicas: 2
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: ecommerce/user-service:latest
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: user-db-url
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: jwt-secrets
              key: secret
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5

---
# Service definitions
apiVersion: v1
kind: Service
metadata:
  name: user-service
  namespace: ecommerce
spec:
  selector:
    app: user-service
  ports:
  - port: 8080
    targetPort: 8080
  type: ClusterIP

---
# Ingress for external access
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ecommerce-ingress
  namespace: ecommerce
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.ecommerce.com
    secretName: ecommerce-tls
  rules:
  - host: api.ecommerce.com
    http:
      paths:
      - path: /api/v1/users
        pathType: Prefix
        backend:
          service:
            name: user-service
            port:
              number: 8080
      - path: /api/v1/products
        pathType: Prefix
        backend:
          service:
            name: product-service
            port:
              number: 8080
                    """,
                    "cicd_pipeline": {
                        "stages": [
                            "Build Docker images",
                            "Run unit and integration tests",
                            "Security scanning",
                            "Deploy to staging",
                            "Run e2e tests",
                            "Deploy to production"
                        ],
                        "tools": [
                            "GitHub Actions / GitLab CI",
                            "Docker for containerization",
                            "Helm for package management",
                            "ArgoCD for GitOps deployment"
                        ]
                    }
                },
                success_criteria={
                    "microservices_deployed": True,
                    "kubernetes_configured": True,
                    "observability_implemented": True,
                    "cicd_pipeline": True,
                    "production_ready": True
                }
            )
        ]

    def get_content_for_topic(self, topic: str) -> list:
        """Get all content modules for a specific topic."""
        return self.content_modules.get(topic, [])

    def get_all_topics(self) -> list:
        """Get all available topics."""
        return list(self.content_modules.keys())

    def search_content(self, query: str, topic: str = None) -> list:
        """Search content by query and optional topic filter."""
        results = []

        topics_to_search = [topic] if topic else self.get_all_topics()

        for search_topic in topics_to_search:
            modules = self.content_modules.get(search_topic, [])
            for module in modules:
                if (query.lower() in module.title.lower() or
                    query.lower() in ' '.join(module.learning_objectives).lower() or
                    query.lower() in json.dumps(module.content_data).lower()):
                    results.append(module)

        return results
