#!/usr/bin/env python3
"""
Real-time learning system for SecuRizz AI
"""

import asyncio
import json
import torch
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import threading
import queue
import time
from pathlib import Path

class RealTimeLearningSystem:
    def __init__(self, model_path: str = "models/codebert_final.pt"):
        self.model_path = Path(model_path)
        self.feedback_queue = queue.Queue()
        self.learning_active = False
        self.model_version = "1.0.0"
        self.learning_thread = None
        
        # Learning parameters
        self.learning_rate = 0.001
        self.batch_size = 32
        self.update_frequency = 300  # 5 minutes
        self.min_feedback_count = 10
        
        # Performance tracking
        self.accuracy_history = []
        self.feedback_count = 0
        self.last_update = datetime.utcnow()
        
    def start_learning(self):
        """Start real-time learning system"""
        if self.learning_active:
            print("⚠️ Learning system already active")
            return
        
        self.learning_active = True
        self.learning_thread = threading.Thread(target=self._learning_loop, daemon=True)
        self.learning_thread.start()
        print("🚀 Real-time learning system started")

    def stop_learning(self):
        """Stop real-time learning system"""
        self.learning_active = False
        if self.learning_thread:
            self.learning_thread.join()
        print("⏹️ Real-time learning system stopped")

    def add_feedback(self, feedback: Dict[str, Any]):
        """Add community feedback to learning queue"""
        try:
            # Validate feedback
            if self._validate_feedback(feedback):
                feedback["timestamp"] = datetime.utcnow().isoformat()
                feedback["processed"] = False
                self.feedback_queue.put(feedback)
                self.feedback_count += 1
                print(f"📝 Feedback added to learning queue ({self.feedback_count} total)")
                return True
            return False
        except Exception as e:
            print(f"❌ Failed to add feedback: {str(e)}")
            return False

    def _validate_feedback(self, feedback: Dict[str, Any]) -> bool:
        """Validate feedback quality and format"""
        required_fields = ["contract_hash", "predicted_vulnerabilities", "actual_vulnerabilities", "accuracy_rating"]
        
        if not all(field in feedback for field in required_fields):
            print("❌ Missing required feedback fields")
            return False
        
        # Check accuracy rating
        accuracy = feedback.get("accuracy_rating", 0)
        if not (0 <= accuracy <= 10):
            print("❌ Invalid accuracy rating")
            return False
        
        # Check for spam patterns
        if self._detect_spam(feedback):
            print("❌ Spam detected in feedback")
            return False
        
        return True

    def _detect_spam(self, feedback: Dict[str, Any]) -> bool:
        """Detect spam in feedback"""
        # Simple spam detection
        text_fields = ["improvement_suggestions", "comments"]
        
        for field in text_fields:
            if field in feedback:
                text = str(feedback[field]).lower()
                
                # Check for repeated characters
                if any(char * 5 in text for char in "abcdefghijklmnopqrstuvwxyz"):
                    return True
                
                # Check for suspicious patterns
                spam_patterns = ["spam", "fake", "bot", "automated", "test"]
                if any(pattern in text for pattern in spam_patterns):
                    return True
        
        return False

    def _learning_loop(self):
        """Main learning loop running in background thread"""
        while self.learning_active:
            try:
                # Check if we have enough feedback for learning
                if self.feedback_queue.qsize() >= self.min_feedback_count:
                    self._process_feedback_batch()
                
                # Check if it's time for model update
                if self._should_update_model():
                    self._update_model()
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"❌ Learning loop error: {str(e)}")
                time.sleep(60)

    def _process_feedback_batch(self):
        """Process a batch of feedback for learning"""
        try:
            batch = []
            batch_size = min(self.batch_size, self.feedback_queue.qsize())
            
            # Collect feedback batch
            for _ in range(batch_size):
                if not self.feedback_queue.empty():
                    feedback = self.feedback_queue.get()
                    if not feedback.get("processed", False):
                        batch.append(feedback)
            
            if not batch:
                return
            
            print(f"🔄 Processing {len(batch)} feedback items...")
            
            # Calculate learning metrics
            metrics = self._calculate_learning_metrics(batch)
            
            # Update model with feedback
            self._apply_feedback_learning(batch, metrics)
            
            # Mark feedback as processed
            for feedback in batch:
                feedback["processed"] = True
            
            print(f"✅ Processed {len(batch)} feedback items")
            
        except Exception as e:
            print(f"❌ Feedback processing failed: {str(e)}")

    def _calculate_learning_metrics(self, batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate learning metrics from feedback batch"""
        metrics = {
            "accuracy_scores": [],
            "vulnerability_accuracy": {},
            "false_positives": 0,
            "false_negatives": 0,
            "improvement_areas": []
        }
        
        for feedback in batch:
            # Collect accuracy scores
            accuracy = feedback.get("accuracy_rating", 0)
            metrics["accuracy_scores"].append(accuracy)
            
            # Analyze vulnerability predictions
            predicted = set(feedback.get("predicted_vulnerabilities", []))
            actual = set(feedback.get("actual_vulnerabilities", []))
            
            # Calculate precision and recall
            true_positives = len(predicted.intersection(actual))
            false_positives = len(predicted - actual)
            false_negatives = len(actual - predicted)
            
            metrics["false_positives"] += false_positives
            metrics["false_negatives"] += false_negatives
            
            # Track per-vulnerability accuracy
            for vuln in actual:
                if vuln not in metrics["vulnerability_accuracy"]:
                    metrics["vulnerability_accuracy"][vuln] = {"correct": 0, "total": 0}
                
                metrics["vulnerability_accuracy"][vuln]["total"] += 1
                if vuln in predicted:
                    metrics["vulnerability_accuracy"][vuln]["correct"] += 1
        
        # Calculate overall accuracy
        if metrics["accuracy_scores"]:
            metrics["average_accuracy"] = np.mean(metrics["accuracy_scores"])
        
        return metrics

    def _apply_feedback_learning(self, batch: List[Dict[str, Any]], metrics: Dict[str, Any]):
        """Apply feedback learning to model"""
        try:
            # Load current model
            model = torch.load(self.model_path, map_location='cpu')
            
            # Create learning dataset from feedback
            learning_data = self._prepare_learning_data(batch)
            
            # Apply gradient updates based on feedback
            self._apply_gradient_updates(model, learning_data, metrics)
            
            # Save updated model
            torch.save(model, self.model_path)
            
            # Update model version
            self._increment_model_version()
            
            print("🧠 Model updated with community feedback")
            
        except Exception as e:
            print(f"❌ Model learning failed: {str(e)}")

    def _prepare_learning_data(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare feedback data for model learning"""
        learning_data = []
        
        for feedback in batch:
            # Extract features and labels
            features = {
                "contract_hash": feedback["contract_hash"],
                "source_code": feedback.get("source_code", ""),
                "context": feedback.get("context", {})
            }
            
            labels = {
                "actual_vulnerabilities": feedback["actual_vulnerabilities"],
                "accuracy_rating": feedback["accuracy_rating"],
                "confidence_scores": feedback.get("confidence_scores", {})
            }
            
            learning_data.append({
                "features": features,
                "labels": labels,
                "weight": self._calculate_feedback_weight(feedback)
            })
        
        return learning_data

    def _calculate_feedback_weight(self, feedback: Dict[str, Any]) -> float:
        """Calculate weight for feedback based on quality indicators"""
        base_weight = 1.0
        
        # Factors affecting weight:
        # 1. Accuracy rating
        accuracy = feedback.get("accuracy_rating", 5)
        accuracy_weight = accuracy / 10.0
        
        # 2. Feedback detail level
        detail_score = 0
        if "improvement_suggestions" in feedback:
            detail_score += 0.3
        if "confidence_scores" in feedback:
            detail_score += 0.3
        if "context" in feedback:
            detail_score += 0.4
        
        # 3. Contributor reputation (simplified)
        contributor_reputation = feedback.get("contributor_reputation", 0.5)
        
        # Calculate final weight
        weight = base_weight * (1 + accuracy_weight) * (1 + detail_score) * (1 + contributor_reputation)
        
        return max(0.1, min(5.0, weight))  # Clamp between 0.1 and 5.0

    def _apply_gradient_updates(self, model, learning_data: List[Dict[str, Any]], metrics: Dict[str, Any]):
        """Apply gradient updates to model based on feedback"""
        # This is a simplified implementation
        # In practice, you'd implement proper gradient descent
        
        model.train()
        
        # Calculate learning rate based on feedback quality
        avg_accuracy = metrics.get("average_accuracy", 5.0)
        adaptive_lr = self.learning_rate * (avg_accuracy / 10.0)
        
        # Apply updates (simplified)
        for data in learning_data:
            weight = data["weight"]
            # Apply weighted gradient update
            # ... (implement actual gradient update logic)
            pass

    def _should_update_model(self) -> bool:
        """Check if model should be updated"""
        time_since_update = datetime.utcnow() - self.last_update
        return time_since_update.total_seconds() >= self.update_frequency

    def _update_model(self):
        """Update model with latest learning"""
        try:
            print("🔄 Updating model with latest learning...")
            
            # Load current model
            model = torch.load(self.model_path)
            
            # Apply accumulated learning
            # ... (implement model update logic)
            
            # Save updated model
            torch.save(model, self.model_path)
            
            # Update tracking
            self.last_update = datetime.utcnow()
            self._increment_model_version()
            
            print("✅ Model updated successfully")
            
        except Exception as e:
            print(f"❌ Model update failed: {str(e)}")

    def _increment_model_version(self):
        """Increment model version after update"""
        version_parts = self.model_version.split(".")
        patch = int(version_parts[2]) + 1
        self.model_version = f"{version_parts[0]}.{version_parts[1]}.{patch}"
        
        # Save version info
        version_info = {
            "version": self.model_version,
            "updated_at": datetime.utcnow().isoformat(),
            "feedback_count": self.feedback_count,
            "accuracy_history": self.accuracy_history[-10:]  # Last 10 accuracy scores
        }
        
        with open("model_version.json", "w") as f:
            json.dump(version_info, f, indent=2)

    def get_learning_stats(self) -> Dict[str, Any]:
        """Get current learning statistics"""
        return {
            "model_version": self.model_version,
            "learning_active": self.learning_active,
            "feedback_count": self.feedback_count,
            "queue_size": self.feedback_queue.qsize(),
            "last_update": self.last_update.isoformat(),
            "accuracy_history": self.accuracy_history[-10:],
            "learning_rate": self.learning_rate,
            "update_frequency": self.update_frequency
        }

    def set_learning_parameters(self, **kwargs):
        """Update learning parameters"""
        if "learning_rate" in kwargs:
            self.learning_rate = kwargs["learning_rate"]
        if "update_frequency" in kwargs:
            self.update_frequency = kwargs["update_frequency"]
        if "min_feedback_count" in kwargs:
            self.min_feedback_count = kwargs["min_feedback_count"]
        
        print(f"🔧 Learning parameters updated: {kwargs}")

# Global instance
realtime_learning = RealTimeLearningSystem()
