import React, { useState, useEffect } from 'react';
import { useWallet } from './WalletProvider';

interface Proposal {
  id: number;
  title: string;
  description: string;
  proposer: string;
  created_at: string;
  voting_start: string;
  voting_end: string;
  status: 'active' | 'passed' | 'rejected' | 'executed';
  votes_for: number;
  votes_against: number;
  total_votes: number;
  execution_delay: number;
}

interface Vote {
  proposal_id: number;
  voter: string;
  vote_weight: number;
  support: boolean;
  voted_at: string;
}

export const DAOGovernance: React.FC = () => {
  const { connected, publicKey, signTransaction } = useWallet();
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [votes, setVotes] = useState<Vote[]>([]);
  const [userStake, setUserStake] = useState(0);
  const [votingPower, setVotingPower] = useState(0);
  const [newProposal, setNewProposal] = useState({
    title: '',
    description: '',
    execution_delay: 86400 // 1 day
  });

  useEffect(() => {
    if (connected) {
      loadProposals();
      loadUserVotes();
      loadUserStake();
    }
  }, [connected, publicKey]);

  const loadProposals = async () => {
    try {
      const response = await fetch('/api/governance/proposals');
      const data = await response.json();
      setProposals(data);
    } catch (error) {
      console.error('Failed to load proposals:', error);
    }
  };

  const loadUserVotes = async () => {
    if (!publicKey) return;
    
    try {
      const response = await fetch(`/api/governance/votes/${publicKey}`);
      const data = await response.json();
      setVotes(data);
    } catch (error) {
      console.error('Failed to load votes:', error);
    }
  };

  const loadUserStake = async () => {
    if (!publicKey) return;
    
    try {
      const response = await fetch(`/api/governance/stake/${publicKey}`);
      const data = await response.json();
      setUserStake(data.amount);
      setVotingPower(data.voting_power);
    } catch (error) {
      console.error('Failed to load stake:', error);
    }
  };

  const createProposal = async () => {
    if (!connected || !publicKey) {
      alert('Please connect your wallet');
      return;
    }

    try {
      const response = await fetch('/api/governance/proposals', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newProposal,
          proposer: publicKey
        })
      });

      if (response.ok) {
        alert('Proposal created successfully!');
        setNewProposal({ title: '', description: '', execution_delay: 86400 });
        loadProposals();
      } else {
        throw new Error('Failed to create proposal');
      }
    } catch (error) {
      console.error('Failed to create proposal:', error);
      alert('Failed to create proposal');
    }
  };

  const voteOnProposal = async (proposalId: number, support: boolean) => {
    if (!connected || !publicKey) {
      alert('Please connect your wallet');
      return;
    }

    if (votingPower === 0) {
      alert('You need to stake SECURIZZ tokens to vote');
      return;
    }

    try {
      // Create vote transaction
      const voteData = {
        proposal_id: proposalId,
        voter: publicKey,
        vote_weight: votingPower,
        support: support
      };

      const response = await fetch('/api/governance/vote', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(voteData)
      });

      if (response.ok) {
        alert('Vote cast successfully!');
        loadProposals();
        loadUserVotes();
      } else {
        throw new Error('Failed to cast vote');
      }
    } catch (error) {
      console.error('Failed to vote:', error);
      alert('Failed to cast vote');
    }
  };

  const executeProposal = async (proposalId: number) => {
    if (!connected || !publicKey) {
      alert('Please connect your wallet');
      return;
    }

    try {
      const response = await fetch(`/api/governance/execute/${proposalId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        alert('Proposal executed successfully!');
        loadProposals();
      } else {
        throw new Error('Failed to execute proposal');
      }
    } catch (error) {
      console.error('Failed to execute proposal:', error);
      alert('Failed to execute proposal');
    }
  };

  const getUserVote = (proposalId: number): Vote | undefined => {
    return votes.find(vote => vote.proposal_id === proposalId);
  };

  const canVote = (proposal: Proposal): boolean => {
    const now = new Date();
    const votingStart = new Date(proposal.voting_start);
    const votingEnd = new Date(proposal.voting_end);
    
    return proposal.status === 'active' && 
           now >= votingStart && 
           now <= votingEnd && 
           votingPower > 0 &&
           !getUserVote(proposal.id);
  };

  const canExecute = (proposal: Proposal): boolean => {
    const now = new Date();
    const executionTime = new Date(proposal.voting_end);
    executionTime.setSeconds(executionTime.getSeconds() + proposal.execution_delay);
    
    return proposal.status === 'passed' && 
           now >= executionTime &&
           proposal.votes_for > proposal.votes_against;
  };

  return (
    <div className="dao-governance">
      <div className="governance-header">
        <h1>🏛️ SecuRizz DAO Governance</h1>
        <div className="user-stats">
          <div className="stat">
            <span className="label">Your Stake:</span>
            <span className="value">{userStake.toLocaleString()} SECURIZZ</span>
          </div>
          <div className="stat">
            <span className="label">Voting Power:</span>
            <span className="value">{votingPower.toLocaleString()}</span>
          </div>
        </div>
      </div>

      {/* Create Proposal Section */}
      <div className="create-proposal">
        <h2>Create New Proposal</h2>
        <div className="proposal-form">
          <input
            type="text"
            placeholder="Proposal Title"
            value={newProposal.title}
            onChange={(e) => setNewProposal({...newProposal, title: e.target.value})}
            className="form-input"
          />
          <textarea
            placeholder="Proposal Description"
            value={newProposal.description}
            onChange={(e) => setNewProposal({...newProposal, description: e.target.value})}
            className="form-textarea"
            rows={4}
          />
          <div className="form-row">
            <label>
              Execution Delay (seconds):
              <input
                type="number"
                value={newProposal.execution_delay}
                onChange={(e) => setNewProposal({...newProposal, execution_delay: parseInt(e.target.value)})}
                className="form-input"
              />
            </label>
          </div>
          <button 
            onClick={createProposal}
            className="create-button"
            disabled={!newProposal.title || !newProposal.description}
          >
            Create Proposal
          </button>
        </div>
      </div>

      {/* Proposals List */}
      <div className="proposals-list">
        <h2>Active Proposals</h2>
        {proposals.length === 0 ? (
          <p className="no-proposals">No proposals found</p>
        ) : (
          proposals.map((proposal) => (
            <div key={proposal.id} className="proposal-card">
              <div className="proposal-header">
                <h3>{proposal.title}</h3>
                <span className={`status ${proposal.status}`}>
                  {proposal.status.toUpperCase()}
                </span>
              </div>
              
              <div className="proposal-content">
                <p>{proposal.description}</p>
                
                <div className="proposal-meta">
                  <div className="meta-item">
                    <span className="label">Proposer:</span>
                    <span className="value">{proposal.proposer.slice(0, 8)}...{proposal.proposer.slice(-8)}</span>
                  </div>
                  <div className="meta-item">
                    <span className="label">Voting Period:</span>
                    <span className="value">
                      {new Date(proposal.voting_start).toLocaleDateString()} - {new Date(proposal.voting_end).toLocaleDateString()}
                    </span>
                  </div>
                </div>
                
                <div className="voting-stats">
                  <div className="vote-bar">
                    <div className="vote-for" style={{width: `${(proposal.votes_for / proposal.total_votes) * 100}%`}}>
                      <span>For: {proposal.votes_for}</span>
                    </div>
                    <div className="vote-against" style={{width: `${(proposal.votes_against / proposal.total_votes) * 100}%`}}>
                      <span>Against: {proposal.votes_against}</span>
                    </div>
                  </div>
                  <div className="total-votes">
                    Total Votes: {proposal.total_votes}
                  </div>
                </div>
                
                <div className="proposal-actions">
                  {getUserVote(proposal.id) ? (
                    <div className="voted">
                      You voted: {getUserVote(proposal.id)?.support ? 'FOR' : 'AGAINST'}
                    </div>
                  ) : canVote(proposal) ? (
                    <div className="vote-buttons">
                      <button 
                        onClick={() => voteOnProposal(proposal.id, true)}
                        className="vote-button for"
                      >
                        Vote FOR
                      </button>
                      <button 
                        onClick={() => voteOnProposal(proposal.id, false)}
                        className="vote-button against"
                      >
                        Vote AGAINST
                      </button>
                    </div>
                  ) : (
                    <div className="cannot-vote">
                      {votingPower === 0 ? 'Stake tokens to vote' : 'Voting period ended'}
                    </div>
                  )}
                  
                  {canExecute(proposal) && (
                    <button 
                      onClick={() => executeProposal(proposal.id)}
                      className="execute-button"
                    >
                      Execute Proposal
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default DAOGovernance;
