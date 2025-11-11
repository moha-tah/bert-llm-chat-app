import type { Metadata } from "next";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";

export const metadata: Metadata = {
  title: "Ask Barfield AI",
  description: "Your intelligent document assistant powered by advanced language models",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning style={{
      "--font-excellence-text": "'Excellence in Motion Text', -apple-system, BlinkMacSystemFont, sans-serif",
      "--font-excellence-display": "'Excellence in Motion Display', -apple-system, BlinkMacSystemFont, sans-serif"
    } as React.CSSProperties}>
      <body className="antialiased">
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
