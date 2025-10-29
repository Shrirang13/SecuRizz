#!/usr/bin/env python3
"""
Comprehensive vulnerable contract extraction from multiple sources.
Extracts Rust/Solana contracts from various security databases and reports.
"""

import json
import requests
import re
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import hashlib
from bs4 import BeautifulSoup
import feedparser


class VulnerableContractExtractor:
    def __init__(self, output_dir: str = "datasets/raw"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Vulnerability patterns for Rust/Solana
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

    def extract_from_rekt_news(self) -> List[Dict[str, Any]]:
        """Extract vulnerable contracts from Rekt.news"""
        print("Extracting from Rekt.news...")
        contracts = []
        
        try:
            # Get the main page
            response = requests.get("https://rekt.news/", timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find links to hack reports
            hack_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/rekt/' in href or '/hack/' in href:
                    hack_links.append(urljoin("https://rekt.news", href))
            
            # Process each hack report
            for link in hack_links[:20]:  # Limit to 20 reports
                try:
                    time.sleep(1)  # Be respectful
                    report_response = requests.get(link, timeout=30)
                    report_response.raise_for_status()
                    report_soup = BeautifulSoup(report_response.content, 'html.parser')
                    
                    # Extract code blocks
                    code_blocks = report_soup.find_all(['code', 'pre'])
                    for block in code_blocks:
                        code_text = block.get_text().strip()
                        if self._is_rust_code(code_text):
                            vulnerabilities = self._detect_vulnerabilities(code_text)
                            if vulnerabilities:
                                contract = {
                                    "contract_id": f"rekt_{hashlib.md5(link.encode()).hexdigest()[:8]}",
                                    "source_code": code_text,
                                    "vulnerabilities": vulnerabilities,
                                    "severity": ["high"],
                                    "source": "rekt_news",
                                    "file_path": f"rekt_{link.split('/')[-1]}.rs",
                                    "url": link
                                }
                                contracts.append(contract)
                                
                except Exception as e:
                    print(f"Error processing {link}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error extracting from Rekt.news: {e}")
        
        print(f"Extracted {len(contracts)} contracts from Rekt.news")
        return contracts

    def extract_from_immunefi(self) -> List[Dict[str, Any]]:
        """Extract vulnerable contracts from Immunefi reports"""
        print("Extracting from Immunefi...")
        contracts = []
        
        try:
            # Get the explore page
            response = requests.get("https://immunefi.com/explore/", timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find report links
            report_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/exploit/' in href or '/bug-bounty/' in href:
                    report_links.append(urljoin("https://immunefi.com", href))
            
            # Process reports
            for link in report_links[:15]:  # Limit to 15 reports
                try:
                    time.sleep(1)
                    report_response = requests.get(link, timeout=30)
                    report_response.raise_for_status()
                    report_soup = BeautifulSoup(report_response.content, 'html.parser')
                    
                    # Extract code blocks
                    code_blocks = report_soup.find_all(['code', 'pre'])
                    for block in code_blocks:
                        code_text = block.get_text().strip()
                        if self._is_rust_code(code_text):
                            vulnerabilities = self._detect_vulnerabilities(code_text)
                            if vulnerabilities:
                                contract = {
                                    "contract_id": f"immunefi_{hashlib.md5(link.encode()).hexdigest()[:8]}",
                                    "source_code": code_text,
                                    "vulnerabilities": vulnerabilities,
                                    "severity": ["high"],
                                    "source": "immunefi",
                                    "file_path": f"immunefi_{link.split('/')[-1]}.rs",
                                    "url": link
                                }
                                contracts.append(contract)
                                
                except Exception as e:
                    print(f"Error processing {link}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error extracting from Immunefi: {e}")
        
        print(f"Extracted {len(contracts)} contracts from Immunefi")
        return contracts

    def extract_from_slowmist(self) -> List[Dict[str, Any]]:
        """Extract vulnerable contracts from SlowMist Hacked"""
        print("Extracting from SlowMist Hacked...")
        contracts = []
        
        try:
            response = requests.get("https://hacked.slowmist.io/en/", timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find hack report links
            report_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/hack/' in href:
                    report_links.append(urljoin("https://hacked.slowmist.io", href))
            
            # Process reports
            for link in report_links[:15]:
                try:
                    time.sleep(1)
                    report_response = requests.get(link, timeout=30)
                    report_response.raise_for_status()
                    report_soup = BeautifulSoup(report_response.content, 'html.parser')
                    
                    # Extract code blocks
                    code_blocks = report_soup.find_all(['code', 'pre'])
                    for block in code_blocks:
                        code_text = block.get_text().strip()
                        if self._is_rust_code(code_text):
                            vulnerabilities = self._detect_vulnerabilities(code_text)
                            if vulnerabilities:
                                contract = {
                                    "contract_id": f"slowmist_{hashlib.md5(link.encode()).hexdigest()[:8]}",
                                    "source_code": code_text,
                                    "vulnerabilities": vulnerabilities,
                                    "severity": ["high"],
                                    "source": "slowmist",
                                    "file_path": f"slowmist_{link.split('/')[-1]}.rs",
                                    "url": link
                                }
                                contracts.append(contract)
                                
                except Exception as e:
                    print(f"Error processing {link}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error extracting from SlowMist: {e}")
        
        print(f"Extracted {len(contracts)} contracts from SlowMist")
        return contracts

    def extract_from_cve_database(self) -> List[Dict[str, Any]]:
        """Extract Rust-related CVEs from NVD"""
        print("Extracting from CVE database...")
        contracts = []
        
        try:
            # Search for Rust-related CVEs
            search_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
            params = {
                "keywordSearch": "rust",
                "resultsPerPage": 100
            }
            
            response = requests.get(search_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            for cve in data.get('vulnerabilities', []):
                cve_data = cve.get('cve', {})
                cve_id = cve_data.get('id', '')
                description = cve_data.get('descriptions', [{}])[0].get('value', '')
                
                # Look for code snippets in description
                if 'rust' in description.lower() or 'solana' in description.lower():
                    # Extract any code-like content
                    code_matches = re.findall(r'```[\s\S]*?```|`[^`]+`', description)
                    for code_match in code_matches:
                        code_text = re.sub(r'```.*?\n?', '', code_match).strip()
                        if self._is_rust_code(code_text):
                            vulnerabilities = self._detect_vulnerabilities(code_text)
                            if vulnerabilities:
                                contract = {
                                    "contract_id": f"cve_{cve_id}",
                                    "source_code": code_text,
                                    "vulnerabilities": vulnerabilities,
                                    "severity": ["high"],
                                    "source": "cve_database",
                                    "file_path": f"cve_{cve_id}.rs",
                                    "cve_id": cve_id
                                }
                                contracts.append(contract)
                                
        except Exception as e:
            print(f"Error extracting from CVE database: {e}")
        
        print(f"Extracted {len(contracts)} contracts from CVE database")
        return contracts

    def extract_from_github_issues(self, repo_owner: str, repo_name: str, max_issues: int = 50) -> List[Dict[str, Any]]:
        """Extract vulnerable code from GitHub issues"""
        print(f"Extracting from GitHub issues: {repo_owner}/{repo_name}")
        contracts = []
        
        try:
            # Get issues with security-related labels
            issues_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
            params = {
                "state": "all",
                "labels": "security,vulnerability,bug",
                "per_page": max_issues
            }
            
            response = requests.get(issues_url, params=params, timeout=30)
            response.raise_for_status()
            issues = response.json()
            
            for issue in issues:
                issue_body = issue.get('body', '')
                issue_title = issue.get('title', '')
                
                # Extract code blocks from issue body
                code_blocks = re.findall(r'```(?:rust)?\s*(.*?)```', issue_body, re.DOTALL)
                for code_text in code_blocks:
                    code_text = code_text.strip()
                    if self._is_rust_code(code_text):
                        vulnerabilities = self._detect_vulnerabilities(code_text)
                        if vulnerabilities:
                            contract = {
                                "contract_id": f"github_{repo_owner}_{repo_name}_{issue['number']}",
                                "source_code": code_text,
                                "vulnerabilities": vulnerabilities,
                                "severity": ["medium"],
                                "source": f"github_{repo_owner}_{repo_name}",
                                "file_path": f"github_issue_{issue['number']}.rs",
                                "issue_url": issue['html_url']
                            }
                            contracts.append(contract)
                            
        except Exception as e:
            print(f"Error extracting from GitHub issues: {e}")
        
        print(f"Extracted {len(contracts)} contracts from GitHub issues")
        return contracts

    def _is_rust_code(self, code: str) -> bool:
        """Check if code appears to be Rust"""
        rust_indicators = [
            'use ', 'fn ', 'struct ', 'impl ', 'pub ', 'let ', 'mut ',
            'anchor_lang', 'solana_program', 'borsh', 'derive',
            'AccountInfo', 'Program', 'Context', 'Result<()>'
        ]
        
        code_lower = code.lower()
        rust_score = sum(1 for indicator in rust_indicators if indicator in code_lower)
        
        # Must have at least 3 Rust indicators and be reasonably long
        return rust_score >= 3 and len(code) > 100

    def _detect_vulnerabilities(self, code: str) -> List[str]:
        """Detect vulnerabilities in Rust code"""
        vulnerabilities = []
        code_lower = code.lower()
        
        for vuln_type, patterns in self.vulnerability_patterns.items():
            for pattern in patterns:
                if re.search(pattern, code_lower):
                    if vuln_type not in vulnerabilities:
                        vulnerabilities.append(vuln_type)
                    break
        
        return vulnerabilities

    def extract_all_sources(self) -> List[Dict[str, Any]]:
        """Extract from all available sources"""
        print("Starting comprehensive vulnerable contract extraction...")
        all_contracts = []
        
        # Extract from various sources
        sources = [
            self.extract_from_rekt_news,
            self.extract_from_immunefi,
            self.extract_from_slowmist,
            self.extract_from_cve_database,
        ]
        
        # Add GitHub issues for major Solana repos
        github_repos = [
            ("solana-labs", "solana-program-library"),
            ("coral-xyz", "anchor"),
            ("project-serum", "anchor"),
        ]
        
        for repo_owner, repo_name in github_repos:
            all_contracts.extend(self.extract_from_github_issues(repo_owner, repo_name))
        
        for source_func in sources:
            try:
                contracts = source_func()
                all_contracts.extend(contracts)
            except Exception as e:
                print(f"Error in {source_func.__name__}: {e}")
                continue
        
        # Save extracted contracts
        output_file = self.output_dir / "extracted_vulnerable_contracts.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_contracts, f, indent=2, ensure_ascii=False)
        
        print(f"Total extracted contracts: {len(all_contracts)}")
        print(f"Saved to: {output_file}")
        
        return all_contracts


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract vulnerable contracts from multiple sources")
    parser.add_argument("--output-dir", type=str, default="datasets/raw", help="Output directory")
    parser.add_argument("--source", type=str, choices=["all", "rekt", "immunefi", "slowmist", "cve", "github"], 
                       default="all", help="Specific source to extract from")
    
    args = parser.parse_args()
    
    extractor = VulnerableContractExtractor(args.output_dir)
    
    if args.source == "all":
        extractor.extract_all_sources()
    elif args.source == "rekt":
        extractor.extract_from_rekt_news()
    elif args.source == "immunefi":
        extractor.extract_from_immunefi()
    elif args.source == "slowmist":
        extractor.extract_from_slowmist()
    elif args.source == "cve":
        extractor.extract_from_cve_database()
    elif args.source == "github":
        extractor.extract_from_github_issues("solana-labs", "solana-program-library")


if __name__ == "__main__":
    main()
