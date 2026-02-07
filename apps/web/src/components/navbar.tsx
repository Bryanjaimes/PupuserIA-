"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { Menu, X, Bitcoin } from "lucide-react";

const navLinks = [
  { href: "/explore", label: "Explore" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/marketplace", label: "Marketplace" },
  { href: "/invest", label: "Invest" },
  { href: "/foundation", label: "Foundation" },
  { href: "/blog", label: "Blog" },
];

export function Navbar() {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 right-0 left-0 z-50 transition-all duration-500 ease-out ${
        scrolled
          ? "glass border-b border-white/30 shadow-lg shadow-sv-500/5"
          : "bg-transparent"
      }`}
    >
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3.5">
        {/* Logo */}
        <Link href="/" className="group flex items-center gap-3 font-bold">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-sv-500 to-sv-700 text-lg text-white shadow-lg shadow-sv-500/25 transition-transform duration-300 group-hover:scale-105">
            🇸🇻
          </span>
          <div className="hidden sm:block">
            <span className={`text-lg font-extrabold transition-colors duration-500 ${scrolled ? "text-sv-900" : "text-white"}`}>Gateway</span>
            <span className="ml-1 text-lg font-extrabold text-gold-500">ES</span>
          </div>
        </Link>

        {/* Desktop links */}
        <div className="hidden items-center gap-0.5 md:flex">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`relative rounded-xl px-4 py-2.5 text-sm font-medium transition-all duration-300 ${
                scrolled
                  ? "text-sv-700 hover:bg-sv-500/8 hover:text-sv-500"
                  : "text-white/70 hover:bg-white/10 hover:text-white"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </div>

        {/* CTA */}
        <div className="hidden items-center gap-3 md:flex">
          <div className={`flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium transition-all duration-500 ${
            scrolled
              ? "glass-gold text-gold-700"
              : "border border-gold-400/20 bg-gold-400/10 text-gold-300 backdrop-blur-sm"
          }`}>
            <Bitcoin size={13} />
            <span>BTC Ready</span>
          </div>
          <Link
            href="#waitlist"
            className={`rounded-xl px-6 py-2.5 text-sm font-semibold transition-all duration-300 ${
              scrolled
                ? "bg-gradient-to-r from-sv-500 to-sv-600 text-white shadow-lg shadow-sv-500/20 hover:shadow-xl hover:shadow-sv-500/30 hover:brightness-110"
                : "bg-white/10 text-white border border-white/15 backdrop-blur-sm hover:bg-white/20"
            }`}
          >
            Get Early Access
          </Link>
        </div>

        {/* Mobile toggle */}
        <button
          onClick={() => setOpen(!open)}
          className={`rounded-xl p-2.5 transition md:hidden ${
            scrolled ? "text-sv-700 hover:bg-sv-500/8" : "text-white/70 hover:bg-white/10"
          }`}
          aria-label="Toggle menu"
        >
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
      </nav>

      {/* Mobile menu */}
      <div
        className={`overflow-hidden transition-all duration-500 ease-out md:hidden ${
          open ? "max-h-96 opacity-100" : "max-h-0 opacity-0"
        }`}
      >
        <div className={`border-t px-6 py-5 ${
          scrolled
            ? "glass border-white/20"
            : "bg-sv-950/80 border-white/10 backdrop-blur-xl"
        }`}>
          <div className="space-y-1">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setOpen(false)}
                className={`block rounded-xl px-4 py-3 text-sm font-medium transition-all duration-200 ${
                  scrolled
                    ? "text-sv-800 hover:bg-sv-500/8 hover:text-sv-500"
                    : "text-white/70 hover:bg-white/10 hover:text-white"
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>
          <div className="mt-4 flex flex-col gap-2">
            <div className={`flex items-center justify-center gap-1.5 rounded-xl px-3 py-2.5 text-xs font-medium ${
              scrolled ? "glass-gold text-gold-700" : "border border-gold-400/20 bg-gold-400/10 text-gold-300"
            }`}>
              <Bitcoin size={13} />
              <span>Bitcoin Ready</span>
            </div>
            <Link
              href="#waitlist"
              onClick={() => setOpen(false)}
              className="block rounded-xl bg-gradient-to-r from-sv-500 to-sv-600 px-4 py-3 text-center text-sm font-semibold text-white shadow-lg shadow-sv-500/20"
            >
              Get Early Access
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}
