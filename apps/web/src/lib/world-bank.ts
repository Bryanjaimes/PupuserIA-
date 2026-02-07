/**
 * World Bank Open Data API — Free, no API key required
 * Docs: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
 *
 * Country code for El Salvador: SLV
 */

const BASE = "https://api.worldbank.org/v2/country/SLV/indicator";
const COUNTRY = "SLV";

/* ──────────────────────────────────────────────
   Indicator code map
   World Bank indicator IDs for every metric we can fetch live.
   ────────────────────────────────────────────── */

export const WB_INDICATORS: Record<string, { code: string; label: string; unit: string; section: string }> = {
  // I-A  Macroeconomic
  gdp:                { code: "NY.GDP.MKTP.CD",      label: "GDP (current US$)",                       unit: "usd",     section: "macro" },
  gdpReal:            { code: "NY.GDP.MKTP.KD",      label: "Real GDP (constant 2015 US$)",            unit: "usd",     section: "macro" },
  gdpPerCapita:       { code: "NY.GDP.PCAP.CD",      label: "GDP per Capita",                          unit: "usd",     section: "macro" },
  gdpGrowth:          { code: "NY.GDP.MKTP.KD.ZG",   label: "GDP Growth Rate",                         unit: "%",       section: "macro" },
  gniPerCapita:       { code: "NY.GNI.PCAP.CD",      label: "GNI per Capita",                          unit: "usd",     section: "macro" },
  inflationCpi:       { code: "FP.CPI.TOTL.ZG",      label: "Inflation Rate (CPI)",                    unit: "%",       section: "macro" },
  unemployment:       { code: "SL.UEM.TOTL.ZS",      label: "Unemployment Rate",                       unit: "%",       section: "macro" },
  youthUnemployment:  { code: "SL.UEM.1524.ZS",      label: "Youth Unemployment (15-24)",              unit: "%",       section: "macro" },
  laborForce:         { code: "SL.TLF.CACT.ZS",      label: "Labor Force Participation Rate",          unit: "%",       section: "macro" },
  debtGdp:            { code: "GC.DOD.TOTL.GD.ZS",   label: "Public Debt (% GDP)",                     unit: "%",       section: "macro" },
  tradeBalance:       { code: "NE.RSB.GNFS.ZS",      label: "Trade Balance (% GDP)",                   unit: "%",       section: "macro" },
  currentAccount:     { code: "BN.CAB.XOKA.GD.ZS",   label: "Current Account Balance (% GDP)",         unit: "%",       section: "macro" },
  fdi:                { code: "BX.KLT.DINV.WD.GD.ZS", label: "Foreign Direct Investment (% GDP)",      unit: "%",       section: "macro" },
  exports:            { code: "NE.EXP.GNFS.ZS",      label: "Exports (% GDP)",                         unit: "%",       section: "macro" },
  imports:            { code: "NE.IMP.GNFS.ZS",      label: "Imports (% GDP)",                         unit: "%",       section: "macro" },
  taxRevenue:         { code: "GC.TAX.TOTL.GD.ZS",   label: "Tax Revenue (% GDP)",                     unit: "%",       section: "macro" },
  govExpenditure:     { code: "GC.XPN.TOTL.GD.ZS",   label: "Government Expenditure (% GDP)",          unit: "%",       section: "macro" },

  // I-B  Business & Innovation
  rdExpenditure:      { code: "GB.XPD.RSDV.GD.ZS",   label: "R&D Expenditure (% GDP)",                 unit: "%",       section: "business" },
  highTechExports:    { code: "TX.VAL.TECH.MF.ZS",   label: "High-Tech Exports (% mfg exports)",       unit: "%",       section: "business" },
  patentApps:         { code: "IP.PAT.RESD",          label: "Patent Applications (residents)",          unit: "count",   section: "business" },
  trademarkApps:      { code: "IP.TMK.TOTL",          label: "Trademark Applications",                  unit: "count",   section: "business" },

  // I-C  Financial Health of Citizens
  povertyRate:        { code: "SI.POV.DDAY",          label: "Poverty Rate ($2.15/day)",                 unit: "%",       section: "financial" },
  povertyNational:    { code: "SI.POV.NAHC",          label: "Poverty Rate (national line)",             unit: "%",       section: "financial" },
  gini:               { code: "SI.POV.GINI",          label: "Gini Coefficient",                        unit: "index",   section: "financial" },
  incomeShare10:      { code: "SI.DST.10TH.10",       label: "Income Share (top 10%)",                  unit: "%",       section: "financial" },
  incomeShareBottom:  { code: "SI.DST.FRST.10",       label: "Income Share (bottom 10%)",               unit: "%",       section: "financial" },
  financialInclusion: { code: "FX.OWN.TOTL.ZS",      label: "Financial Inclusion (% adults with account)", unit: "%",   section: "financial" },
  remittances:        { code: "BX.TRF.PWKR.DT.GD.ZS", label: "Personal Remittances (% GDP)",           unit: "%",       section: "financial" },

  // II-A  Mortality & Life Expectancy
  lifeExpectancy:     { code: "SP.DYN.LE00.IN",       label: "Life Expectancy at Birth",                unit: "years",   section: "health_mortality" },
  lifeExpMale:        { code: "SP.DYN.LE00.MA.IN",    label: "Life Expectancy (Male)",                  unit: "years",   section: "health_mortality" },
  lifeExpFemale:      { code: "SP.DYN.LE00.FE.IN",    label: "Life Expectancy (Female)",                unit: "years",   section: "health_mortality" },
  infantMortality:    { code: "SP.DYN.IMRT.IN",       label: "Infant Mortality Rate (per 1,000)",       unit: "per1k",   section: "health_mortality" },
  maternalMortality:  { code: "SH.STA.MMRT",          label: "Maternal Mortality Ratio (per 100k)",     unit: "per100k", section: "health_mortality" },
  under5Mortality:    { code: "SH.DYN.MORT",          label: "Under-5 Mortality Rate (per 1,000)",      unit: "per1k",   section: "health_mortality" },
  neonatalMortality:  { code: "SH.DYN.NMRT",          label: "Neonatal Mortality Rate (per 1,000)",     unit: "per1k",   section: "health_mortality" },
  suicideMortality:   { code: "SH.STA.SUIC.P5",       label: "Suicide Mortality Rate (per 100k)",       unit: "per100k", section: "health_mortality" },

  // II-B  Disease & Morbidity
  hivPrevalence:      { code: "SH.DYN.AIDS.ZS",       label: "HIV Prevalence (% 15-49)",                unit: "%",       section: "health_disease" },
  tbIncidence:        { code: "SH.TBS.INCD",           label: "TB Incidence (per 100k)",                 unit: "per100k", section: "health_disease" },
  diabetesPrevalence: { code: "SH.STA.DIAB.ZS",       label: "Diabetes Prevalence (%)",                 unit: "%",       section: "health_disease" },
  undernourishment:   { code: "SN.ITK.DEFC.ZS",       label: "Undernourishment (%)",                    unit: "%",       section: "health_disease" },
  stunting:           { code: "SH.STA.STNT.ZS",       label: "Stunting (% children under 5)",           unit: "%",       section: "health_disease" },
  overweight:         { code: "SH.STA.OWGH.ZS",       label: "Overweight (% children under 5)",         unit: "%",       section: "health_disease" },

  // II-C  Healthcare Access & Quality
  healthExpGdp:       { code: "SH.XPD.CHEX.GD.ZS",    label: "Health Expenditure (% GDP)",              unit: "%",       section: "health_access" },
  healthExpCapita:    { code: "SH.XPD.CHEX.PC.CD",     label: "Health Expenditure per Capita",           unit: "usd",     section: "health_access" },
  outOfPocket:        { code: "SH.XPD.OOPC.CH.ZS",    label: "Out-of-Pocket Health Spending (%)",       unit: "%",       section: "health_access" },
  doctors:            { code: "SH.MED.PHYS.ZS",        label: "Physicians (per 1,000)",                  unit: "per1k",   section: "health_access" },
  nurses:             { code: "SH.MED.NUMW.P3",        label: "Nurses & Midwives (per 1,000)",           unit: "per1k",   section: "health_access" },
  hospitalBeds:       { code: "SH.MED.BEDS.ZS",        label: "Hospital Beds (per 1,000)",               unit: "per1k",   section: "health_access" },
  uhcIndex:           { code: "SH.UHC.SRVS.CV.XD",     label: "UHC Service Coverage Index",             unit: "index",   section: "health_access" },
  immunizationDtp:    { code: "SH.IMM.IDPT",            label: "DTP3 Immunization (%)",                  unit: "%",       section: "health_access" },
  immunizationMeasles:{ code: "SH.IMM.MEAS",            label: "Measles Immunization (%)",               unit: "%",       section: "health_access" },

  // III  Education & Human Capital
  literacyAdult:      { code: "SE.ADT.LITR.ZS",        label: "Adult Literacy Rate (%)",                unit: "%",       section: "education_access" },
  literacyYouth:      { code: "SE.ADT.1524.LT.ZS",     label: "Youth Literacy Rate (%)",                unit: "%",       section: "education_access" },
  enrollmentPrimary:  { code: "SE.PRM.NENR",            label: "Net Enrollment (Primary)",               unit: "%",       section: "education_access" },
  enrollmentSecondary:{ code: "SE.SEC.NENR",            label: "Net Enrollment (Secondary)",             unit: "%",       section: "education_access" },
  enrollmentTertiary: { code: "SE.TER.ENRR",            label: "Enrollment (Tertiary, gross)",           unit: "%",       section: "education_access" },
  preprimaryEnroll:   { code: "SE.PRE.ENRR",            label: "Pre-primary Enrollment (gross)",         unit: "%",       section: "education_access" },
  meanYearsSchool:    { code: "HD.HCI.EYRS",            label: "Expected Years of Schooling",            unit: "years",   section: "education_access" },
  pupilTeacher:       { code: "SE.PRM.ENRL.TC.ZS",     label: "Student-Teacher Ratio (primary)",         unit: "ratio",   section: "education_quality" },
  completionPrimary:  { code: "SE.PRM.CMPT.ZS",         label: "Primary Completion Rate (%)",            unit: "%",       section: "education_quality" },
  completionSecondary:{ code: "SE.SEC.CMPT.LO.ZS",     label: "Lower Secondary Completion Rate (%)",    unit: "%",       section: "education_quality" },
  govEducSpending:    { code: "SE.XPD.TOTL.GD.ZS",     label: "Govt Education Spending (% GDP)",        unit: "%",       section: "education_quality" },
  govEducSpendPct:    { code: "SE.XPD.TOTL.GB.ZS",     label: "Education (% of Govt Spending)",          unit: "%",       section: "education_quality" },
  trainedTeachers:    { code: "SE.PRM.TCAQ.ZS",         label: "Trained Teachers (% primary)",           unit: "%",       section: "education_quality" },

  // IV-A  Environment
  co2PerCapita:       { code: "EN.ATM.CO2E.PC",         label: "CO₂ Emissions per Capita (metric tons)", unit: "tons",   section: "environment" },
  co2Total:           { code: "EN.ATM.CO2E.KT",         label: "CO₂ Emissions Total (kt)",               unit: "kt",     section: "environment" },
  renewableEnergy:    { code: "EG.FEC.RNEW.ZS",         label: "Renewable Energy (% total)",             unit: "%",       section: "environment" },
  renewableElec:      { code: "EG.ELC.RNEW.ZS",         label: "Renewable Electricity Output (%)",        unit: "%",       section: "environment" },
  forestArea:         { code: "AG.LND.FRST.ZS",         label: "Forest Area (% of land)",                unit: "%",       section: "environment" },
  protectedAreas:     { code: "ER.LND.PTLD.ZS",         label: "Terrestrial Protected Areas (%)",        unit: "%",       section: "environment" },
  marineProtected:    { code: "ER.MRN.PTMR.ZS",         label: "Marine Protected Areas (%)",             unit: "%",       section: "environment" },
  waterAccess:        { code: "SH.H2O.SMDW.ZS",         label: "Access to Clean Water (%)",              unit: "%",       section: "environment" },
  sanitation:         { code: "SH.STA.SMSS.ZS",         label: "Access to Sanitation (%)",               unit: "%",       section: "environment" },
  pm25:               { code: "EN.ATM.PM25.MC.M3",      label: "PM2.5 Air Pollution (μg/m³)",            unit: "μg/m³",   section: "environment" },

  // IV-B  Infrastructure & Technology
  internetUsers:      { code: "IT.NET.USER.ZS",         label: "Internet Users (% population)",          unit: "%",       section: "infrastructure" },
  mobileSubs:         { code: "IT.CEL.SETS.P2",          label: "Mobile Subscriptions (per 100)",         unit: "per100",  section: "infrastructure" },
  broadbandSubs:      { code: "IT.NET.BBND.P2",         label: "Fixed Broadband Subscriptions (per 100)",unit: "per100",  section: "infrastructure" },
  electrification:    { code: "EG.ELC.ACCS.ZS",         label: "Access to Electricity (%)",              unit: "%",       section: "infrastructure" },
  electricityRural:   { code: "EG.ELC.ACCS.RU.ZS",      label: "Rural Electricity Access (%)",           unit: "%",       section: "infrastructure" },
  logistics:          { code: "LP.LPI.OVRL.XQ",          label: "Logistics Performance Index",           unit: "index",   section: "infrastructure" },

  // V-A  Safety & Crime
  homicideRate:       { code: "VC.IHR.PSRC.P5",         label: "Intentional Homicides (per 100k)",       unit: "per100k", section: "safety" },

  // V-B  Governance
  ruleOfLaw:          { code: "RL.EST",                  label: "Rule of Law (estimate)",                 unit: "index",   section: "governance" },
  govEffectiveness:   { code: "GE.EST",                  label: "Government Effectiveness (estimate)",    unit: "index",   section: "governance" },
  regulatoryQuality:  { code: "RQ.EST",                  label: "Regulatory Quality (estimate)",          unit: "index",   section: "governance" },
  controlCorruption:  { code: "CC.EST",                  label: "Control of Corruption (estimate)",       unit: "index",   section: "governance" },
  politicalStability: { code: "PV.EST",                  label: "Political Stability (estimate)",         unit: "index",   section: "governance" },
  voiceAccount:       { code: "VA.EST",                  label: "Voice & Accountability (estimate)",      unit: "index",   section: "governance" },

  // V-C  Social Cohesion & Demographics
  population:         { code: "SP.POP.TOTL",             label: "Total Population",                      unit: "count",   section: "social" },
  popGrowth:          { code: "SP.POP.GROW",             label: "Population Growth Rate",                 unit: "%",       section: "social" },
  urbanPop:           { code: "SP.URB.TOTL.IN.ZS",      label: "Urban Population (%)",                   unit: "%",       section: "social" },
  ageDependency:      { code: "SP.POP.DPND",             label: "Age Dependency Ratio (% working-age)",  unit: "%",       section: "social" },
  netMigration:       { code: "SM.POP.NETM",             label: "Net Migration",                          unit: "count",   section: "social" },
  fertilityRate:      { code: "SP.DYN.TFRT.IN",          label: "Fertility Rate (births per woman)",      unit: "rate",    section: "social" },
  birthRate:          { code: "SP.DYN.CBRT.IN",          label: "Birth Rate (per 1,000)",                 unit: "per1k",   section: "social" },
  deathRate:          { code: "SP.DYN.CDRT.IN",          label: "Death Rate (per 1,000)",                 unit: "per1k",   section: "social" },
  femLaborForce:      { code: "SL.TLF.CACT.FE.ZS",      label: "Female Labor Force Participation (%)",   unit: "%",       section: "social" },
  genderParityPrimary:{ code: "SE.ENR.PRIM.FM.ZS",      label: "Gender Parity Index (primary)",          unit: "ratio",   section: "social" },
  genderParitySec:    { code: "SE.ENR.SECO.FM.ZS",      label: "Gender Parity Index (secondary)",        unit: "ratio",   section: "social" },
  adolescentFertility:{ code: "SP.ADO.TFRT",             label: "Adolescent Fertility Rate (per 1,000)",  unit: "per1k",   section: "social" },

  // Misc
  arableLand:         { code: "AG.LND.ARBL.ZS",          label: "Arable Land (% of land area)",          unit: "%",       section: "misc" },
  energyIntensity:    { code: "EG.EGY.PRIM.PP.KD",       label: "Energy Intensity (MJ/$2017 PPP GDP)",   unit: "MJ",      section: "misc" },
  militaryExpenditure:{ code: "MS.MIL.XPND.GD.ZS",       label: "Military Expenditure (% GDP)",          unit: "%",       section: "misc" },
  tourism:            { code: "ST.INT.ARVL",               label: "International Tourism Arrivals",        unit: "count",   section: "misc" },
  tourismReceipts:    { code: "ST.INT.RCPT.CD",            label: "Tourism Receipts (US$)",                unit: "usd",     section: "misc" },
};

