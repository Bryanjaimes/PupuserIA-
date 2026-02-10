"use client";

import { useLanguage } from "@/context/language-context";

export default function BlogPage() {
  const { t } = useLanguage();

  const categories = [
    { key: "blog.all" },
    { key: "blog.travel" },
    { key: "blog.investment" },
    { key: "blog.culture" },
    { key: "blog.safety" },
    { key: "blog.bitcoin" },
  ];

  const posts = [
    { titleKey: "blog.post1", tag: "Bitcoin", emoji: "₿" },
    { titleKey: "blog.post2", tag: "Travel", emoji: "💰" },
    { titleKey: "blog.post3", tag: "Safety", emoji: "🛡️" },
  ];

  return (
    <main className="min-h-screen bg-gradient-to-b from-white via-sv-50 to-white pt-20">
      <div className="mx-auto max-w-4xl px-6 py-24">
        <div className="mb-3 inline-flex items-center gap-2 text-sm font-semibold tracking-wider text-sv-500 uppercase">
          <span className="h-px w-8 bg-sv-500/30" />
          {t("blog.stories")}
          <span className="h-px w-8 bg-sv-500/30" />
        </div>
        <h1 className="mb-4 text-4xl font-extrabold text-sv-950 md:text-5xl">{t("blog.title")}</h1>
        <p className="mb-12 max-w-2xl text-lg text-sv-700/50">
          {t("blog.desc")}
        </p>

        {/* Category pills */}
        <div className="mb-10 flex flex-wrap gap-2">
          {categories.map((cat, i) => (
            <button
              key={cat.key}
              className={`rounded-full px-5 py-2 text-sm font-medium transition-all duration-300 ${
                i === 0
                  ? "bg-gradient-to-r from-sv-500 to-sv-600 text-white shadow-lg shadow-sv-500/20"
                  : "glass-card text-sv-700 hover:shadow-md"
              }`}
            >
              {t(cat.key)}
            </button>
          ))}
        </div>

        {/* Placeholder posts */}
        <div className="space-y-4">
          {posts.map((post) => (
            <div key={post.titleKey} className="glass-card rounded-2xl p-6 transition-all duration-500 hover:shadow-xl hover:-translate-y-0.5">
              <div className="flex items-start gap-4">
                <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-sv-100 to-sv-50 text-xl">
                  {post.emoji}
                </div>
                <div>
                  <h3 className="mb-1 text-lg font-bold text-sv-900">{t(post.titleKey)}</h3>
                  <div className="flex items-center gap-3">
                    <span className="rounded-full bg-sv-500/8 px-2.5 py-0.5 text-xs font-medium text-sv-500">{post.tag}</span>
                    <span className="text-xs text-sv-600/40">{t("blog.comingSoon")}</span>
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
