import { useState } from 'react'
import { useWallet } from '@solana/wallet-adapter-react'
import Head from 'next/head'
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui'
import toast from 'react-hot-toast'
import axios from 'axios'
import VulnerabilityCard from '../components/VulnerabilityCard'
import RiskGauge from '../components/RiskGauge'
import ProofVerifier from '../components/ProofVerifier'

interface Vulnerability {
  vulnerability: string
  probability: number
}

interface AnalysisResult {
  contract_hash: string
  report_hash: string
  ipfs_cid?: string
  risk_score: number
  vulnerabilities: Vulnerability[]
  mitigation_strategies: Record<string, string>
  created_at: string
}

export default function Home() {
  const { connected } = useWallet()
  const [sourceCode, setSourceCode] = useState('')
  const [contractName, setContractName] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [activeTab, setActiveTab] = useState<'upload' | 'reports' | 'verify'>('upload')

  const handleAnalyze = async () => {
    if (!sourceCode.trim()) {
      toast.error('Please enter contract source code')
      return
    }

    setIsAnalyzing(true)
    try {
      const response = await axios.post(`${process.env.NEXT_PUBLIC_BACKEND_URL}/analyze`, {
        source_code: sourceCode,
        contract_name: contractName || undefined
      })
      
      setAnalysisResult(response.data)
      toast.success('Analysis completed successfully!')
    } catch (error) {
      console.error('Analysis failed:', error)
      toast.error('Analysis failed. Please try again.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const getSeverityClass = (probability: number) => {
    if (probability >= 0.8) return 'critical'
    if (probability >= 0.6) return 'high'
    if (probability >= 0.4) return 'medium'
    return 'low'
  }

  return (
    <>
      <Head>
        <title>SecuRizz - Smart Contract Vulnerability Auditor</title>
        <meta name="description" content="ML-powered smart contract vulnerability auditor with on-chain proofs" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold text-gray-900">SecuRizz</h1>
                <span className="ml-2 text-sm text-gray-500">Smart Contract Auditor</span>
              </div>
              <WalletMultiButton />
            </div>
          </div>
        </header>

        {/* Navigation Tabs */}
        <div className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <nav className="flex space-x-8">
              {[
                { id: 'upload', label: 'Upload & Analyze' },
                { id: 'reports', label: 'View Reports' },
                { id: 'verify', label: 'Verify Proofs' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {activeTab === 'upload' && (
            <div className="px-4 py-6 sm:px-0">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Upload Form */}
                <div className="card">
                  <h2 className="text-xl font-semibold mb-4">Upload Smart Contract</h2>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Contract Name (Optional)
                      </label>
                      <input
                        type="text"
                        value={contractName}
                        onChange={(e) => setContractName(e.target.value)}
                        className="input-field"
                        placeholder="MyContract.sol"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Source Code
                      </label>
                      <textarea
                        value={sourceCode}
                        onChange={(e) => setSourceCode(e.target.value)}
                        className="input-field h-64 resize-none"
                        placeholder="pragma solidity ^0.8.0;&#10;&#10;contract MyContract {&#10;    // Your contract code here&#10;}"
                      />
                    </div>
                    
                    <button
                      onClick={handleAnalyze}
                      disabled={isAnalyzing || !sourceCode.trim()}
                      className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isAnalyzing ? 'Analyzing...' : 'Analyze Contract'}
                    </button>
                  </div>
                </div>

                {/* Analysis Results */}
                <div className="card">
                  <h2 className="text-xl font-semibold mb-4">Analysis Results</h2>
                  
                  {analysisResult ? (
                    <div className="space-y-6">
                      {/* Risk Score */}
                      <div>
                        <h3 className="text-lg font-medium mb-3">Risk Assessment</h3>
                        <RiskGauge score={analysisResult.risk_score} />
                      </div>

                      {/* Vulnerabilities */}
                      <div>
                        <h3 className="text-lg font-medium mb-3">
                          Vulnerabilities Found ({analysisResult.vulnerabilities.length})
                        </h3>
                        <div className="space-y-3">
                          {analysisResult.vulnerabilities.map((vuln, index) => (
                            <VulnerabilityCard
                              key={index}
                              vulnerability={vuln.vulnerability}
                              probability={vuln.probability}
                              severity={getSeverityClass(vuln.probability)}
                              mitigation={analysisResult.mitigation_strategies[vuln.vulnerability]}
                            />
                          ))}
                        </div>
                      </div>

                      {/* Report Info */}
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-medium mb-2">Report Information</h4>
                        <div className="text-sm space-y-1">
                          <p><span className="font-medium">Contract Hash:</span> {analysisResult.contract_hash}</p>
                          <p><span className="font-medium">Report Hash:</span> {analysisResult.report_hash}</p>
                          {analysisResult.ipfs_cid && (
                            <p><span className="font-medium">IPFS CID:</span> {analysisResult.ipfs_cid}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center text-gray-500 py-8">
                      <p>Upload a contract to see analysis results</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'reports' && (
            <div className="px-4 py-6 sm:px-0">
              <div className="card">
                <h2 className="text-xl font-semibold mb-4">Audit Reports</h2>
                <p className="text-gray-500">View all audit reports and their on-chain verification status.</p>
                {/* Reports list would be implemented here */}
              </div>
            </div>
          )}

          {activeTab === 'verify' && (
            <div className="px-4 py-6 sm:px-0">
              <ProofVerifier />
            </div>
          )}
        </main>
      </div>
    </>
  )
}
