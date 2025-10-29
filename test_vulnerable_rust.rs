// VULNERABLE RUST CONTRACT - Test Case for SecuRizz AI
// This contract contains multiple vulnerabilities for testing

use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount, Transfer, Mint, MintTo};
use std::collections::HashMap;

declare_id!("TestVulnerableContract111111111111111111111111111");

#[program]
pub mod vulnerable_contract {
    use super::*;

    // VULNERABILITY 1: Unsafe code without proper validation
    pub fn unsafe_transfer(ctx: Context<UnsafeTransfer>, amount: u64) -> Result<()> {
        // VULNERABILITY: No amount validation
        let cpi_accounts = Transfer {
            from: ctx.accounts.from.to_account_info(),
            to: ctx.accounts.to.to_account_info(),
            authority: ctx.accounts.authority.to_account_info(),
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts);
        
        // VULNERABILITY: Direct transfer without checks
        token::transfer(cpi_ctx, amount)?;
        Ok(())
    }

    // VULNERABILITY 2: Integer overflow/underflow
    pub fn vulnerable_arithmetic(ctx: Context<VulnerableArithmetic>, a: u64, b: u64) -> Result<()> {
        // VULNERABILITY: No overflow protection
        let result = a + b; // Can overflow
        let difference = a - b; // Can underflow
        
        // VULNERABILITY: Unsafe arithmetic operations
        let multiplication = a * b; // Can overflow
        let division = a / b; // Can panic on division by zero
        
        msg!("Result: {}, Difference: {}, Multiplication: {}, Division: {}", 
             result, difference, multiplication, division);
        
        Ok(())
    }

    // VULNERABILITY 3: Panic handling issues
    pub fn panic_prone_function(ctx: Context<PanicProne>, value: u64) -> Result<()> {
        // VULNERABILITY: Direct unwrap without error handling
        let result = Some(value).unwrap();
        
        // VULNERABILITY: Array access without bounds checking
        let array = [1, 2, 3, 4, 5];
        let element = array[value as usize]; // Can panic if value > 4
        
        // VULNERABILITY: Division by zero potential
        let division_result = 100 / value; // Will panic if value is 0
        
        msg!("Result: {}, Element: {}, Division: {}", result, element, division_result);
        Ok(())
    }

    // VULNERABILITY 4: Memory leak potential
    pub fn memory_leak_function(ctx: Context<MemoryLeak>) -> Result<()> {
        // VULNERABILITY: Unbounded vector growth
        let mut data = Vec::new();
        for i in 0..1000000 {
            data.push(i); // Can cause memory exhaustion
        }
        
        // VULNERABILITY: String concatenation in loop
        let mut result = String::new();
        for i in 0..10000 {
            result.push_str(&format!("iteration_{}", i)); // Memory leak
        }
        
        msg!("Data length: {}, Result length: {}", data.len(), result.len());
        Ok(())
    }

    // VULNERABILITY 5: Use after free (simulated)
    pub fn use_after_free(ctx: Context<UseAfterFree>) -> Result<()> {
        let mut data = Some(Box::new(42));
        let reference = data.as_ref().unwrap();
        
        // VULNERABILITY: Taking ownership after reference
        let owned = data.take(); // data is now None
        let value = reference.as_ref(); // Use after free!
        
        msg!("Value: {}", value);
        Ok(())
    }

    // VULNERABILITY 6: Buffer overflow simulation
    pub fn buffer_overflow(ctx: Context<BufferOverflow>, input: Vec<u8>) -> Result<()> {
        // VULNERABILITY: No bounds checking
        let mut buffer = [0u8; 10];
        for (i, byte) in input.iter().enumerate() {
            buffer[i] = *byte; // Can overflow buffer
        }
        
        msg!("Buffer: {:?}", buffer);
        Ok(())
    }

    // VULNERABILITY 7: Null pointer dereference
    pub fn null_pointer_deref(ctx: Context<NullPointer>) -> Result<()> {
        // VULNERABILITY: Potential null pointer
        let option: Option<u64> = None;
        let value = option.unwrap(); // Will panic
        
        msg!("Value: {}", value);
        Ok(())
    }

    // VULNERABILITY 8: Double free simulation
    pub fn double_free(ctx: Context<DoubleFree>) -> Result<()> {
        let mut data = Box::new(42);
        let ptr = Box::into_raw(data);
        
        // VULNERABILITY: Double free
        unsafe {
            Box::from_raw(ptr);
            Box::from_raw(ptr); // Double free!
        }
        
        Ok(())
    }

    // VULNERABILITY 9: Format string vulnerability
    pub fn format_string_vuln(ctx: Context<FormatString>, user_input: String) -> Result<()> {
        // VULNERABILITY: Direct format without validation
        msg!("User input: {}", user_input); // Could be exploited
        
        // VULNERABILITY: Unsafe string formatting
        let formatted = format!("Data: {}", user_input);
        msg!("Formatted: {}", formatted);
        
        Ok(())
    }

