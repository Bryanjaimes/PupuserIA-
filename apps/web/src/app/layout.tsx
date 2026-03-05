import type { Metadata } from "next";
import { Inter, Playfair_Display } from "next/font/google";
import { Navbar } from "@/components/navbar";
import { Footer } from "@/components/footer";
import { LanguageProvider } from "@/context/language-provider";
import { LanguageToggle } from "@/components/language-toggle";
import { AnalyticsProvider } from "@/components/analytics-provider";
import { ViewModeProvider } from "@/context/view-mode";
import "./globals.css";

const inter = Inter({
  subsets: ["latin", "latin-ext"],
  variable: "--font-sans",
  display: "swap",
});

const playfair = Playfair_Display({
  subsets: ["latin"],
  variable: "--font-serif",
  display: "swap",
  weight: ["400", "600", "700", "800", "900"],
});

export const metadata: Metadata = {
  title: {
    default: "PupuserIA — Discover, Invest, Transform",
    template: "%s | PupuserIA",
  },
  description:
    "PupuserIA — the AI-powered platform connecting the world to El Salvador. Explore, invest, and fund education for Salvadoran children.",
  keywords: [
    "El Salvador",
    "tourism",
    "real estate",
    "investment",
    "diaspora",
    "Bitcoin",
    "education",
    "AI",
    "travel",
  ],
  authors: [{ name: "PupuserIA" }],
  openGraph: {
    type: "website",
    locale: "en_US",
    alternateLocale: "es_SV",
    siteName: "PupuserIA",
    title: "PupuserIA — Discover, Invest, Transform",
    description:
      "The AI-powered platform connecting the world to El Salvador. Every transaction funds education for children.",
  },
  twitter: {
    card: "summary_large_image",
    title: "PupuserIA",
    description:
      "Discover El Salvador. Invest in its future. Fund education for its children.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${playfair.variable}`}>
      <body className="min-h-screen bg-black font-sans">
        <LanguageProvider>
          <ViewModeProvider>
            <AnalyticsProvider>
              <Navbar />
              {children}
              <Footer />
              <LanguageToggle />
            </AnalyticsProvider>
          </ViewModeProvider>
        </LanguageProvider>
      </body>
    </html>
  );
}
