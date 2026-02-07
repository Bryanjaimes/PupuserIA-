/**
 * Static metrics for El Salvador that don't have a live World Bank API indicator.
 * Every entry has a source and year for transparency.
 *
 * These supplement the live World Bank data on the dashboard.
 */

export interface StaticMetric {
  label: string;
  value: string;
  numericValue?: number;
  unit: string;
  year: string;
  source: string;
  sourceUrl?: string;
  section: string;
  subsection?: string;
  trend?: "up" | "down" | "stable";
  trendGood?: boolean; // whether the trend direction is positive
}

export const STATIC_METRICS: StaticMetric[] = [
  // ── I-A Macroeconomic (supplementary) ──
  { label: "Sovereign Credit Rating (Moody's)", value: "Caa3 → Caa1 (upgrade 2024)", unit: "rating", year: "2024", source: "Moody's", sourceUrl: "https://www.moodys.com", section: "macro", trend: "up", trendGood: true },
  { label: "Sovereign Credit Rating (S&P)", value: "B- (stable)", unit: "rating", year: "2024", source: "S&P Global", section: "macro" },
  { label: "Sovereign Credit Rating (Fitch)", value: "B (positive outlook)", unit: "rating", year: "2024", source: "Fitch Ratings", section: "macro", trend: "up", trendGood: true },
  { label: "Currency", value: "US Dollar (USD) — since 2001", unit: "text", year: "2001", source: "BCR El Salvador", section: "macro" },
  { label: "Central Bank Interest Rate", value: "N/A (dollarized — follows US Fed)", unit: "text", year: "2025", source: "BCR", section: "macro" },
  { label: "Budget Deficit (% GDP)", value: "-2.7%", numericValue: -2.7, unit: "%", year: "2024", source: "IMF Fiscal Monitor", sourceUrl: "https://www.imf.org", section: "macro", trend: "down", trendGood: true },

  // ── I-B Business & Innovation ──
  { label: "Ease of Doing Business (WB legacy)", value: "91st / 190", numericValue: 91, unit: "rank", year: "2020", source: "World Bank (discontinued)", section: "business" },
  { label: "Business Confidence Index", value: "52.4", numericValue: 52.4, unit: "index", year: "2024", source: "BCR El Salvador", section: "business", trend: "up", trendGood: true },
  { label: "Corporate Tax Rate", value: "30%", numericValue: 30, unit: "%", year: "2025", source: "Deloitte", section: "business" },
  { label: "VAT Rate", value: "13%", numericValue: 13, unit: "%", year: "2025", source: "Deloitte", section: "business" },
  { label: "Start-up Density (per 1,000)", value: "1.2", numericValue: 1.2, unit: "per1k", year: "2023", source: "IDB", section: "business" },
  { label: "Economic Complexity Index (ECI)", value: "-0.38", numericValue: -0.38, unit: "index", year: "2022", source: "OEC / Harvard Growth Lab", sourceUrl: "https://oec.world/en/profile/country/slv", section: "business" },
  { label: "Market Cap (BVES)", value: "~$8.2B", numericValue: 8.2e9, unit: "usd", year: "2024", source: "Bolsa de Valores de ES", section: "business" },

  // ── I-C Financial Health ──
  { label: "Median Household Income", value: "$4,400/yr", numericValue: 4400, unit: "usd", year: "2023", source: "DIGESTYC / EHPM", section: "financial" },
  { label: "Minimum Wage (commerce)", value: "$365/mo", numericValue: 365, unit: "usd/mo", year: "2025", source: "Ministry of Labor", section: "financial" },
  { label: "Personal Savings Rate", value: "5.3%", numericValue: 5.3, unit: "%", year: "2023", source: "BCR", section: "financial" },
  { label: "Consumer Confidence Index", value: "48.7", numericValue: 48.7, unit: "index", year: "2024", source: "BCR / FUSADES", section: "financial", trend: "up", trendGood: true },
  { label: "Household Debt to Income", value: "~38%", numericValue: 38, unit: "%", year: "2023", source: "BCR", section: "financial" },
  { label: "Bankruptcy Rate", value: "Low (limited formal system)", unit: "text", year: "2024", source: "CNR", section: "financial" },

  // ── II-A Health — Mortality ──
  { label: "Healthy Life Expectancy (HALE)", value: "63.4 yrs", numericValue: 63.4, unit: "years", year: "2021", source: "WHO GHO", sourceUrl: "https://www.who.int/data/gho", section: "health_mortality" },
  { label: "Preventable Death Rate", value: "198 per 100k", numericValue: 198, unit: "per100k", year: "2021", source: "WHO", section: "health_mortality" },

  // ── II-B Disease ──
  { label: "Obesity Rate (adults)", value: "26.4%", numericValue: 26.4, unit: "%", year: "2022", source: "WHO GHO", section: "health_disease", trend: "up", trendGood: false },
  { label: "Mental Health Disorders (%)", value: "~15%", numericValue: 15, unit: "%", year: "2022", source: "PAHO / WHO", section: "health_disease" },
  { label: "Substance Abuse Rate", value: "~4.2% alcohol use disorder", numericValue: 4.2, unit: "%", year: "2021", source: "WHO", section: "health_disease" },
  { label: "Cancer Incidence (per 100k)", value: "117.8", numericValue: 117.8, unit: "per100k", year: "2022", source: "IARC / Globocan", section: "health_disease" },
  { label: "Cardiovascular Disease Deaths (per 100k)", value: "139.5", numericValue: 139.5, unit: "per100k", year: "2021", source: "WHO", section: "health_disease" },

  // ── II-C Healthcare Access ──
  { label: "UHC Service Coverage Index", value: "67", numericValue: 67, unit: "index", year: "2021", source: "WHO / World Bank", section: "health_access" },
  { label: "Access to Essential Medicines", value: "Moderate (~65%)", numericValue: 65, unit: "%", year: "2022", source: "PAHO", section: "health_access" },
  { label: "Ambulance Response Time", value: "~12-18 min (urban)", unit: "minutes", year: "2024", source: "ISSS / Ministry of Health", section: "health_access" },
  { label: "Wait Times (specialist)", value: "~30-90 days (public)", unit: "days", year: "2024", source: "ISSS", section: "health_access" },

  // ── III Education ──
  { label: "Mean Years of Schooling (25+)", value: "7.1 yrs", numericValue: 7.1, unit: "years", year: "2022", source: "UNDP HDR", sourceUrl: "https://hdr.undp.org", section: "education_access" },
  { label: "PISA Scores", value: "Not yet participating", unit: "text", year: "2025", source: "OECD PISA", section: "education_quality" },
  { label: "STEM Graduates (% of tertiary)", value: "~18%", numericValue: 18, unit: "%", year: "2022", source: "MINED", section: "education_quality" },
  { label: "Quality of Vocational Training", value: "INSAFORP — 70+ programs", unit: "text", year: "2024", source: "INSAFORP", section: "education_quality" },
  { label: "Schools Remodeled (Bukele admin)", value: "5,000+", numericValue: 5000, unit: "count", year: "2025", source: "MINED / Govt", section: "education_quality", trend: "up", trendGood: true },
  { label: "CUBO Youth Centers Built", value: "11", numericValue: 11, unit: "count", year: "2024", source: "Government of El Salvador", section: "education_quality", trend: "up", trendGood: true },

  // ── IV-A Environment ──
  { label: "Waste Recycling Rate", value: "~5%", numericValue: 5, unit: "%", year: "2023", source: "MARN", section: "environment", trend: "stable", trendGood: false },
  { label: "Plastic Waste (kg/capita/yr)", value: "~12", numericValue: 12, unit: "kg", year: "2022", source: "UNEP", section: "environment" },
  { label: "Biodiversity: Species Threatened", value: "112", numericValue: 112, unit: "count", year: "2023", source: "IUCN Red List", section: "environment" },
  { label: "Water Stress Level", value: "High (55%+)", numericValue: 55, unit: "%", year: "2023", source: "WRI Aqueduct", section: "environment", trend: "stable", trendGood: false },
  { label: "Geothermal Capacity", value: "204.4 MW", numericValue: 204.4, unit: "MW", year: "2024", source: "LaGeo", section: "environment", trend: "up", trendGood: true },

  // ── IV-B Infrastructure ──
  { label: "Broadband Speed (avg download)", value: "26 Mbps", numericValue: 26, unit: "Mbps", year: "2024", source: "Ookla Speedtest", section: "infrastructure" },
  { label: "Road Quality Index", value: "3.5/7", numericValue: 3.5, unit: "index", year: "2023", source: "WEF GCI", section: "infrastructure" },
  { label: "Public Transport Access", value: "~55% (urban)", numericValue: 55, unit: "%", year: "2023", source: "VMT", section: "infrastructure" },
  { label: "Housing Affordability Index", value: "~8.5× income", numericValue: 8.5, unit: "ratio", year: "2024", source: "FSV", section: "infrastructure" },
  { label: "Homelessness Rate", value: "~5.2 per 10k", numericValue: 5.2, unit: "per10k", year: "2023", source: "DIGESTYC", section: "infrastructure" },
  { label: "Severe Housing Deprivation", value: "~12%", numericValue: 12, unit: "%", year: "2023", source: "EHPM / DIGESTYC", section: "infrastructure" },

  // ── V-A Safety & Crime ──
  { label: "Homicide Rate (2024)", value: "1.7 per 100k", numericValue: 1.7, unit: "per100k", year: "2024", source: "PNC / Government", section: "safety", trend: "down", trendGood: true },
  { label: "Homicide Rate (2015 — peak)", value: "103 per 100k", numericValue: 103, unit: "per100k", year: "2015", source: "UNODC", section: "safety" },
  { label: "Gang Arrests (State of Exception)", value: "94,844+", numericValue: 94844, unit: "count", year: "2025", source: "PNC / Govt", section: "safety" },
  { label: "CECOT Prison Capacity", value: "40,000", numericValue: 40000, unit: "count", year: "2023", source: "Government of El Salvador", section: "safety" },
  { label: "Incarceration Rate (per 100k)", value: "~600", numericValue: 600, unit: "per100k", year: "2024", source: "World Prison Brief", sourceUrl: "https://www.prisonstudies.org", section: "safety", trend: "up", trendGood: false },
  { label: "Perception of Safety (%)", value: "91% feel safe", numericValue: 91, unit: "%", year: "2024", source: "CID Gallup", section: "safety", trend: "up", trendGood: true },
  { label: "Traffic Mortality (per 100k)", value: "14.8", numericValue: 14.8, unit: "per100k", year: "2022", source: "WHO", section: "safety" },
  { label: "Police Reliability (trust %)", value: "~78%", numericValue: 78, unit: "%", year: "2024", source: "CID Gallup / LPG", section: "safety", trend: "up", trendGood: true },

  // ── V-B Governance ──
  { label: "Corruption Perceptions Index", value: "31/100 (#116)", numericValue: 31, unit: "rank", year: "2024", source: "Transparency International", sourceUrl: "https://www.transparency.org", section: "governance" },
  { label: "Press Freedom Index", value: "#133 / 180", numericValue: 133, unit: "rank", year: "2024", source: "RSF", sourceUrl: "https://rsf.org", section: "governance", trend: "down", trendGood: false },
  { label: "Democracy Index", value: "4.57 — Hybrid regime", numericValue: 4.57, unit: "index", year: "2024", source: "EIU", section: "governance" },
  { label: "Voter Turnout (last election)", value: "52.6%", numericValue: 52.6, unit: "%", year: "2024", source: "TSE", section: "governance" },
  { label: "Global Peace Index", value: "#79 / 163", numericValue: 79, unit: "rank", year: "2024", source: "IEP / Vision of Humanity", sourceUrl: "https://www.visionofhumanity.org", section: "governance", trend: "up", trendGood: true },
  { label: "Fragile States Index", value: "73.2 — Elevated Warning", numericValue: 73.2, unit: "index", year: "2024", source: "Fund for Peace", section: "governance" },
  { label: "Bukele Approval Rating", value: "91%", numericValue: 91, unit: "%", year: "2024", source: "CID Gallup", section: "governance", trend: "up", trendGood: true },
  { label: "Re-election Result", value: "84.65%", numericValue: 84.65, unit: "%", year: "2024", source: "TSE", section: "governance" },

  // ── V-C Social Cohesion ──
  { label: "Social Progress Index", value: "65.2 (#81)", numericValue: 65.2, unit: "index", year: "2024", source: "Social Progress Imperative", section: "social" },
  { label: "Gender Inequality Index", value: "0.383 (#87)", numericValue: 0.383, unit: "index", year: "2022", source: "UNDP HDR", section: "social" },
  { label: "Global Gender Gap Index", value: "0.710 (#57)", numericValue: 0.710, unit: "index", year: "2024", source: "WEF", section: "social" },
  { label: "Social Mobility Index", value: "#67 / 82", numericValue: 67, unit: "rank", year: "2020", source: "WEF", section: "social" },
  { label: "Human Development Index (HDI)", value: "0.675 — Medium", numericValue: 0.675, unit: "index", year: "2022", source: "UNDP", sourceUrl: "https://hdr.undp.org", section: "social" },
  { label: "Religious Freedom", value: "Generally respected", unit: "text", year: "2024", source: "US State Dept IRF Report", section: "social" },
  { label: "LGBTQ+ Equality Index", value: "Limited protections", unit: "text", year: "2024", source: "Equaldex", section: "social" },
  { label: "Human Rights Index", value: "4.5/10 — Concerning", numericValue: 4.5, unit: "index", year: "2024", source: "V-Dem", section: "social" },

  // ── VI Happiness & Well-being ──
  { label: "World Happiness Rank", value: "#68 / 143", numericValue: 68, unit: "rank", year: "2024", source: "World Happiness Report", sourceUrl: "https://worldhappiness.report", section: "happiness" },
  { label: "Life Satisfaction Score", value: "6.36 / 10", numericValue: 6.36, unit: "index", year: "2024", source: "World Happiness Report", section: "happiness", trend: "up", trendGood: true },
  { label: "Positive Affect (joy, laughter)", value: "0.79", numericValue: 0.79, unit: "index", year: "2024", source: "Gallup World Poll", section: "happiness" },
  { label: "Negative Affect (worry, sadness)", value: "0.27", numericValue: 0.27, unit: "index", year: "2024", source: "Gallup World Poll", section: "happiness" },
  { label: "Social Support", value: "0.83", numericValue: 0.83, unit: "index", year: "2024", source: "Gallup World Poll", section: "happiness" },
  { label: "Freedom to Make Life Choices", value: "0.84", numericValue: 0.84, unit: "index", year: "2024", source: "Gallup World Poll", section: "happiness", trend: "up", trendGood: true },
  { label: "Generosity", value: "0.08", numericValue: 0.08, unit: "index", year: "2024", source: "Gallup World Poll", section: "happiness" },
  { label: "Work-Life Balance", value: "Moderate (~45hr avg work week)", unit: "text", year: "2024", source: "ILO / EHPM", section: "happiness" },
  { label: "Community Belonging (%)", value: "~72%", numericValue: 72, unit: "%", year: "2024", source: "CID Gallup", section: "happiness" },
  { label: "Loneliness Index", value: "~25% report frequent loneliness", numericValue: 25, unit: "%", year: "2023", source: "Gallup / Meta", section: "happiness" },

  // ── VII Miscellaneous ──
  { label: "Big Mac Index (PPP)", value: "$3.50 (−44% vs US)", numericValue: 3.50, unit: "usd", year: "2024", source: "The Economist", sourceUrl: "https://www.economist.com/big-mac-index", section: "misc" },
  { label: "Food Security Index", value: "54.4 (#70)", numericValue: 54.4, unit: "index", year: "2022", source: "EIU GFSI", section: "misc" },
  { label: "Public Libraries", value: "~85", numericValue: 85, unit: "count", year: "2024", source: "CONCULTURA / Biblioteca Nacional", section: "misc" },
  { label: "Museums per Capita", value: "~12 major + 30 local", numericValue: 42, unit: "count", year: "2024", source: "MICULTURA", section: "misc" },
  { label: "Cinema Admissions (per capita)", value: "~0.3", numericValue: 0.3, unit: "per capita", year: "2023", source: "UIS", section: "misc" },
  { label: "Passport Power (visa-free)", value: "135 destinations (#37)", numericValue: 135, unit: "countries", year: "2025", source: "Henley Passport Index", section: "misc", trend: "up", trendGood: true },
  { label: "Global Innovation Index", value: "#103 / 132", numericValue: 103, unit: "rank", year: "2024", source: "WIPO", sourceUrl: "https://www.wipo.int/gii", section: "misc" },
  { label: "Olympic Medals (all time)", value: "0", numericValue: 0, unit: "count", year: "2024", source: "IOC", section: "misc" },
  { label: "Coffee Production", value: "~530k bags/yr", numericValue: 530000, unit: "bags", year: "2023", source: "ICO / CSC", section: "misc" },
  { label: "Coffee Consumption (kg/capita)", value: "~3.2", numericValue: 3.2, unit: "kg", year: "2023", source: "ICO", section: "misc" },
  { label: "Cybersecurity Index", value: "37.6 (#108)", numericValue: 37.6, unit: "index", year: "2024", source: "ITU GCI", section: "misc" },
  { label: "Digital Skills Gap", value: "Significant — 34% lack basic digital skills", numericValue: 34, unit: "%", year: "2023", source: "IDB / PNUD", section: "misc" },
  { label: "Researchers per Million", value: "~47", numericValue: 47, unit: "per million", year: "2022", source: "UNESCO UIS", section: "misc" },
  { label: "Paid Parental Leave", value: "12 weeks maternity / 3 days paternity", unit: "text", year: "2025", source: "ILO / Labor Code", section: "misc" },
  { label: "Childcare Cost (% of wage)", value: "~20-30%", numericValue: 25, unit: "%", year: "2024", source: "IDB", section: "misc" },
  { label: "Avg Time in Traffic (hr/yr)", value: "~120 (San Salvador)", numericValue: 120, unit: "hr/yr", year: "2024", source: "TomTom Traffic Index", section: "misc" },
  { label: "Trust in Media", value: "~38%", numericValue: 38, unit: "%", year: "2024", source: "Edelman / Gallup", section: "misc" },
  { label: "Trust in Scientists", value: "~62%", numericValue: 62, unit: "%", year: "2024", source: "Wellcome Global Monitor", section: "misc" },
  { label: "Volunteering Rate", value: "~15%", numericValue: 15, unit: "%", year: "2023", source: "Gallup World Poll", section: "misc" },
  { label: "Green Tech Patents", value: "~3/yr", numericValue: 3, unit: "count", year: "2023", source: "WIPO", section: "misc" },
  { label: "Energy Intensity (MJ/$PPP)", value: "3.8", numericValue: 3.8, unit: "MJ", year: "2022", source: "IEA", section: "misc" },
];

