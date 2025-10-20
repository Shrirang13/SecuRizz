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
