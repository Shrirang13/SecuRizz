import { useEffect, useState } from 'react'

interface RiskGaugeProps {
  score: number // 0-1
}

export default function RiskGauge({ score }: RiskGaugeProps) {
  const [animatedScore, setAnimatedScore] = useState(0)

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedScore(score)
    }, 100)
    return () => clearTimeout(timer)
  }, [score])

  const percentage = Math.round(animatedScore * 100)
  const circumference = 2 * Math.PI * 45 // radius = 45
  const strokeDasharray = circumference
  const strokeDashoffset = circumference - (animatedScore * circumference)

  const getRiskLevel = (score: number) => {
    if (score >= 0.8) return { level: 'Critical', color: 'text-danger-600', bg: 'bg-danger-50' }
    if (score >= 0.6) return { level: 'High', color: 'text-danger-500', bg: 'bg-danger-25' }
    if (score >= 0.4) return { level: 'Medium', color: 'text-warning-600', bg: 'bg-warning-50' }
    if (score >= 0.2) return { level: 'Low', color: 'text-warning-500', bg: 'bg-warning-25' }
    return { level: 'Minimal', color: 'text-success-600', bg: 'bg-success-50' }
  }

  const getStrokeColor = (score: number) => {
    if (score >= 0.8) return '#dc2626' // red-600
    if (score >= 0.6) return '#ef4444' // red-500
    if (score >= 0.4) return '#f59e0b' // amber-500
    if (score >= 0.2) return '#eab308' // yellow-500
    return '#22c55e' // green-500
  }

  const riskInfo = getRiskLevel(score)

  return (
    <div className={`${riskInfo.bg} rounded-lg p-6`}>
      <div className="flex items-center justify-center space-x-8">
        {/* Gauge */}
        <div className="relative">
          <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 100 100">
            {/* Background circle */}
            <circle
              cx="50"
              cy="50"
              r="45"
              stroke="#e5e7eb"
              strokeWidth="8"
              fill="transparent"
            />
            {/* Progress circle */}
            <circle
              cx="50"
              cy="50"
              r="45"
              stroke={getStrokeColor(score)}
              strokeWidth="8"
              fill="transparent"
              strokeDasharray={strokeDasharray}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              className="transition-all duration-1000 ease-out"
            />
          </svg>
          
          {/* Center text */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{percentage}%</div>
              <div className="text-xs text-gray-500">Risk Score</div>
            </div>
          </div>
        </div>

        {/* Risk Info */}
        <div className="space-y-2">
          <div>
            <h3 className={`text-lg font-semibold ${riskInfo.color}`}>
              {riskInfo.level} Risk
            </h3>
            <p className="text-sm text-gray-600">
              Based on detected vulnerabilities
            </p>
          </div>
          
          <div className="space-y-1 text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-danger-500 rounded-full"></div>
              <span>Critical: 80-100%</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-danger-400 rounded-full"></div>
              <span>High: 60-79%</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-warning-500 rounded-full"></div>
              <span>Medium: 40-59%</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-warning-400 rounded-full"></div>
              <span>Low: 20-39%</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-success-500 rounded-full"></div>
              <span>Minimal: 0-19%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
