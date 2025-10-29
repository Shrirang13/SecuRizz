#!/usr/bin/env python3
"""
Dataset aggregation script for SecuRizz ML training data - RUST/SOLANA FOCUS.
Combines Rust vulnerability datasets for Solana smart contract security.
"""

import json
import os
import requests
import zipfile
from pathlib import Path
from typing import List, Dict, Any
import hashlib
import re
from huggingface_hub import snapshot_download
from github import Github
import pandas as pd


class RustDatasetAggregator:
    def __init__(self, output_dir: str = "datasets", github_token: str = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.raw_dir = self.output_dir / "raw"
        self.processed_dir = self.output_dir / "processed"
        self.raw_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)
        
        # Initialize GitHub client if token provided
        self.github = Github(github_token) if github_token else None
        
        # Rust/Solana vulnerability type mapping
        self.vulnerability_mapping = {
            # Rust-specific vulnerabilities
            "unsafe_code": "unsafe_code",
            "integer_overflow": "integer_overflow",
            "integer_underflow": "integer_underflow", 
            "panic_handling": "panic_handling",
            "memory_leak": "memory_leak",
            "use_after_free": "use_after_free",
            "buffer_overflow": "buffer_overflow",
            "null_pointer": "null_pointer",
            "double_free": "double_free",
            "format_string": "format_string",
            "race_condition": "race_condition",
            "deadlock": "deadlock",
            "resource_exhaustion": "resource_exhaustion",
            "infinite_loop": "infinite_loop",
            "stack_overflow": "stack_overflow",
            
            # Solana-specific vulnerabilities
            "account_validation": "account_validation",
            "program_derivation": "program_derivation", 
            "seed_validation": "seed_validation",
            "signature_verification": "signature_verification",
            "instruction_validation": "instruction_validation",
            "data_validation": "data_validation",
            "authority_validation": "authority_validation",
            "rent_exemption": "rent_exemption",
            "account_lamports": "account_lamports",
            "program_ownership": "program_ownership",
            "cross_program_invocation": "cross_program_invocation",
            "syscall_validation": "syscall_validation",
            "token_program": "token_program",
            "associated_token": "associated_token",
            "pda_validation": "pda_validation"
        }

    def download_huggingface_solana_dataset(self) -> List[Dict[str, Any]]:
        """Download Solana vulnerability dataset from Hugging Face"""
        print("Downloading Solana vulnerability dataset from Hugging Face...")
        contracts = []
        
        try:
            # Download the dataset
            dataset_path = snapshot_download(
                repo_id="FraChiacc99/solana-vuln-rust",
                repo_type="dataset"
            )
            
            # Look for data files (JSON, JSONL, and Parquet)
            dataset_dir = Path(dataset_path)
            data_files = (list(dataset_dir.glob("*.json")) + 
                         list(dataset_dir.glob("*.jsonl")) + 
                         list(dataset_dir.glob("data/*.parquet")))
            
            for data_file in data_files:
                print(f"Processing {data_file.name}...")
                
                if data_file.suffix == '.parquet':
                    # Handle Parquet files
                    df = pd.read_parquet(data_file)
                    data = df.to_dict('records')
                else:
                    # Handle JSON/JSONL files
                    with open(data_file, 'r', encoding='utf-8') as f:
                        if data_file.suffix == '.jsonl':
                            data = [json.loads(line) for line in f]
                        else:
                            data = json.load(f)
                
                for i, record in enumerate(data):
                    # Extract text content
                    text_content = record.get('text', '')
                    
                    if text_content:
                        # Parse instruction-following format to extract Rust code and vulnerability info
                        parsed_data = self._parse_instruction_text(text_content)
                        
                        if parsed_data['source_code'] and parsed_data['vulnerabilities']:
                            contract = {
                                "contract_id": f"hf_solana_{i:06d}",
                                "source_code": parsed_data['source_code'],
                                "vulnerabilities": parsed_data['vulnerabilities'],
                                "severity": parsed_data['severity'],
                                "source": "huggingface_solana",
                                "file_path": f"hf_solana_{i:06d}.rs"
                            }
                            contracts.append(contract)
            
            print(f"Downloaded {len(contracts)} contracts from Hugging Face")
            
        except Exception as e:
            print(f"Failed to download Hugging Face dataset: {e}")
            print("Continuing with other sources...")
        
        return contracts

    def download_github_solana_datasets(self) -> List[Dict[str, Any]]:
        """Download Solana vulnerability data from GitHub repositories"""
        print("Downloading Solana vulnerability data from GitHub...")
        contracts = []
        
        if not self.github:
            print("No GitHub token provided, skipping GitHub data collection")
            return contracts
        
        # Target repositories for Solana security data
        target_repos = [
            "az0mb13/awesome-solana-security",
            "sannykim/solsec", 
            "solana-labs/solana-program-library",
            "coral-xyz/anchor"
        ]
        
        vulnerability_keywords = [
            "vulnerability", "vuln", "security", "exploit", "hack", "audit",
            "unsafe", "panic", "overflow", "underflow", "validation", "authority",
            "signature", "account", "pda", "seed", "cpi", "token", "rent"
        ]
        
        for repo_name in target_repos:
            try:
                print(f"Processing repository: {repo_name}")
                repo = self.github.get_repo(repo_name)
                
                # Search for Rust files with vulnerability-related content
                query = f"repo:{repo_name} language:rust ({' OR '.join(vulnerability_keywords)})"
                results = self.github.search_code(query, sort="indexed")
                
                for file in results[:50]:  # Limit to 50 files per repo
                    try:
                        content = file.decoded_content.decode('utf-8')
                        
                        # Extract vulnerabilities based on code patterns
                        detected_vulns = self._detect_vulnerabilities_in_code(content)
                        
                        if detected_vulns:
                            contract = {
                                "contract_id": f"github_{repo_name.replace('/', '_')}_{file.sha[:8]}",
                                "source_code": content,
                                "vulnerabilities": detected_vulns,
                                "severity": ["medium"],  # Default severity
                                "source": f"github_{repo_name}",
                                "file_path": file.path
                            }
                            contracts.append(contract)
                            
                    except Exception as e:
                        print(f"Error processing file {file.path}: {e}")
                        continue
                        
            except Exception as e:
                print(f"Error processing repository {repo_name}: {e}")
                continue
        
        print(f"Downloaded {len(contracts)} contracts from GitHub")
        return contracts

    def _detect_vulnerabilities_in_code(self, code: str) -> List[str]:
        """Detect vulnerabilities in Rust code using pattern matching"""
        vulnerabilities = []
        code_lower = code.lower()
        
        # Pattern-based vulnerability detection
        patterns = {
            "unsafe_code": [r"unsafe\s*\{", r"std::ptr::", r"transmute"],
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
        
        for vuln_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, code_lower):
                    if vuln_type not in vulnerabilities:
                        vulnerabilities.append(vuln_type)
                    break
        
        return vulnerabilities

    def _parse_instruction_text(self, text: str) -> Dict[str, Any]:
        """Parse instruction-following text to extract Rust code and vulnerability info"""
        source_code = ""
        vulnerabilities = []
        severity = ["medium"]
        
        # Extract Rust code from markdown code blocks
        rust_code_pattern = r'```(?:rust)?\s*(.*?)```'
        rust_matches = re.findall(rust_code_pattern, text, re.DOTALL)
        
        if rust_matches:
            source_code = rust_matches[0].strip()
        
        # Determine if vulnerable based on response
        text_lower = text.lower()
        
        # Check for vulnerability indicators in the response
        if any(indicator in text_lower for indicator in [
            "vulnerable", "vulnerability", "exploit", "attack", "unsafe", 
            "security issue", "bug", "flaw", "weakness", "risk"
        ]):
            # Extract specific vulnerability types from the text
            vuln_patterns = {
                "unsafe_code": [r"unsafe", r"unsafe\s*\{", r"transmute", r"std::ptr"],
                "account_validation": [r"account.*validation", r"missing.*account", r"account.*check"],
                "signature_verification": [r"signature", r"signer", r"authority", r"permission"],
                "integer_overflow": [r"overflow", r"underflow", r"arithmetic", r"wrapping"],
                "panic_handling": [r"panic", r"unwrap", r"expect", r"unreachable"],
                "program_derivation": [r"program.*derivation", r"pda", r"program.*address"],
                "seed_validation": [r"seed", r"seeds", r"program.*derived"],
                "authority_validation": [r"authority", r"owner", r"admin", r"permission"],
                "instruction_validation": [r"instruction", r"cpi", r"invoke"],
                "data_validation": [r"data.*validation", r"deserialize", r"serialize"],
                "rent_exemption": [r"rent", r"lamports", r"exemption"],
                "token_program": [r"token", r"spl", r"transfer", r"mint"],
                "cross_program_invocation": [r"cpi", r"invoke", r"cross.*program"],
                "pda_validation": [r"pda", r"program.*derived.*address", r"seeds"]
            }
            
            for vuln_type, patterns in vuln_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, text_lower):
                        if vuln_type not in vulnerabilities:
                            vulnerabilities.append(vuln_type)
                        break
            
            # If no specific vulnerabilities found, add generic ones
            if not vulnerabilities:
                vulnerabilities = ["unsafe_code", "account_validation"]
                severity = ["high"]
        else:
            # No vulnerabilities detected
            vulnerabilities = []
            severity = []
        
        return {
            "source_code": source_code,
            "vulnerabilities": vulnerabilities,
            "severity": severity
        }

    def create_rust_safe_contracts(self, count: int = 100) -> List[Dict[str, Any]]:
        """Create mock safe Rust contracts for balanced dataset"""
        print(f"Creating {count} mock safe Rust contracts...")
        contracts = []
        
        safe_contract_template = '''
use anchor_lang::prelude::*;
use anchor_spl::token::{{self, Token, TokenAccount, Transfer}};

#[program]
pub mod safe_contract_{id} {{
    use super::*;

    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {{
        let user_account = &mut ctx.accounts.user_account;
        user_account.bump = *ctx.bumps.get("user_account").unwrap();
        Ok(())
    }}

    pub fn deposit(ctx: Context<Deposit>, amount: u64) -> Result<()> {{
        require!(amount > 0, ErrorCode::InvalidAmount);
        
        let transfer_instruction = Transfer {{
            from: ctx.accounts.from.to_account_info(),
            to: ctx.accounts.to.to_account_info(),
            authority: ctx.accounts.authority.to_account_info(),
        }};
        
        let cpi_ctx = CpiContext::new(
            ctx.accounts.token_program.to_account_info(),
            transfer_instruction,
        );
        
        token::transfer(cpi_ctx, amount)?;
        Ok(())
    }}

    pub fn withdraw(ctx: Context<Withdraw>, amount: u64) -> Result<()> {{
        require!(amount > 0, ErrorCode::InvalidAmount);
        require!(ctx.accounts.user_account.balance >= amount, ErrorCode::InsufficientBalance);
        
        let transfer_instruction = Transfer {{
            from: ctx.accounts.from.to_account_info(),
            to: ctx.accounts.to.to_account_info(),
            authority: ctx.accounts.authority.to_account_info(),
        }};
        
        let cpi_ctx = CpiContext::new(
            ctx.accounts.token_program.to_account_info(),
            transfer_instruction,
        );
        
        token::transfer(cpi_ctx, amount)?;
        Ok(())
    }}
}}

#[derive(Accounts)]
pub struct Initialize<'info> {{
    #[account(
        init,
        payer = user,
        space = 8 + UserAccount::INIT_SPACE,
        seeds = [b"user", user.key().as_ref()],
        bump
    )]
    pub user_account: Account<'info, UserAccount>,
    #[account(mut)]
    pub user: Signer<'info>,
    pub system_program: Program<'info, System>,
}}

#[derive(Accounts)]
pub struct Deposit<'info> {{
    #[account(mut)]
    pub from: Account<'info, TokenAccount>,
    #[account(mut)]
    pub to: Account<'info, TokenAccount>,
    pub authority: Signer<'info>,
    pub token_program: Program<'info, Token>,
}}

#[derive(Accounts)]
pub struct Withdraw<'info> {{
    #[account(mut)]
    pub from: Account<'info, TokenAccount>,
    #[account(mut)]
    pub to: Account<'info, TokenAccount>,
    pub authority: Signer<'info>,
    pub token_program: Program<'info, Token>,
}}

#[account]
#[derive(InitSpace)]
pub struct UserAccount {{
    pub balance: u64,
    pub bump: u8,
}}

#[error_code]
pub enum ErrorCode {{
    #[msg("Invalid amount")]
    InvalidAmount,
    #[msg("Insufficient balance")]
    InsufficientBalance,
}}
'''
        
        for i in range(count):
            contract = {
                "contract_id": f"safe_rust_contract_{i:03d}",
                "source_code": safe_contract_template.format(id=i),
                "vulnerabilities": [],  # No vulnerabilities
                "severity": [],  # No severity
                "source": "mock_safe_rust",
                "file_path": f"mock_safe_rust_contract_{i:03d}.rs"
            }
            contracts.append(contract)
        
        return contracts

    def create_rust_vulnerable_contracts(self, count: int = 50) -> List[Dict[str, Any]]:
        """Create mock vulnerable Rust contracts for testing"""
        print(f"Creating {count} mock vulnerable Rust contracts...")
        contracts = []
        
        vulnerable_templates = [
            {
                "vulnerability": "unsafe_code",
                "template": '''
use anchor_lang::prelude::*;

#[program]
pub mod vulnerable_unsafe_{id} {{
    use super::*;

    pub fn dangerous_operation(ctx: Context<DangerousOperation>) -> Result<()> {{
        // VULNERABLE: Using unsafe code without proper validation
        unsafe {{
            let ptr = std::ptr::null_mut::<u8>();
            *ptr = 42; // This will cause undefined behavior
        }}
        Ok(())
    }}
}}

#[derive(Accounts)]
pub struct DangerousOperation<'info> {{
    #[account(mut)]
    pub user: Signer<'info>,
}}
'''
            },
            {
                "vulnerability": "account_validation",
                "template": '''
use anchor_lang::prelude::*;

#[program]
pub mod vulnerable_account_{id} {{
    use super::*;

    pub fn transfer_funds(ctx: Context<TransferFunds>, amount: u64) -> Result<()> {{
        // VULNERABLE: No account validation
        let from_account = &mut ctx.accounts.from;
        let to_account = &mut ctx.accounts.to;
        
        from_account.balance -= amount;
        to_account.balance += amount;
        
        Ok(())
    }}
}}

#[derive(Accounts)]
pub struct TransferFunds<'info> {{
    #[account(mut)]
    pub from: Account<'info, UserAccount>, // No validation!
    #[account(mut)]
    pub to: Account<'info, UserAccount>,   // No validation!
}}
'''
            },
            {
                "vulnerability": "integer_overflow",
                "template": '''
use anchor_lang::prelude::*;

#[program]
pub mod vulnerable_overflow_{id} {{
    use super::*;

    pub fn add_balance(ctx: Context<AddBalance>, amount: u64) -> Result<()> {{
        let user_account = &mut ctx.accounts.user_account;
        
        // VULNERABLE: Potential integer overflow
        user_account.balance = user_account.balance + amount; // No overflow check
        
        Ok(())
    }}
}}

#[derive(Accounts)]
pub struct AddBalance<'info> {{
    #[account(mut)]
    pub user_account: Account<'info, UserAccount>,
}}
'''
            },
            {
                "vulnerability": "signature_verification",
                "template": '''
use anchor_lang::prelude::*;

#[program]
pub mod vulnerable_signature_{id} {{
    use super::*;

    pub fn admin_operation(ctx: Context<AdminOperation>) -> Result<()> {{
        // VULNERABLE: No signature verification
        let admin = &ctx.accounts.admin;
        // Missing: require!(admin.is_signer, ErrorCode::Unauthorized);
        
        // Perform admin operation without verification
        Ok(())
    }}
}}

#[derive(Accounts)]
pub struct AdminOperation<'info> {{
    pub admin: AccountInfo<'info>, // No Signer constraint!
}}
'''
            },
            {
                "vulnerability": "panic_handling",
                "template": '''
use anchor_lang::prelude::*;

#[program]
pub mod vulnerable_panic_{id} {{
    use super::*;

    pub fn risky_operation(ctx: Context<RiskyOperation>, divisor: u64) -> Result<()> {{
        // VULNERABLE: No panic handling
        let result = 1000 / divisor; // Will panic if divisor is 0
        
        let user_account = &mut ctx.accounts.user_account;
        user_account.value = result;
        
        Ok(())
    }}
}}

#[derive(Accounts)]
pub struct RiskyOperation<'info> {{
    #[account(mut)]
    pub user_account: Account<'info, UserAccount>,
}}
'''
            }
        ]
        
        for i in range(count):
            template = vulnerable_templates[i % len(vulnerable_templates)]
            contract = {
                "contract_id": f"vulnerable_rust_{template['vulnerability']}_{i:03d}",
                "source_code": template["template"].format(id=i),
                "vulnerabilities": [template["vulnerability"]],
                "severity": ["high"],
                "source": "mock_vulnerable_rust",
                "file_path": f"mock_vulnerable_rust_{template['vulnerability']}_{i:03d}.rs"
            }
            contracts.append(contract)
        
        return contracts

    def aggregate_all(self) -> str:
        """Aggregate all Rust datasets into unified format"""
        print("Starting Rust dataset aggregation...")
        
        all_contracts = []
        
        # Download Hugging Face Solana dataset
        try:
            hf_contracts = self.download_huggingface_solana_dataset()
            all_contracts.extend(hf_contracts)
            print(f"Added {len(hf_contracts)} contracts from Hugging Face")
        except Exception as e:
            print(f"Hugging Face download failed: {e}")
        
        # Download GitHub Solana datasets
        try:
            github_contracts = self.download_github_solana_datasets()
            all_contracts.extend(github_contracts)
            print(f"Added {len(github_contracts)} contracts from GitHub")
        except Exception as e:
            print(f"GitHub download failed: {e}")
        
        # Add mock safe Rust contracts
        safe_contracts = self.create_rust_safe_contracts(100)
        all_contracts.extend(safe_contracts)
        
        # Add mock vulnerable Rust contracts
        vulnerable_contracts = self.create_rust_vulnerable_contracts(50)
        all_contracts.extend(vulnerable_contracts)
        
        # Save unified dataset
        output_file = self.processed_dir / "unified_rust_dataset.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_contracts, f, indent=2, ensure_ascii=False)
        
        # Generate statistics
        stats = self.generate_statistics(all_contracts)
        stats_file = self.processed_dir / "rust_dataset_statistics.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"Rust dataset aggregation complete!")
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
    import argparse
    
    parser = argparse.ArgumentParser(description="Aggregate Rust/Solana vulnerability datasets")
    parser.add_argument("--github-token", type=str, help="GitHub personal access token for API access")
    parser.add_argument("--output-dir", type=str, default="datasets", help="Output directory for datasets")
    
    args = parser.parse_args()
    
    aggregator = RustDatasetAggregator(output_dir=args.output_dir, github_token=args.github_token)
    output_file = aggregator.aggregate_all()
    print(f"Unified Rust dataset saved to: {output_file}")


if __name__ == "__main__":
    main()
