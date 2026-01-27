import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8000/api/:path*", // Proxy to Backend
      },
      {
        source: "/opentargets/:path*",
        destination: "http://127.0.0.1:8000/opentargets/:path*", // Proxy to Backend
      },
      {
        source: "/agent/:path*",
        destination: "http://127.0.0.1:8000/agent/:path*", // Proxy to Backend
      },
      {
        source: "/protein/:path*",
        destination: "http://127.0.0.1:8000/protein/:path*", // Proxy to Backend
      }
    ];
  },
};

export default nextConfig;
