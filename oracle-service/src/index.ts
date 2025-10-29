import { Connection, PublicKey, Keypair } from '@solana/web3.js';
import { SwitchboardProgram } from '@switchboard-xyz/solana.js';
import axios from 'axios';
import * as dotenv from 'dotenv';
import bs58 from 'bs58';

dotenv.config();

interface AnalysisRequest {
  contract_hash: string;
  report_hash: string;
  ipfs_cid: string;
  risk_score: number;
}

interface OracleConfig {
  rpcUrl: string;
  programId: string;
  switchboardQueue: string;
  backendUrl: string;
  walletPath?: string;
}

class SecuRizzOracle {
  private connection: Connection;
  private programId: PublicKey;
  private switchboardProgram: SwitchboardProgram;
  private backendUrl: string;
  private isRunning: boolean = false;

  constructor(config: OracleConfig) {
    this.connection = new Connection(config.rpcUrl, 'confirmed');
    this.programId = new PublicKey(config.programId);
    this.backendUrl = config.backendUrl;
    
    this.switchboardProgram = new SwitchboardProgram(
      this.connection,
      new PublicKey(config.switchboardQueue)
    );
  }

  async start(): Promise<void> {
    console.log('Starting SecuRizz Oracle...');
    this.isRunning = true;

    const pollInterval = parseInt(process.env.ORACLE_POLL_INTERVAL || '30000');
    setInterval(async () => {
      if (this.isRunning) {
        await this.processAnalysisRequests();
      }
    }, pollInterval);

    // Integrity verification every 5 minutes
    const integrityInterval = 5 * 60 * 1000; // 5 minutes
    setInterval(async () => {
      if (this.isRunning) {
        await this.verifyProofIntegrity();
      }
    }, integrityInterval);

    console.log('Oracle started successfully');
  }

  async stop(): Promise<void> {
    console.log('Stopping SecuRizz Oracle...');
    this.isRunning = false;
  }

  private async processAnalysisRequests(): Promise<void> {
    try {
      const response = await axios.get(`${this.backendUrl}/reports`);
      const reports = response.data;

      for (const report of reports) {
        if (report.ipfs_cid && !report.on_chain_submitted) {
          await this.submitProofToChain(report);
        }
      }
    } catch (error) {
      console.error('Error processing analysis requests:', error);
    }
  }

  private async verifyProofIntegrity(): Promise<void> {
    try {
      console.log('Verifying proof integrity...');
      
      // Get all submitted proofs
      const proofs = await this.getSubmittedProofs();
      
      for (const proof of proofs) {
        try {
          // Re-fetch IPFS content
          const ipfsContent = await this.fetchIpfsContent(proof.ipfs_cid);
          
          if (ipfsContent) {
            // Calculate SHA256 hash
            const currentHash = this.calculateSha256(JSON.stringify(ipfsContent));
            
            // Compare with stored hash
            if (currentHash !== proof.report_hash) {
              console.warn(`Hash mismatch detected for proof ${proof.contract_hash}`);
              await this.emitIntegrityWarning(proof);
            } else {
              console.log(`Integrity verified for proof ${proof.contract_hash}`);
            }
          }
        } catch (error) {
          console.error(`Failed to verify proof ${proof.contract_hash}:`, error);
        }
      }
    } catch (error) {
      console.error('Error in proof integrity verification:', error);
    }
  }

  private async fetchIpfsContent(ipfsCid: string): Promise<any> {
    try {
      const response = await axios.get(`https://gateway.pinata.cloud/ipfs/${ipfsCid}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch IPFS content for ${ipfsCid}:`, error);
      return null;
    }
  }

  private calculateSha256(content: string): string {
    const crypto = require('crypto');
    return crypto.createHash('sha256').update(content).digest('hex');
  }

  private async emitIntegrityWarning(proof: any): Promise<void> {
    try {
      // Emit AuditVerified event with integrity warning
      const instruction = await this.createIntegrityWarningInstruction(proof);
      const signature = await this.connection.sendTransaction(instruction, []);
      await this.connection.confirmTransaction(signature);
      
      console.log(`Integrity warning emitted for ${proof.contract_hash}: ${signature}`);
    } catch (error) {
      console.error('Failed to emit integrity warning:', error);
    }
  }

