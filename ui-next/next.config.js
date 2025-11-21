/** @type {import('next').NextConfig} */
const nextConfig = {
    // Disable strict mode for easier debugging during development
    reactStrictMode: true,
    // Enable standalone output for Docker deployment
    output: 'standalone',
};

module.exports = nextConfig;
