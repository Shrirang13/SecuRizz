#!/usr/bin/env python3
"""
Mass download all available Rust/Solana datasets from GitHub and Hugging Face.
"""

import subprocess
import os
import json
from pathlib import Path
from huggingface_hub import list_datasets, snapshot_download
import requests

def clone_github_repos():
    """Clone all relevant GitHub repositories"""
    repos = [
        # Solana repositories
        "https://github.com/solana-labs/solana-program-library.git",
        "https://github.com/coral-xyz/anchor.git", 
        "https://github.com/project-serum/anchor.git",
        "https://github.com/solana-labs/solana.git",
        "https://github.com/solana-labs/solana-web3.js.git",
        
        # Security repositories
        "https://github.com/az0mb13/awesome-solana-security.git",
        "https://github.com/sannykim/solsec.git",
        "https://github.com/trailofbits/publications.git",
        "https://github.com/ottersec/audit-reports.git",
        
        # Vulnerability datasets
        "https://github.com/Messi-Q/Smart-Contract-Dataset.git",
        "https://github.com/smartbugs/smartbugs.git",
        "https://github.com/ConsenSys/smart-contract-best-practices.git",
        
        # Rust security
        "https://github.com/RustSec/advisory-db.git",
        "https://github.com/rust-lang/rust.git",
        
        # More Solana projects
        "https://github.com/raydium-io/raydium-sdk.git",
        "https://github.com/step-finance/step-staking.git",
        "https://github.com/solana-labs/token-list.git",
        "https://github.com/solana-labs/wallet-adapter.git",
    ]
    
    print("Cloning GitHub repositories...")
    for repo in repos:
        try:
            repo_name = repo.split('/')[-1].replace('.git', '')
            if not os.path.exists(f"datasets/raw/{repo_name}"):
                print(f"Cloning {repo_name}...")
                subprocess.run(["git", "clone", repo, f"datasets/raw/{repo_name}"], 
                             capture_output=True, timeout=300)
            else:
                print(f"Already exists: {repo_name}")
        except Exception as e:
            print(f"Failed to clone {repo}: {e}")

def download_huggingface_datasets():
    """Download all relevant Hugging Face datasets"""
    datasets = [
        "FraChiacc99/solana-vuln-rust",
        "darkknight25/Smart_Contract_Vulnerability_Dataset", 
        "DanCip/github-issues-vulnerability-detection",
        "microsoft/codebert-base",
        "huggingface/CodeBERTa-small-v1",
        "microsoft/graphcodebert-base",
        "facebook/incoder-1B",
        "Salesforce/codet5-base",
        "microsoft/unixcoder-base",
        "microsoft/codebert-base-mlm",
    ]
    
    print("Downloading Hugging Face datasets...")
    for dataset in datasets:
        try:
            print(f"Downloading {dataset}...")
            snapshot_download(repo_id=dataset, repo_type="dataset", 
                            local_dir=f"datasets/raw/hf_{dataset.replace('/', '_')}")
        except Exception as e:
            print(f"Failed to download {dataset}: {e}")

def download_additional_sources():
    """Download from other sources"""
    print("Downloading additional sources...")
    
    # Download SmartBugs dataset
    try:
        subprocess.run([
            "wget", "-O", "datasets/raw/smartbugs.zip",
            "https://github.com/smartbugs/smartbugs/archive/refs/heads/master.zip"
        ], capture_output=True, timeout=300)
    except:
        print("Failed to download SmartBugs")

def main():
    print("Starting mass dataset download...")
    
    # Create directories
    Path("datasets/raw").mkdir(parents=True, exist_ok=True)
    
    # Download everything
    clone_github_repos()
    download_huggingface_datasets() 
    download_additional_sources()
    
    print("Mass download complete!")

if __name__ == "__main__":
    main()
