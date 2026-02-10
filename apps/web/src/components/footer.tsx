"use client";

import Link from "next/link";
import {
  Globe,
  Mail,
  MapPin,
  Bitcoin,
} from "lucide-react";
import { useLanguage } from "@/context/language-context";

export function Footer() {
  const { t } = useLanguage();

  const footerLinks = {
    discover: [
      { labelKey: "footer.exploreMap", href: "/explore" },
      { labelKey: "footer.safetyDashboard", href: "/explore#safety" },
      { labelKey: "footer.bitcoinGuide", href: "/blog/bitcoin-el-salvador" },
      { labelKey: "footer.costOfLiving", href: "/blog/cost-of-living" },
    ],
    invest: [
      { labelKey: "footer.propertyMarketplace", href: "/marketplace" },
      { labelKey: "footer.diasporaPortal", href: "/invest" },
      { labelKey: "footer.bookConsulting", href: "/invest#consulting" },
      { labelKey: "footer.tourExperiences", href: "/marketplace#tours" },
    ],
    foundation: [
      { labelKey: "footer.impactDashboard", href: "/foundation" },
      { labelKey: "footer.aiTutoring", href: "/foundation#tutoring" },
      { labelKey: "footer.partnerSchools", href: "/foundation#schools" },
      { labelKey: "footer.donate", href: "/foundation#donate" },
    ],
  };

  return (
    <footer className="border-t border-gray-200 bg-sv-950">
      <div className="mx-auto max-w-7xl px-6 py-16">
        <div className="grid gap-12 md:grid-cols-2 lg:grid-cols-5">
          {/* Brand */}
          <div className="lg:col-span-2">
            <div className="mb-5 flex items-center gap-2.5">
              <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-sv-500 text-base text-white">
                🇸🇻
              </span>
              <div>
                <span className="text-lg font-bold text-white">Gateway</span>
                <span className="ml-1 text-lg font-bold text-gold-400">ES</span>
              </div>
            </div>
            <p className="mb-6 max-w-sm text-sm leading-relaxed text-white/40">
              {t("footer.desc")}
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
                  className="flex h-9 w-9 items-center justify-center rounded-md text-white/30 transition-colors hover:bg-white/5 hover:text-gold-400"
                >
                  <social.icon size={16} />
                </a>
              ))}
            </div>
          </div>

          {/* Links */}
          {[
            { titleKey: "footer.discover", links: footerLinks.discover },
            { titleKey: "footer.invest", links: footerLinks.invest },
            { titleKey: "footer.foundation", links: footerLinks.foundation },
          ].map((section) => (
            <div key={section.titleKey}>
              <h4 className="mb-4 text-xs font-semibold uppercase tracking-wider text-white/50">{t(section.titleKey)}</h4>
              <ul className="space-y-3">
                {section.links.map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      className="text-sm text-white/30 transition-colors hover:text-gold-400"
                    >
                      {t(link.labelKey)}
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
            {t("footer.copyright")}
          </p>
          <div className="flex items-center gap-4 text-xs text-white/25">
            <span className="uppercase tracking-wider">{t("footer.engineered")}</span>
            <span className="text-sm">🇸🇻</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
