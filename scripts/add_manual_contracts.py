#!/usr/bin/env python3
"""
Interactive script to manually add vulnerable contracts to the dataset.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any


class ManualContractAdder:
    def __init__(self, output_file: str = "datasets/raw/manual_vulnerable_contracts.json"):
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing contracts if file exists
        if self.output_file.exists():
            with open(self.output_file, 'r', encoding='utf-8') as f:
                self.contracts = json.load(f)
        else:
            self.contracts = []
        
        # Available vulnerability types
        self.vulnerability_types = [
            "unsafe_code", "integer_overflow", "integer_underflow", "panic_handling",
            "memory_leak", "use_after_free", "buffer_overflow", "null_pointer",
            "double_free", "format_string", "race_condition", "deadlock",
            "resource_exhaustion", "infinite_loop", "stack_overflow",
            "account_validation", "program_derivation", "seed_validation",
            "signature_verification", "instruction_validation", "data_validation",
            "authority_validation", "rent_exemption", "account_lamports",
            "program_ownership", "cross_program_invocation", "syscall_validation",
            "token_program", "associated_token", "pda_validation"
        ]
        
        self.severity_levels = ["critical", "high", "medium", "low"]

    def add_contract_interactive(self):
        """Interactively add a new contract"""
        print("\n=== Adding New Vulnerable Contract ===")
        
        # Get contract ID
        contract_id = input("Contract ID (e.g., 'rekt_001'): ").strip()
        if not contract_id:
            contract_id = f"manual_{len(self.contracts) + 1:03d}"
        
        # Get source code
        print("\nPaste the Rust source code (end with 'END' on a new line):")
        source_code_lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            source_code_lines.append(line)
        
        source_code = "\n".join(source_code_lines)
        if not source_code.strip():
            print("No source code provided. Skipping.")
            return
        
        # Get vulnerabilities
        print(f"\nAvailable vulnerability types:")
        for i, vuln_type in enumerate(self.vulnerability_types, 1):
            print(f"{i:2d}. {vuln_type}")
        
        print("\nEnter vulnerability numbers (comma-separated, e.g., '1,5,12'):")
        vuln_input = input().strip()
        vulnerabilities = []
        
        if vuln_input:
            try:
                vuln_indices = [int(x.strip()) - 1 for x in vuln_input.split(',')]
                vulnerabilities = [self.vulnerability_types[i] for i in vuln_indices if 0 <= i < len(self.vulnerability_types)]
            except (ValueError, IndexError):
                print("Invalid input. Please enter numbers separated by commas.")
                return
        
        # Get severity
        print(f"\nAvailable severity levels:")
        for i, severity in enumerate(self.severity_levels, 1):
            print(f"{i}. {severity}")
        
        severity_input = input("Enter severity number (1-4): ").strip()
        severity = ["high"]  # default
        
        if severity_input.isdigit():
            severity_idx = int(severity_input) - 1
            if 0 <= severity_idx < len(self.severity_levels):
                severity = [self.severity_levels[severity_idx]]
        
        # Get source
        source = input("Source (e.g., 'rekt_news', 'immunefi'): ").strip() or "manual"
        
        # Get file path
        file_path = input("File path (e.g., 'rekt_001.rs'): ").strip() or f"{contract_id}.rs"
        
        # Get URL (optional)
        url = input("URL (optional): ").strip()
        
        # Get description (optional)
        description = input("Description (optional): ").strip()
        
        # Create contract
        contract = {
            "contract_id": contract_id,
            "source_code": source_code,
            "vulnerabilities": vulnerabilities,
            "severity": severity,
            "source": source,
            "file_path": file_path
        }
        
        if url:
            contract["url"] = url
        if description:
            contract["description"] = description
        
        # Add to list
        self.contracts.append(contract)
        
        print(f"\n✅ Added contract: {contract_id}")
        print(f"   Vulnerabilities: {', '.join(vulnerabilities)}")
        print(f"   Severity: {', '.join(severity)}")
        print(f"   Source: {source}")

    def save_contracts(self):
        """Save contracts to file"""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.contracts, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved {len(self.contracts)} contracts to {self.output_file}")

    def list_contracts(self):
        """List all contracts"""
        print(f"\n=== Current Contracts ({len(self.contracts)}) ===")
        for i, contract in enumerate(self.contracts, 1):
            print(f"{i:2d}. {contract['contract_id']} - {', '.join(contract['vulnerabilities'])} - {contract['source']}")

    def run_interactive(self):
        """Run interactive mode"""
        print("=== Manual Contract Adder ===")
        print("Commands: 'add', 'list', 'save', 'quit'")
        
        while True:
            command = input("\nCommand: ").strip().lower()
            
            if command == 'add':
                self.add_contract_interactive()
            elif command == 'list':
                self.list_contracts()
            elif command == 'save':
                self.save_contracts()
            elif command == 'quit':
                self.save_contracts()
                print("Goodbye!")
                break
            else:
                print("Unknown command. Use: add, list, save, quit")


def main():
    adder = ManualContractAdder()
    adder.run_interactive()


if __name__ == "__main__":
    main()

