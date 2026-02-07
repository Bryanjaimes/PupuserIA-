export default function BlogPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-white via-sv-50 to-white pt-20">
      <div className="mx-auto max-w-4xl px-6 py-24">
        <div className="mb-3 inline-flex items-center gap-2 text-sm font-semibold tracking-wider text-sv-500 uppercase">
          <span className="h-px w-8 bg-sv-500/30" />
          Stories
          <span className="h-px w-8 bg-sv-500/30" />
        </div>
        <h1 className="mb-4 text-4xl font-extrabold text-sv-950 md:text-5xl">Blog</h1>
        <p className="mb-12 max-w-2xl text-lg text-sv-700/50">
          Guides, deep-dives, and stories about El Salvador.
        </p>

        {/* Category pills */}
        <div className="mb-10 flex flex-wrap gap-2">
          {["All", "Travel", "Investment", "Culture", "Safety", "Bitcoin"].map((cat, i) => (
            <button
              key={cat}
              className={`rounded-full px-5 py-2 text-sm font-medium transition-all duration-300 ${
                i === 0
                  ? "bg-gradient-to-r from-sv-500 to-sv-600 text-white shadow-lg shadow-sv-500/20"
                  : "glass-card text-sv-700 hover:shadow-md"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Placeholder posts */}
        <div className="space-y-4">
          {[
            { title: "The Complete Bitcoin Guide for El Salvador", tag: "Bitcoin", date: "Coming soon", emoji: "₿" },
            { title: "Cost of Living in El Salvador: 2026 Edition", tag: "Travel", date: "Coming soon", emoji: "💰" },
            { title: "Safety Transformation: By the Numbers", tag: "Safety", date: "Coming soon", emoji: "🛡️" },
          ].map((post) => (
            <div key={post.title} className="glass-card rounded-2xl p-6 transition-all duration-500 hover:shadow-xl hover:-translate-y-0.5">
              <div className="flex items-start gap-4">
                <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-sv-100 to-sv-50 text-xl">
                  {post.emoji}
                </div>
                <div>
                  <h3 className="mb-1 text-lg font-bold text-sv-900">{post.title}</h3>
                  <div className="flex items-center gap-3">
                    <span className="rounded-full bg-sv-500/8 px-2.5 py-0.5 text-xs font-medium text-sv-500">{post.tag}</span>
                    <span className="text-xs text-sv-600/40">{post.date}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
