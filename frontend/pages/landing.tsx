import { useState } from 'react'
import Head from 'next/head'
import { useWallet } from '@solana/wallet-adapter-react'
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui'
import toast from 'react-hot-toast'
import { useRouter } from 'next/router'

export default function LandingPage() {
  const { connected } = useWallet()
  const router = useRouter()
  const [isUploading, setIsUploading] = useState(false)

  const handleStartAudit = () => {
    if (connected) {
      router.push('/god-level')
    } else {
      toast.error('Please connect your wallet first')
    }
  }

  const handleViewDemo = () => {
    router.push('/god-level')
  }

  const handleUploadFile = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.sol,.vy,.rs,.ts'
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (file) {
        setIsUploading(true)
        // Simulate upload
        setTimeout(() => {
          setIsUploading(false)
          toast.success('Contract uploaded! Redirecting to analysis...')
          router.push('/god-level')
        }, 2000)
      }
    }
    input.click()
  }

  return (
    <>
      <Head>
        <title>SecuRizz - Enterprise Smart Contract Security Platform</title>
        <meta name="description" content="AI-powered smart contract vulnerability auditor with on-chain proofs" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet" />
      </Head>

      <div className="min-h-screen bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-5">
          {/* Header */}
          <div className="flex justify-between items-center py-8 border-b border-purple-500/20">
            <div className="flex items-center gap-5">
              <div className="w-14 h-14 bg-gradient-to-br from-purple-600 to-pink-500 rounded-2xl flex items-center justify-center text-2xl shadow-lg shadow-purple-500/50">
                🔒
              </div>
              <div>
                <h1 className="text-4xl font-black bg-gradient-to-r from-white via-purple-400 to-pink-400 bg-clip-text text-transparent">
                  SecuRizz
                </h1>
                <p className="text-sm text-gray-400 font-medium">Enterprise Smart Contract Security</p>
              </div>
            </div>
            <div className="flex items-center gap-8">
              <a href="#features" className="text-gray-400 hover:text-white transition-colors font-medium">Features</a>
              <a href="#pricing" className="text-gray-400 hover:text-white transition-colors font-medium">Pricing</a>
              <a href="#docs" className="text-gray-400 hover:text-white transition-colors font-medium">Documentation</a>
              <a href="#about" className="text-gray-400 hover:text-white transition-colors font-medium">About</a>
              <WalletMultiButton className="!bg-gradient-to-r !from-purple-600 !to-pink-500 !rounded-xl !px-8 !py-3 !text-white !font-bold !shadow-lg hover:!shadow-xl transition-all duration-300" />
            </div>
          </div>

          {/* Hero Section */}
          <div className="text-center py-20">
            <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/30 px-5 py-2 rounded-full text-sm font-semibold mb-6">
              <span>✨</span>
              <span>Powered by AI • Verified on Solana</span>
            </div>
            <h2 className="text-7xl font-black leading-tight mb-6 bg-gradient-to-r from-white via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Secure Your Smart<br />Contracts with SecuRizz
            </h2>
            <p className="text-xl text-gray-300 max-w-4xl mx-auto mb-10 leading-relaxed">
              AI-powered security analysis that detects vulnerabilities before they become exploits.
              Trusted by leading DeFi protocols and blockchain projects worldwide.
            </p>
            <div className="flex gap-4 justify-center mb-16">
              <button 
                onClick={handleStartAudit}
                className="px-12 py-5 bg-gradient-to-r from-purple-600 to-pink-500 rounded-2xl text-white font-bold text-lg shadow-lg shadow-purple-500/50 hover:shadow-xl hover:shadow-purple-500/60 transition-all duration-300 hover:-translate-y-1"
              >
                Start Free Audit
              </button>
              <button 
                onClick={handleViewDemo}
                className="px-12 py-5 bg-purple-500/10 border-2 border-purple-500/40 rounded-2xl text-white font-bold text-lg hover:bg-purple-500/20 transition-all duration-300"
              >
                View Demo
              </button>
            </div>
          </div>

          {/* Trust Section */}
          <div className="text-center py-10 bg-purple-500/5 rounded-3xl border border-purple-500/20 mb-20">
            <div className="text-sm text-gray-400 uppercase tracking-wider font-semibold mb-6">Trusted by Leading Blockchain Projects</div>
            <div className="flex justify-center gap-16 flex-wrap">
              <div className="text-2xl opacity-60 hover:opacity-100 transition-all duration-300 hover:scale-110">⟠ Solana</div>
              <div className="text-2xl opacity-60 hover:opacity-100 transition-all duration-300 hover:scale-110">◆ Ethereum</div>
              <div className="text-2xl opacity-60 hover:opacity-100 transition-all duration-300 hover:scale-110">⬡ Polygon</div>
              <div className="text-2xl opacity-60 hover:opacity-100 transition-all duration-300 hover:scale-110">⚡ Avalanche</div>
              <div className="text-2xl opacity-60 hover:opacity-100 transition-all duration-300 hover:scale-110">🔷 Arbitrum</div>
            </div>
          </div>

          {/* Upload Section */}
          <div className="bg-gradient-to-br from-purple-500/15 to-pink-500/10 border-2 border-purple-500/40 rounded-3xl p-20 text-center mb-20">
            <div className="text-8xl mb-8">📄</div>
            <div className="text-5xl font-bold mb-4 bg-gradient-to-r from-white to-purple-400 bg-clip-text text-transparent">
              Scan Your Smart Contract
            </div>
            <div className="text-lg text-gray-300 mb-10 max-w-3xl mx-auto leading-relaxed">
              Upload your contract and get AI-powered security analysis in seconds.<br />
              Detects 15+ vulnerability types including reentrancy, access control, and overflow issues.
            </div>
            <button 
              onClick={handleUploadFile}
              disabled={isUploading}
              className="px-16 py-6 bg-gradient-to-r from-purple-600 to-pink-500 rounded-2xl text-white font-bold text-xl shadow-lg shadow-purple-500/50 hover:shadow-xl hover:shadow-purple-500/60 transition-all duration-300 hover:-translate-y-1 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isUploading ? 'Uploading...' : '📤 Choose Contract File'}
            </button>
            <div className="flex gap-3 justify-center mt-4">
              <span className="bg-purple-500/15 border border-purple-500/30 px-4 py-2 rounded-full text-sm font-bold">.SOL Solidity</span>
              <span className="bg-purple-500/15 border border-purple-500/30 px-4 py-2 rounded-full text-sm font-bold">.VY Vyper</span>
              <span className="bg-purple-500/15 border border-purple-500/30 px-4 py-2 rounded-full text-sm font-bold">.RS Rust/Solana</span>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-4 gap-6 mb-20">
            <div className="bg-purple-500/8 border border-purple-500/20 rounded-3xl p-10 text-center hover:bg-purple-500/12 transition-all duration-300 hover:-translate-y-2">
              <div className="text-5xl mb-5">🎯</div>
              <div className="text-5xl font-black mb-3 bg-gradient-to-r from-white to-purple-400 bg-clip-text text-transparent">10K+</div>
              <div className="text-gray-400 font-semibold">Contracts Audited</div>
            </div>
            <div className="bg-purple-500/8 border border-purple-500/20 rounded-3xl p-10 text-center hover:bg-purple-500/12 transition-all duration-300 hover:-translate-y-2">
              <div className="text-5xl mb-5">⚠️</div>
              <div className="text-5xl font-black mb-3 bg-gradient-to-r from-white to-purple-400 bg-clip-text text-transparent">50K+</div>
              <div className="text-gray-400 font-semibold">Vulnerabilities Found</div>
            </div>
            <div className="bg-purple-500/8 border border-purple-500/20 rounded-3xl p-10 text-center hover:bg-purple-500/12 transition-all duration-300 hover:-translate-y-2">
              <div className="text-5xl mb-5">💰</div>
              <div className="text-5xl font-black mb-3 bg-gradient-to-r from-white to-purple-400 bg-clip-text text-transparent">$2.5B</div>
              <div className="text-gray-400 font-semibold">Assets Protected</div>
            </div>
            <div className="bg-purple-500/8 border border-purple-500/20 rounded-3xl p-10 text-center hover:bg-purple-500/12 transition-all duration-300 hover:-translate-y-2">
              <div className="text-5xl mb-5">✅</div>
              <div className="text-5xl font-black mb-3 bg-gradient-to-r from-white to-purple-400 bg-clip-text text-transparent">99.2%</div>
              <div className="text-gray-400 font-semibold">Detection Accuracy</div>
            </div>
          </div>

          {/* Features Section */}
          <div className="text-center mb-16">
            <h2 className="text-5xl font-black mb-4 bg-gradient-to-r from-white to-purple-400 bg-clip-text text-transparent">
              Why Choose SecuRizz?
            </h2>
            <p className="text-lg text-gray-400">Comprehensive security analysis powered by cutting-edge AI technology</p>
          </div>

          <div className="grid grid-cols-3 gap-8 mb-24">
            <div className="bg-purple-500/5 border border-purple-500/20 rounded-3xl p-12 hover:bg-purple-500/10 transition-all duration-300 hover:-translate-y-2">
              <div className="w-18 h-18 bg-gradient-to-br from-purple-500/30 to-pink-500/30 rounded-2xl flex items-center justify-center text-4xl mb-6">
                🤖
              </div>
              <div className="text-2xl font-bold mb-3">AI-Powered Analysis</div>
              <div className="text-gray-400 leading-relaxed">
                Advanced machine learning models trained on millions of smart contracts to detect even the most subtle vulnerabilities.
              </div>
            </div>

            <div className="bg-purple-500/5 border border-purple-500/20 rounded-3xl p-12 hover:bg-purple-500/10 transition-all duration-300 hover:-translate-y-2">
              <div className="w-18 h-18 bg-gradient-to-br from-purple-500/30 to-pink-500/30 rounded-2xl flex items-center justify-center text-4xl mb-6">
                ⚡
              </div>
              <div className="text-2xl font-bold mb-3">Instant Results</div>
              <div className="text-gray-400 leading-relaxed">
                Get comprehensive security reports in seconds, not days. No more waiting weeks for manual audits.
              </div>
            </div>

            <div className="bg-purple-500/5 border border-purple-500/20 rounded-3xl p-12 hover:bg-purple-500/10 transition-all duration-300 hover:-translate-y-2">
              <div className="w-18 h-18 bg-gradient-to-br from-purple-500/30 to-pink-500/30 rounded-2xl flex items-center justify-center text-4xl mb-6">
                ⛓️
              </div>
              <div className="text-2xl font-bold mb-3">On-Chain Proofs</div>
              <div className="text-gray-400 leading-relaxed">
                All audit results are cryptographically signed and stored on Solana blockchain for permanent verification.
              </div>
            </div>

            <div className="bg-purple-500/5 border border-purple-500/20 rounded-3xl p-12 hover:bg-purple-500/10 transition-all duration-300 hover:-translate-y-2">
              <div className="w-18 h-18 bg-gradient-to-br from-purple-500/30 to-pink-500/30 rounded-2xl flex items-center justify-center text-4xl mb-6">
                🔍
              </div>
              <div className="text-2xl font-bold mb-3">15+ Vulnerability Types</div>
              <div className="text-gray-400 leading-relaxed">
                Detects reentrancy, access control, integer overflow, timestamp dependency, and many more critical issues.
              </div>
            </div>

            <div className="bg-purple-500/5 border border-purple-500/20 rounded-3xl p-12 hover:bg-purple-500/10 transition-all duration-300 hover:-translate-y-2">
              <div className="w-18 h-18 bg-gradient-to-br from-purple-500/30 to-pink-500/30 rounded-2xl flex items-center justify-center text-4xl mb-6">
                💡
              </div>
              <div className="text-2xl font-bold mb-3">Fix Recommendations</div>
              <div className="text-gray-400 leading-relaxed">
                Don't just find bugs—fix them. Get detailed code suggestions and best practices for every vulnerability.
              </div>
            </div>

            <div className="bg-purple-500/5 border border-purple-500/20 rounded-3xl p-12 hover:bg-purple-500/10 transition-all duration-300 hover:-translate-y-2">
              <div className="w-18 h-18 bg-gradient-to-br from-purple-500/30 to-pink-500/30 rounded-2xl flex items-center justify-center text-4xl mb-6">
                📊
              </div>
              <div className="text-2xl font-bold mb-3">Detailed Reports</div>
              <div className="text-gray-400 leading-relaxed">
                Export professional PDF reports with executive summaries, technical details, and compliance documentation.
              </div>
            </div>
          </div>

          {/* Recent Scans Section */}
          <div className="text-center mb-16">
            <h2 className="text-5xl font-black mb-4 bg-gradient-to-r from-white to-purple-400 bg-clip-text text-transparent">
              Recent Security Scans
            </h2>
            <p className="text-lg text-gray-400">Real-time vulnerability detection across the blockchain ecosystem</p>
          </div>

          <div className="grid grid-cols-3 gap-8 mb-24">
            <div className="col-span-2 bg-white/2 border border-purple-500/20 rounded-3xl p-9">
              <div className="flex items-center gap-3 mb-6">
                <span>🔍</span>
                <span className="text-2xl font-bold">Recent Vulnerabilities</span>
              </div>

              <div className="space-y-4">
                <div className="bg-purple-500/5 border border-purple-500/15 rounded-2xl p-7 hover:bg-purple-500/10 transition-all duration-300 hover:translate-x-2">
                  <div className="flex justify-between mb-4">
                    <div>
                      <div className="font-bold text-lg mb-2">Reentrancy Vulnerability</div>
                      <div className="text-sm text-gray-400 mb-5">TokenSwap.sol → withdraw()</div>
                    </div>
                    <span className="bg-red-500/20 text-red-400 border border-red-500 px-4 py-2 rounded-xl text-xs font-bold uppercase">Critical</span>
                  </div>
                  <div className="flex gap-3">
                    <button className="px-5 py-2 bg-gradient-to-r from-purple-600 to-pink-500 rounded-xl text-white font-semibold text-sm hover:-translate-y-1 transition-all duration-300">Fix Now</button>
                    <button className="px-5 py-2 bg-purple-500/10 border border-purple-500/30 rounded-xl text-white font-semibold text-sm hover:bg-purple-500/20 transition-all duration-300">Details</button>
                    <button className="px-5 py-2 bg-purple-500/10 border border-purple-500/30 rounded-xl text-white font-semibold text-sm hover:bg-purple-500/20 transition-all duration-300">Export</button>
                  </div>
                </div>

                <div className="bg-purple-500/5 border border-purple-500/15 rounded-2xl p-7 hover:bg-purple-500/10 transition-all duration-300 hover:translate-x-2">
                  <div className="flex justify-between mb-4">
                    <div>
                      <div className="font-bold text-lg mb-2">Unchecked External Call</div>
                      <div className="text-sm text-gray-400 mb-5">DeFiVault.sol → transferFunds()</div>
                    </div>
                    <span className="bg-orange-500/20 text-orange-400 border border-orange-500 px-4 py-2 rounded-xl text-xs font-bold uppercase">High</span>
                  </div>
                  <div className="flex gap-3">
                    <button className="px-5 py-2 bg-gradient-to-r from-purple-600 to-pink-500 rounded-xl text-white font-semibold text-sm hover:-translate-y-1 transition-all duration-300">Fix Now</button>
                    <button className="px-5 py-2 bg-purple-500/10 border border-purple-500/30 rounded-xl text-white font-semibold text-sm hover:bg-purple-500/20 transition-all duration-300">Details</button>
                    <button className="px-5 py-2 bg-purple-500/10 border border-purple-500/30 rounded-xl text-white font-semibold text-sm hover:bg-purple-500/20 transition-all duration-300">Export</button>
                  </div>
                </div>

                <div className="bg-purple-500/5 border border-purple-500/15 rounded-2xl p-7 hover:bg-purple-500/10 transition-all duration-300 hover:translate-x-2">
                  <div className="flex justify-between mb-4">
                    <div>
                      <div className="font-bold text-lg mb-2">Access Control Missing</div>
                      <div className="text-sm text-gray-400 mb-5">GovernanceToken.sol → mint()</div>
                    </div>
                    <span className="bg-red-500/20 text-red-400 border border-red-500 px-4 py-2 rounded-xl text-xs font-bold uppercase">Critical</span>
                  </div>
                  <div className="flex gap-3">
                    <button className="px-5 py-2 bg-gradient-to-r from-purple-600 to-pink-500 rounded-xl text-white font-semibold text-sm hover:-translate-y-1 transition-all duration-300">Fix Now</button>
                    <button className="px-5 py-2 bg-purple-500/10 border border-purple-500/30 rounded-xl text-white font-semibold text-sm hover:bg-purple-500/20 transition-all duration-300">Details</button>
                    <button className="px-5 py-2 bg-purple-500/10 border border-purple-500/30 rounded-xl text-white font-semibold text-sm hover:bg-purple-500/20 transition-all duration-300">Export</button>
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-6">
              <div className="bg-white/2 border border-purple-500/20 rounded-3xl p-9">
                <div className="flex flex-col gap-4 mb-8">
                  <button className="p-5 bg-purple-500/10 border border-purple-500/30 rounded-2xl text-white font-semibold hover:bg-purple-500/20 transition-all duration-300 hover:translate-x-1 flex items-center gap-4 text-left">
                    <span>📤</span>
                    <span>Upload Contract</span>
                  </button>
                  <button className="p-5 bg-purple-500/10 border border-purple-500/30 rounded-2xl text-white font-semibold hover:bg-purple-500/20 transition-all duration-300 hover:translate-x-1 flex items-center gap-4 text-left">
                    <span>📊</span>
                    <span>View Reports</span>
                  </button>
                  <button className="p-5 bg-purple-500/10 border border-purple-500/30 rounded-2xl text-white font-semibold hover:bg-purple-500/20 transition-all duration-300 hover:translate-x-1 flex items-center gap-4 text-left">
                    <span>⚙️</span>
                    <span>Settings</span>
                  </button>
                </div>

                <div className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-blue-500/30 rounded-2xl p-7">
                  <div className="font-bold text-lg mb-4 text-blue-400">Blockchain Integration</div>
                  <div className="text-sm text-gray-400 leading-relaxed">
                    All audit results are cryptographically signed and stored on Solana blockchain for permanent verification and transparency.
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="bg-purple-500/5 border-t border-purple-500/20 py-20 mt-24">
            <div className="grid grid-cols-4 gap-16 mb-16">
              <div>
                <h3 className="text-3xl font-black mb-4 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                  SecuRizz
                </h3>
                <p className="text-gray-400 leading-relaxed">
                  The most advanced AI-powered smart contract security platform, trusted by leading blockchain projects worldwide.
                </p>
              </div>
              <div>
                <h4 className="text-lg font-bold mb-5">Product</h4>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors mb-3">Features</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors mb-3">Pricing</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors mb-3">API</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors mb-3">Documentation</a>
              </div>
              <div>
                <h4 className="text-lg font-bold mb-5">Company</h4>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors mb-3">About</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors mb-3">Blog</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors mb-3">Careers</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors mb-3">Contact</a>
              </div>
              <div>
                <h4 className="text-lg font-bold mb-5">Support</h4>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors mb-3">Help Center</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors mb-3">Community</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors mb-3">Status</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors mb-3">Security</a>
              </div>
            </div>
            <div className="flex justify-between pt-8 border-t border-purple-500/20 text-gray-400 text-sm">
              <div>© 2024 SecuRizz. All rights reserved.</div>
              <div>Built for Colosseum Cypherpunk 2025</div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
