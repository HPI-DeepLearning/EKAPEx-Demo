import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: process.env.NEXT_PUBLIC_API_HOSTNAME || 'localhost',
        port: process.env.NEXT_PUBLIC_API_PORT || '8000',
        pathname: '/backend-fast-api/streaming/**',
      },
    ],
  },
};

export default nextConfig;
