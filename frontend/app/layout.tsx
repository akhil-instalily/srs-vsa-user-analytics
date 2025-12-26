import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Auth0ProviderWrapper } from "@/components/Auth0ProviderWrapper";
import { AuthGuard } from "@/components/AuthGuard";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "SRS VSA Analytics",
  description: "Analytics dashboard for Virtual Shopping Assistant interactions and performance metrics",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <Auth0ProviderWrapper>
          <AuthGuard>{children}</AuthGuard>
        </Auth0ProviderWrapper>
      </body>
    </html>
  );
}