/* ── BTC Reserve (live-supplemented) ── */
export const BTC_RESERVE = {
  totalBtc: 6_043.18,
  avgBuyPrice: 44_292,
  firstBuy: "Sep 7, 2021",
  dailyBuySince: "Nov 17, 2022",
  managedBy: "National Bitcoin Office (ONBTC)",
  directors: "Max Keiser & Stacy Herbert",
  imfStatus: "BTC voluntary for merchants (Jan 2025)",
  imfLoan: "$1.4B Extended Fund Facility (Dec 2024)",
};

/* ── Major Investments ── */
export interface Investment {
  title: string;
  amount: string;
  partner: string;
  status: "active" | "approved" | "construction" | "executed" | "planned";
  desc: string;
  iconName: string;
}

export const INVESTMENTS: Investment[] = [
  { title: "Port Modernization", amount: "$1.6B", partner: "Yılport Holding", status: "active", desc: "50-year concession — Puerto Acajutla & Puerto La Unión Cutuco. Largest private investment in ES history.", iconName: "Ship" },
  { title: "IMF Loan Program", amount: "$1.4B", partner: "International Monetary Fund", status: "approved", desc: "Extended Fund Facility (Dec 2024). Structural reforms, fiscal consolidation, governance improvements.", iconName: "Landmark" },
  { title: "Debt-for-Nature Swap", amount: "$1.03B", partner: "JP Morgan", status: "executed", desc: "Largest debt-for-nature swap in history. Marine conservation, mangroves, Jiquilisco UNESCO Biosphere.", iconName: "Leaf" },
  { title: "CABEI Infrastructure Grant", amount: "$646M", partner: "Central American Bank (BCIE)", status: "approved", desc: "Largest CABEI grant ever. Roads, water treatment, public buildings, rural development, all 14 departments.", iconName: "Building2" },
  { title: "Airport of the Pacific", amount: "Mega-project", partner: "Government of El Salvador", status: "construction", desc: "New international airport near La Unión. Groundbreaking Feb 2025, terraforming 75% done. Target: H1 2027.", iconName: "Plane" },
  { title: "Strategic Bitcoin Reserve", amount: "6,043 BTC", partner: "National Bitcoin Office", status: "active", desc: "Nation-state BTC accumulation. Buying 1 BTC/day since Nov 2022. Managed by ONBTC.", iconName: "Bitcoin" },
  { title: "Hospital El Salvador", amount: "3,000 beds", partner: "Ministry of Health", status: "active", desc: "2nd largest hospital in Latin America. Built during COVID-19, now permanent mega-hospital in San Bartolo.", iconName: "Heart" },
  { title: "School Remodeling Program", amount: "5,000+ schools", partner: "Ministry of Education", status: "active", desc: "Nationwide remodeling with modern infrastructure, technology labs, and safe learning environments.", iconName: "School" },
];

