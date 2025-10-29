import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ExternalLinkIcon, DocumentIcon, ShieldCheckIcon } from '@heroicons/react/24/outline';

interface AuditReport {
  id: number;
  contract_id: number;
  report_hash: string;
  ipfs_cid: string;
  risk_score: number;
  vulnerabilities: any[];
  mitigation_strategies: Record<string, string>;
  created_at: string;
}

interface AuditHistoryProps {
  onReportSelect?: (report: AuditReport) => void;
}

const AuditHistory: React.FC<AuditHistoryProps> = ({ onReportSelect }) => {
  const [reports, setReports] = useState<AuditReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const response = await axios.get(`${backendUrl}/reports`);
      setReports(response.data);
    } catch (err) {
      setError('Failed to fetch audit reports');
      console.error('Error fetching reports:', err);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 0.8) return 'text-red-600 bg-red-100';
    if (score >= 0.6) return 'text-orange-600 bg-orange-100';
    if (score >= 0.4) return 'text-yellow-600 bg-yellow-100';
    return 'text-green-600 bg-green-100';
  };

  const getRiskLevel = (score: number) => {
    if (score >= 0.8) return 'CRITICAL';
    if (score >= 0.6) return 'HIGH';
    if (score >= 0.4) return 'MEDIUM';
    return 'LOW';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading audit history...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-600">{error}</p>
        <button 
          onClick={fetchReports}
          className="mt-2 text-red-600 hover:text-red-800 underline"
        >
          Try again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Audit History</h2>
        <button 
          onClick={fetchReports}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          Refresh
        </button>
      </div>

      {reports.length === 0 ? (
        <div className="text-center py-12">
          <DocumentIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No audit reports</h3>
          <p className="mt-1 text-sm text-gray-500">
            Upload and analyze a smart contract to see audit history.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {reports.map((report) => (
            <div 
              key={report.id}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => onReportSelect?.(report)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <ShieldCheckIcon className="h-5 w-5 text-gray-400" />
                    <div>
                      <h3 className="text-sm font-medium text-gray-900">
                        Audit Report #{report.id}
                      </h3>
                      <p className="text-xs text-gray-500">
                        {formatDate(report.created_at)}
                      </p>
                    </div>
                  </div>
                  
                  <div className="mt-3 grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-gray-500">Risk Level</p>
                      <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(report.risk_score)}`}>
                        {getRiskLevel(report.risk_score)}
                      </span>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Vulnerabilities</p>
                      <p className="text-sm font-medium">{report.vulnerabilities.length}</p>
                    </div>
                  </div>
                </div>

                <div className="flex flex-col items-end space-y-2">
                  <div className="text-right">
                    <p className="text-xs text-gray-500">Risk Score</p>
                    <p className="text-lg font-bold" style={{ color: getRiskColor(report.risk_score).split(' ')[0].replace('text-', '').replace('-600', '') }}>
                      {Math.round(report.risk_score * 100)}
                    </p>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        copyToClipboard(report.report_hash);
                      }}
                      className="text-xs text-gray-500 hover:text-gray-700"
                      title="Copy report hash"
                    >
                      Hash
                    </button>
                    {report.ipfs_cid && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          window.open(`https://gateway.pinata.cloud/ipfs/${report.ipfs_cid}`, '_blank');
                        }}
                        className="text-xs text-blue-600 hover:text-blue-800 flex items-center"
                        title="View on IPFS"
                      >
                        <ExternalLinkIcon className="h-3 w-3 mr-1" />
                        IPFS
                      </button>
                    )}
                  </div>
                </div>
              </div>

              {/* Vulnerability Summary */}
              {report.vulnerabilities.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <p className="text-xs text-gray-500 mb-2">Key Vulnerabilities:</p>
                  <div className="flex flex-wrap gap-1">
                    {report.vulnerabilities.slice(0, 3).map((vuln, index) => (
                      <span 
                        key={index}
                        className="inline-flex px-2 py-1 rounded text-xs bg-gray-100 text-gray-700"
                      >
                        {vuln.vulnerability.replace('_', ' ')}
                      </span>
                    ))}
                    {report.vulnerabilities.length > 3 && (
                      <span className="inline-flex px-2 py-1 rounded text-xs bg-gray-100 text-gray-700">
                        +{report.vulnerabilities.length - 3} more
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AuditHistory;

