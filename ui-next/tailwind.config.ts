import type { Config } from "tailwindcss";

const config: Config = {
    content: [
        "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "var(--background)",
                foreground: "var(--foreground)",
                // Agent status colors
                'agent-active': '#4CAF50',
                'agent-waiting': '#FFC107',
                'agent-idle': '#9E9E9E',
                'agent-error': '#F44336',
                // Tier colors
                'tier-liaison': '#4CAF50',
                'tier-pl': '#2196F3',
                'tier-dl': '#FF9800',
                'tier-executor': '#9C27B0',
            },
        },
    },
    plugins: [],
};
export default config;
