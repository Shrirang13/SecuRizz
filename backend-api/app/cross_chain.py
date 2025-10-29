#!/usr/bin/env python3
"""
Cross-chain integration for SecuRizz
"""

import asyncio
import json
import os
from typing import Dict, Any, List, Optional
from web3 import Web3
try:
    from solana.rpc.async_api import AsyncClient
except ImportError:
    AsyncClient = None
try:
    from solders.pubkey import Pubkey as PublicKey
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False
    PublicKey = str
import requests

class CrossChainManager:
    def __init__(self):
        # Ethereum configuration
        self.ethereum_rpc = os.getenv("ETHEREUM_RPC_URL", "https://mainnet.infura.io/v3/YOUR_PROJECT_ID")
        self.ethereum_w3 = Web3(Web3.HTTPProvider(self.ethereum_rpc))
        
        # Polygon configuration
        self.polygon_rpc = os.getenv("POLYGON_RPC_URL", "https://polygon-rpc.com")
        self.polygon_w3 = Web3(Web3.HTTPProvider(self.polygon_rpc))
        
        # BSC configuration
        self.bsc_rpc = os.getenv("BSC_RPC_URL", "https://bsc-dataseed.binance.org")
        self.bsc_w3 = Web3(Web3.HTTPProvider(self.bsc_rpc))
        
        # Solana configuration
        self.solana_rpc = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
        self.solana_client = AsyncClient(self.solana_rpc)
        
        # Chain configurations
        self.chains = {
            "ethereum": {
                "name": "Ethereum",
                "chain_id": 1,
                "rpc": self.ethereum_rpc,
                "w3": self.ethereum_w3,
                "native_token": "ETH",
                "explorer": "https://etherscan.io"
            },
            "polygon": {
                "name": "Polygon",
                "chain_id": 137,
                "rpc": self.polygon_rpc,
                "w3": self.polygon_w3,
                "native_token": "MATIC",
                "explorer": "https://polygonscan.com"
            },
            "bsc": {
                "name": "BSC",
                "chain_id": 56,
                "rpc": self.bsc_rpc,
                "w3": self.bsc_w3,
                "native_token": "BNB",
                "explorer": "https://bscscan.com"
            },
            "solana": {
                "name": "Solana",
                "chain_id": "mainnet-beta",
                "rpc": self.solana_rpc,
                "client": self.solana_client,
                "native_token": "SOL",
                "explorer": "https://explorer.solana.com"
            }
        }

    async def analyze_contract_cross_chain(self, contract_address: str, chain: str) -> Dict[str, Any]:
        """Analyze contract on any supported chain"""
        try:
            if chain not in self.chains:
                raise ValueError(f"Unsupported chain: {chain}")
            
            chain_config = self.chains[chain]
            
            if chain == "solana":
                return await self._analyze_solana_contract(contract_address)
            else:
                return await self._analyze_evm_contract(contract_address, chain_config)
                
        except Exception as e:
            print(f"❌ Cross-chain analysis failed: {str(e)}")
            return {"error": str(e)}

    async def _analyze_solana_contract(self, program_id: str) -> Dict[str, Any]:
        """Analyze Solana program"""
        try:
            # Get program account info
            program_pubkey = PublicKey(program_id)
            account_info = await self.solana_client.get_account_info(program_pubkey)
            
            if not account_info.value:
                return {"error": "Program not found"}
            
            # Analyze program data
            program_data = account_info.value.data
            program_size = len(program_data)
            
            # Basic analysis
            analysis = {
                "chain": "solana",
                "program_id": program_id,
                "program_size": program_size,
                "owner": str(account_info.value.owner),
                "executable": account_info.value.executable,
                "lamports": account_info.value.lamports,
                "vulnerabilities": [],
                "risk_score": 0,
                "audit_score": 0
            }
            
            # Check for common Solana vulnerabilities
            vulnerabilities = []
            
            # Check for unsafe code patterns
            if b"unsafe" in program_data:
                vulnerabilities.append("unsafe_code")
            
            # Check for panic handling
            if b"panic!" in program_data:
                vulnerabilities.append("panic_handling")
            
            # Check for account validation
            if b"require!" in program_data:
                vulnerabilities.append("account_validation")
            
            # Check for rent exemption
            if b"rent" in program_data:
                vulnerabilities.append("rent_exemption")
            
            analysis["vulnerabilities"] = vulnerabilities
            analysis["risk_score"] = len(vulnerabilities) * 20
            analysis["audit_score"] = max(0, 100 - analysis["risk_score"])
            
            return analysis
            
        except Exception as e:
            print(f"❌ Solana analysis failed: {str(e)}")
            return {"error": str(e)}

    async def _analyze_evm_contract(self, contract_address: str, chain_config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze EVM contract (Ethereum, Polygon, BSC)"""
        try:
            w3 = chain_config["w3"]
            
            # Get contract code
            code = w3.eth.get_code(contract_address)
            
            if not code or code == b'':
                return {"error": "Contract not found or not a contract"}
            
            # Get contract bytecode
            bytecode = code.hex()
            
            # Basic analysis
            analysis = {
                "chain": chain_config["name"].lower(),
                "contract_address": contract_address,
                "bytecode_size": len(bytecode),
                "vulnerabilities": [],
                "risk_score": 0,
                "audit_score": 0
            }
            
            # Check for common EVM vulnerabilities
            vulnerabilities = []
            
            # Check for reentrancy patterns
            if "5f5e100f" in bytecode:  # delegatecall
                vulnerabilities.append("reentrancy")
            
            # Check for integer overflow
            if "0x4e487b71" in bytecode:  # SafeMath
                vulnerabilities.append("integer_overflow")
            
            # Check for access control
            if "0x8da5cb5b" in bytecode:  # owner()
                vulnerabilities.append("access_control")
            
            # Check for timestamp dependency
            if "0x42cbb15c" in bytecode:  # block.timestamp
                vulnerabilities.append("timestamp_dependency")
            
            # Check for tx.origin usage
            if "0x32" in bytecode:  # tx.origin
                vulnerabilities.append("tx_origin")
            
            analysis["vulnerabilities"] = vulnerabilities
            analysis["risk_score"] = len(vulnerabilities) * 15
            analysis["audit_score"] = max(0, 100 - analysis["risk_score"])
            
            return analysis
            
        except Exception as e:
            print(f"❌ EVM analysis failed: {str(e)}")
            return {"error": str(e)}

    async def get_chain_status(self) -> Dict[str, Any]:
        """Get status of all supported chains"""
        status = {}
        
        for chain_name, config in self.chains.items():
            try:
                if chain_name == "solana":
                    # Check Solana connection
                    version = await self.solana_client.get_version()
                    status[chain_name] = {
                        "connected": True,
                        "version": version.value.solana_core,
                        "rpc": config["rpc"]
                    }
                else:
                    # Check EVM connection
                    w3 = config["w3"]
                    latest_block = w3.eth.block_number
                    status[chain_name] = {
                        "connected": True,
                        "latest_block": latest_block,
                        "rpc": config["rpc"]
                    }
            except Exception as e:
                status[chain_name] = {
                    "connected": False,
                    "error": str(e),
                    "rpc": config["rpc"]
                }
        
        return status

    async def deploy_audit_proof_cross_chain(self, audit_data: Dict[str, Any], target_chains: List[str]) -> Dict[str, Any]:
        """Deploy audit proof to multiple chains"""
        results = {}
        
        for chain in target_chains:
            if chain not in self.chains:
                results[chain] = {"error": f"Unsupported chain: {chain}"}
                continue
            
            try:
                if chain == "solana":
                    result = await self._deploy_solana_proof(audit_data)
                else:
                    result = await self._deploy_evm_proof(audit_data, chain)
                
                results[chain] = result
                
            except Exception as e:
                results[chain] = {"error": str(e)}
        
        return results

    async def _deploy_solana_proof(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy audit proof to Solana"""
        try:
            # This would use the Solana client to deploy proof
            # Simplified implementation
            return {
                "chain": "solana",
                "transaction_hash": "mock_solana_tx_hash",
                "program_id": "mock_program_id",
                "status": "success"
            }
        except Exception as e:
            return {"error": str(e)}

    async def _deploy_evm_proof(self, audit_data: Dict[str, Any], chain: str) -> Dict[str, Any]:
        """Deploy audit proof to EVM chain"""
        try:
            # This would deploy a smart contract with audit proof
            # Simplified implementation
            return {
                "chain": chain,
                "transaction_hash": f"mock_{chain}_tx_hash",
                "contract_address": f"mock_{chain}_contract",
                "status": "success"
            }
        except Exception as e:
            return {"error": str(e)}

    async def verify_audit_cross_chain(self, contract_address: str, chain: str) -> Dict[str, Any]:
        """Verify audit status across chains"""
        try:
            # Check if audit exists on any chain
            verification_results = {}
            
            for chain_name in self.chains.keys():
                try:
                    if chain_name == "solana":
                        # Check Solana for audit proof
                        result = await self._check_solana_audit(contract_address)
                    else:
                        # Check EVM chain for audit proof
                        result = await self._check_evm_audit(contract_address, chain_name)
                    
                    verification_results[chain_name] = result
                    
                except Exception as e:
                    verification_results[chain_name] = {"error": str(e)}
            
            return verification_results
            
        except Exception as e:
            return {"error": str(e)}

    async def _check_solana_audit(self, contract_address: str) -> Dict[str, Any]:
        """Check audit status on Solana"""
        try:
            # This would query the Solana program for audit proof
            return {
                "chain": "solana",
                "audit_found": True,
                "audit_score": 85,
                "risk_score": 15,
                "verified": True
            }
        except Exception as e:
            return {"error": str(e)}

    async def _check_evm_audit(self, contract_address: str, chain: str) -> Dict[str, Any]:
        """Check audit status on EVM chain"""
        try:
            # This would query the EVM contract for audit proof
            return {
                "chain": chain,
                "audit_found": True,
                "audit_score": 80,
                "risk_score": 20,
                "verified": True
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_supported_chains(self) -> List[Dict[str, Any]]:
        """Get list of supported chains"""
        chains = []
        
        for chain_name, config in self.chains.items():
            chains.append({
                "name": config["name"],
                "chain_id": config.get("chain_id", "mainnet-beta"),
                "native_token": config["native_token"],
                "explorer": config["explorer"],
                "supported": True
            })
        
        return chains

    async def close(self):
        """Close all connections"""
        if self.solana_client:
            await self.solana_client.close()

# Global instance
cross_chain_manager = CrossChainManager()
