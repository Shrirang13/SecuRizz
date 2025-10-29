#!/usr/bin/env python3
"""
Federated Learning for SecuRizz - Community-driven model improvement
"""

import torch
import torch.nn as nn
import numpy as np
from typing import List, Dict, Any, Tuple
import json
import hashlib
from datetime import datetime
import requests
from pathlib import Path

class FederatedLearningManager:
    def __init__(self, model_path: str = "models/codebert_final.pt"):
        self.model_path = Path(model_path)
        self.community_contributions = []
        self.aggregation_weights = {}
        
    def collect_community_feedback(self, contract_hash: str, feedback: Dict[str, Any]) -> bool:
        """Collect feedback from community for model improvement"""
        try:
            contribution = {
                "contract_hash": contract_hash,
                "feedback": feedback,
                "timestamp": datetime.utcnow().isoformat(),
                "contributor_id": self._generate_contributor_id(),
                "verified": False
            }
            
            # Verify feedback authenticity
            if self._verify_feedback(contribution):
                self.community_contributions.append(contribution)
                self._reward_contributor(contribution["contributor_id"])
                return True
            return False
        except Exception as e:
            print(f"❌ Failed to collect feedback: {str(e)}")
            return False

    def aggregate_community_learning(self) -> Dict[str, Any]:
        """Aggregate community feedback for model improvement"""
        if not self.community_contributions:
            return {"status": "no_contributions"}
        
        # Calculate aggregation weights based on contributor reputation
        total_weight = 0
        for contribution in self.community_contributions:
            weight = self._calculate_contributor_weight(contribution)
            self.aggregation_weights[contribution["contributor_id"]] = weight
            total_weight += weight
        
        # Normalize weights
        for cid in self.aggregation_weights:
            self.aggregation_weights[cid] /= total_weight
        
        # Aggregate feedback
        aggregated_feedback = self._aggregate_feedback()
        
        return {
            "status": "success",
            "contributions_count": len(self.community_contributions),
            "aggregated_feedback": aggregated_feedback,
            "weights": self.aggregation_weights
        }

    def update_model_with_community_data(self, new_data: List[Dict[str, Any]]) -> bool:
        """Update model with community-contributed data"""
        try:
            # Load current model
            model = torch.load(self.model_path)
            
            # Prepare new training data
            training_data = self._prepare_training_data(new_data)
            
            # Fine-tune model with new data
            updated_model = self._fine_tune_model(model, training_data)
            
            # Save updated model
            torch.save(updated_model, self.model_path)
            
            # Update model version
            self._update_model_version()
            
            return True
        except Exception as e:
            print(f"❌ Model update failed: {str(e)}")
            return False

    def create_community_challenge(self, challenge_type: str, reward_amount: float) -> str:
        """Create community challenges for data contribution"""
        challenge = {
            "id": self._generate_challenge_id(),
            "type": challenge_type,
            "reward_amount": reward_amount,
            "created_at": datetime.utcnow().isoformat(),
            "status": "active",
            "participants": [],
            "submissions": []
        }
        
        # Store challenge
        self._store_challenge(challenge)
        
        return challenge["id"]

    def submit_challenge_solution(self, challenge_id: str, solution: Dict[str, Any]) -> bool:
        """Submit solution to community challenge"""
        try:
            # Validate solution
            if self._validate_solution(challenge_id, solution):
                # Store solution
                self._store_solution(challenge_id, solution)
                
                # Award tokens
                self._award_challenge_tokens(challenge_id, solution["contributor_id"])
                
                return True
            return False
        except Exception as e:
            print(f"❌ Solution submission failed: {str(e)}")
            return False

    def _generate_contributor_id(self) -> str:
        """Generate unique contributor ID"""
        timestamp = str(datetime.utcnow().timestamp())
        random_data = str(np.random.random())
        return hashlib.sha256(f"{timestamp}{random_data}".encode()).hexdigest()[:16]

    def _verify_feedback(self, contribution: Dict[str, Any]) -> bool:
        """Verify feedback authenticity and quality"""
        # Check if feedback has required fields
        required_fields = ["accuracy_rating", "vulnerability_feedback", "improvement_suggestions"]
        if not all(field in contribution["feedback"] for field in required_fields):
            return False
        
        # Check feedback quality
        accuracy = contribution["feedback"]["accuracy_rating"]
        if not (0 <= accuracy <= 10):
            return False
        
        # Check for spam patterns
        if self._detect_spam(contribution):
            return False
        
        return True

    def _calculate_contributor_weight(self, contribution: Dict[str, Any]) -> float:
        """Calculate weight for contributor based on reputation"""
        base_weight = 1.0
        
        # Factors affecting weight:
        # 1. Historical accuracy
        # 2. Contribution frequency
        # 3. Community rating
        # 4. Staking amount
        
        contributor_id = contribution["contributor_id"]
        
        # Get historical accuracy (mock implementation)
        historical_accuracy = self._get_historical_accuracy(contributor_id)
        
        # Get staking amount (mock implementation)
        staking_amount = self._get_staking_amount(contributor_id)
        
        # Calculate weight
        weight = base_weight * (1 + historical_accuracy) * (1 + staking_amount / 1000)
        
        return max(0.1, min(10.0, weight))  # Clamp between 0.1 and 10.0

    def _aggregate_feedback(self) -> Dict[str, Any]:
        """Aggregate community feedback using weighted average"""
        if not self.community_contributions:
            return {}
        
        aggregated = {
            "accuracy_ratings": [],
            "vulnerability_feedback": {},
            "improvement_suggestions": [],
            "weighted_scores": {}
        }
        
        for contribution in self.community_contributions:
            contributor_id = contribution["contributor_id"]
            weight = self.aggregation_weights.get(contributor_id, 0)
            feedback = contribution["feedback"]
            
            # Weighted accuracy rating
            accuracy = feedback["accuracy_rating"] * weight
            aggregated["accuracy_ratings"].append(accuracy)
            
            # Aggregate vulnerability feedback
            for vuln, feedback_text in feedback["vulnerability_feedback"].items():
                if vuln not in aggregated["vulnerability_feedback"]:
                    aggregated["vulnerability_feedback"][vuln] = []
                aggregated["vulnerability_feedback"][vuln].append({
                    "feedback": feedback_text,
                    "weight": weight
                })
            
            # Collect improvement suggestions
            aggregated["improvement_suggestions"].extend(feedback["improvement_suggestions"])
        
        # Calculate weighted averages
        if aggregated["accuracy_ratings"]:
            aggregated["weighted_scores"]["average_accuracy"] = sum(aggregated["accuracy_ratings"]) / len(aggregated["accuracy_ratings"])
        
        return aggregated

    def _prepare_training_data(self, new_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare new data for model training"""
        training_data = []
        
        for item in new_data:
            # Extract features and labels
            features = {
                "source_code": item["source_code"],
                "contract_hash": item["contract_hash"]
            }
            
            labels = {
                "vulnerabilities": item["vulnerabilities"],
                "severity": item["severity"],
                "community_feedback": item.get("community_feedback", {})
            }
            
            training_data.append({
                "features": features,
                "labels": labels,
                "weight": item.get("weight", 1.0)
            })
        
        return training_data

    def _fine_tune_model(self, model: nn.Module, training_data: List[Dict[str, Any]]) -> nn.Module:
        """Fine-tune model with new community data"""
        # This is a simplified implementation
        # In practice, you'd implement proper fine-tuning
        
        # Set model to training mode
        model.train()
        
        # Create optimizer
        optimizer = torch.optim.Adam(model.parameters(), lr=1e-5)
        
        # Training loop (simplified)
        for epoch in range(3):  # 3 epochs for fine-tuning
            for item in training_data:
                # Forward pass
                # ... (implement actual training logic)
                pass
        
        return model

    def _update_model_version(self):
        """Update model version after community learning"""
        version_file = Path("models/model_version.json")
        
        if version_file.exists():
            with open(version_file, 'r') as f:
                version_data = json.load(f)
        else:
            version_data = {"version": "1.0.0", "updates": []}
        
        # Increment version
        major, minor, patch = version_data["version"].split(".")
        patch = str(int(patch) + 1)
        new_version = f"{major}.{minor}.{patch}"
        
        # Update version data
        version_data["version"] = new_version
        version_data["updates"].append({
            "version": new_version,
            "timestamp": datetime.utcnow().isoformat(),
            "contributions_count": len(self.community_contributions),
            "type": "community_learning"
        })
        
        # Save version
        with open(version_file, 'w') as f:
            json.dump(version_data, f, indent=2)

    def _detect_spam(self, contribution: Dict[str, Any]) -> bool:
        """Detect spam in community contributions"""
        # Simple spam detection
        feedback_text = str(contribution["feedback"])
        
        # Check for repeated characters
        if any(char * 5 in feedback_text for char in "abcdefghijklmnopqrstuvwxyz"):
            return True
        
        # Check for suspicious patterns
        suspicious_patterns = ["spam", "fake", "bot", "automated"]
        if any(pattern in feedback_text.lower() for pattern in suspicious_patterns):
            return True
        
        return False

    def _get_historical_accuracy(self, contributor_id: str) -> float:
        """Get historical accuracy for contributor (mock)"""
        # In practice, this would query a database
        return np.random.uniform(0.5, 1.0)

    def _get_staking_amount(self, contributor_id: str) -> float:
        """Get staking amount for contributor (mock)"""
        # In practice, this would query the blockchain
        return np.random.uniform(0, 10000)

    def _reward_contributor(self, contributor_id: str):
        """Reward contributor with tokens"""
        # In practice, this would mint tokens on Solana
        print(f"🎁 Rewarding contributor {contributor_id} with SECURIZZ tokens")

    def _generate_challenge_id(self) -> str:
        """Generate unique challenge ID"""
        timestamp = str(datetime.utcnow().timestamp())
        return hashlib.sha256(timestamp.encode()).hexdigest()[:12]

    def _store_challenge(self, challenge: Dict[str, Any]):
        """Store challenge data"""
        challenges_file = Path("data/community_challenges.json")
        challenges_file.parent.mkdir(exist_ok=True)
        
        if challenges_file.exists():
            with open(challenges_file, 'r') as f:
                challenges = json.load(f)
        else:
            challenges = []
        
        challenges.append(challenge)
        
        with open(challenges_file, 'w') as f:
            json.dump(challenges, f, indent=2)

    def _validate_solution(self, challenge_id: str, solution: Dict[str, Any]) -> bool:
        """Validate challenge solution"""
        # Check if solution has required fields
        required_fields = ["solution_data", "contributor_id", "verification_proof"]
        return all(field in solution for field in required_fields)

    def _store_solution(self, challenge_id: str, solution: Dict[str, Any]):
        """Store challenge solution"""
        solutions_file = Path("data/challenge_solutions.json")
        solutions_file.parent.mkdir(exist_ok=True)
        
        if solutions_file.exists():
            with open(solutions_file, 'r') as f:
                solutions = json.load(f)
        else:
            solutions = []
        
        solution["challenge_id"] = challenge_id
        solution["submitted_at"] = datetime.utcnow().isoformat()
        solutions.append(solution)
        
        with open(solutions_file, 'w') as f:
            json.dump(solutions, f, indent=2)

    def _award_challenge_tokens(self, challenge_id: str, contributor_id: str):
        """Award tokens for challenge completion"""
        print(f"🏆 Awarding tokens to {contributor_id} for challenge {challenge_id}")

# Global instance
federated_learning = FederatedLearningManager()
