use anchor_lang::prelude::*;

declare_id!("ReplaceWithDeployedProgramId");

#[program]
pub mod securizz {
    use super::*;

    pub fn submit_proof(
        ctx: Context<SubmitProof>,
        contract_hash: [u8; 32],
        report_hash: [u8; 32],
        ipfs_cid: String,
        risk_score: u64,
    ) -> Result<()> {
        let audit_proof = &mut ctx.accounts.audit_proof;
        let clock = Clock::get()?;

        audit_proof.contract_hash = contract_hash;
        audit_proof.report_hash = report_hash;
        audit_proof.ipfs_cid = ipfs_cid;
        audit_proof.risk_score = risk_score;
        audit_proof.timestamp = clock.unix_timestamp;
        audit_proof.verified = false;
        audit_proof.oracle = ctx.accounts.oracle.key();

        emit!(ProofSubmitted {
            contract_hash,
            report_hash,
            risk_score,
            timestamp: clock.unix_timestamp,
        });

        Ok(())
    }

    pub fn update_verification(
        ctx: Context<UpdateVerification>,
        verified: bool,
    ) -> Result<()> {
        let audit_proof = &mut ctx.accounts.audit_proof;
        
        require!(
            ctx.accounts.authority.key() == audit_proof.oracle,
            ErrorCode::Unauthorized
        );

        audit_proof.verified = verified;

        emit!(VerificationUpdated {
            contract_hash: audit_proof.contract_hash,
            verified,
        });

        Ok(())
    }

    pub fn get_proof(ctx: Context<GetProof>) -> Result<()> {
        let audit_proof = &ctx.accounts.audit_proof;
        
        emit!(ProofRetrieved {
            contract_hash: audit_proof.contract_hash,
            report_hash: audit_proof.report_hash,
            ipfs_cid: audit_proof.ipfs_cid.clone(),
            risk_score: audit_proof.risk_score,
            timestamp: audit_proof.timestamp,
            verified: audit_proof.verified,
        });

        Ok(())
    }
}

#[derive(Accounts)]
#[instruction(contract_hash: [u8; 32])]
pub struct SubmitProof<'info> {
    #[account(
        init,
        payer = oracle,
        space = 8 + 32 + 32 + 4 + 100 + 8 + 8 + 1 + 32,
        seeds = [b"audit_proof", contract_hash.as_ref()],
        bump
    )]
    pub audit_proof: Account<'info, AuditProof>,
    
    #[account(mut)]
    pub oracle: Signer<'info>,
    
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct UpdateVerification<'info> {
    #[account(mut)]
    pub audit_proof: Account<'info, AuditProof>,
    
    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct GetProof<'info> {
    pub audit_proof: Account<'info, AuditProof>,
}

#[account]
pub struct AuditProof {
    pub contract_hash: [u8; 32],
    pub report_hash: [u8; 32],
    pub ipfs_cid: String,
    pub risk_score: u64,
    pub timestamp: i64,
    pub verified: bool,
    pub oracle: Pubkey,
}

#[event]
pub struct ProofSubmitted {
    pub contract_hash: [u8; 32],
    pub report_hash: [u8; 32],
    pub risk_score: u64,
    pub timestamp: i64,
}

#[event]
pub struct VerificationUpdated {
    pub contract_hash: [u8; 32],
    pub verified: bool,
}

#[event]
pub struct ProofRetrieved {
    pub contract_hash: [u8; 32],
    pub report_hash: [u8; 32],
    pub ipfs_cid: String,
    pub risk_score: u64,
    pub timestamp: i64,
    pub verified: bool,
}

#[error_code]
pub enum ErrorCode {
    #[msg("Unauthorized access")]
    Unauthorized,
    #[msg("Invalid risk score")]
    InvalidRiskScore,
    #[msg("Proof not found")]
    ProofNotFound,
}
