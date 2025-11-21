import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'MAF Studio - Agent Visualization',
  description: 'Real-time visualization of hierarchical multi-agent framework',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.Node;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
