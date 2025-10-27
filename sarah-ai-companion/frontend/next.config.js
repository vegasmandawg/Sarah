/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    domains: ['localhost'],
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'api_gateway',
        port: '80',
        pathname: '/outputs/**',
      },
    ],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api/:path*',
      },
      {
        source: '/ws/:path*',
        destination: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8080/ws/:path*',
      },
    ]
  },
}

module.exports = nextConfig
