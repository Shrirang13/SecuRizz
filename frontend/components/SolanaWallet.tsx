import React, { useState, useEffect } from 'react';
import { Connection, PublicKey, Transaction, SystemProgram, LAMPORTS_PER_SOL } from '@solana/web3.js';
import { WalletAdapterNetwork } from '@solana/wallet-adapter-base';
import { useWallet } from '@solana/wallet-adapter-react';
import { WalletMultiButton, WalletDisconnectButton } from '@solana/wallet-adapter-react-ui';

interface SolanaWalletProps {
  onWalletConnect?: (publicKey: PublicKey) => void;
  onWalletDisconnect?: () => void;
}

export default function SolanaWallet({ onWalletConnect, onWalletDisconnect }: SolanaWalletProps) {
  const { publicKey, connected, signTransaction, signAllTransactions } = useWallet();
  const [balance, setBalance] = useState<number>(0);
  const [connection] = useState(new Connection(
    process.env.NEXT_PUBLIC_SOLANA_RPC_URL || 'https://api.devnet.solana.com'
  ));

  useEffect(() => {
    if (publicKey) {
      getBalance();
      onWalletConnect?.(publicKey);
    } else {
      setBalance(0);
      onWalletDisconnect?.();
    }
  }, [publicKey, connection]);

  const getBalance = async () => {
    if (publicKey) {
      try {
        const balance = await connection.getBalance(publicKey);
        setBalance(balance / LAMPORTS_PER_SOL);
      } catch (error) {
        console.error('Failed to get balance:', error);
      }
    }
  };

  const requestAirdrop = async () => {
    if (publicKey) {
      try {
        const signature = await connection.requestAirdrop(publicKey, LAMPORTS_PER_SOL);
        await connection.confirmTransaction(signature);
        await getBalance();
        alert('Airdrop successful!');
      } catch (error) {
        console.error('Airdrop failed:', error);
        alert('Airdrop failed. Please try again.');
      }
    }
  };

  const signMessage = async () => {
    if (publicKey && signTransaction) {
      try {
        const message = new TextEncoder().encode('SecuRizz Audit Verification');
        // Note: This is a simplified example. In practice, you'd use a proper message signing method
        alert('Message signing would be implemented here');
      } catch (error) {
        console.error('Message signing failed:', error);
      }
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 text-white">
      <h3 className="text-xl font-bold mb-4">Solana Wallet</h3>
      
      {!connected ? (
        <div className="text-center">
          <p className="mb-4 text-gray-300">Connect your Solana wallet to continue</p>
          <WalletMultiButton className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded" />
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-300">Connected:</span>
            <span className="font-mono text-sm">{publicKey?.toString().slice(0, 8)}...{publicKey?.toString().slice(-8)}</span>
          </div>
          
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-300">Balance:</span>
            <span className="font-bold">{balance.toFixed(4)} SOL</span>
          </div>
          
          <div className="flex space-x-2">
            <button
              onClick={requestAirdrop}
              className="bg-green-600 hover:bg-green-700 text-white text-sm py-1 px-3 rounded"
            >
              Airdrop 1 SOL
            </button>
            
            <button
              onClick={signMessage}
              className="bg-blue-600 hover:bg-blue-700 text-white text-sm py-1 px-3 rounded"
            >
              Sign Message
            </button>
          </div>
          
          <WalletDisconnectButton className="bg-red-600 hover:bg-red-700 text-white text-sm py-1 px-3 rounded w-full" />
        </div>
      )}
    </div>
  );
}
