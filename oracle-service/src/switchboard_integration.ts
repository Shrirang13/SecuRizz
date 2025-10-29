import { SwitchboardProgram } from "@switchboard-xyz/solana.js";
import { Connection, PublicKey, Keypair } from "@solana/web3.js";
import { OracleJob } from "@switchboard-xyz/solana.js";

export class SecuRizzOracle {
  private program: SwitchboardProgram;
  private connection: Connection;
  private oracleKey: PublicKey;

  constructor(
    connection: Connection,
    program: SwitchboardProgram,
    oracleKey: PublicKey
  ) {
    this.connection = connection;
    this.program = program;
    this.oracleKey = oracleKey;
  }

  async submitAuditProof(
    contractHash: string,
    reportHash: string,
    ipfsCid: string,
    riskScore: number,
    auditScore: number,
    contractAddress: PublicKey
  ): Promise<string> {
    try {
      // Create oracle job for audit verification
      const job = new OracleJob({
        tasks: [
          {
            httpTask: {
              url: `https://api.securizz.com/verify/${contractHash}`,
              method: "GET",
              headers: {
                "Content-Type": "application/json",
              },
            },
          },
          {
            jsonParseTask: {
              path: "$.verified",
            },
          },
        ],
      });

      // Submit to Switchboard
      const result = await this.program.oracleQueue.addJob({
        name: `SecuRizz Audit ${contractHash.slice(0, 8)}`,
        metadata: {
          contractHash,
          reportHash,
          ipfsCid,
          riskScore,
          auditScore,
          contractAddress: contractAddress.toString(),
        },
        job: job,
        authority: this.oracleKey,
      });

      console.log(`✅ Oracle job submitted: ${result.pubkey.toString()}`);
      return result.pubkey.toString();
    } catch (error) {
      console.error("❌ Oracle submission failed:", error);
      throw error;
    }
  }

  async verifyAuditIntegrity(
    contractHash: string,
    expectedIpfsHash: string
  ): Promise<boolean> {
    try {
      // Create verification job
      const verificationJob = new OracleJob({
        tasks: [
          {
            httpTask: {
              url: `https://gateway.pinata.cloud/ipfs/${expectedIpfsHash}`,
              method: "GET",
            },
          },
          {
            jsonParseTask: {
              path: "$.contract_hash",
            },
          },
          {
            conditionalTask: {
              if: {
                equals: [contractHash],
              },
              then: {
                valueTask: {
                  value: true,
                },
              },
              else: {
                valueTask: {
                  value: false,
                },
              },
            },
          },
        ],
      });

      const result = await this.program.oracleQueue.addJob({
        name: `SecuRizz Verification ${contractHash.slice(0, 8)}`,
        metadata: {
          contractHash,
          expectedIpfsHash,
        },
        job: verificationJob,
        authority: this.oracleKey,
      });

      return true;
    } catch (error) {
      console.error("❌ Verification failed:", error);
      return false;
    }
  }

  async getAuditData(contractHash: string): Promise<any> {
    try {
      // Query oracle for audit data
      const job = new OracleJob({
        tasks: [
          {
            httpTask: {
              url: `https://api.securizz.com/audit/${contractHash}`,
              method: "GET",
            },
          },
          {
            jsonParseTask: {
              path: "$",
            },
          },
        ],
      });

      const result = await this.program.oracleQueue.addJob({
        name: `SecuRizz Query ${contractHash.slice(0, 8)}`,
        job: job,
        authority: this.oracleKey,
      });

      return result;
    } catch (error) {
      console.error("❌ Data retrieval failed:", error);
      return null;
    }
  }

  async createAuditAggregator(): Promise<PublicKey> {
    try {
      // Create aggregator for audit statistics
      const aggregator = await this.program.aggregatorAccount.create({
        name: "SecuRizz Audit Statistics",
        metadata: {
          description: "Aggregated audit statistics for SecuRizz platform",
          tags: ["security", "audit", "blockchain"],
        },
        batchSize: 1,
        minOracleResults: 1,
        minJobResults: 1,
        authority: this.oracleKey,
      });

      console.log(`✅ Aggregator created: ${aggregator.pubkey.toString()}`);
      return aggregator.pubkey;
    } catch (error) {
      console.error("❌ Aggregator creation failed:", error);
      throw error;
    }
  }

  async updateAuditMetrics(
    totalAudits: number,
    averageRiskScore: number,
    vulnerabilityCounts: Record<string, number>
  ): Promise<string> {
    try {
      const metricsJob = new OracleJob({
        tasks: [
          {
            valueTask: {
              value: {
                totalAudits,
                averageRiskScore,
                vulnerabilityCounts,
                timestamp: Date.now(),
              },
            },
          },
        ],
      });

      const result = await this.program.oracleQueue.addJob({
        name: "SecuRizz Metrics Update",
        metadata: {
          totalAudits,
          averageRiskScore,
          vulnerabilityCounts,
        },
        job: metricsJob,
        authority: this.oracleKey,
      });

      return result.pubkey.toString();
    } catch (error) {
      console.error("❌ Metrics update failed:", error);
      throw error;
    }
  }
}

export default SecuRizzOracle;
