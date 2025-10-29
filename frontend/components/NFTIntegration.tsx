import React, { useState, useEffect } from 'react';
import { useWallet } from './WalletProvider';

interface AuditNFT {
  id: string;
  contract_hash: string;
  audit_score: number;
  risk_score: number;
  vulnerabilities: string[];
  minted_at: string;
  owner: string;
  metadata_uri: string;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
}

interface NFTMarketplace {
  nfts: AuditNFT[];
  total_supply: number;
  floor_price: number;
  volume_24h: number;
}

export const NFTIntegration: React.FC = () => {
  const { connected, publicKey } = useWallet();
  const [nfts, setNfts] = useState<AuditNFT[]>([]);
  const [marketplace, setMarketplace] = useState<NFTMarketplace | null>(null);
  const [selectedNFT, setSelectedNFT] = useState<AuditNFT | null>(null);
  const [mintForm, setMintForm] = useState({
    contract_hash: '',
    audit_score: 0,
    risk_score: 0,
    vulnerabilities: [] as string[]
  });

  useEffect(() => {
    if (connected) {
      loadUserNFTs();
      loadMarketplace();
    }
  }, [connected, publicKey]);

  const loadUserNFTs = async () => {
    if (!publicKey) return;
    
    try {
      const response = await fetch(`/api/nfts/user/${publicKey}`);
      const data = await response.json();
      setNfts(data);
    } catch (error) {
      console.error('Failed to load NFTs:', error);
    }
  };

  const loadMarketplace = async () => {
    try {
      const response = await fetch('/api/nfts/marketplace');
      const data = await response.json();
      setMarketplace(data);
    } catch (error) {
      console.error('Failed to load marketplace:', error);
    }
  };

  const mintAuditNFT = async () => {
    if (!connected || !publicKey) {
      alert('Please connect your wallet');
      return;
    }

    try {
      const response = await fetch('/api/nfts/mint', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...mintForm,
          owner: publicKey
        })
      });

      if (response.ok) {
        const nft = await response.json();
        alert(`NFT minted successfully! Token ID: ${nft.id}`);
        setMintForm({
          contract_hash: '',
          audit_score: 0,
          risk_score: 0,
          vulnerabilities: []
        });
        loadUserNFTs();
        loadMarketplace();
      } else {
        throw new Error('Failed to mint NFT');
      }
    } catch (error) {
      console.error('Failed to mint NFT:', error);
      alert('Failed to mint NFT');
    }
  };

  const calculateRarity = (auditScore: number, riskScore: number, vulnerabilityCount: number): string => {
    if (auditScore >= 95 && riskScore <= 5 && vulnerabilityCount === 0) {
      return 'legendary';
    } else if (auditScore >= 90 && riskScore <= 10 && vulnerabilityCount <= 1) {
      return 'epic';
    } else if (auditScore >= 80 && riskScore <= 20 && vulnerabilityCount <= 3) {
      return 'rare';
    } else {
      return 'common';
    }
  };

  const getRarityColor = (rarity: string): string => {
    switch (rarity) {
      case 'legendary': return '#FFD700';
      case 'epic': return '#9B59B6';
      case 'rare': return '#3498DB';
      default: return '#95A5A6';
    }
  };

  const getRarityIcon = (rarity: string): string => {
    switch (rarity) {
      case 'legendary': return '👑';
      case 'epic': return '💎';
      case 'rare': return '⭐';
      default: return '🔹';
    }
  };

  return (
    <div className="nft-integration">
      <div className="nft-header">
        <h1>🎨 SecuRizz Audit NFTs</h1>
        <p>Turn your audit reports into collectible NFTs</p>
      </div>

      {/* Mint NFT Section */}
      <div className="mint-section">
        <h2>Mint Audit NFT</h2>
        <div className="mint-form">
          <input
            type="text"
            placeholder="Contract Hash"
            value={mintForm.contract_hash}
            onChange={(e) => setMintForm({...mintForm, contract_hash: e.target.value})}
            className="form-input"
          />
          
          <div className="form-row">
            <label>
              Audit Score (0-100):
              <input
                type="number"
                min="0"
                max="100"
                value={mintForm.audit_score}
                onChange={(e) => setMintForm({...mintForm, audit_score: parseInt(e.target.value)})}
                className="form-input"
              />
            </label>
            
            <label>
              Risk Score (0-100):
              <input
                type="number"
                min="0"
                max="100"
                value={mintForm.risk_score}
                onChange={(e) => setMintForm({...mintForm, risk_score: parseInt(e.target.value)})}
                className="form-input"
              />
            </label>
          </div>
          
          <div className="vulnerabilities-section">
            <label>Vulnerabilities Found:</label>
            <div className="vulnerability-tags">
              {['reentrancy', 'overflow', 'access_control', 'timestamp', 'tx_origin'].map(vuln => (
                <label key={vuln} className="vulnerability-tag">
                  <input
                    type="checkbox"
                    checked={mintForm.vulnerabilities.includes(vuln)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setMintForm({
                          ...mintForm,
                          vulnerabilities: [...mintForm.vulnerabilities, vuln]
                        });
                      } else {
                        setMintForm({
                          ...mintForm,
                          vulnerabilities: mintForm.vulnerabilities.filter(v => v !== vuln)
                        });
                      }
                    }}
                  />
                  <span>{vuln}</span>
                </label>
              ))}
            </div>
          </div>
          
          <button 
            onClick={mintAuditNFT}
            className="mint-button"
            disabled={!mintForm.contract_hash || mintForm.audit_score === 0}
          >
            Mint NFT
          </button>
        </div>
      </div>

      {/* User NFTs */}
      <div className="user-nfts">
        <h2>Your Audit NFTs</h2>
        {nfts.length === 0 ? (
          <p className="no-nfts">No NFTs found. Mint your first audit NFT!</p>
        ) : (
          <div className="nft-grid">
            {nfts.map((nft) => (
              <div 
                key={nft.id} 
                className="nft-card"
                onClick={() => setSelectedNFT(nft)}
              >
                <div className="nft-header">
                  <span className="nft-id">#{nft.id.slice(0, 8)}</span>
                  <span 
                    className="rarity-badge"
                    style={{ backgroundColor: getRarityColor(nft.rarity) }}
                  >
                    {getRarityIcon(nft.rarity)} {nft.rarity.toUpperCase()}
                  </span>
                </div>
                
                <div className="nft-scores">
                  <div className="score">
                    <span className="label">Audit Score:</span>
                    <span className="value">{nft.audit_score}/100</span>
                  </div>
                  <div className="score">
                    <span className="label">Risk Score:</span>
                    <span className="value">{nft.risk_score}/100</span>
                  </div>
                </div>
                
                <div className="nft-vulnerabilities">
                  <span className="label">Vulnerabilities:</span>
                  <div className="vulnerability-list">
                    {nft.vulnerabilities.map((vuln, index) => (
                      <span key={index} className="vulnerability-chip">
                        {vuln}
                      </span>
                    ))}
                  </div>
                </div>
                
                <div className="nft-footer">
                  <span className="mint-date">
                    Minted: {new Date(nft.minted_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Marketplace */}
      {marketplace && (
        <div className="marketplace">
          <h2>NFT Marketplace</h2>
          <div className="marketplace-stats">
            <div className="stat">
              <span className="label">Total Supply:</span>
              <span className="value">{marketplace.total_supply.toLocaleString()}</span>
            </div>
            <div className="stat">
              <span className="label">Floor Price:</span>
              <span className="value">{marketplace.floor_price} SOL</span>
            </div>
            <div className="stat">
              <span className="label">24h Volume:</span>
              <span className="value">{marketplace.volume_24h} SOL</span>
            </div>
          </div>
        </div>
      )}

      {/* NFT Detail Modal */}
      {selectedNFT && (
        <div className="nft-modal">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Audit NFT #{selectedNFT.id.slice(0, 8)}</h3>
              <button 
                onClick={() => setSelectedNFT(null)}
                className="close-button"
              >
                ×
              </button>
            </div>
            
            <div className="modal-body">
              <div className="nft-details">
                <div className="detail-row">
                  <span className="label">Contract Hash:</span>
                  <span className="value">{selectedNFT.contract_hash}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Audit Score:</span>
                  <span className="value">{selectedNFT.audit_score}/100</span>
                </div>
                <div className="detail-row">
                  <span className="label">Risk Score:</span>
                  <span className="value">{selectedNFT.risk_score}/100</span>
                </div>
                <div className="detail-row">
                  <span className="label">Rarity:</span>
                  <span 
                    className="value rarity"
                    style={{ color: getRarityColor(selectedNFT.rarity) }}
                  >
                    {getRarityIcon(selectedNFT.rarity)} {selectedNFT.rarity.toUpperCase()}
                  </span>
                </div>
                <div className="detail-row">
                  <span className="label">Vulnerabilities:</span>
                  <div className="vulnerability-list">
                    {selectedNFT.vulnerabilities.map((vuln, index) => (
                      <span key={index} className="vulnerability-chip">
                        {vuln}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="detail-row">
                  <span className="label">Minted:</span>
                  <span className="value">{new Date(selectedNFT.minted_at).toLocaleString()}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Owner:</span>
                  <span className="value">{selectedNFT.owner.slice(0, 8)}...{selectedNFT.owner.slice(-8)}</span>
                </div>
              </div>
            </div>
            
            <div className="modal-footer">
              <button className="action-button">View on Solscan</button>
              <button className="action-button">Share</button>
              <button className="action-button">Trade</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NFTIntegration;
