#!/usr/bin/env python3
"""
Process all downloaded repositories to extract Rust/Solana contracts.
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any
import hashlib

class RepositoryProcessor:
    def __init__(self, raw_dir: str = "datasets/raw", output_file: str = "datasets/processed/all_extracted_contracts.json"):
        self.raw_dir = Path(raw_dir)
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.contracts = []
        
        # Vulnerability patterns
        self.vulnerability_patterns = {
            "unsafe_code": [r"unsafe\s*\{", r"std::ptr::", r"transmute", r"raw.*pointer"],
            "account_validation": [r"#\[account\(\)\]", r"AccountInfo", r"require!.*account"],
            "signature_verification": [r"is_signer", r"require!.*signer", r"msg\.sender"],
            "integer_overflow": [r"\.wrapping_add", r"\.wrapping_sub", r"checked_add", r"checked_sub"],
            "panic_handling": [r"panic!", r"unwrap\(\)", r"expect\(", r"unreachable!"],
            "program_derivation": [r"find_program_address", r"create_program_address", r"try_find_program_address"],
            "seed_validation": [r"seeds.*b\"", r"PDA", r"program_derived_address"],
            "authority_validation": [r"authority", r"owner", r"admin", r"only_owner"],
            "instruction_validation": [r"instruction", r"cpi", r"invoke", r"invoke_signed"],
            "data_validation": [r"deserialize", r"serialize", r"borsh", r"anchor_lang"],
            "rent_exemption": [r"rent", r"lamports", r"minimum_balance", r"rent_exempt"],
            "token_program": [r"token_program", r"spl_token", r"transfer", r"mint"],
            "cross_program_invocation": [r"invoke", r"invoke_signed", r"cpi", r"cross_program"],
            "pda_validation": [r"program_derived_address", r"find_program_address", r"seeds"]
        }

    def is_rust_file(self, file_path: Path) -> bool:
        """Check if file is a Rust file"""
        return file_path.suffix == '.rs' and not any(part.startswith('.') for part in file_path.parts)

    def is_solana_rust(self, content: str) -> bool:
        """Check if Rust code is Solana-related"""
        solana_indicators = [
            'anchor_lang', 'solana_program', 'borsh', 'AccountInfo', 'Program',
            'Context', 'Result<()>', 'pubkey', 'lamports', 'rent', 'system_program',
            'token_program', 'associated_token', 'program_derived_address'
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in solana_indicators)

    def detect_vulnerabilities(self, content: str) -> List[str]:
        """Detect vulnerabilities in Rust code"""
        vulnerabilities = []
        content_lower = content.lower()
        
        for vuln_type, patterns in self.vulnerability_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    if vuln_type not in vulnerabilities:
                        vulnerabilities.append(vuln_type)
                    break
        
        return vulnerabilities

    def process_rust_file(self, file_path: Path, repo_name: str) -> Dict[str, Any]:
        """Process a single Rust file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not self.is_solana_rust(content):
                return None
            
            vulnerabilities = self.detect_vulnerabilities(content)
            
            # Determine if it's vulnerable or safe
            is_vulnerable = len(vulnerabilities) > 0
            
            contract = {
                "contract_id": f"{repo_name}_{hashlib.md5(str(file_path).encode()).hexdigest()[:8]}",
                "source_code": content,
                "vulnerabilities": vulnerabilities if is_vulnerable else [],
                "severity": ["high"] if is_vulnerable else [],
                "source": f"repo_{repo_name}",
                "file_path": str(file_path.relative_to(self.raw_dir)),
                "repo": repo_name
            }
            
            return contract
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None

    def process_repository(self, repo_path: Path) -> int:
        """Process all Rust files in a repository"""
        repo_name = repo_path.name
        print(f"Processing repository: {repo_name}")
        
        count = 0
        for rust_file in repo_path.rglob("*.rs"):
            if self.is_rust_file(rust_file):
                contract = self.process_rust_file(rust_file, repo_name)
                if contract:
                    self.contracts.append(contract)
                    count += 1
                    if count % 100 == 0:
                        print(f"  Processed {count} files...")
        
        print(f"  Found {count} Solana Rust contracts in {repo_name}")
        return count

    def process_huggingface_datasets(self):
        """Process Hugging Face datasets"""
        print("Processing Hugging Face datasets...")
        
        hf_dirs = [d for d in self.raw_dir.iterdir() if d.is_dir() and d.name.startswith('hf_')]
        
        for hf_dir in hf_dirs:
            print(f"Processing HF dataset: {hf_dir.name}")
            
            # Look for data files
            data_files = list(hf_dir.rglob("*.json")) + list(hf_dir.rglob("*.jsonl")) + list(hf_dir.rglob("*.parquet"))
            
            for data_file in data_files:
                try:
                    if data_file.suffix == '.parquet':
                        import pandas as pd
                        df = pd.read_parquet(data_file)
                        data = df.to_dict('records')
                    elif data_file.suffix == '.jsonl':
                        with open(data_file, 'r', encoding='utf-8') as f:
                            data = [json.loads(line) for line in f]
                    else:
                        with open(data_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                    
                    for i, record in enumerate(data):
                        # Extract code from various field names
                        source_code = (record.get('code') or 
                                     record.get('source_code') or 
                                     record.get('text') or 
                                     record.get('content', ''))
                        
                        if source_code and self.is_solana_rust(source_code):
                            vulnerabilities = self.detect_vulnerabilities(source_code)
                            
                            contract = {
                                "contract_id": f"hf_{hf_dir.name}_{i:06d}",
                                "source_code": source_code,
                                "vulnerabilities": vulnerabilities,
                                "severity": ["high"] if vulnerabilities else [],
                                "source": f"hf_{hf_dir.name}",
                                "file_path": f"hf_{hf_dir.name}_{i:06d}.rs"
                            }
                            self.contracts.append(contract)
                            
                except Exception as e:
                    print(f"Error processing {data_file}: {e}")

    def process_all(self):
        """Process all repositories and datasets"""
        print("Starting comprehensive repository processing...")
        
        # Process GitHub repositories
        repo_dirs = [d for d in self.raw_dir.iterdir() 
                    if d.is_dir() and not d.name.startswith('hf_') and not d.name.startswith('.')]
        
        total_repos = 0
        for repo_dir in repo_dirs:
            try:
                count = self.process_repository(repo_dir)
                total_repos += count
            except Exception as e:
                print(f"Error processing repository {repo_dir}: {e}")
        
        # Process Hugging Face datasets
        self.process_huggingface_datasets()
        
        print(f"\nTotal contracts extracted: {len(self.contracts)}")
        print(f"From repositories: {total_repos}")
        print(f"From HF datasets: {len(self.contracts) - total_repos}")
        
        # Save results
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.contracts, f, indent=2, ensure_ascii=False)
        
        # Generate statistics
        self.generate_statistics()
        
        print(f"Results saved to: {self.output_file}")

    def generate_statistics(self):
        """Generate statistics about extracted contracts"""
        total = len(self.contracts)
        vulnerable = sum(1 for c in self.contracts if c['vulnerabilities'])
        safe = total - vulnerable
        
        # Count by vulnerability type
        vuln_counts = {}
        for contract in self.contracts:
            for vuln in contract['vulnerabilities']:
                vuln_counts[vuln] = vuln_counts.get(vuln, 0) + 1
        
        # Count by source
        source_counts = {}
        for contract in self.contracts:
            source = contract['source']
            source_counts[source] = source_counts.get(source, 0) + 1
        
        stats = {
            "total_contracts": total,
            "vulnerable_contracts": vulnerable,
            "safe_contracts": safe,
            "vulnerability_distribution": vuln_counts,
            "source_distribution": source_counts
        }
        
        stats_file = self.output_file.parent / "extraction_statistics.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"Statistics saved to: {stats_file}")

def main():
    processor = RepositoryProcessor()
    processor.process_all()

if __name__ == "__main__":
    main()
