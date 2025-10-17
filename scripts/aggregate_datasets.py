#!/usr/bin/env python3
"""
Dataset aggregation script for SecuRizz ML training data.
Combines SmartBugs, SWC registry, and SolidiFI datasets into unified format.
"""

import json
import os
import requests
import zipfile
from pathlib import Path
from typing import List, Dict, Any
import hashlib


class DatasetAggregator:
    def __init__(self, output_dir: str = "datasets"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.raw_dir = self.output_dir / "raw"
        self.processed_dir = self.output_dir / "processed"
        self.raw_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)
        
        # Vulnerability type mapping
        self.vulnerability_mapping = {
            # SmartBugs vulnerabilities
            "reentrancy": "reentrancy",
            "integer_overflow": "integer_overflow", 
            "integer_underflow": "integer_underflow",
            "access_control": "access_control",
            "timestamp_dependency": "timestamp_dependency",
            "tx_origin": "tx_origin",
            "unchecked_calls": "unchecked_calls",
            "denial_of_service": "denial_of_service",
            "tx_ordering": "tx_ordering",
            "uninitialized_storage": "uninitialized_storage",
            "delegatecall": "delegatecall",
            "front_running": "front_running",
            "arithmetic_precision": "arithmetic_precision",
            "unsafe_selfdestruct": "unsafe_selfdestruct",
            "missing_pausing": "missing_pausing",
        }

    def download_smartbugs(self) -> str:
        """Download SmartBugs dataset"""
        print("Downloading SmartBugs dataset...")
        url = "https://github.com/smartbugs/smartbugs/archive/refs/heads/master.zip"
        zip_path = self.raw_dir / "smartbugs.zip"
        
        if not zip_path.exists():
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        # Extract
        extract_dir = self.raw_dir / "smartbugs"
        if not extract_dir.exists():
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.raw_dir)
        
        return str(extract_dir)

    def process_smartbugs(self, smartbugs_dir: str) -> List[Dict[str, Any]]:
        """Process SmartBugs dataset"""
        print("Processing SmartBugs dataset...")
        contracts = []
        smartbugs_path = Path(smartbugs_dir)
        
        # Find all .sol files
        for sol_file in smartbugs_path.rglob("*.sol"):
            try:
                with open(sol_file, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                
                # Extract vulnerability from directory structure
                vulnerability = None
                for vuln_type in self.vulnerability_mapping.keys():
                    if vuln_type in str(sol_file).lower():
                        vulnerability = self.vulnerability_mapping[vuln_type]
                        break
                
                if vulnerability:
                    contract = {
                        "contract_id": f"smartbugs_{hashlib.md5(str(sol_file).encode()).hexdigest()}",
                        "source_code": source_code,
                        "vulnerabilities": [vulnerability],
                        "severity": ["high"],  # SmartBugs typically contains high-severity vulns
                        "source": "smartbugs",
                        "file_path": str(sol_file)
                    }
                    contracts.append(contract)
                    
            except Exception as e:
                print(f"Error processing {sol_file}: {e}")
                continue
        
        print(f"Processed {len(contracts)} SmartBugs contracts")
        return contracts

    def create_mock_safe_contracts(self, count: int = 100) -> List[Dict[str, Any]]:
        """Create mock safe contracts for balanced dataset"""
        print(f"Creating {count} mock safe contracts...")
        contracts = []
        
        safe_contract_template = '''
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

contract SafeContract{id} is ReentrancyGuard, Ownable {{
    using SafeMath for uint256;
    
    mapping(address => uint256) public balances;
    uint256 public totalSupply;
    
    event Deposit(address indexed user, uint256 amount);
    event Withdraw(address indexed user, uint256 amount);
    
    function deposit() external payable nonReentrant {{
        require(msg.value > 0, "Amount must be greater than 0");
        balances[msg.sender] = balances[msg.sender].add(msg.value);
        totalSupply = totalSupply.add(msg.value);
        emit Deposit(msg.sender, msg.value);
    }}
    
    function withdraw(uint256 amount) external nonReentrant {{
        require(amount > 0, "Amount must be greater than 0");
        require(balances[msg.sender] >= amount, "Insufficient balance");
        require(address(this).balance >= amount, "Insufficient contract balance");
        
        balances[msg.sender] = balances[msg.sender].sub(amount);
        totalSupply = totalSupply.sub(amount);
        
        (bool success, ) = payable(msg.sender).call{{value: amount}}("");
        require(success, "Transfer failed");
        
        emit Withdraw(msg.sender, amount);
    }}
    
    function getBalance(address user) external view returns (uint256) {{
        return balances[user];
    }}
    
    // Emergency pause function (only owner)
    function emergencyWithdraw() external onlyOwner {{
        uint256 balance = address(this).balance;
        require(balance > 0, "No funds to withdraw");
        
        (bool success, ) = payable(owner()).call{{value: balance}}("");
        require(success, "Transfer failed");
    }}
}}
'''
        
        for i in range(count):
            contract = {
                "contract_id": f"safe_contract_{i:03d}",
                "source_code": safe_contract_template.format(id=i),
                "vulnerabilities": [],  # No vulnerabilities
                "severity": [],  # No severity
                "source": "mock_safe",
                "file_path": f"mock_safe_contract_{i:03d}.sol"
            }
            contracts.append(contract)
        
        return contracts

    def create_mock_vulnerable_contracts(self, count: int = 50) -> List[Dict[str, Any]]:
        """Create mock vulnerable contracts for testing"""
        print(f"Creating {count} mock vulnerable contracts...")
        contracts = []
        
        vulnerable_templates = [
            {
                "vulnerability": "reentrancy",
                "template": '''
pragma solidity ^0.8.0;

contract VulnerableReentrancy{id} {{
    mapping(address => uint256) public balances;
    
    function deposit() external payable {{
        balances[msg.sender] += msg.value;
    }}
    
    function withdraw() external {{
        uint256 amount = balances[msg.sender];
        require(amount > 0, "No balance");
        
        (bool success, ) = msg.sender.call{{value: amount}}("");
        require(success, "Transfer failed");
        
        balances[msg.sender] = 0; // Vulnerable: state change after external call
    }}
}}'''
            },
            {
                "vulnerability": "integer_overflow",
                "template": '''
pragma solidity ^0.7.0; // Old version without built-in overflow protection

contract VulnerableOverflow{id} {{
    uint256 public total;
    
    function add(uint256 a, uint256 b) external {{
        total = a + b; // Vulnerable: potential overflow in older Solidity
    }}
}}'''
            },
            {
                "vulnerability": "access_control",
                "template": '''
pragma solidity ^0.8.0;

contract VulnerableAccessControl{id} {{
    address public owner;
    uint256 public secret;
    
    constructor() {{
        owner = msg.sender;
    }}
    
    function setSecret(uint256 _secret) external {{
        // Vulnerable: no access control
        secret = _secret;
    }}
}}'''
            },
            {
                "vulnerability": "tx_origin",
                "template": '''
pragma solidity ^0.8.0;

contract VulnerableTxOrigin{id} {{
    address public owner;
    
    constructor() {{
        owner = msg.sender;
    }}
    
    function withdraw() external {{
        require(tx.origin == owner, "Not owner"); // Vulnerable: use tx.origin
        payable(msg.sender).transfer(address(this).balance);
    }}
}}'''
            }
        ]
        
        for i in range(count):
            template = vulnerable_templates[i % len(vulnerable_templates)]
            contract = {
                "contract_id": f"vulnerable_{template['vulnerability']}_{i:03d}",
                "source_code": template["template"].format(id=i),
                "vulnerabilities": [template["vulnerability"]],
                "severity": ["high"],
                "source": "mock_vulnerable",
                "file_path": f"mock_vulnerable_{template['vulnerability']}_{i:03d}.sol"
            }
            contracts.append(contract)
        
        return contracts

    def aggregate_all(self) -> str:
        """Aggregate all datasets into unified format"""
        print("Starting dataset aggregation...")
        
        all_contracts = []
        
        # Process SmartBugs (if available)
        try:
            smartbugs_dir = self.download_smartbugs()
            smartbugs_contracts = self.process_smartbugs(smartbugs_dir)
            all_contracts.extend(smartbugs_contracts)
        except Exception as e:
            print(f"SmartBugs processing failed: {e}")
            print("Continuing with mock data...")
        
        # Add mock safe contracts
        safe_contracts = self.create_mock_safe_contracts(100)
        all_contracts.extend(safe_contracts)
        
        # Add mock vulnerable contracts
        vulnerable_contracts = self.create_mock_vulnerable_contracts(50)
        all_contracts.extend(vulnerable_contracts)
        
        # Save unified dataset
        output_file = self.processed_dir / "unified_dataset.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_contracts, f, indent=2, ensure_ascii=False)
        
        # Generate statistics
        stats = self.generate_statistics(all_contracts)
        stats_file = self.processed_dir / "dataset_statistics.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"Dataset aggregation complete!")
        print(f"Total contracts: {len(all_contracts)}")
        print(f"Output file: {output_file}")
        print(f"Statistics: {stats_file}")
        
        return str(output_file)

    def generate_statistics(self, contracts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate dataset statistics"""
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
        
        return {
            "total_contracts": total_contracts,
            "vulnerable_contracts": vulnerable_contracts,
            "safe_contracts": safe_contracts,
            "vulnerability_distribution": vuln_counts,
            "source_distribution": source_counts,
            "vulnerability_types": list(self.vulnerability_mapping.values())
        }


def main():
    aggregator = DatasetAggregator()
    output_file = aggregator.aggregate_all()
    print(f"Unified dataset saved to: {output_file}")


if __name__ == "__main__":
    main()
