/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    NEXT_PUBLIC_BACKEND_URL: process.env.BACKEND_URL || 'http://localhost:8000',
    NEXT_PUBLIC_SOLANA_CLUSTER: process.env.SOLANA_CLUSTER || 'https://api.devnet.solana.com',
    NEXT_PUBLIC_PROGRAM_ID: process.env.SOLANA_PROGRAM_ID || 'ReplaceWithDeployedProgramId',
  },
}

module.exports = nextConfig
