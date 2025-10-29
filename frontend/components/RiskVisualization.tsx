import React from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface Vulnerability {
  vulnerability: string;
  probability: number;
  confidence?: number;
  severity: string;
  lines?: number[];
}

interface RiskVisualizationProps {
  riskScore: number;
  vulnerabilities: Vulnerability[];
  aiSummary?: string;
}

const RiskVisualization: React.FC<RiskVisualizationProps> = ({
  riskScore,
  vulnerabilities,
  aiSummary
}) => {
  // Prepare data for donut chart
  const severityData = [
    { name: 'Critical', value: vulnerabilities.filter(v => v.severity === 'CRITICAL').length, color: '#ef4444' },
    { name: 'High', value: vulnerabilities.filter(v => v.severity === 'HIGH').length, color: '#f97316' },
    { name: 'Medium', value: vulnerabilities.filter(v => v.severity === 'MEDIUM').length, color: '#eab308' },
    { name: 'Low', value: vulnerabilities.filter(v => v.severity === 'LOW').length, color: '#22c55e' },
  ];

  // Prepare data for vulnerability bar chart
  const vulnerabilityData = vulnerabilities.map(vuln => ({
    name: vuln.vulnerability.replace('_', ' ').toUpperCase(),
    probability: vuln.probability * 100,
    confidence: vuln.confidence ? vuln.confidence * 100 : vuln.probability * 100,
    severity: vuln.severity
  }));

  const getRiskLevel = (score: number) => {
    if (score >= 0.8) return { level: 'CRITICAL', color: '#ef4444' };
    if (score >= 0.6) return { level: 'HIGH', color: '#f97316' };
    if (score >= 0.4) return { level: 'MEDIUM', color: '#eab308' };
    return { level: 'LOW', color: '#22c55e' };
  };

  const riskLevel = getRiskLevel(riskScore);

  return (
    <div className="space-y-6">
      {/* Risk Score Gauge */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold mb-4">Risk Assessment</h3>
        <div className="flex items-center space-x-6">
          <div className="relative">
            <div className="w-32 h-32 relative">
              <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 120 120">
                {/* Background circle */}
                <circle
                  cx="60"
                  cy="60"
                  r="50"
                  stroke="#e5e7eb"
                  strokeWidth="8"
                  fill="transparent"
                />
                {/* Progress circle */}
                <circle
                  cx="60"
                  cy="60"
                  r="50"
                  stroke={riskLevel.color}
                  strokeWidth="8"
                  fill="transparent"
                  strokeDasharray={`${2 * Math.PI * 50}`}
                  strokeDashoffset={`${2 * Math.PI * 50 * (1 - riskScore)}`}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-2xl font-bold" style={{ color: riskLevel.color }}>
                    {Math.round(riskScore * 100)}
                  </div>
                  <div className="text-sm text-gray-500">Risk Score</div>
                </div>
              </div>
            </div>
          </div>
          <div className="flex-1">
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <div 
                  className="w-4 h-4 rounded-full" 
                  style={{ backgroundColor: riskLevel.color }}
                ></div>
                <span className="font-medium">{riskLevel.level} RISK</span>
              </div>
              {aiSummary && (
                <p className="text-sm text-gray-600 mt-3">{aiSummary}</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Vulnerability Severity Breakdown */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold mb-4">Vulnerability Breakdown</h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Donut Chart */}
          <div>
            <h4 className="text-md font-medium mb-3">Severity Distribution</h4>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={severityData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {severityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Vulnerability Chart */}
          <div>
            <h4 className="text-md font-medium mb-3">Vulnerability Details</h4>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={vulnerabilityData} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" domain={[0, 100]} />
                <YAxis type="category" dataKey="name" width={80} />
                <Tooltip formatter={(value) => [`${value}%`, 'Probability']} />
                <Bar dataKey="probability" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Vulnerability List */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold mb-4">Detailed Vulnerabilities</h3>
        <div className="space-y-3">
          {vulnerabilities.map((vuln, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <span className="font-medium capitalize">
                    {vuln.vulnerability.replace('_', ' ')}
                  </span>
                  <span 
                    className={`px-2 py-1 rounded-full text-xs font-medium ${
                      vuln.severity === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                      vuln.severity === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                      vuln.severity === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}
                  >
                    {vuln.severity}
                  </span>
                </div>
                {vuln.lines && vuln.lines.length > 0 && (
                  <div className="text-sm text-gray-500 mt-1">
                    Lines: {vuln.lines.join(', ')}
                  </div>
                )}
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <div className="text-sm font-medium">
                    {Math.round(vuln.probability * 100)}%
                  </div>
                  <div className="text-xs text-gray-500">Probability</div>
                </div>
                {vuln.confidence && (
                  <div className="text-right">
                    <div className="text-sm font-medium">
                      {Math.round(vuln.confidence * 100)}%
                    </div>
                    <div className="text-xs text-gray-500">Confidence</div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RiskVisualization;

