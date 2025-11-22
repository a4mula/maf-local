/** @type {import('next').NextConfig} */
const nextConfig = {
    // Disable strict mode for easier debugging during development
    reactStrictMode: true,
    // Enable standalone output for Docker deployment
    output: 'standalone',
    // Allow iframe embedding from localhost (for Streamlit integration)
    async headers() {
        return [
            {
                source: '/:path*',
                headers: [
                    {
                        key: 'X-Frame-Options',
                        value: 'ALLOWALL',
                    },
                    {
                        key: 'Content-Security-Policy',
                        value: "frame-ancestors 'self' http://localhost:* http://127.0.0.1:*",
                    },
                ],
            },
        ];
    },
};

module.exports = nextConfig;
