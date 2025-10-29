#!/usr/bin/env python3
"""
Merge all collected datasets into a unified format for training.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
import hashlib


class DatasetMerger:
    def __init__(self, datasets_dir: str = "datasets"):
        self.datasets_dir = Path(datasets_dir)
        self.raw_dir = self.datasets_dir / "raw"
        self.processed_dir = self.datasets_dir / "processed"
        
        # Ensure directories exist
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def load_json_dataset(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load a JSON dataset file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return []

    def deduplicate_contracts(self, contracts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate contracts based on source code hash"""
        seen_hashes = set()
        unique_contracts = []
        
        for contract in contracts:
            # Create hash of source code
            source_code = contract.get('source_code', '')
            code_hash = hashlib.md5(source_code.encode('utf-8')).hexdigest()
            
            if code_hash not in seen_hashes:
                seen_hashes.add(code_hash)
                unique_contracts.append(contract)
            else:
                print(f"Removed duplicate: {contract.get('contract_id', 'unknown')}")
        
        return unique_contracts

    def validate_contract(self, contract: Dict[str, Any]) -> bool:
        """Validate that a contract has required fields"""
        required_fields = ['contract_id', 'source_code', 'vulnerabilities', 'severity', 'source']
        
        for field in required_fields:
            if field not in contract:
                print(f"Invalid contract missing {field}: {contract.get('contract_id', 'unknown')}")
                return False
        
        # Check that source code is not empty
        if not contract['source_code'].strip():
            print(f"Invalid contract with empty source code: {contract['contract_id']}")
            return False
        
        return True

    def merge_all_datasets(self) -> str:
        """Merge all available datasets"""
        print("Starting dataset merge...")
        
        all_contracts = []
        
        # Load existing unified dataset
        unified_file = self.processed_dir / "unified_rust_dataset.json"
        if unified_file.exists():
            existing_contracts = self.load_json_dataset(unified_file)
            all_contracts.extend(existing_contracts)
            print(f"Loaded {len(existing_contracts)} existing contracts")
        
        # Load manual contracts
        manual_file = self.raw_dir / "manual_vulnerable_contracts.json"
        if manual_file.exists():
            manual_contracts = self.load_json_dataset(manual_file)
            all_contracts.extend(manual_contracts)
            print(f"Loaded {len(manual_contracts)} manual contracts")
        
        # Load extracted contracts
        extracted_file = self.raw_dir / "extracted_vulnerable_contracts.json"
        if extracted_file.exists():
            extracted_contracts = self.load_json_dataset(extracted_file)
            all_contracts.extend(extracted_contracts)
            print(f"Loaded {len(extracted_contracts)} extracted contracts")
        
        # Load any other JSON files in raw directory
        for json_file in self.raw_dir.glob("*.json"):
            if json_file.name not in ["manual_vulnerable_contracts.json", "extracted_vulnerable_contracts.json"]:
                additional_contracts = self.load_json_dataset(json_file)
                all_contracts.extend(additional_contracts)
                print(f"Loaded {len(additional_contracts)} contracts from {json_file.name}")
        
        print(f"Total contracts before deduplication: {len(all_contracts)}")
        
        # Validate contracts
        valid_contracts = [c for c in all_contracts if self.validate_contract(c)]
        print(f"Valid contracts: {len(valid_contracts)}")
        
        # Deduplicate
        unique_contracts = self.deduplicate_contracts(valid_contracts)
        print(f"Unique contracts after deduplication: {len(unique_contracts)}")
        
        # Save merged dataset
        output_file = self.processed_dir / "unified_rust_dataset_merged.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(unique_contracts, f, indent=2, ensure_ascii=False)
        
        # Generate statistics
        stats = self.generate_statistics(unique_contracts)
        stats_file = self.processed_dir / "merged_dataset_statistics.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Dataset merge complete!")
        print(f"   Total contracts: {len(unique_contracts)}")
        print(f"   Output file: {output_file}")
        print(f"   Statistics: {stats_file}")
        
        return str(output_file)

    def generate_statistics(self, contracts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive dataset statistics"""
        total_contracts = len(contracts)
        vulnerable_contracts = sum(1 for c in contracts if c["vulnerabilities"])
        safe_contracts = total_contracts - vulnerable_contracts
        
        # Count by vulnerability type
        vuln_counts = {}
        for contract in contracts:
            for vuln in contract["vulnerabilities"]:
                vuln_counts[vuln] = vuln_counts.get(vuln, 0) + 1
        
        # Count by source
        source_counts = {}
        for contract in contracts:
            source = contract["source"]
            source_counts[source] = source_counts.get(source, 0) + 1
        
        # Count by severity
        severity_counts = {}
        for contract in contracts:
            for severity in contract["severity"]:
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Calculate average vulnerabilities per contract
        total_vulns = sum(len(c["vulnerabilities"]) for c in contracts)
        avg_vulns_per_contract = total_vulns / total_contracts if total_contracts > 0 else 0
        
        return {
            "total_contracts": total_contracts,
            "vulnerable_contracts": vulnerable_contracts,
            "safe_contracts": safe_contracts,
            "vulnerability_distribution": vuln_counts,
            "source_distribution": source_counts,
            "severity_distribution": severity_counts,
            "average_vulnerabilities_per_contract": round(avg_vulns_per_contract, 2),
            "vulnerability_types": list(vuln_counts.keys()),
            "sources": list(source_counts.keys())
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Merge all collected datasets")
    parser.add_argument("--datasets-dir", type=str, default="datasets", help="Datasets directory")
    parser.add_argument("--output-name", type=str, default="unified_rust_dataset_merged", help="Output filename")
    
    args = parser.parse_args()
    
    merger = DatasetMerger(args.datasets_dir)
    output_file = merger.merge_all_datasets()
    
    print(f"\n🎉 Merged dataset ready for training!")
    print(f"   Use: python ml-engine/train.py --data {output_file}")


if __name__ == "__main__":
    main()

