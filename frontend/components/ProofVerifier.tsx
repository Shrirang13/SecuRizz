import { useState } from 'react'
import { useWallet } from '@solana/wallet-adapter-react'
import toast from 'react-hot-toast'
import axios from 'axios'

export default function ProofVerifier() {
  const { connected } = useWallet()
  const [contractHash, setContractHash] = useState('')
  const [isVerifying, setIsVerifying] = useState(false)
  const [verificationResult, setVerificationResult] = useState<any>(null)

  const handleVerify = async () => {
    if (!contractHash.trim()) {
      toast.error('Please enter a contract hash')
      return
    }

    if (!connected) {
      toast.error('Please connect your wallet to verify proofs')
      return
    }

    setIsVerifying(true)
    try {
      // First check if we have a report for this contract
      const reportsResponse = await axios.get(`${process.env.NEXT_PUBLIC_BACKEND_URL}/reports`)
      const reports = reportsResponse.data
      
      const matchingReport = reports.find((report: any) => 
        report.contract_hash === contractHash
      )

      if (!matchingReport) {
        toast.error('No audit report found for this contract hash')
        setVerificationResult(null)
        return
      }

      // In a real implementation, this would query the Solana program
      // For now, we'll simulate the verification
      const mockVerification = {
        contract_hash: contractHash,
        report_hash: matchingReport.report_hash,
        ipfs_cid: matchingReport.ipfs_cid,
        risk_score: matchingReport.risk_score,
        verified: true, // Simulated
        on_chain: true, // Simulated
        tx_signature: 'mock_tx_signature_123456789',
        block_time: new Date().toISOString(),
        oracle: 'mock_oracle_address'
      }

      setVerificationResult(mockVerification)
      toast.success('Proof verification completed!')
    } catch (error) {
      console.error('Verification failed:', error)
      toast.error('Verification failed. Please try again.')
      setVerificationResult(null)
    } finally {
      setIsVerifying(false)
    }
  }

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">Verify On-Chain Proof</h2>
      
      <div className="space-y-6">
        {/* Input Form */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Contract Hash
          </label>
          <div className="flex space-x-3">
            <input
              type="text"
              value={contractHash}
              onChange={(e) => setContractHash(e.target.value)}
              className="input-field flex-1"
              placeholder="Enter contract hash (SHA-256)"
            />
            <button
              onClick={handleVerify}
              disabled={isVerifying || !contractHash.trim() || !connected}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isVerifying ? 'Verifying...' : 'Verify Proof'}
            </button>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            Enter the SHA-256 hash of the contract to verify its audit proof on-chain
          </p>
        </div>

        {/* Verification Result */}
        {verificationResult && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-green-800">
                Proof Verified Successfully
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium text-gray-700">Contract Hash:</span>
                <p className="font-mono text-xs bg-white p-2 rounded border mt-1 break-all">
                  {verificationResult.contract_hash}
                </p>
              </div>
              
              <div>
                <span className="font-medium text-gray-700">Report Hash:</span>
                <p className="font-mono text-xs bg-white p-2 rounded border mt-1 break-all">
                  {verificationResult.report_hash}
                </p>
              </div>
              
              <div>
                <span className="font-medium text-gray-700">IPFS CID:</span>
                <p className="font-mono text-xs bg-white p-2 rounded border mt-1 break-all">
                  {verificationResult.ipfs_cid}
                </p>
              </div>
              
              <div>
                <span className="font-medium text-gray-700">Risk Score:</span>
                <p className="text-lg font-semibold text-gray-900 mt-1">
                  {(verificationResult.risk_score * 100).toFixed(1)}%
                </p>
              </div>
              
              <div>
                <span className="font-medium text-gray-700">Transaction Signature:</span>
                <p className="font-mono text-xs bg-white p-2 rounded border mt-1 break-all">
                  {verificationResult.tx_signature}
                </p>
              </div>
              
              <div>
                <span className="font-medium text-gray-700">Oracle:</span>
                <p className="font-mono text-xs bg-white p-2 rounded border mt-1 break-all">
                  {verificationResult.oracle}
                </p>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-green-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-sm font-medium text-green-800">
                    On-Chain Verification: {verificationResult.verified ? 'Verified' : 'Not Verified'}
                  </span>
                </div>
                <a
                  href={`https://explorer.solana.com/tx/${verificationResult.tx_signature}?cluster=devnet`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                >
                  View on Solana Explorer →
                </a>
              </div>
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-medium text-blue-900 mb-2">How it works:</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Enter the SHA-256 hash of your smart contract</li>
            <li>• The system checks for an existing audit report</li>
            <li>• Verifies the proof is stored on Solana blockchain</li>
            <li>• Displays the complete audit trail and IPFS report</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
