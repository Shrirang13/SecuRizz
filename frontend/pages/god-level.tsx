import { useState, useEffect } from 'react'
import Head from 'next/head'
import { useWallet } from '@solana/wallet-adapter-react'
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui'
import toast from 'react-hot-toast'
import axios from 'axios'

interface Vulnerability {
  vulnerability: string
  probability: number
  confidence?: number
  severity?: string
  lines?: number[]
}

interface AnalysisResult {
  contract_hash: string
  report_hash: string
  ipfs_cid?: string
  risk_score: number
  vulnerabilities: Vulnerability[]
  mitigation_strategies: Record<string, string>
  created_at: string
  ai_summary?: string
}

export default function GodLevelSecuRizz() {
  const { connected, publicKey } = useWallet()
  const [sourceCode, setSourceCode] = useState('')
  const [contractName, setContractName] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [activeTab, setActiveTab] = useState<'analyze' | 'reports' | 'governance' | 'nft' | 'staking'>('analyze')
  const [darkMode, setDarkMode] = useState(false)

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme === 'dark') {
      setDarkMode(true)
      document.documentElement.classList.add('dark')
    }
  }, [])

  const toggleDarkMode = () => {
    setDarkMode(!darkMode)
    if (!darkMode) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }

  const handleAnalyze = async () => {
    if (!sourceCode.trim()) {
      toast.error('Please enter contract source code')
      return
    }

    setIsAnalyzing(true)
    try {
      const response = await axios.post('http://localhost:8001/analyze', {
        source_code: sourceCode,
        contract_name: contractName || 'Unnamed Contract'
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

  const getSeverityColor = (probability: number) => {
    if (probability >= 0.8) return 'text-red-600 bg-red-50 border-red-200'
    if (probability >= 0.6) return 'text-orange-600 bg-orange-50 border-orange-200'
    if (probability >= 0.4) return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    return 'text-green-600 bg-green-50 border-green-200'
  }

  const getSeverityIcon = (probability: number) => {
    if (probability >= 0.8) return '🚨'
    if (probability >= 0.6) return '⚠️'
    if (probability >= 0.4) return '⚡'
    return '✅'
  }

  return (
    <>
      <Head>
        <title>SecuRizz - GOD-LEVEL Security Auditor</title>
        <meta name="description" content="AI-powered smart contract vulnerability auditor with on-chain proofs" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className={`min-h-screen transition-colors duration-300 ${darkMode ? 'dark bg-gray-900' : 'bg-gradient-to-br from-blue-50 via-white to-purple-50'}`}>
        {/* Animated Header */}
        <header className={`sticky top-0 z-50 backdrop-blur-md border-b transition-colors duration-300 ${
          darkMode ? 'bg-gray-900/80 border-gray-700' : 'bg-white/80 border-gray-200'
        }`}>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold text-sm">🔒</span>
                  </div>
                  <div>
                    <h1 className={`text-2xl font-bold transition-colors duration-300 ${
                      darkMode ? 'text-white' : 'text-gray-900'
                    }`}>SecuRizz</h1>
                    <p className={`text-xs transition-colors duration-300 ${
                      darkMode ? 'text-gray-400' : 'text-gray-500'
                    }`}>GOD-LEVEL Security Auditor</p>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <button
                  onClick={toggleDarkMode}
                  className={`p-2 rounded-lg transition-colors duration-300 ${
                    darkMode ? 'bg-gray-800 text-yellow-400 hover:bg-gray-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {darkMode ? '☀️' : '🌙'}
                </button>
                <WalletMultiButton className="!bg-gradient-to-r !from-blue-600 !to-purple-600 !rounded-lg !px-6 !py-2 !text-white !font-semibold !shadow-lg hover:!shadow-xl transition-all duration-300" />
              </div>
            </div>
          </div>
        </header>

        {/* Navigation Tabs */}
        <div className={`border-b transition-colors duration-300 ${
          darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
        }`}>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <nav className="flex space-x-8 overflow-x-auto">
              {[
                { id: 'analyze', label: '🔍 Analyze', icon: '🔍' },
                { id: 'reports', label: '📊 Reports', icon: '📊' },
                { id: 'governance', label: '🏛️ DAO', icon: '🏛️' },
                { id: 'nft', label: '🎨 NFTs', icon: '🎨' },
                { id: 'staking', label: '💰 Staking', icon: '💰' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap transition-all duration-300 ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : darkMode 
                        ? 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          {activeTab === 'analyze' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Upload Form */}
              <div className={`rounded-2xl shadow-xl p-8 transition-colors duration-300 ${
                darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
              } border`}>
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                    <span className="text-white text-lg">🔍</span>
                  </div>
                  <h2 className={`text-2xl font-bold transition-colors duration-300 ${
                    darkMode ? 'text-white' : 'text-gray-900'
                  }`}>Smart Contract Analysis</h2>
                </div>
                
                <div className="space-y-6">
                  <div>
                    <label className={`block text-sm font-medium mb-2 transition-colors duration-300 ${
                      darkMode ? 'text-gray-300' : 'text-gray-700'
                    }`}>
                      Contract Name
                    </label>
                    <input
                      type="text"
                      value={contractName}
                      onChange={(e) => setContractName(e.target.value)}
                      className={`w-full px-4 py-3 rounded-lg border transition-colors duration-300 ${
                        darkMode 
                          ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:border-blue-500' 
                          : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500 focus:border-blue-500'
                      } focus:outline-none focus:ring-2 focus:ring-blue-500/20`}
                      placeholder="MyAwesomeContract.sol"
                    />
                  </div>
                  
                  <div>
                    <label className={`block text-sm font-medium mb-2 transition-colors duration-300 ${
                      darkMode ? 'text-gray-300' : 'text-gray-700'
                    }`}>
                      Source Code
                    </label>
                    <textarea
                      value={sourceCode}
                      onChange={(e) => setSourceCode(e.target.value)}
                      className={`w-full h-80 px-4 py-3 rounded-lg border font-mono text-sm transition-colors duration-300 ${
                        darkMode 
                          ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:border-blue-500' 
                          : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500 focus:border-blue-500'
                      } focus:outline-none focus:ring-2 focus:ring-blue-500/20 resize-none`}
                      placeholder="// Paste your Rust/Solana contract code here...
use anchor_lang::prelude::*;

#[program]
pub mod my_program {
    use super::*;
    
    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        // Your code here
        Ok(())
    }
}"
                    />
                  </div>
                  
                  <button
                    onClick={handleAnalyze}
                    disabled={isAnalyzing || !sourceCode.trim()}
                    className={`w-full py-4 px-6 rounded-lg font-semibold text-white transition-all duration-300 ${
                      isAnalyzing || !sourceCode.trim()
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl'
                    }`}
                  >
                    {isAnalyzing ? (
                      <div className="flex items-center justify-center space-x-2">
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        <span>Analyzing...</span>
                      </div>
                    ) : (
                      '🚀 Analyze Contract'
                    )}
                  </button>
                </div>
              </div>

              {/* Analysis Results */}
              <div className="space-y-6">
                {analysisResult ? (
                  <>
                    {/* Risk Score */}
                    <div className={`rounded-2xl shadow-xl p-8 transition-colors duration-300 ${
                      darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
                    } border`}>
                      <div className="flex items-center justify-between mb-6">
                        <h3 className={`text-xl font-bold transition-colors duration-300 ${
                          darkMode ? 'text-white' : 'text-gray-900'
                        }`}>Risk Assessment</h3>
                        <div className={`px-4 py-2 rounded-full text-sm font-semibold ${
                          analysisResult.risk_score > 0.7 
                            ? 'bg-red-100 text-red-800' 
                            : analysisResult.risk_score > 0.4 
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {Math.round(analysisResult.risk_score * 100)}% Risk
                        </div>
                      </div>
                      
                      <div className="w-full bg-gray-200 rounded-full h-4 mb-4">
                        <div 
                          className={`h-4 rounded-full transition-all duration-1000 ${
                            analysisResult.risk_score > 0.7 
                              ? 'bg-gradient-to-r from-red-500 to-red-600' 
                              : analysisResult.risk_score > 0.4 
                              ? 'bg-gradient-to-r from-yellow-500 to-orange-500'
                              : 'bg-gradient-to-r from-green-500 to-green-600'
                          }`}
                          style={{ width: `${analysisResult.risk_score * 100}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Vulnerabilities */}
                    <div className={`rounded-2xl shadow-xl p-8 transition-colors duration-300 ${
                      darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
                    } border`}>
                      <h3 className={`text-xl font-bold mb-6 transition-colors duration-300 ${
                        darkMode ? 'text-white' : 'text-gray-900'
                      }`}>Detected Vulnerabilities</h3>
                      
                      {analysisResult.vulnerabilities.length > 0 ? (
                        <div className="space-y-4">
                          {analysisResult.vulnerabilities.map((vuln, index) => (
                            <div key={index} className={`p-4 rounded-lg border transition-colors duration-300 ${getSeverityColor(vuln.probability)}`}>
                              <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-3">
                                  <span className="text-2xl">{getSeverityIcon(vuln.probability)}</span>
                                  <div>
                                    <h4 className="font-semibold capitalize">{vuln.vulnerability.replace(/_/g, ' ')}</h4>
                                    <p className="text-sm opacity-75">
                                      Confidence: {Math.round(vuln.probability * 100)}%
                                    </p>
                                  </div>
                                </div>
                                <div className="text-right">
                                  <div className="text-sm font-medium">
                                    {vuln.probability >= 0.8 ? 'CRITICAL' : 
                                     vuln.probability >= 0.6 ? 'HIGH' : 
                                     vuln.probability >= 0.4 ? 'MEDIUM' : 'LOW'}
                                  </div>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-8">
                          <div className="text-6xl mb-4">✅</div>
                          <h4 className={`text-lg font-semibold mb-2 transition-colors duration-300 ${
                            darkMode ? 'text-white' : 'text-gray-900'
                          }`}>No Vulnerabilities Detected</h4>
                          <p className={`transition-colors duration-300 ${
                            darkMode ? 'text-gray-400' : 'text-gray-600'
                          }`}>Your contract appears to be secure!</p>
                        </div>
                      )}
                    </div>

                    {/* Report Info */}
                    <div className={`rounded-2xl shadow-xl p-8 transition-colors duration-300 ${
                      darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
                    } border`}>
                      <h3 className={`text-xl font-bold mb-6 transition-colors duration-300 ${
                        darkMode ? 'text-white' : 'text-gray-900'
                      }`}>Report Information</h3>
                      
                      <div className="space-y-4">
                        <div>
                          <label className={`text-sm font-medium transition-colors duration-300 ${
                            darkMode ? 'text-gray-400' : 'text-gray-500'
                          }`}>Contract Hash</label>
                          <p className={`font-mono text-xs break-all transition-colors duration-300 ${
                            darkMode ? 'text-gray-300' : 'text-gray-700'
                          }`}>{analysisResult.contract_hash}</p>
                        </div>
                        
                        <div>
                          <label className={`text-sm font-medium transition-colors duration-300 ${
                            darkMode ? 'text-gray-400' : 'text-gray-500'
                          }`}>Report Hash</label>
                          <p className={`font-mono text-xs break-all transition-colors duration-300 ${
                            darkMode ? 'text-gray-300' : 'text-gray-700'
                          }`}>{analysisResult.report_hash}</p>
                        </div>
                        
                        {analysisResult.ipfs_cid && (
                          <div>
                            <label className={`text-sm font-medium transition-colors duration-300 ${
                              darkMode ? 'text-gray-400' : 'text-gray-500'
                            }`}>IPFS CID</label>
                            <p className={`font-mono text-xs break-all transition-colors duration-300 ${
                              darkMode ? 'text-gray-300' : 'text-gray-700'
                            }`}>{analysisResult.ipfs_cid}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </>
                ) : (
                  <div className={`rounded-2xl shadow-xl p-8 text-center transition-colors duration-300 ${
                    darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
                  } border`}>
                    <div className="text-6xl mb-4">🔍</div>
                    <h3 className={`text-xl font-semibold mb-2 transition-colors duration-300 ${
                      darkMode ? 'text-white' : 'text-gray-900'
                    }`}>Ready to Analyze</h3>
                    <p className={`transition-colors duration-300 ${
                      darkMode ? 'text-gray-400' : 'text-gray-600'
                    }`}>Upload a contract to see AI-powered vulnerability analysis</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'reports' && (
            <div className={`rounded-2xl shadow-xl p-8 transition-colors duration-300 ${
              darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
            } border`}>
              <h2 className={`text-2xl font-bold mb-6 transition-colors duration-300 ${
                darkMode ? 'text-white' : 'text-gray-900'
              }`}>📊 Audit Reports</h2>
              <p className={`transition-colors duration-300 ${
                darkMode ? 'text-gray-400' : 'text-gray-600'
              }`}>Your audit history and reports will appear here</p>
            </div>
          )}

          {activeTab === 'governance' && (
            <div className={`rounded-2xl shadow-xl p-8 transition-colors duration-300 ${
              darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
            } border`}>
              <h2 className={`text-2xl font-bold mb-6 transition-colors duration-300 ${
                darkMode ? 'text-white' : 'text-gray-900'
              }`}>🏛️ DAO Governance</h2>
              <p className={`transition-colors duration-300 ${
                darkMode ? 'text-gray-400' : 'text-gray-600'
              }`}>Participate in SecuRizz governance and voting</p>
            </div>
          )}

          {activeTab === 'nft' && (
            <div className={`rounded-2xl shadow-xl p-8 transition-colors duration-300 ${
              darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
            } border`}>
              <h2 className={`text-2xl font-bold mb-6 transition-colors duration-300 ${
                darkMode ? 'text-white' : 'text-gray-900'
              }`}>🎨 Audit NFTs</h2>
              <p className={`transition-colors duration-300 ${
                darkMode ? 'text-gray-400' : 'text-gray-600'
              }`}>Turn your audit reports into collectible NFTs</p>
            </div>
          )}

          {activeTab === 'staking' && (
            <div className={`rounded-2xl shadow-xl p-8 transition-colors duration-300 ${
              darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
            } border`}>
              <h2 className={`text-2xl font-bold mb-6 transition-colors duration-300 ${
                darkMode ? 'text-white' : 'text-gray-900'
              }`}>💰 Staking & Rewards</h2>
              <p className={`transition-colors duration-300 ${
                darkMode ? 'text-gray-400' : 'text-gray-600'
              }`}>Stake SECURIZZ tokens and earn rewards</p>
            </div>
          )}
        </main>

        {/* Footer */}
        <footer className={`mt-16 py-8 transition-colors duration-300 ${
          darkMode ? 'bg-gray-900 border-t border-gray-700' : 'bg-gray-50 border-t border-gray-200'
        }`}>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <p className={`transition-colors duration-300 ${
              darkMode ? 'text-gray-400' : 'text-gray-600'
            }`}>
              Built for Colosseum Cypherpunk 2025 • SecuRizz - GOD-LEVEL Security Auditor
            </p>
          </div>
        </footer>
      </div>
    </>
  )
}
