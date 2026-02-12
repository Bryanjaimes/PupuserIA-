/* ═══════════════════════════════════════════════════════
   Department Descriptions — brief history, geography,
   and cultural highlights for each of El Salvador's
   14 departments.
   ═══════════════════════════════════════════════════════ */

export interface DepartmentInfo {
  name: string;
  capital: string;
  population: string;
  area_km2: number;
  elevation: string;
  summary: string;
  history: string;
  highlights: string[];
  emoji: string;
}

export const DEPARTMENT_INFO: Record<string, DepartmentInfo> = {
  Ahuachapán: {
    name: "Ahuachapán",
    capital: "Ahuachapán",
    population: "~343,000",
    area_km2: 1240,
    elevation: "785 m",
    emoji: "🌋",
    summary:
      "The westernmost department of El Salvador, famous for its geothermal hot springs (Los Ausoles), the cloud forests of El Imposible National Park, and the scenic Ruta de las Flores. Coffee country at its finest.",
    history:
      "Named from the Nahuatl word meaning 'City of the oak houses,' Ahuachapán was one of the first regions settled by the Pipil people. It became a department in 1869. The area played a key role in the 19th-century coffee boom that shaped the Salvadoran economy. Los Ausoles geothermal fields have been harnessed for electricity since the 1970s, making the region a pioneer in renewable energy. Towns like Apaneca, Ataco, and Juayúa along the Ruta de las Flores have become cultural tourism magnets.",
    highlights: [
      "Ruta de las Flores (Apaneca, Ataco)",
      "El Imposible National Park",
      "Los Ausoles geothermal fields",
      "Barra de Santiago mangroves",
      "Coffee farm tours",
    ],
  },
  "Santa Ana": {
    name: "Santa Ana",
    capital: "Santa Ana",
    population: "~572,000",
    area_km2: 2023,
    elevation: "665 m",
    emoji: "⛪",
    summary:
      "The second-largest department, home to Ilamatepec (the country's highest volcano), Lake Coatepeque, Cerro Verde, and the stunning neo-Gothic cathedral. The coffee capital of El Salvador.",
    history:
      "Originally inhabited by the Pokomam Maya and later the Pipil, the city of Santa Ana was founded as 'Sihuatehuacán.' The Spanish renamed it after Saint Anne. It grew wealthy during the 19th-century coffee era, with planters building the ornate cathedral (completed 1913) and the Teatro Nacional. The Santa Ana volcano erupted in 2005, reminding residents of the region's volcanic heritage. Today it's a gateway to Montecristo Cloud Forest and the Trifinio Biosphere Reserve.",
    highlights: [
      "Santa Ana Volcano (2,381 m)",
      "Lake Coatepeque",
      "Cerro Verde National Park",
      "Tazumal Maya ruins",
      "Neo-Gothic Cathedral",
    ],
  },
  Sonsonate: {
    name: "Sonsonate",
    capital: "Sonsonate",
    population: "~478,000",
    area_km2: 1226,
    elevation: "225 m",
    emoji: "🏖️",
    summary:
      "A department that stretches from the Pacific coast to volcanic highlands. Famous for its Holy Week processions (among the most elaborate in the Americas), the Izalco volcano, and vibrant indigenous Nahua-Pipil heritage.",
    history:
      "Sonsonate was a major cacao-producing region during the pre-Columbian and colonial periods, with the port of Acajutla serving as the primary export hub. The 1932 Matanza — a peasant uprising and subsequent massacre — profoundly shaped the region's indigenous communities, particularly in Nahuizalco and Izalco. The Izalco volcano earned the nickname 'Lighthouse of the Pacific' for its continuous eruptions from 1770 to 1966. Today the department balances its indigenous heritage with beach tourism at Los Cóbanos and coffee cultivation along the Ruta de las Flores.",
    highlights: [
      "Izalco Volcano",
      "Los Cóbanos coral reef",
      "Holy Week processions",
      "Port of Acajutla",
      "Nahuizalco indigenous market",
    ],
  },
  Chalatenango: {
    name: "Chalatenango",
    capital: "Chalatenango",
    population: "~200,000",
    area_km2: 2017,
    elevation: "380 m",
    emoji: "🏔️",
    summary:
      "The mountainous northern frontier — pine-clad highlands reaching 2,730m at Cerro El Pital, the country's highest point. Cool-climate agriculture, artisan villages, and a landscape shaped by the civil war.",
    history:
      "Chalatenango's mountains provided natural fortress terrain during the 1980–92 civil war, becoming a stronghold of the FMLN guerrillas. Towns like La Palma were established as art cooperatives by Fernando Llort, whose distinctive naïf paintings became a national symbol. The department was founded in 1855 and historically served as a frontier against neighboring Honduras. Today the region attracts eco-tourists and hikers with El Pital, La Montañona cloud forest, and the shores of Suchitlán Lake (Cerrón Grande reservoir).",
    highlights: [
      "Cerro El Pital (2,730 m)",
      "La Palma artisan village",
      "La Montañona cloud forest",
      "Suchitlán Lake",
      "Civil war historic trail",
    ],
  },
  "La Libertad": {
    name: "La Libertad",
    capital: "Santa Tecla (Nueva San Salvador)",
    population: "~785,000",
    area_km2: 1653,
    elevation: "900 m (Santa Tecla)",
    emoji: "🏄",
    summary:
      "El Salvador's surf coast and economic powerhouse. Home to El Tunco, El Zonte (Bitcoin Beach), the Joya de Cerén UNESCO site, and the suburban hub of Santa Tecla. This is where the Pacific meets innovation.",
    history:
      "La Libertad was carved out of San Salvador department in 1865. Its Pacific coastline became synonymous with surfing after international competitions in the 2000s — the government's 'Surf City' branding campaign made it world-famous. El Zonte pioneered Bitcoin adoption in 2019 through the grassroots 'Bitcoin Beach' initiative, predating the national Bitcoin Law. The port town of La Libertad has been a fishing hub for centuries, while the inland city of Santa Tecla (founded 1854 after an earthquake destroyed San Salvador) is now a thriving cultural center. Joya de Cerén, preserved by volcanic ash since 600 AD, is a UNESCO World Heritage Site.",
    highlights: [
      "El Tunco & El Zonte surf beaches",
      "Joya de Cerén (UNESCO)",
      "Santa Tecla / Paseo El Carmen",
      "Bitcoin Beach origin story",
      "Tamanique waterfalls",
    ],
  },
  "San Salvador": {
    name: "San Salvador",
    capital: "San Salvador",
    population: "~1,800,000",
    area_km2: 886,
    elevation: "658 m",
    emoji: "🏙️",
    summary:
      "The smallest department but the most densely populated — home to the capital city, major museums, government institutions, the San Salvador volcano (El Boquerón), and a rapidly modernizing urban center.",
    history:
      "Founded by Spanish conquistador Pedro de Alvarado in 1525, San Salvador has been rebuilt multiple times after devastating earthquakes (most recently 1986 and 2001). The city served as capital of the Central American Federation (1834–39). During the 20th century it grew into a sprawling metropolis. It was the epicenter of the civil war's urban conflicts. Under President Bukele, the city has undergone major modernization — new libraries, the renovated historic center, and mega-infrastructure projects. Lake Ilopango, created by a catastrophic volcanic eruption in 431 AD, borders the eastern edge.",
    highlights: [
      "El Boquerón volcano crater",
      "Lake Ilopango",
      "National Theater & MARTE museum",
      "Iglesia El Rosario (brutalist masterpiece)",
      "Puerta del Diablo viewpoint",
    ],
  },
  Cuscatlán: {
    name: "Cuscatlán",
    capital: "Cojutepeque",
    population: "~240,000",
    area_km2: 756,
    elevation: "860 m",
    emoji: "🎨",
    summary:
      "The heart of the ancient Cuzcatlán kingdom — the name from which El Salvador's indigenous identity derives. Home to Suchitoto, the country's cultural capital, and the basalt-column Los Tercios waterfall.",
    history:
      "Cuscatlán takes its name from the Nahuatl 'Cuzcatlán' (Land of Precious Jewels), the indigenous name for the Pipil-controlled territory the Spanish encountered. The colonial town of Suchitoto served as the original capital before it was moved to San Salvador. During the civil war, Suchitoto was near the frontlines but survived largely intact, later becoming an arts and culture hub. Cojutepeque, the departmental capital, is famous for its embutidos (sausages) and the Cerro de las Pavas viewpoint. The department was established in 1835.",
    highlights: [
      "Suchitoto (cultural capital)",
      "Los Tercios waterfall",
      "Lake Suchitlán birdwatching",
      "Cihuatán Maya ruins",
      "Cojutepeque embutidos",
    ],
  },
  "La Paz": {
    name: "La Paz",
    capital: "Zacatecoluca",
    population: "~350,000",
    area_km2: 1224,
    elevation: "340 m",
    emoji: "🫓",
    summary:
      "The birthplace of the pupusa as we know it — Olocuilta is the unofficial pupusa capital of the world. The department stretches from volcanic foothills to the Costa del Sol beach strip and mangrove estuaries.",
    history:
      "La Paz was created as a department in 1852. Its town of Olocuilta perfected the rice-flour pupusa (pupusa de arroz), which differs from the corn-based version found elsewhere. The Costa del Sol peninsula became a resort destination in the mid-20th century. Zacatecoluca, the capital, is gateway to the Nonualco indigenous region. The department's coastal mangroves connect to the Bay of Jiquilisco ecosystem. Ichanmichen natural springs park, near Zacatecoluca, has been a beloved family destination for generations.",
    highlights: [
      "Olocuilta (pupusa capital)",
      "Costa del Sol beaches",
      "Ichanmichen water park",
      "Nonualco indigenous region",
      "Mangrove estuaries",
    ],
  },
  Cabañas: {
    name: "Cabañas",
    capital: "Sensuntepeque",
    population: "~165,000",
    area_km2: 1104,
    elevation: "760 m",
    emoji: "🌿",
    summary:
      "A quiet, rural department of rolling hills and traditional agriculture. One of the least touristed regions — an authentic window into Salvadoran campesino life and sustainable farming.",
    history:
      "Named after General José Trinidad Cabañas, a Honduran liberal hero, the department was created in 1873. It remains one of the most rural and least developed departments. In the 2000s, international mining companies proposed gold extraction projects at El Dorado, but community-led resistance and environmental activism led El Salvador to become the first country in the world to ban metal mining (2017). The region is known for small-scale cattle ranching, basic grains, and a slower pace of life.",
    highlights: [
      "Sensuntepeque historic center",
      "Anti-mining heritage",
      "Rural agricultural scenery",
      "Traditional campesino culture",
      "Rolling hill landscapes",
    ],
  },
  "San Vicente": {
    name: "San Vicente",
    capital: "San Vicente",
    population: "~175,000",
    area_km2: 1184,
    elevation: "380 m",
    emoji: "🌐",
    summary:
      "Dominated by the twin-peaked Chinchontepec volcano and home to the CECOT mega-prison — a symbol of President Bukele's historic security transformation. Hot springs bubble at the volcano's base.",
    history:
      "San Vicente was founded in 1635 by 50 Spanish families. The iconic Pilar clock tower (Torre El Pilar) was built in the 1880s and survived the devastating 2001 earthquake. The Chinchontepec volcano (2,182 m) with its twin peaks features prominently in the department's identity. In 2022, the massive CECOT prison (capacity: 40,000) was built in Tecoluca as the centerpiece of Bukele's 'State of Exception' anti-gang campaign, which reduced El Salvador's murder rate from one of the world's highest to one of the lowest. Los Infiernillos hot springs at the volcano's base have been visited since colonial times.",
    highlights: [
      "Chinchontepec volcano",
      "CECOT mega-prison",
      "Torre El Pilar clock tower",
      "Los Infiernillos hot springs",
      "2001 earthquake memorial",
    ],
  },
  Usulután: {
    name: "Usulután",
    capital: "Usulután",
    population: "~370,000",
    area_km2: 2130,
    elevation: "90 m",
    emoji: "🐢",
    summary:
      "From the emerald crater lake of Alegría to the UNESCO Bay of Jiquilisco mangroves — the most biodiverse department. Sea turtles nest on its shores; geothermal energy flows beneath.",
    history:
      "The name derives from the Lenca word 'Usulutlán' (City of the Ocelots). The Bay of Jiquilisco was designated a UNESCO Biosphere Reserve in 2007, protecting Central America's largest mangrove ecosystem across 27 islands. The charming mountain town of Alegría sits at 1,240m above a stunning emerald volcanic crater lagoon. Berlín, another highland town, is surrounded by geothermal fields that generate a significant portion of El Salvador's electricity. In 2025, El Salvador completed a historic $1.03B debt-for-nature swap — the world's largest — directing funds to Jiquilisco conservation.",
    highlights: [
      "Bay of Jiquilisco (UNESCO biosphere)",
      "Alegría crater lagoon",
      "Berlín coffee & geothermal",
      "Sea turtle nesting beaches",
      "$1B debt-for-nature swap",
    ],
  },
  "San Miguel": {
    name: "San Miguel",
    capital: "San Miguel",
    population: "~510,000",
    area_km2: 2077,
    elevation: "110 m",
    emoji: "🎉",
    summary:
      "The eastern capital — famous for its November Carnival (Carnaval de San Miguel), the imposing Chaparrastique volcano, and world-class surf breaks at Playa Las Flores and Punta Mango.",
    history:
      "Founded in 1530, San Miguel is one of El Salvador's oldest cities. Its November carnival, held since 1959, is the country's largest festival. The Chaparrastique volcano (2,130m) is one of the most active in Central America, with its latest eruption in 2013. The eastern coast features legendary surf spots — Playa Las Flores and the remote Punta Mango attract surfers from around the world. The city serves as the commercial hub for the entire eastern region and has a thriving market economy.",
    highlights: [
      "Carnaval de San Miguel",
      "Chaparrastique active volcano",
      "Playa Las Flores surf",
      "Punta Mango (boat-access surf)",
      "Eastern commercial hub",
    ],
  },
  Morazán: {
    name: "Morazán",
    capital: "San Francisco Gotera",
    population: "~195,000",
    area_km2: 1447,
    elevation: "370 m",
    emoji: "📻",
    summary:
      "The mountain department that housed the FMLN's guerrilla headquarters during the civil war. Home to the Museum of the Revolution, the pristine Río Sapo, and a powerful history of resistance.",
    history:
      "Named after Francisco Morazán, the Central American unifier, this department became the heartland of the FMLN guerrilla movement during the 1980–92 civil war. Perquín served as the rebel headquarters, from where Radio Venceremos broadcast across the country. The El Mozote massacre of December 1981, where nearly 1,000 civilians were killed, remains one of the darkest chapters in Salvadoran history. Today, the Museum of the Revolution in Perquín preserves this history. The Río Sapo, with its crystal-clear pools, offers some of the best nature swimming in El Salvador.",
    highlights: [
      "Museum of the Revolution (Perquín)",
      "Río Sapo natural pools",
      "El Mozote memorial",
      "Radio Venceremos history",
      "Mountain hiking trails",
    ],
  },
  "La Unión": {
    name: "La Unión",
    capital: "La Unión",
    population: "~265,000",
    area_km2: 2074,
    elevation: "95 m",
    emoji: "✈️",
    summary:
      "The far-eastern frontier on the Gulf of Fonseca — volcanic islands, a reactivated port, and the site of El Salvador's massive new Pacific airport. Where Central America's next mega-development is rising.",
    history:
      "La Unión sits on the Gulf of Fonseca, shared with Honduras and Nicaragua. The Conchagua volcano overlooks the gulf, offering views of all three countries. The port of La Unión (Cutuco) was built with Japanese cooperation in the 2000s but lay underutilized until its recent reactivation under a $200M Yılport concession. The department now hosts El Salvador's most ambitious project: the Airport of the Pacific, with groundbreaking in February 2025, scheduled for 2027. The Gulf's volcanic islands — Meanguera, Zacatillo, and Conejo — are home to small fishing communities with spectacular sunsets.",
    highlights: [
      "Airport of the Pacific (2027)",
      "Gulf of Fonseca islands",
      "Conchagua volcano viewpoint",
      "Port of La Unión (reactivated)",
      "Bitcoin City (planned)",
    ],
  },
};

/** Get department info or a fallback */
export function getDepartmentInfo(name: string): DepartmentInfo | undefined {
  return DEPARTMENT_INFO[name];
}
