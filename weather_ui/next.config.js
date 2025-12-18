/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: '*',
        port: '8000',
        pathname: '/backend-fast-api/**',
      },
    ],
  },
}

module.exports = nextConfig 