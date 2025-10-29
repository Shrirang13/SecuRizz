use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount, Mint, MintTo, Transfer};
use anchor_spl::associated_token::AssociatedToken;

declare_id!("ReplaceWithDeployedProgramId");

#[program]
pub mod securizz_tokenomics {
    use super::*;

    // Initialize SECURIZZ token
    pub fn initialize_token(
        ctx: Context<InitializeToken>,
        decimals: u8,
    ) -> Result<()> {
        let mint = &mut ctx.accounts.mint;
        mint.mint_authority = COption::Some(ctx.accounts.authority.key());
        mint.supply = 0;
        mint.decimals = decimals;
        mint.is_initialized = true;
        mint.freeze_authority = COption::Some(ctx.accounts.authority.key());
        Ok(())
    }

    // Stake SECURIZZ tokens for audit rewards
    pub fn stake_tokens(
        ctx: Context<StakeTokens>,
        amount: u64,
        duration: u64, // in seconds
    ) -> Result<()> {
        let stake_account = &mut ctx.accounts.stake_account;
        let clock = Clock::get()?;
        
        require!(amount > 0, ErrorCode::InvalidAmount);
        require!(duration >= 86400, ErrorCode::InvalidDuration); // Minimum 1 day
        
        stake_account.user = ctx.accounts.user.key();
        stake_account.amount = amount;
        stake_account.duration = duration;
        stake_account.staked_at = clock.unix_timestamp;
        stake_account.unlock_time = clock.unix_timestamp + duration as i64;
        stake_account.rewards_claimed = 0;
        
        // Transfer tokens to staking pool
        let cpi_accounts = Transfer {
            from: ctx.accounts.user_token_account.to_account_info(),
            to: ctx.accounts.staking_pool.to_account_info(),
            authority: ctx.accounts.user.to_account_info(),
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts);
        token::transfer(cpi_ctx, amount)?;
        
        emit!(TokensStaked {
            user: ctx.accounts.user.key(),
            amount,
            duration,
            unlock_time: stake_account.unlock_time,
        });
        
        Ok(())
    }

    // Claim staking rewards
    pub fn claim_rewards(ctx: Context<ClaimRewards>) -> Result<()> {
        let stake_account = &mut ctx.accounts.stake_account;
        let clock = Clock::get()?;
        
        require!(clock.unix_timestamp >= stake_account.unlock_time, ErrorCode::StakeNotUnlocked);
        
        // Calculate rewards (1% daily)
        let staking_duration = clock.unix_timestamp - stake_account.staked_at;
        let daily_rewards = stake_account.amount / 100; // 1% daily
        let total_rewards = (daily_rewards * staking_duration as u64) / 86400;
        let claimable_rewards = total_rewards - stake_account.rewards_claimed;
        
        require!(claimable_rewards > 0, ErrorCode::NoRewardsAvailable);
        
        stake_account.rewards_claimed += claimable_rewards;
        
        // Transfer rewards to user
        let cpi_accounts = Transfer {
            from: ctx.accounts.staking_pool.to_account_info(),
            to: ctx.accounts.user_token_account.to_account_info(),
            authority: ctx.accounts.staking_authority.to_account_info(),
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        let cpi_ctx = CpiContext::new_with_signer(cpi_program, cpi_accounts, &[&ctx.accounts.staking_authority_seeds]);
        token::transfer(cpi_ctx, claimable_rewards)?;
        
        emit!(RewardsClaimed {
            user: ctx.accounts.user.key(),
            amount: claimable_rewards,
            total_claimed: stake_account.rewards_claimed,
        });
        
        Ok(())
    }

    // Pay for audit with SECURIZZ tokens
    pub fn pay_for_audit(
        ctx: Context<PayForAudit>,
        audit_fee: u64,
    ) -> Result<()> {
        require!(audit_fee > 0, ErrorCode::InvalidAmount);
        
        // Transfer payment to treasury
        let cpi_accounts = Transfer {
            from: ctx.accounts.user_token_account.to_account_info(),
            to: ctx.accounts.treasury.to_account_info(),
            authority: ctx.accounts.user.to_account_info(),
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts);
        token::transfer(cpi_ctx, audit_fee)?;
        
        emit!(AuditPaid {
            user: ctx.accounts.user.key(),
            amount: audit_fee,
            contract_hash: ctx.accounts.audit_proof.contract_hash,
        });
        
        Ok(())
    }

    // Governance voting with staked tokens
    pub fn vote_on_proposal(
        ctx: Context<VoteOnProposal>,
        proposal_id: u64,
        vote_weight: u64,
        support: bool,
    ) -> Result<()> {
        let vote_account = &mut ctx.accounts.vote_account;
        let stake_account = &ctx.accounts.stake_account;
        
        require!(stake_account.amount >= vote_weight, ErrorCode::InsufficientStake);
        require!(vote_weight > 0, ErrorCode::InvalidVoteWeight);
        
        vote_account.proposal_id = proposal_id;
        vote_account.voter = ctx.accounts.voter.key();
        vote_account.vote_weight = vote_weight;
        vote_account.support = support;
        vote_account.voted_at = Clock::get()?.unix_timestamp;
        
        emit!(VoteCast {
            proposal_id,
            voter: ctx.accounts.voter.key(),
            vote_weight,
            support,
        });
        
        Ok(())
    }
}

#[derive(Accounts)]
pub struct InitializeToken<'info> {
    #[account(
        init,
        payer = authority,
        mint::decimals = 9,
        mint::authority = authority,
    )]
    pub mint: Account<'info, Mint>,
    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
    pub token_program: Program<'info, Token>,
    pub rent: Sysvar<'info, Rent>,
}