/* ── Timeline ── */
export interface TimelineEvent {
  date: string;
  title: string;
  desc: string;
  icon: string;
  category: string;
}

export const TIMELINE: TimelineEvent[] = [
  { date: "Jun 2019", title: "Bukele inaugurated", desc: "43rd President. Nuevas Ideas party.", icon: "🏛️", category: "governance" },
  { date: "Jun 2019", title: "Plan Control Territorial", desc: "5-phase security plan: deployment, opportunity, modernization, rehabilitation, reinsertion.", icon: "🛡️", category: "security" },
  { date: "Sep 2021", title: "Bitcoin Law takes effect", desc: "First nation to adopt BTC as legal tender. Government buys first 200 BTC.", icon: "₿", category: "bitcoin" },
  { date: "Sep 2021", title: "Chivo Wallet launch", desc: "$30 BTC bonus per citizen. 200+ Chivo ATMs deployed nationwide.", icon: "📱", category: "bitcoin" },
  { date: "Mar 2022", title: "State of Exception", desc: "Emergency powers to combat gangs. Extended 47+ times. 94k+ arrested.", icon: "⚖️", category: "security" },
  { date: "Nov 2022", title: "1 BTC/day program", desc: "El Salvador starts buying 1 Bitcoin every day. Continues through 2025.", icon: "📈", category: "bitcoin" },
  { date: "Jan 2023", title: "CECOT opens", desc: "World's largest prison (40k capacity). Tecoluca, San Vicente.", icon: "🔒", category: "security" },
  { date: "May 2023", title: "Yılport port deal", desc: "$1.6B, 50-year concession for Acajutla & La Unión ports.", icon: "🚢", category: "infrastructure" },
  { date: "2023", title: "CUBO youth centers", desc: "11 free tech labs, sports, arts, education centers for at-risk youth.", icon: "🏫", category: "social" },
  { date: "Feb 2024", title: "Re-election: 84.65%", desc: "Largest electoral victory in ES history. NI supermajority.", icon: "🗳️", category: "governance" },
  { date: "Dec 2024", title: "IMF $1.4B program", desc: "Extended Fund Facility approved. BTC merchant acceptance now voluntary.", icon: "🏦", category: "finance" },
  { date: "Jan 2025", title: "BTC legal tender rescinded", desc: "BTC accepted but no longer mandatory. Strategic reserve continues.", icon: "⚖️", category: "bitcoin" },
  { date: "Feb 2025", title: "Airport groundbreaking", desc: "New international airport near Conchagua. Terraforming 75% done.", icon: "✈️", category: "infrastructure" },
  { date: "2025", title: "$1.03B debt-for-nature swap", desc: "Largest ever. JP Morgan. Marine conservation & mangroves.", icon: "🌿", category: "finance" },
  { date: "2025", title: "5,000+ schools remodeled", desc: "Massive nationwide education infrastructure investment.", icon: "📚", category: "social" },
  { date: "Aug 2025", title: "Indefinite re-election approved", desc: "Constitutional change allowing indefinite presidential re-election.", icon: "📜", category: "governance" },
  { date: "H1 2027", title: "Airport of the Pacific (target)", desc: "New airport planned opening, eastern ES connectivity.", icon: "🛬", category: "infrastructure" },
];