/* ──────────────────────────────────────────────
   Fetch helpers
   ────────────────────────────────────────────── */

export interface WBDataPoint {
  indicator: string;
  value: number | null;
  date: string;
  label: string;
  unit: string;
  section: string;
}

/**
 * Fetch a single indicator for El Salvador.
 * Tries the most recent 10 years and returns the latest non-null value.
 */
async function fetchSingle(key: string): Promise<WBDataPoint | null> {
  const ind = WB_INDICATORS[key];
  if (!ind) return null;

  try {
    const url = `${BASE}/${ind.code}?country=${COUNTRY}&format=json&date=2015:2025&per_page=20`;
    const res = await fetch(url, { next: { revalidate: 3600 } }); // cache 1hr
    const json = await res.json();

    if (!json[1] || json[1].length === 0) return null;

    // Find the most recent non-null entry
    const sorted = json[1].sort((a: any, b: any) => Number(b.date) - Number(a.date));
    const valid = sorted.find((d: any) => d.value !== null);

    if (!valid) return null;

    return {
      indicator: key,
      value: valid.value,
      date: valid.date,
      label: ind.label,
      unit: ind.unit,
      section: ind.section,
    };
  } catch {
    return null;
  }
}

/**
 * Fetch all indicators in parallel batches to avoid overwhelming the API.
 * Returns a Map<indicatorKey, WBDataPoint>.
 */
