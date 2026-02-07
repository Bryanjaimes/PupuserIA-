import { ShoppingBag, Home, Plane } from "lucide-react";

export default function MarketplacePage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-white via-sv-50 to-white pt-20">
      <div className="mx-auto max-w-7xl px-6 py-24">
        <div className="mb-3 inline-flex items-center gap-2 text-sm font-semibold tracking-wider text-gold-600 uppercase">
          <span className="h-px w-8 bg-gold-500/30" />
          Commerce
          <span className="h-px w-8 bg-gold-500/30" />
        </div>
        <h1 className="mb-4 text-4xl font-extrabold text-sv-950 md:text-5xl">
          Marketplace
        </h1>
        <p className="mb-12 max-w-2xl text-lg text-sv-700/50">
          Tours, properties, and investment opportunities — all in one place.
        </p>

        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {[
            { icon: Plane, title: "Tours & Experiences", desc: "Book curated adventures across El Salvador with instant confirmation", emoji: "✈️" },
            { icon: Home, title: "Properties", desc: "Browse real estate with AI-powered valuations — no MLS required", emoji: "🏡" },
            { icon: ShoppingBag, title: "Diaspora Portal", desc: "Invest in Salvadoran real estate from $150/month, anywhere in the world", emoji: "💼" },
          ].map((card) => (
            <div key={card.title} className="glass-card rounded-2xl p-8 transition-all duration-500 hover:shadow-xl hover:-translate-y-1">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-gold-100 to-gold-50 text-xl">
                {card.emoji}
              </div>
              <h3 className="mb-2 text-lg font-bold text-sv-900">{card.title}</h3>
              <p className="text-sm leading-relaxed text-sv-700/50">{card.desc}</p>
              <div className="mt-4 inline-flex items-center rounded-full bg-gold-500/10 px-3 py-1 text-xs font-medium text-gold-700">
                Coming soon
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
