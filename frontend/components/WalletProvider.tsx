import React, { createContext, useContext, useEffect, useState } from 'react';
import { ConnectionProvider, WalletProvider } from '@solana/wallet-adapter-react';
import { WalletAdapterNetwork } from '@solana/wallet-adapter-base';
import { PhantomWalletAdapter, SolflareWalletAdapter, TorusWalletAdapter } from '@solana/wallet-adapter-wallets';
import { WalletModalProvider } from '@solana/wallet-adapter-react-ui';
import { clusterApiUrl } from '@solana/web3.js';

// Import wallet adapters
import { PhantomWalletAdapter as Phantom } from '@solana/wallet-adapter-phantom';
import { SolflareWalletAdapter as Solflare } from '@solana/wallet-adapter-solflare';
import { TorusWalletAdapter as Torus } from '@solana/wallet-adapter-torus';
import { LedgerWalletAdapter } from '@solana/wallet-adapter-ledger';
import { MathWalletAdapter } from '@solana/wallet-adapter-mathwallet';

interface WalletContextType {
  connected: boolean;
  publicKey: string | null;
  balance: number;
  connect: () => Promise<void>;
  disconnect: () => Promise<void>;
  signMessage: (message: string) => Promise<string>;
  signTransaction: (transaction: any) => Promise<any>;
  requestAirdrop: () => Promise<void>;
}

const WalletContext = createContext<WalletContextType | null>(null);

export const useWallet = () => {
  const context = useContext(WalletContext);
  if (!context) {
    throw new Error('useWallet must be used within WalletProvider');
  }
  return context;
};

interface WalletProviderProps {
  children: React.ReactNode;
}

export const SecuRizzWalletProvider: React.FC<WalletProviderProps> = ({ children }) => {
  const [connected, setConnected] = useState(false);
  const [publicKey, setPublicKey] = useState<string | null>(null);
  const [balance, setBalance] = useState(0);
  const [connection] = useState(new Connection(clusterApiUrl('devnet')));

  // Configure wallets
  const wallets = [
    new Phantom(),
    new Solflare(),
    new Torus(),
    new LedgerWalletAdapter(),
    new MathWalletAdapter(),
  ];

  const network = WalletAdapterNetwork.Devnet;
  const endpoint = clusterApiUrl(network);

  useEffect(() => {
    // Check if wallet is already connected
    const checkConnection = async () => {
      if (typeof window !== 'undefined' && window.solana?.isConnected) {
        setConnected(true);
        setPublicKey(window.solana.publicKey?.toString() || null);
        await updateBalance();
      }
    };

    checkConnection();
  }, []);

  const updateBalance = async () => {
    if (publicKey) {
      try {
        const balance = await connection.getBalance(new PublicKey(publicKey));
        setBalance(balance / 1e9); // Convert lamports to SOL
      } catch (error) {
        console.error('Failed to get balance:', error);
      }
    }
  };

  const connect = async () => {
    try {
      if (window.solana && window.solana.isPhantom) {
        const response = await window.solana.connect();
        setConnected(true);
        setPublicKey(response.publicKey.toString());
        await updateBalance();
      } else {
        throw new Error('Phantom wallet not found');
      }
    } catch (error) {
      console.error('Failed to connect wallet:', error);
      throw error;
    }
  };

  const disconnect = async () => {
    try {
      if (window.solana) {
        await window.solana.disconnect();
        setConnected(false);
        setPublicKey(null);
        setBalance(0);
      }
    } catch (error) {
      console.error('Failed to disconnect wallet:', error);
    }
  };

  const signMessage = async (message: string): Promise<string> => {
    try {
      if (!window.solana || !connected) {
        throw new Error('Wallet not connected');
      }

      const messageBytes = new TextEncoder().encode(message);
      const signature = await window.solana.signMessage(messageBytes);
      return signature.toString('base64');
    } catch (error) {
      console.error('Failed to sign message:', error);
      throw error;
    }
  };

  const signTransaction = async (transaction: any): Promise<any> => {
    try {
      if (!window.solana || !connected) {
        throw new Error('Wallet not connected');
      }

      const signedTransaction = await window.solana.signTransaction(transaction);
      return signedTransaction;
    } catch (error) {
      console.error('Failed to sign transaction:', error);
      throw error;
    }
  };

  const requestAirdrop = async () => {
    try {
      if (!publicKey) {
        throw new Error('Wallet not connected');
      }

      const signature = await connection.requestAirdrop(
        new PublicKey(publicKey),
        1e9 // 1 SOL
      );

      await connection.confirmTransaction(signature);
      await updateBalance();
    } catch (error) {
      console.error('Failed to request airdrop:', error);
      throw error;
    }
  };

  const contextValue: WalletContextType = {
    connected,
    publicKey,
    balance,
    connect,
    disconnect,
    signMessage,
    signTransaction,
    requestAirdrop,
  };

  return (
    <ConnectionProvider endpoint={endpoint}>
      <WalletProvider wallets={wallets} autoConnect>
        <WalletModalProvider>
          <WalletContext.Provider value={contextValue}>
            {children}
          </WalletContext.Provider>
        </WalletModalProvider>
      </WalletProvider>
    </ConnectionProvider>
  );
};

