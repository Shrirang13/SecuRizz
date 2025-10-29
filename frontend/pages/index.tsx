import { useEffect } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'

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
  fix_suggestions?: Record<string, any>
}

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    // Redirect to landing page
    router.push('/landing')
  }, [router])

  return (
    <>
      <Head>
        <title>SecuRizz - Redirecting to GOD-LEVEL Interface</title>
        <meta name="description" content="Redirecting to GOD-LEVEL Security Auditor" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold text-2xl">🔒</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">SecuRizz</h1>
          <p className="text-gray-600 mb-4">Redirecting to GOD-LEVEL interface...</p>
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
        </div>
      </div>
    </>
  )
}