    // VULNERABILITY 10: Race condition
    pub fn race_condition(ctx: Context<RaceCondition>, amount: u64) -> Result<()> {
        // VULNERABILITY: Non-atomic operations
        let mut balance = 1000u64;
        balance += amount; // Not atomic
        balance -= amount; // Race condition potential
        
        msg!("Balance: {}", balance);
        Ok(())
    }

    // VULNERABILITY 11: Deadlock potential
    pub fn deadlock_function(ctx: Context<Deadlock>) -> Result<()> {
        // VULNERABILITY: Potential deadlock
        let mutex1 = std::sync::Mutex::new(0);
        let mutex2 = std::sync::Mutex::new(0);
        
        // VULNERABILITY: Lock order not consistent
        let _lock1 = mutex1.lock().unwrap();
        let _lock2 = mutex2.lock().unwrap();
        
        Ok(())
    }

    // VULNERABILITY 12: Resource exhaustion
    pub fn resource_exhaustion(ctx: Context<ResourceExhaustion>) -> Result<()> {
        // VULNERABILITY: Infinite loop potential
        let mut counter = 0;
        loop {
            counter += 1;
            if counter > 1000000 {
                break; // But could be infinite
            }
        }
        
        msg!("Counter: {}", counter);
        Ok(())
    }

    // VULNERABILITY 13: Stack overflow
    pub fn stack_overflow(ctx: Context<StackOverflow>, depth: u32) -> Result<()> {
        // VULNERABILITY: Recursive function without limit
        if depth > 0 {
            return stack_overflow(ctx, depth - 1);
        }
        
        Ok(())
    }

    // VULNERABILITY 14: Account validation issues
    pub fn account_validation_issues(ctx: Context<AccountValidation>) -> Result<()> {
        // VULNERABILITY: No proper account validation
        let account = &ctx.accounts.account;
        
        // VULNERABILITY: Missing owner checks
        // VULNERABILITY: No authority validation
        // VULNERABILITY: No rent exemption checks
        
        msg!("Account: {}", account.key());
        Ok(())
    }

    // VULNERABILITY 15: Program derivation issues
    pub fn program_derivation_issues(ctx: Context<ProgramDerivation>) -> Result<()> {
        // VULNERABILITY: Unsafe program derivation
        let seeds = &[b"vulnerable", b"seeds"];
        let (pda, bump) = Pubkey::find_program_address(seeds, &crate::ID);
        
        // VULNERABILITY: No bump validation
        // VULNERABILITY: No seed validation
        
        msg!("PDA: {}, Bump: {}", pda, bump);
        Ok(())
    }

    // VULNERABILITY 16: Seed validation issues
    pub fn seed_validation_issues(ctx: Context<SeedValidation>, user_seed: String) -> Result<()> {
        // VULNERABILITY: No seed validation
        let seeds = &[b"user", user_seed.as_bytes()];
        let (pda, _) = Pubkey::find_program_address(seeds, &crate::ID);
        
        // VULNERABILITY: User-controlled seeds
        msg!("PDA: {}", pda);
        Ok(())
    }

    // VULNERABILITY 17: Signature verification issues
    pub fn signature_verification_issues(ctx: Context<SignatureVerification>) -> Result<()> {
        // VULNERABILITY: No signature verification
        let authority = &ctx.accounts.authority;
        
        // VULNERABILITY: Missing is_signer check
        // VULNERABILITY: No signature validation
        
        msg!("Authority: {}", authority.key());
        Ok(())
    }

    // VULNERABILITY 18: Instruction validation issues
    pub fn instruction_validation_issues(ctx: Context<InstructionValidation>, data: Vec<u8>) -> Result<()> {
        // VULNERABILITY: No instruction validation
        // VULNERABILITY: Direct data processing
        msg!("Data length: {}", data.len());
        Ok(())
    }

    // VULNERABILITY 19: Data validation issues
    pub fn data_validation_issues(ctx: Context<DataValidation>, user_data: String) -> Result<()> {
        // VULNERABILITY: No data validation
        // VULNERABILITY: Direct user input processing
        msg!("User data: {}", user_data);
        Ok(())
    }

    // VULNERABILITY 20: Authority validation issues
    pub fn authority_validation_issues(ctx: Context<AuthorityValidation>) -> Result<()> {
        // VULNERABILITY: No authority validation
        let authority = &ctx.accounts.authority;
        
        // VULNERABILITY: Missing authority checks
        // VULNERABILITY: No permission validation
        
        msg!("Authority: {}", authority.key());
        Ok(())
    }

    // VULNERABILITY 21: Rent exemption issues
    pub fn rent_exemption_issues(ctx: Context<RentExemption>) -> Result<()> {
        // VULNERABILITY: No rent exemption checks
        let account = &ctx.accounts.account;
        
        // VULNERABILITY: Missing rent exemption validation
        // VULNERABILITY: No lamports checks
        
        msg!("Account: {}", account.key());
        Ok(())
    }