// Mobile-optimized wallet connection component
export const MobileWalletConnection: React.FC = () => {
  const { connected, publicKey, balance, connect, disconnect, requestAirdrop } = useWallet();

  if (!connected) {
    return (
      <div className="mobile-wallet-connection">
        <div className="wallet-prompt">
          <h3>Connect Your Wallet</h3>
          <p>Connect your Solana wallet to start auditing contracts</p>
          
          <div className="wallet-options">
            <button 
              onClick={connect}
              className="connect-button"
            >
              Connect Phantom
            </button>
            
            <button 
              onClick={connect}
              className="connect-button secondary"
            >
              Connect Solflare
            </button>
          </div>
          
          <div className="wallet-features">
            <div className="feature">
              <span className="icon">🔒</span>
              <span>Secure & Private</span>
            </div>
            <div className="feature">
              <span className="icon">⚡</span>
              <span>Fast Transactions</span>
            </div>
            <div className="feature">
              <span className="icon">🌐</span>
              <span>Web3 Native</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mobile-wallet-connected">
      <div className="wallet-info">
        <div className="wallet-address">
          <span className="label">Address:</span>
          <span className="address">{publicKey?.slice(0, 8)}...{publicKey?.slice(-8)}</span>
        </div>
        
        <div className="wallet-balance">
          <span className="label">Balance:</span>
          <span className="balance">{balance.toFixed(4)} SOL</span>
        </div>
      </div>
      
      <div className="wallet-actions">
        <button 
          onClick={requestAirdrop}
          className="action-button"
        >
          Get Test SOL
        </button>
        
        <button 
          onClick={disconnect}
          className="action-button secondary"
        >
          Disconnect
        </button>
      </div>
    </div>
  );
};

// Dark mode support
export const DarkModeToggle: React.FC = () => {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      setIsDark(true);
      document.documentElement.classList.add('dark');
    }
  }, []);

  const toggleDarkMode = () => {
    setIsDark(!isDark);
    if (!isDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  };

  return (
    <button 
      onClick={toggleDarkMode}
      className="dark-mode-toggle"
      aria-label="Toggle dark mode"
    >
      {isDark ? '☀️' : '🌙'}
    </button>
  );
};

// Mobile-responsive navigation
export const MobileNavigation: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <nav className="mobile-nav">
      <div className="nav-header">
        <div className="logo">
          <span className="logo-icon">🔒</span>
          <span className="logo-text">SecuRizz</span>
        </div>
        
        <button 
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          className="menu-toggle"
          aria-label="Toggle menu"
        >
          <span className="hamburger"></span>
          <span className="hamburger"></span>
          <span className="hamburger"></span>
        </button>
      </div>
      
      {isMenuOpen && (
        <div className="mobile-menu">
          <a href="/" className="menu-item">Home</a>
          <a href="/audit" className="menu-item">Audit Contract</a>
          <a href="/reports" className="menu-item">My Reports</a>
          <a href="/staking" className="menu-item">Staking</a>
          <a href="/governance" className="menu-item">Governance</a>
          <a href="/profile" className="menu-item">Profile</a>
        </div>
      )}
    </nav>
  );
};

export default SecuRizzWalletProvider;