export async function fetchAllIndicators(): Promise<Map<string, WBDataPoint>> {
  const keys = Object.keys(WB_INDICATORS);
  const results = new Map<string, WBDataPoint>();

  // Batch into groups of 15 to be polite to the API
  const BATCH_SIZE = 15;
  for (let i = 0; i < keys.length; i += BATCH_SIZE) {
    const batch = keys.slice(i, i + BATCH_SIZE);
    const promises = batch.map((k) => fetchSingle(k));
    const settled = await Promise.allSettled(promises);

    settled.forEach((result, idx) => {
      if (result.status === "fulfilled" && result.value) {
        results.set(batch[idx], result.value);
      }
    });
  }

  return results;
}

/**
 * Format a value for display based on its unit type.
 */
export function formatValue(value: number | null | undefined, unit: string): string {
  if (value == null) return "N/A";

  switch (unit) {
    case "usd":
      if (Math.abs(value) >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
      if (Math.abs(value) >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
      if (Math.abs(value) >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
      return `$${value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
    case "%":
      return `${value.toFixed(1)}%`;
    case "years":
      return `${value.toFixed(1)} yrs`;
    case "per1k":
      return `${value.toFixed(1)}`;
    case "per100k":
      return `${value.toFixed(1)}`;
    case "per100":
      return `${value.toFixed(1)}`;
    case "count":
      return value.toLocaleString(undefined, { maximumFractionDigits: 0 });
    case "index":
      return value.toFixed(2);
    case "ratio":
      return value.toFixed(2);
    case "tons":
    case "kt":
      return value.toLocaleString(undefined, { maximumFractionDigits: 1 });
    case "μg/m³":
      return `${value.toFixed(1)} μg/m³`;
    case "MJ":
      return value.toFixed(1);
    default:
      return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
  }
}