    // VULNERABILITY 22: Account lamports issues
    pub fn account_lamports_issues(ctx: Context<AccountLamports>) -> Result<()> {
        // VULNERABILITY: No lamports validation
        let account = &ctx.accounts.account;
        
        // VULNERABILITY: Missing lamports checks
        // VULNERABILITY: No balance validation
        
        msg!("Account: {}", account.key());
        Ok(())
    }

    // VULNERABILITY 23: Program ownership issues
    pub fn program_ownership_issues(ctx: Context<ProgramOwnership>) -> Result<()> {
        // VULNERABILITY: No ownership validation
        let account = &ctx.accounts.account;
        
        // VULNERABILITY: Missing ownership checks
        // VULNERABILITY: No program validation
        
        msg!("Account: {}", account.key());
        Ok(())
    }

    // VULNERABILITY 24: Cross program invocation issues
    pub fn cross_program_invocation_issues(ctx: Context<CrossProgramInvocation>) -> Result<()> {
        // VULNERABILITY: Unsafe CPI
        let cpi_program = ctx.accounts.program.to_account_info();
        
        // VULNERABILITY: No program validation
        // VULNERABILITY: Unsafe CPI calls
        
        msg!("Program: {}", cpi_program.key());
        Ok(())
    }

    // VULNERABILITY 25: Syscall validation issues
    pub fn syscall_validation_issues(ctx: Context<SyscallValidation>) -> Result<()> {
        // VULNERABILITY: No syscall validation
        // VULNERABILITY: Unsafe syscalls
        
        msg!("Syscall validation missing");
        Ok(())
    }

    // VULNERABILITY 26: Token program issues
    pub fn token_program_issues(ctx: Context<TokenProgram>) -> Result<()> {
        // VULNERABILITY: No token program validation
        let token_program = &ctx.accounts.token_program;
        
        // VULNERABILITY: Missing token program checks
        // VULNERABILITY: No program validation
        
        msg!("Token program: {}", token_program.key());
        Ok(())
    }

    // VULNERABILITY 27: Associated token issues
    pub fn associated_token_issues(ctx: Context<AssociatedToken>) -> Result<()> {
        // VULNERABILITY: No associated token validation
        let associated_token = &ctx.accounts.associated_token;
        
        // VULNERABILITY: Missing associated token checks
        // VULNERABILITY: No derivation validation
        
        msg!("Associated token: {}", associated_token.key());
        Ok(())
    }

    // VULNERABILITY 28: PDA validation issues
    pub fn pda_validation_issues(ctx: Context<PDAValidation>) -> Result<()> {
        // VULNERABILITY: No PDA validation
        let pda = &ctx.accounts.pda;
        
        // VULNERABILITY: Missing PDA checks
        // VULNERABILITY: No derivation validation
        
        msg!("PDA: {}", pda.key());
        Ok(())
    }
}

// Account structures for vulnerabilities
#[derive(Accounts)]
pub struct UnsafeTransfer<'info> {
    #[account(mut)]
    pub from: Account<'info, TokenAccount>,
    #[account(mut)]
    pub to: Account<'info, TokenAccount>,
    pub authority: Signer<'info>,
    pub token_program: Program<'info, Token>,
}

#[derive(Accounts)]
pub struct VulnerableArithmetic<'info> {
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct PanicProne<'info> {
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct MemoryLeak<'info> {
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct UseAfterFree<'info> {
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct BufferOverflow<'info> {
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct NullPointer<'info> {
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct DoubleFree<'info> {
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct FormatString<'info> {
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct RaceCondition<'info> {
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct Deadlock<'info> {
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct ResourceExhaustion<'info> {
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct StackOverflow<'info> {
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct AccountValidation<'info> {
    /// CHECK: No validation
    pub account: UncheckedAccount<'info>,
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct ProgramDerivation<'info> {
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct SeedValidation<'info> {
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct SignatureVerification<'info> {
    /// CHECK: No signature validation
    pub authority: UncheckedAccount<'info>,
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct InstructionValidation<'info> {
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct DataValidation<'info> {
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct AuthorityValidation<'info> {
    /// CHECK: No authority validation
    pub authority: UncheckedAccount<'info>,
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct RentExemption<'info> {
    /// CHECK: No rent exemption validation
    pub account: UncheckedAccount<'info>,
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct AccountLamports<'info> {
    /// CHECK: No lamports validation
    pub account: UncheckedAccount<'info>,
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct ProgramOwnership<'info> {
    /// CHECK: No ownership validation
    pub account: UncheckedAccount<'info>,
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct CrossProgramInvocation<'info> {
    /// CHECK: No program validation
    pub program: UncheckedAccount<'info>,
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct SyscallValidation<'info> {
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct TokenProgram<'info> {
    /// CHECK: No token program validation
    pub token_program: UncheckedAccount<'info>,
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct AssociatedToken<'info> {
    /// CHECK: No associated token validation
    pub associated_token: UncheckedAccount<'info>,
    pub user: Signer<'info>,
}

#[derive(Accounts)]
pub struct PDAValidation<'info> {
    /// CHECK: No PDA validation
    pub pda: UncheckedAccount<'info>,
    pub user: Signer<'info>,
}