/* ── Section definitions ── */
export const SECTIONS = [
  { id: "macro",             title: "Macroeconomic Indicators",        icon: "📊", parent: "I. Economic Health & Stability" },
  { id: "business",          title: "Business & Innovation",           icon: "💼", parent: "I. Economic Health & Stability" },
  { id: "financial",         title: "Financial Health of Citizens",    icon: "💰", parent: "I. Economic Health & Stability" },
  { id: "health_mortality",  title: "Mortality & Life Expectancy",    icon: "❤️", parent: "II. Health & Wellness" },
  { id: "health_disease",    title: "Disease & Morbidity",            icon: "🦠", parent: "II. Health & Wellness" },
  { id: "health_access",     title: "Healthcare Access & Quality",    icon: "🏥", parent: "II. Health & Wellness" },
  { id: "education_access",  title: "Education Access & Enrollment",  icon: "📚", parent: "III. Education & Human Capital" },
  { id: "education_quality", title: "Education Quality & Outcomes",   icon: "🎓", parent: "III. Education & Human Capital" },
  { id: "environment",       title: "Environmental Quality",          icon: "🌿", parent: "IV. Environment & Infrastructure" },
  { id: "infrastructure",    title: "Infrastructure & Technology",    icon: "🏗️", parent: "IV. Environment & Infrastructure" },
  { id: "safety",            title: "Safety & Crime",                  icon: "🛡️", parent: "V. Social & Political Stability" },
  { id: "governance",        title: "Governance & Freedom",           icon: "⚖️", parent: "V. Social & Political Stability" },
  { id: "social",            title: "Social Cohesion & Equality",     icon: "🤝", parent: "V. Social & Political Stability" },
  { id: "happiness",         title: "Happiness & Subjective Well-being", icon: "😊", parent: "VI. Happiness & Well-being" },
  { id: "misc",              title: "Miscellaneous / Niche Metrics",  icon: "📌", parent: "VII. Miscellaneous" },
] as const;

export const SECTION_IDS = SECTIONS.map((s) => s.id);
