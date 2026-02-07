import Link from "next/link";
import {
  Globe,
  Mail,
  MapPin,
  Bitcoin,
} from "lucide-react";

const footerLinks = {
  discover: [
    { label: "Explore Map", href: "/explore" },
    { label: "Safety Dashboard", href: "/explore#safety" },
    { label: "Bitcoin Guide", href: "/blog/bitcoin-el-salvador" },
    { label: "Cost of Living", href: "/blog/cost-of-living" },
  ],
  invest: [
    { label: "Property Marketplace", href: "/marketplace" },
    { label: "Diaspora Portal", href: "/invest" },
    { label: "Book Consulting", href: "/invest#consulting" },
    { label: "Tour & Experiences", href: "/marketplace#tours" },
  ],
  foundation: [
    { label: "Impact Dashboard", href: "/foundation" },
    { label: "AI Tutoring", href: "/foundation#tutoring" },
    { label: "Partner Schools", href: "/foundation#schools" },
    { label: "Donate", href: "/foundation#donate" },
  ],
};

export function Footer() {
  return (
    <footer className="relative overflow-hidden bg-gradient-to-b from-sv-950 to-sv-950/95">
      {/* Subtle decorative glow */}
      <div className="pointer-events-none absolute top-0 left-1/2 h-px w-full max-w-4xl -translate-x-1/2 bg-gradient-to-r from-transparent via-sv-500/20 to-transparent" />

      <div className="mx-auto max-w-7xl px-6 py-16">
        <div className="grid gap-12 md:grid-cols-2 lg:grid-cols-5">
          {/* Brand */}
          <div className="lg:col-span-2">
            <div className="mb-5 flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-sv-500 to-sv-700 text-base text-white shadow-lg shadow-sv-500/20">
                🇸🇻
              </span>
              <div>
                <span className="text-lg font-extrabold text-white">Gateway</span>
                <span className="ml-1 text-lg font-extrabold text-gold-400">ES</span>
              </div>
            </div>
            <p className="mb-6 max-w-sm text-sm leading-relaxed text-white/40">
              The AI-powered platform connecting the world to El Salvador.
              Every transaction funds education for children in underserved
              communities.
            </p>
            <div className="flex items-center gap-1">
              {[
                { icon: Globe, label: "Website" },
                { icon: MapPin, label: "Location" },
                { icon: Bitcoin, label: "Bitcoin" },
                { icon: Mail, label: "Email" },
              ].map((social) => (
                <a
                  key={social.label}
                  href="#"
                  aria-label={social.label}
                  className="flex h-9 w-9 items-center justify-center rounded-lg text-white/30 transition-all duration-300 hover:bg-white/5 hover:text-gold-400"
                >
                  <social.icon size={16} />
                </a>
              ))}
            </div>
          </div>

          {/* Links */}
          {[
            { title: "Discover", links: footerLinks.discover },
            { title: "Invest", links: footerLinks.invest },
            { title: "Foundation", links: footerLinks.foundation },
          ].map((section) => (
            <div key={section.title}>
              <h4 className="mb-4 text-sm font-semibold text-white/70">{section.title}</h4>
              <ul className="space-y-3">
                {section.links.map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      className="text-sm text-white/30 transition-all duration-200 hover:text-gold-400"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="mt-14 flex flex-col items-center justify-between gap-4 border-t border-white/5 pt-8 md:flex-row">
          <p className="text-xs text-white/25">
            © 2026 Gateway El Salvador. Built with AI. For the children of El Salvador.
          </p>
          <div className="flex items-center gap-2 text-xs text-white/25">
            <span>Hecho con amor</span>
            <span className="text-sm">🇸🇻</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
