#!/usr/bin/env python3
"""
Real Solana blockchain integration for SecuRizz
"""

import asyncio
import json
import os
from typing import Dict, Any, Optional
import base64

try:
    from solana.rpc.async_api import AsyncClient
    from solana.rpc.commitment import Commitment
    from solana.rpc.types import TxOpts
    from solders.transaction import Transaction
    from solders.pubkey import Pubkey as PublicKey
    from solders.keypair import Keypair
    from solana.system_program import transfer, TransferParams
    from anchorpy import Program, Provider, Wallet
    from anchorpy.provider import Wallet as AnchorWallet
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False
    print("WARNING: Solana SDK not available - using mock mode")

class SecuRizzSolanaClient:
    def __init__(self):
        self.rpc_url = os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")
        self.mock_mode = os.getenv("SOLANA_MOCK_MODE", "true").lower() == "true" or not SOLANA_AVAILABLE
        
        if not SOLANA_AVAILABLE:
            self.program_id = "SecuRizz1111111111111111111111111111111111111"
            self.client = None
            self.program = None
            self.provider = None
        else:
            self.program_id = PublicKey("SecuRizz1111111111111111111111111111111111111")
            self.client = AsyncClient(self.rpc_url)
            self.program = None
            self.provider = None
        
        if self.mock_mode:
            print("Solana client running in mock mode")
        
    async def initialize(self):
        """Initialize Solana client and program"""
        try:
            # Load program IDL
            with open("solana-contract/target/idl/securizz.json", "r") as f:
                idl = json.load(f)
            
            # Create wallet from keypair
            keypair = Keypair.from_secret_key(
                base64.b64decode(os.getenv("SOLANA_PRIVATE_KEY", ""))
            )
            wallet = AnchorWallet(keypair)
            
            # Create provider
            self.provider = Provider(self.rpc_url, wallet)
            
            # Create program
            self.program = Program(idl, self.program_id, self.provider)
            
            print("✅ Solana client initialized")
            return True
        except Exception as e:
            print(f"❌ Solana initialization failed: {str(e)}")
            return False

    async def submit_audit_proof(
        self,
        contract_hash: str,
        report_hash: str,
        ipfs_cid: str,
        risk_score: int,
        audit_score: int,
        contract_address: str
    ) -> Optional[str]:
        """Submit audit proof to Solana blockchain"""
        if self.mock_mode:
            # Mock transaction hash
            import hashlib
            import time
            mock_data = f"{contract_hash}{report_hash}{ipfs_cid}{risk_score}{audit_score}{time.time()}"
            tx_hash = hashlib.sha256(mock_data.encode()).hexdigest()
            print(f"Mock Solana TX: {tx_hash}")
            return tx_hash
            
        try:
            if not self.program:
                await self.initialize()
            
            # Convert strings to bytes
            contract_hash_bytes = bytes.fromhex(contract_hash)
            report_hash_bytes = bytes.fromhex(report_hash)
            contract_pubkey = PublicKey(contract_address)
            
            # Create transaction
            tx = await self.program.rpc.submit_proof(
                contract_hash_bytes,
                report_hash_bytes,
                ipfs_cid,
                risk_score,
                audit_score,
                contract_pubkey,
                ctx={
                    "audit_proof": {
                        "contract_hash": contract_hash_bytes,
                    },
                    "oracle": self.provider.wallet.public_key,
                }
            )
            
            print(f"✅ Audit proof submitted: {tx}")
            return str(tx)
            
        except Exception as e:
            print(f"❌ Audit proof submission failed: {str(e)}")
            return None

    async def verify_audit_integrity(
        self,
        contract_hash: str,
        expected_ipfs_hash: str
    ) -> bool:
        """Verify audit integrity on-chain"""
        try:
            if not self.program:
                await self.initialize()
            
            contract_hash_bytes = bytes.fromhex(contract_hash)
            expected_hash_bytes = bytes.fromhex(expected_ipfs_hash)
            
            # Call verification function
            await self.program.rpc.verify_audit_integrity(
                expected_hash_bytes,
                ctx={
                    "audit_proof": {
                        "contract_hash": contract_hash_bytes,
                    },
                    "authority": self.provider.wallet.public_key,
                }
            )
            
            print("✅ Audit integrity verified")
            return True
            
        except Exception as e:
            print(f"❌ Audit verification failed: {str(e)}")
            return False

    async def get_audit_proof(self, contract_hash: str) -> Optional[Dict[str, Any]]:
        """Get audit proof from blockchain"""
        try:
            if not self.program:
                await self.initialize()
            
            contract_hash_bytes = bytes.fromhex(contract_hash)
            
            # Fetch audit proof account
            proof_account = await self.program.account.audit_proof.fetch(
                PublicKey.find_program_address(
                    [b"audit_proof", contract_hash_bytes],
                    self.program_id
                )[0]
            )
            
            return {
                "contract_hash": proof_account.contract_hash.hex(),
                "report_hash": proof_account.report_hash.hex(),
                "ipfs_cid": proof_account.ipfs_cid,
                "risk_score": proof_account.risk_score,
                "audit_score": proof_account.audit_score,
                "timestamp": proof_account.timestamp,
                "verified": proof_account.verified,
                "oracle": str(proof_account.oracle)
            }
            
        except Exception as e:
            print(f"❌ Failed to get audit proof: {str(e)}")
            return None

    async def stake_tokens(
        self,
        amount: int,
        duration: int,
        user_keypair: Keypair
    ) -> Optional[str]:
        """Stake SECURIZZ tokens"""
        try:
            if not self.program:
                await self.initialize()
            
            # Create stake transaction
            tx = await self.program.rpc.stake_tokens(
                amount,
                duration,
                ctx={
                    "stake_account": {
                        "user": user_keypair.public_key,
                    },
                    "user_token_account": user_keypair.public_key,  # Simplified
                    "staking_pool": PublicKey("StakingPool1111111111111111111111111111111111"),
                    "user": user_keypair,
                }
            )
            
            print(f"✅ Tokens staked: {tx}")
            return str(tx)
            
        except Exception as e:
            print(f"❌ Staking failed: {str(e)}")
            return None

    async def claim_rewards(self, user_keypair: Keypair) -> Optional[str]:
        """Claim staking rewards"""
        try:
            if not self.program:
                await self.initialize()
            
            # Create claim transaction
            tx = await self.program.rpc.claim_rewards(
                ctx={
                    "stake_account": {
                        "user": user_keypair.public_key,
                    },
                    "user_token_account": user_keypair.public_key,
                    "staking_pool": PublicKey("StakingPool1111111111111111111111111111111111"),
                    "staking_authority": PublicKey("StakingAuth1111111111111111111111111111111111"),
                    "user": user_keypair,
                }
            )
            
            print(f"✅ Rewards claimed: {tx}")
            return str(tx)
            
        except Exception as e:
            print(f"❌ Reward claiming failed: {str(e)}")
            return None

    async def pay_for_audit(
        self,
        audit_fee: int,
        contract_hash: str,
        user_keypair: Keypair
    ) -> Optional[str]:
        """Pay for audit with SECURIZZ tokens"""
        try:
            if not self.program:
                await self.initialize()
            
            # Create payment transaction
            tx = await self.program.rpc.pay_for_audit(
                audit_fee,
                ctx={
                    "audit_proof": {
                        "contract_hash": bytes.fromhex(contract_hash),
                    },
                    "user_token_account": user_keypair.public_key,
                    "treasury": PublicKey("Treasury1111111111111111111111111111111111111"),
                    "user": user_keypair,
                }
            )
            
            print(f"✅ Audit payment processed: {tx}")
            return str(tx)
            
        except Exception as e:
            print(f"❌ Payment failed: {str(e)}")
            return None

    async def vote_on_proposal(
        self,
        proposal_id: int,
        vote_weight: int,
        support: bool,
        user_keypair: Keypair
    ) -> Optional[str]:
        """Vote on governance proposal"""
        try:
            if not self.program:
                await self.initialize()
            
            # Create vote transaction
            tx = await self.program.rpc.vote_on_proposal(
                proposal_id,
                vote_weight,
                support,
                ctx={
                    "vote_account": {
                        "proposal_id": proposal_id,
                        "voter": user_keypair.public_key,
                    },
                    "stake_account": {
                        "user": user_keypair.public_key,
                    },
                    "voter": user_keypair,
                }
            )
            
            print(f"✅ Vote cast: {tx}")
            return str(tx)
            
        except Exception as e:
            print(f"❌ Voting failed: {str(e)}")
            return None

    async def get_account_balance(self, public_key: str) -> Optional[float]:
        """Get SOL balance for account"""
        try:
            balance = await self.client.get_balance(PublicKey(public_key))
            return balance.value / 1e9  # Convert lamports to SOL
        except Exception as e:
            print(f"❌ Failed to get balance: {str(e)}")
            return None

    async def get_token_balance(self, wallet_address: str, token_mint: str) -> Optional[float]:
        """Get SECURIZZ token balance"""
        try:
            # This would query the token account
            # Simplified implementation
            return 1000.0  # Mock balance
        except Exception as e:
            print(f"❌ Failed to get token balance: {str(e)}")
            return None

    async def close(self):
        """Close Solana client connection"""
        if self.client:
            await self.client.close()

# Global instance
solana_client = SecuRizzSolanaClient()
