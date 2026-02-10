import type { Metadata } from "next";
import { Inter, Playfair_Display } from "next/font/google";
import { Navbar } from "@/components/navbar";
import { Footer } from "@/components/footer";
import { LanguageProvider } from "@/context/language-context";
import { LanguageToggle } from "@/components/language-toggle";
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
    default: "Gateway El Salvador — Discover, Invest, Transform",
    template: "%s | Gateway El Salvador",
  },
  description:
    "The definitive digital gateway to El Salvador. Explore the country, book experiences, invest in real estate, and fund education for Salvadoran children.",
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
    siteName: "Gateway El Salvador",
    title: "Gateway El Salvador — Discover, Invest, Transform",
    description:
      "The AI-powered platform connecting the world to El Salvador. Every transaction funds education for children.",
  },
  twitter: {
    card: "summary_large_image",
    title: "Gateway El Salvador",
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
      <body className="min-h-screen bg-white font-sans">
        <LanguageProvider>
          <Navbar />
          {children}
          <Footer />
          <LanguageToggle />
        </LanguageProvider>
      </body>
    </html>
  );
}