  private async createIntegrityWarningInstruction(proof: any) {
    // Create instruction for integrity warning
    return {
      programId: this.programId,
      keys: [
        { pubkey: new PublicKey('11111111111111111111111111111111'), isSigner: false, isWritable: true },
        { pubkey: new PublicKey('11111111111111111111111111111111'), isSigner: true, isWritable: false },
      ],
      data: Buffer.from([]),
    };
  }

  private async getSubmittedProofs(): Promise<any[]> {
    // This would query the Solana program for all submitted proofs
    // For now, return empty array
    return [];
  }

  private async submitProofToChain(report: any): Promise<void> {
    try {
      console.log(`Submitting proof for contract ${report.contract_hash}...`);

      const contractHash = this.hexToByteArray(report.contract_hash);
      const reportHash = this.hexToByteArray(report.report_hash);

      const riskScore = Math.floor(report.risk_score * 10000);

      const instruction = await this.createSubmitProofInstruction(
        contractHash,
        reportHash,
        report.ipfs_cid,
        riskScore
      );

      const signature = await this.connection.sendTransaction(instruction, []);
      await this.connection.confirmTransaction(signature);

      console.log(`Proof submitted successfully: ${signature}`);

      await this.markAsSubmitted(report.id, signature);

    } catch (error) {
      console.error(`Failed to submit proof for ${report.contract_hash}:`, error);
    }
  }

  private async createSubmitProofInstruction(
    contractHash: number[],
    reportHash: number[],
    ipfsCid: string,
    riskScore: number
  ) {
    const instruction = {
      programId: this.programId,
      keys: [
        { pubkey: new PublicKey('11111111111111111111111111111111'), isSigner: false, isWritable: true },
        { pubkey: new PublicKey('11111111111111111111111111111111'), isSigner: true, isWritable: false },
      ],
      data: Buffer.from([]),
    };

    return instruction;
  }

  private hexToByteArray(hex: string): number[] {
    const bytes = [];
    for (let i = 0; i < hex.length; i += 2) {
      bytes.push(parseInt(hex.substr(i, 2), 16));
    }
    return bytes;
  }

  private async markAsSubmitted(reportId: number, txSignature: string): Promise<void> {
    try {
      await axios.post(`${this.backendUrl}/reports/${reportId}/mark-submitted`, {
        tx_signature: txSignature
      });
    } catch (error) {
      console.error('Failed to mark report as submitted:', error);
    }
  }

  async verifyProof(contractHash: string): Promise<any> {
    try {
      const proofAccount = await this.getProofAccount(contractHash);
      
      if (proofAccount) {
        console.log('Proof found on-chain:', proofAccount);
        return proofAccount;
      } else {
        console.log('No proof found for contract:', contractHash);
        return null;
      }
    } catch (error) {
      console.error('Error verifying proof:', error);
      return null;
    }
  }

  private async getProofAccount(contractHash: string): Promise<any> {
    return null;
  }
}

async function main() {
  const config: OracleConfig = {
    rpcUrl: process.env.SOLANA_CLUSTER || 'https://api.devnet.solana.com',
    programId: process.env.SOLANA_PROGRAM_ID || 'ReplaceWithDeployedProgramId',
    switchboardQueue: process.env.SWITCHBOARD_QUEUE || 'devnet-default',
    backendUrl: process.env.BACKEND_URL || 'http://localhost:8000',
    walletPath: process.env.SOLANA_WALLET_PATH || '~/.config/solana/id.json',
  };

  const oracle = new SecuRizzOracle(config);

  process.on('SIGINT', async () => {
    console.log('Received SIGINT, shutting down gracefully...');
    await oracle.stop();
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    console.log('Received SIGTERM, shutting down gracefully...');
    await oracle.stop();
    process.exit(0);
  });

  await oracle.start();
}

if (require.main === module) {
  main().catch(console.error);
}

export { SecuRizzOracle };
