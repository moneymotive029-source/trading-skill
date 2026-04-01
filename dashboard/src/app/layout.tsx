import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Trading Dashboard | Financial Intelligence",
  description: "Real-time trading signals and portfolio analytics powered by multi-agent AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased bg-slate-950 text-slate-100">
        {children}
      </body>
    </html>
  );
}