#[derive(Accounts)]
pub struct StakeTokens<'info> {
    #[account(
        init,
        payer = user,
        space = 8 + StakeAccount::INIT_SPACE,
        seeds = [b"stake", user.key().as_ref()],
        bump
    )]
    pub stake_account: Account<'info, StakeAccount>,
    #[account(mut)]
    pub user_token_account: Account<'info, TokenAccount>,
    #[account(mut)]
    pub staking_pool: Account<'info, TokenAccount>,
    #[account(mut)]
    pub user: Signer<'info>,
    pub token_program: Program<'info, Token>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct ClaimRewards<'info> {
    #[account(
        mut,
        seeds = [b"stake", user.key().as_ref()],
        bump
    )]
    pub stake_account: Account<'info, StakeAccount>,
    #[account(mut)]
    pub user_token_account: Account<'info, TokenAccount>,
    #[account(mut)]
    pub staking_pool: Account<'info, TokenAccount>,
    /// CHECK: This is the staking authority PDA
    #[account(
        seeds = [b"staking_authority"],
        bump
    )]
    pub staking_authority: UncheckedAccount<'info>,
    pub user: Signer<'info>,
    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
pub struct PayForAudit<'info> {
    #[account(mut)]
    pub audit_proof: Account<'info, AuditProof>,
    #[account(mut)]
    pub user_token_account: Account<'info, TokenAccount>,
    #[account(mut)]
    pub treasury: Account<'info, TokenAccount>,
    pub user: Signer<'info>,
    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
pub struct VoteOnProposal<'info> {
    #[account(
        init,
        payer = voter,
        space = 8 + VoteAccount::INIT_SPACE,
        seeds = [b"vote", proposal_id.to_le_bytes().as_ref(), voter.key().as_ref()],
        bump
    )]
    pub vote_account: Account<'info, VoteAccount>,
    #[account(
        seeds = [b"stake", voter.key().as_ref()],
        bump
    )]
    pub stake_account: Account<'info, StakeAccount>,
    #[account(mut)]
    pub voter: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[account]
pub struct StakeAccount {
    pub user: Pubkey,
    pub amount: u64,
    pub duration: u64,
    pub staked_at: i64,
    pub unlock_time: i64,
    pub rewards_claimed: u64,
}

#[account]
pub struct VoteAccount {
    pub proposal_id: u64,
    pub voter: Pubkey,
    pub vote_weight: u64,
    pub support: bool,
    pub voted_at: i64,
}

#[event]
pub struct TokensStaked {
    pub user: Pubkey,
    pub amount: u64,
    pub duration: u64,
    pub unlock_time: i64,
}

#[event]
pub struct RewardsClaimed {
    pub user: Pubkey,
    pub amount: u64,
    pub total_claimed: u64,
}

#[event]
pub struct AuditPaid {
    pub user: Pubkey,
    pub amount: u64,
    pub contract_hash: [u8; 32],
}

#[event]
pub struct VoteCast {
    pub proposal_id: u64,
    pub voter: Pubkey,
    pub vote_weight: u64,
    pub support: bool,
}

#[error_code]
pub enum ErrorCode {
    #[msg("Invalid amount")]
    InvalidAmount,
    #[msg("Invalid duration")]
    InvalidDuration,
    #[msg("Stake not unlocked")]
    StakeNotUnlocked,
    #[msg("No rewards available")]
    NoRewardsAvailable,
    #[msg("Insufficient stake")]
    InsufficientStake,
    #[msg("Invalid vote weight")]
    InvalidVoteWeight,
}
