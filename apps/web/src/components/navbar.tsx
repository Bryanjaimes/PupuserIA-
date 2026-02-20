"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { Menu, X, Bitcoin } from "lucide-react";
import { useTranslations } from "next-intl";

const navLinkKeys = [
  { href: "/explore", labelKey: "nav.explore" },
  { href: "/dashboard", labelKey: "nav.dashboard" },
  { href: "/marketplace", labelKey: "nav.marketplace" },
  { href: "/invest", labelKey: "nav.invest" },
  { href: "/foundation", labelKey: "nav.foundation" },
  { href: "/blog", labelKey: "nav.blog" },
];

export function Navbar() {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const t = useTranslations();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 right-0 left-0 z-50 transition-all duration-300 ${
        scrolled
          ? "border-b border-white/10 bg-[#0a0a0a] shadow-sm"
          : "bg-black/95 backdrop-blur-sm"
      }`}
    >
      {/* Top gov bar */}
      <div className="border-b border-white/5 bg-sv-950">
        <div className="mx-auto flex max-w-7xl items-center px-6 py-1.5">
          <span className="text-[11px] font-medium tracking-wide text-white/60">
            🇸🇻 {t("nav.govBar")}
          </span>
        </div>
      </div>

      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3">
        {/* Logo */}
        <Link href="/" className="group flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center text-2xl">
            🇸🇻
          </span>
          <div>
            <span className="text-lg font-bold tracking-tight text-white/90">Pupuser</span><span className="text-lg font-bold text-gold-500">IA</span>
          </div>
        </Link>

        {/* Desktop links */}
        <div className="hidden items-center gap-1 md:flex">
          {navLinkKeys.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="rounded-md px-3.5 py-2 text-sm font-medium text-white/60 transition-colors hover:bg-white/5 hover:text-gold-400"
            >
              {t(link.labelKey)}
            </Link>
          ))}
        </div>

        {/* CTA */}
        <div className="hidden items-center gap-3 md:flex">
          <div className="flex items-center gap-1.5 rounded-md border border-gold-400/30 bg-gold-500/10 px-3 py-1.5 text-xs font-semibold text-gold-400">
            <Bitcoin size={13} />
            <span>{t("nav.btcReady")}</span>
          </div>
          <Link
            href="#waitlist"
            className="rounded-md bg-sv-500 px-5 py-2 text-sm font-semibold text-white transition-all hover:bg-sv-600"
          >
            {t("nav.earlyAccess")}
          </Link>
        </div>

        {/* Mobile toggle */}
        <button
          onClick={() => setOpen(!open)}
          className="rounded-md p-2 text-white/60 transition hover:bg-white/5 md:hidden"
          aria-label="Toggle menu"
        >
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
      </nav>

      {/* Mobile menu */}
      <div
        className={`overflow-hidden transition-all duration-300 md:hidden ${
          open ? "max-h-96 opacity-100" : "max-h-0 opacity-0"
        }`}
      >
        <div className="border-t border-white/5 bg-[#0a0a0a] px-6 py-4">
          <div className="space-y-1">
            {navLinkKeys.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setOpen(false)}
                className="block rounded-md px-3.5 py-2.5 text-sm font-medium text-white/60 transition-colors hover:bg-white/5 hover:text-gold-400"
              >
                {t(link.labelKey)}
              </Link>
            ))}
          </div>
          <div className="mt-4 flex flex-col gap-2">
            <div className="flex items-center justify-center gap-1.5 rounded-md border border-gold-400/30 bg-gold-500/10 px-3 py-2 text-xs font-semibold text-gold-400">
              <Bitcoin size={13} />
              <span>{t("nav.bitcoinReady")}</span>
            </div>
            <Link
              href="#waitlist"
              onClick={() => setOpen(false)}
              className="block rounded-md bg-sv-500 px-4 py-2.5 text-center text-sm font-semibold text-white hover:bg-sv-600"
            >
              {t("nav.earlyAccess")}
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}
