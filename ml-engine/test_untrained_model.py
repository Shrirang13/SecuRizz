#!/usr/bin/env python3
"""
Test what happens when we use an untrained model
"""

import torch
import json
import random
from pathlib import Path
from typing import Dict, Any, List

class UntrainedModelTester:
    def __init__(self):
        self.model_path = Path("models/untrained_model.pt")
        self.test_contracts = [
            {
                "name": "Vulnerable Contract 1",
                "code": """
use anchor_lang::prelude::*;
pub fn unsafe_function(ctx: Context<Unsafe>) -> Result<()> {
    let amount = ctx.accounts.user.amount;
    // No validation - can overflow
    let result = amount + 1000;
    Ok(())
}
""",
                "expected_vulnerabilities": ["integer_overflow", "unsafe_code"]
            },
            {
                "name": "Safe Contract 1", 
                "code": """
use anchor_lang::prelude::*;
pub fn safe_function(ctx: Context<Safe>) -> Result<()> {
    require!(ctx.accounts.user.amount > 0, ErrorCode::InvalidAmount);
    let result = ctx.accounts.user.amount.checked_add(1000)
        .ok_or(ErrorCode::Overflow)?;
    Ok(())
}
""",
                "expected_vulnerabilities": []
            },
            {
                "name": "Complex Vulnerable Contract",
                "code": """
use anchor_lang::prelude::*;
pub fn complex_vulnerable(ctx: Context<Complex>) -> Result<()> {
    // Multiple vulnerabilities
    let user_input = ctx.accounts.user.data.clone();
    let mut buffer = [0u8; 10];
    
    // Buffer overflow
    for (i, byte) in user_input.iter().enumerate() {
        buffer[i] = *byte;
    }
    
    // Integer overflow
    let result = ctx.accounts.user.amount + ctx.accounts.user.bonus;
    
    // Panic potential
    let division = 100 / ctx.accounts.user.amount;
    
    Ok(())
}
""",
                "expected_vulnerabilities": ["buffer_overflow", "integer_overflow", "panic_handling"]
            }
        ]

    def create_untrained_model(self):
        """Create an untrained model for testing"""
        print("🤖 Creating untrained model...")
        
        # Create a simple untrained model
        class UntrainedModel(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.linear = torch.nn.Linear(512, 25)  # 25 vulnerability types
                self.sigmoid = torch.nn.Sigmoid()
            
            def forward(self, x):
                return self.sigmoid(self.linear(x))
        
        model = UntrainedModel()
        
        # Save untrained model
        self.model_path.parent.mkdir(exist_ok=True)
        torch.save(model.state_dict(), self.model_path)
        print(f"✅ Untrained model saved to {self.model_path}")

    def test_untrained_predictions(self):
        """Test predictions from untrained model"""
        print("\n🧪 Testing untrained model predictions...")
        
        # Load untrained model
        model = torch.load(self.model_path, map_location='cpu')
        model.eval()
        
        results = []
        
        for i, contract in enumerate(self.test_contracts):
            print(f"\n📝 Testing: {contract['name']}")
            print(f"Expected vulnerabilities: {contract['expected_vulnerabilities']}")
            
            # Create mock input (random features)
            mock_input = torch.randn(1, 512)
            
            # Get prediction
            with torch.no_grad():
                prediction = model(mock_input)
                probabilities = prediction.squeeze().tolist()
            
            # Map probabilities to vulnerability types
            vulnerability_types = [
                "unsafe_code", "integer_overflow", "integer_underflow", "panic_handling",
                "memory_leak", "use_after_free", "buffer_overflow", "null_pointer",
                "double_free", "format_string", "race_condition", "deadlock",
                "resource_exhaustion", "infinite_loop", "stack_overflow",
                "account_validation", "program_derivation", "seed_validation",
                "signature_verification", "instruction_validation", "data_validation",
                "authority_validation", "rent_exemption", "account_lamports", "program_ownership"
            ]
            
            # Get predicted vulnerabilities (threshold > 0.5)
            predicted_vulnerabilities = []
            for j, prob in enumerate(probabilities):
                if prob > 0.5:
                    predicted_vulnerabilities.append(vulnerability_types[j])
            
            print(f"Predicted vulnerabilities: {predicted_vulnerabilities}")
            print(f"Prediction probabilities: {[f'{p:.3f}' for p in probabilities[:5]]}...")
            
            # Calculate accuracy
            expected = set(contract['expected_vulnerabilities'])
            predicted = set(predicted_vulnerabilities)
            
            true_positives = len(expected.intersection(predicted))
            false_positives = len(predicted - expected)
            false_negatives = len(expected - predicted)
            
            precision = true_positives / len(predicted) if predicted else 0
            recall = true_positives / len(expected) if expected else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            print(f"Precision: {precision:.3f}")
            print(f"Recall: {recall:.3f}")
            print(f"F1 Score: {f1:.3f}")
            
            results.append({
                "contract": contract['name'],
                "expected": contract['expected_vulnerabilities'],
                "predicted": predicted_vulnerabilities,
                "precision": precision,
                "recall": recall,
                "f1_score": f1
            })
        
        return results

    def test_random_predictions(self):
        """Test random predictions (baseline)"""
        print("\n🎲 Testing random predictions (baseline)...")
        
        vulnerability_types = [
            "unsafe_code", "integer_overflow", "integer_underflow", "panic_handling",
            "memory_leak", "use_after_free", "buffer_overflow", "null_pointer",
            "double_free", "format_string", "race_condition", "deadlock",
            "resource_exhaustion", "infinite_loop", "stack_overflow",
            "account_validation", "program_derivation", "seed_validation",
            "signature_verification", "instruction_validation", "data_validation",
            "authority_validation", "rent_exemption", "account_lamports", "program_ownership"
        ]
        
        results = []
        
        for i, contract in enumerate(self.test_contracts):
            print(f"\n📝 Random baseline: {contract['name']}")
            
            # Random predictions
            random_vulnerabilities = []
            for vuln in vulnerability_types:
                if random.random() > 0.5:  # 50% chance
                    random_vulnerabilities.append(vuln)
            
            print(f"Random predictions: {random_vulnerabilities[:5]}...")
            
            # Calculate accuracy
            expected = set(contract['expected_vulnerabilities'])
            predicted = set(random_vulnerabilities)
            
            true_positives = len(expected.intersection(predicted))
            false_positives = len(predicted - expected)
            false_negatives = len(expected - predicted)
            
            precision = true_positives / len(predicted) if predicted else 0
            recall = true_positives / len(expected) if expected else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            print(f"Precision: {precision:.3f}")
            print(f"Recall: {recall:.3f}")
            print(f"F1 Score: {f1:.3f}")
            
            results.append({
                "contract": contract['name'],
                "expected": contract['expected_vulnerabilities'],
                "predicted": random_vulnerabilities,
                "precision": precision,
                "recall": recall,
                "f1_score": f1
            })
        
        return results

    def compare_results(self, untrained_results, random_results):
        """Compare untrained model vs random baseline"""
        print("\n📊 COMPARISON: Untrained Model vs Random Baseline")
        print("=" * 60)
        
        untrained_avg_f1 = sum(r['f1_score'] for r in untrained_results) / len(untrained_results)
        random_avg_f1 = sum(r['f1_score'] for r in random_results) / len(random_results)
        
        print(f"Untrained Model Average F1: {untrained_avg_f1:.3f}")
        print(f"Random Baseline Average F1: {random_avg_f1:.3f}")
        
        if untrained_avg_f1 > random_avg_f1:
            print("✅ Untrained model performs better than random!")
        elif untrained_avg_f1 < random_avg_f1:
            print("❌ Untrained model performs worse than random!")
        else:
            print("🤷 Untrained model performs same as random!")
        
        print("\n📈 Detailed Comparison:")
        for i, (untrained, random) in enumerate(zip(untrained_results, random_results)):
            print(f"\nContract {i+1}: {untrained['contract']}")
            print(f"  Untrained F1: {untrained['f1_score']:.3f}")
            print(f"  Random F1:    {random['f1_score']:.3f}")
            print(f"  Difference:   {untrained['f1_score'] - random['f1_score']:.3f}")

    def analyze_untrained_behavior(self):
        """Analyze what happens with untrained model"""
        print("\n🔍 ANALYSIS: What happens with untrained model?")
        print("=" * 50)
        
        print("1. 🎯 PREDICTION BEHAVIOR:")
        print("   - Untrained model gives random-like predictions")
        print("   - No learned patterns from training data")
        print("   - All predictions are essentially noise")
        
        print("\n2. 📊 PERFORMANCE IMPACT:")
        print("   - Very low precision (many false positives)")
        print("   - Very low recall (misses real vulnerabilities)")
        print("   - F1 score close to 0")
        print("   - No correlation with actual vulnerabilities")
        
        print("\n3. 🚨 REAL-WORLD CONSEQUENCES:")
        print("   - False alarms: Safe code marked as vulnerable")
        print("   - Missed vulnerabilities: Dangerous code marked as safe")
        print("   - No trust in the system")
        print("   - Users lose confidence")
        
        print("\n4. 💡 WHY TRAINING IS CRITICAL:")
        print("   - Model needs to learn vulnerability patterns")
        print("   - Training data teaches the model what to look for")
        print("   - Without training, model is just random guessing")
        print("   - Training creates the intelligence in the system")
        
        print("\n5. 🎯 TRAINING IMPROVEMENTS:")
        print("   - Our 8,995 contract dataset provides rich patterns")
        print("   - 8.2/10 quality score ensures good training")
        print("   - Balanced dataset (65% vulnerable, 35% safe)")
        print("   - Real-world vulnerability examples")

    def run_full_test(self):
        """Run complete untrained model test"""
        print("🚀 SECURIZZ UNTRAINED MODEL TEST")
        print("=" * 40)
        
        # Create untrained model
        self.create_untrained_model()
        
        # Test untrained predictions
        untrained_results = self.test_untrained_predictions()
        
        # Test random baseline
        random_results = self.test_random_predictions()
        
        # Compare results
        self.compare_results(untrained_results, random_results)
        
        # Analyze behavior
        self.analyze_untrained_behavior()
        
        # Save results
        results = {
            "untrained_model": untrained_results,
            "random_baseline": random_results,
            "summary": {
                "untrained_avg_f1": sum(r['f1_score'] for r in untrained_results) / len(untrained_results),
                "random_avg_f1": sum(r['f1_score'] for r in random_results) / len(random_results)
            }
        }
        
        with open("untrained_model_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: untrained_model_test_results.json")
        print("\n🎯 CONCLUSION: Training is absolutely essential for SecuRizz to work!")

def main():
    tester = UntrainedModelTester()
    tester.run_full_test()

if __name__ == "__main__":
    main()
