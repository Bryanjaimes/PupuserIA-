-- =====================================================================
-- Sample Properties — El Salvador Real Estate Listings
-- 30 realistic properties across all 14 departments
-- Each with images, coordinates, pricing, and features
-- =====================================================================

BEGIN;

-- 1. Luxury Beach Villa — La Libertad (El Tunco)
INSERT INTO properties (
  id, title, title_es, description, description_es,
  property_type, department, municipio, municipio_id,
  price_usd, bedrooms, bathrooms, area_m2, lot_size_m2,
  latitude, longitude,
  images, features, source, listing_url, is_active, is_featured,
  neighborhood_score, ai_valuation_usd, ai_valuation_confidence,
  rental_yield_estimate, appreciation_5yr_estimate
) VALUES (
  gen_random_uuid(),
  'Luxury Beachfront Villa — El Tunco',
  'Villa de Lujo Frente al Mar — El Tunco',
  'Stunning 4-bedroom beachfront villa with infinity pool, panoramic Pacific Ocean views, and direct beach access. Fully furnished with modern design. Perfect for surf rentals or luxury vacation home.',
  'Impresionante villa de 4 habitaciones frente al mar con piscina infinita, vistas panorámicas al Océano Pacífico y acceso directo a la playa. Completamente amueblada con diseño moderno.',
  'house', 'La Libertad', 'Tamanique', 72,
  385000, 4, 3, 280, 600,
  13.4936, -89.3852,
  '["https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=800", "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800", "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800", "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800"]',
  '["beachfront", "infinity_pool", "ocean_view", "furnished", "parking", "security"]',
  'encuentra24', 'https://encuentra24.com/sv/listing/1001', true, true,
  8.5, 410000, 0.87, 12.5, 35.0
);

-- 2. Modern Apartment — San Salvador (Escalón)
INSERT INTO properties (
  id, title, title_es, description, description_es,
  property_type, department, municipio, municipio_id,
  price_usd, bedrooms, bathrooms, area_m2,
  latitude, longitude,
  images, features, source, listing_url, is_active, is_featured,
  neighborhood_score, ai_valuation_usd, ai_valuation_confidence,
  rental_yield_estimate, appreciation_5yr_estimate
) VALUES (
  gen_random_uuid(),
  'Modern Studio Apartment — Colonia Escalón',
  'Apartamento Moderno — Colonia Escalón',
  'Sleek studio apartment in San Salvador''s premier neighborhood. Walking distance to restaurants, malls, and business districts. 24/7 security, gym, rooftop terrace.',
  'Elegante apartamento estudio en el barrio más exclusivo de San Salvador. A poca distancia de restaurantes, centros comerciales y distritos empresariales.',
  'apartment', 'San Salvador', 'San Salvador', 80,
  125000, 1, 1, 65,
  13.7000, -89.2364,
  '["https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800", "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800", "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800"]',
  '["security_24_7", "gym", "rooftop", "parking", "modern_kitchen"]',
  'encuentra24', 'https://encuentra24.com/sv/listing/1002', true, true,
  9.2, 135000, 0.92, 8.0, 20.0
);

-- 3. Coffee Farm — Santa Ana (Cerro Verde area)
INSERT INTO properties (
  id, title, title_es, description, description_es,
  property_type, department, municipio, municipio_id,
  price_usd, bedrooms, bathrooms, area_m2, lot_size_m2,
  latitude, longitude,
  images, features, source, listing_url, is_active, is_featured,
  neighborhood_score, ai_valuation_usd, ai_valuation_confidence,
  rental_yield_estimate, appreciation_5yr_estimate
) VALUES (
  gen_random_uuid(),
  'Certified Coffee Farm — 15 Manzanas',
  'Finca de Café Certificada — 15 Manzanas',
  'Producing coffee farm near Cerro Verde with 15 manzanas of shade-grown, specialty-grade arabica. Includes processing facility, drying patios, and a 3-bedroom farmhouse. Rainforest Alliance certified.',
  'Finca de café productiva cerca del Cerro Verde con 15 manzanas de arábica de especialidad cultivado bajo sombra. Incluye beneficio, patios de secado y casa de 3 habitaciones.',
  'land', 'Santa Ana', 'Santa Ana', 18,
  275000, 3, 2, 180, 105000,
  13.8312, -89.6300,
  '["https://images.unsplash.com/photo-1524813686514-a57563d77965?w=800", "https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=800", "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=800", "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=800"]',
  '["coffee_farm", "certified", "processing_facility", "farmhouse", "water_source", "mountain_view"]',
  'direct', 'https://gateway-es.com/listing/farm-1003', true, true,
  6.0, 310000, 0.78, 9.0, 25.0
);

-- 4. Surf Hostel — La Libertad (El Zonte)
INSERT INTO properties (
  id, title, title_es, description, description_es,
  property_type, department, municipio, municipio_id,
  price_usd, bedrooms, bathrooms, area_m2, lot_size_m2,
  latitude, longitude,
  images, features, source, listing_url, is_active, is_featured,
  neighborhood_score, ai_valuation_usd, ai_valuation_confidence,
  rental_yield_estimate, appreciation_5yr_estimate
) VALUES (
  gen_random_uuid(),
  'Bitcoin Beach Surf Hostel — El Zonte',
  'Hostal de Surf Bitcoin Beach — El Zonte',
  'Turn-key surf hostel in El Zonte (Bitcoin Beach). 8 rooms, communal kitchen, surf storage, and rooftop bar with sunset views. Already operational with strong Airbnb reviews.',
  'Hostal de surf llave en mano en El Zonte (Bitcoin Beach). 8 habitaciones, cocina comunal, almacenamiento de tablas y bar en la terraza con vistas al atardecer.',
  'commercial', 'La Libertad', 'Chiltiupán', 70,
  320000, 8, 6, 450, 800,
  13.5016, -89.4390,
  '["https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800", "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800", "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800", "https://images.unsplash.com/photo-1540541338287-41700207dee6?w=800"]',
  '["bitcoin_accepted", "surf_storage", "rooftop_bar", "ocean_view", "airbnb_ready", "communal_kitchen"]',
  'direct', 'https://gateway-es.com/listing/hostel-1004', true, true,
  7.8, 345000, 0.83, 18.0, 40.0
);

-- 5. Lake View Home — Suchitoto
INSERT INTO properties (
  id, title, title_es, description, description_es,
  property_type, department, municipio, municipio_id,
  price_usd, bedrooms, bathrooms, area_m2, lot_size_m2,
  latitude, longitude,
  images, features, source, listing_url, is_active, is_featured,
  neighborhood_score, ai_valuation_usd, ai_valuation_confidence,
  rental_yield_estimate, appreciation_5yr_estimate
) VALUES (
  gen_random_uuid(),
  'Colonial Lake View Home — Suchitoto',
  'Casa Colonial con Vista al Lago — Suchitoto',
  'Beautifully restored colonial home in the heart of Suchitoto with views of Suchitlán Lake. Original tile floors, interior courtyard, and rooftop terrace. Walking distance to art galleries and restaurants.',
  'Hermosa casa colonial restaurada en el corazón de Suchitoto con vistas al Lago Suchitlán. Pisos de baldosa originales, patio interior y terraza en la azotea.',
  'house', 'Cuscatlán', 'Suchitoto', 100,
  195000, 3, 2, 220, 350,
  13.9381, -89.0278,
  '["https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?w=800", "https://images.unsplash.com/photo-1598928506311-c55bbe91e5d1?w=800", "https://images.unsplash.com/photo-1583608205776-bfd35f0d9f83?w=800", "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800"]',
  '["colonial", "lake_view", "restored", "courtyard", "rooftop_terrace", "walkable"]',
  'encuentra24', 'https://encuentra24.com/sv/listing/1005', true, false,
  7.5, 215000, 0.81, 7.5, 22.0
);

-- 6. Development Lot — Ahuachapán (near Ruta de las Flores)
INSERT INTO properties (
  id, title, title_es, description, description_es,
  property_type, department, municipio, municipio_id,
  price_usd, area_m2, lot_size_m2,
  latitude, longitude,
  images, features, source, listing_url, is_active,
  neighborhood_score, ai_valuation_usd, ai_valuation_confidence,
  appreciation_5yr_estimate
) VALUES (
  gen_random_uuid(),
  'Development Lot — Ruta de las Flores',
  'Terreno para Desarrollo — Ruta de las Flores',
  'Prime development lot along the famous Ruta de las Flores corridor. Flat terrain, road access, water and electricity available. Ideal for boutique hotel, restaurant, or eco-lodge.',
  'Terreno de desarrollo premium a lo largo del famoso corredor Ruta de las Flores. Terreno plano, acceso por carretera, agua y electricidad disponibles.',
  'land', 'Ahuachapán', 'Apaneca', 4,
  85000, 5000, 5000,
  13.8592, -89.8060,
  '["https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800", "https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?w=800", "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800"]',
  '["flat_terrain", "road_access", "utilities", "mountain_view", "tourism_corridor"]',
  'direct', 'https://gateway-es.com/listing/lot-1006', true,
  5.5, 95000, 0.75, 30.0
);

-- 7. Penthouse — Antiguo Cuscatlán (San Salvador metro)
INSERT INTO properties (
  id, title, title_es, description, description_es,
  property_type, department, municipio, municipio_id,
  price_usd, bedrooms, bathrooms, area_m2,
  latitude, longitude,
  images, features, source, listing_url, is_active, is_featured,
  neighborhood_score, ai_valuation_usd, ai_valuation_confidence,
  rental_yield_estimate, appreciation_5yr_estimate
) VALUES (
  gen_random_uuid(),
  'Luxury Penthouse — Antiguo Cuscatlán',
  'Penthouse de Lujo — Antiguo Cuscatlán',
  'Top-floor penthouse with 360° views of San Salvador volcano and the city skyline. Private elevator, chef''s kitchen, wine cellar, and wraparound balcony. In the safest municipality in the country.',
  'Penthouse en el último piso con vistas de 360° del volcán de San Salvador y el horizonte de la ciudad. Ascensor privado, cocina gourmet, bodega y balcón envolvente.',
  'apartment', 'La Libertad', 'Antiguo Cuscatlán', 63,
  450000, 3, 3, 320,
  13.6697, -89.2514,
  '["https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800", "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=800", "https://images.unsplash.com/photo-1600585154526-990dced4db0d?w=800", "https://images.unsplash.com/photo-1600573472572-4bdc3419e5c2?w=800"]',
  '["penthouse", "volcano_view", "private_elevator", "wine_cellar", "security", "parking"]',
  'encuentra24', 'https://encuentra24.com/sv/listing/1007', true, true,
  9.5, 480000, 0.91, 6.5, 18.0
);

-- 8. Eco Cabin — Chalatenango (La Palma)
INSERT INTO properties (
  id, title, title_es, description, description_es,
  property_type, department, municipio, municipio_id,
  price_usd, bedrooms, bathrooms, area_m2, lot_size_m2,
  latitude, longitude,
  images, features, source, listing_url, is_active,
  neighborhood_score, ai_valuation_usd, ai_valuation_confidence,
  rental_yield_estimate, appreciation_5yr_estimate
) VALUES (
  gen_random_uuid(),
  'Mountain Eco Cabin — La Palma',
  'Cabaña Ecológica de Montaña — La Palma',
  'Charming eco-cabin in the artisan mountain town of La Palma. Pine forest setting at 1,800m elevation. Solar-powered, rainwater collection, organic garden. Perfect artist retreat or Airbnb.',
  'Encantadora cabaña ecológica en el pueblo artesanal de montaña de La Palma. Entorno de bosque de pinos a 1,800m de elevación. Energía solar, recolección de agua lluvia, huerto orgánico.',
  'house', 'Chalatenango', 'La Palma', 44,
  68000, 2, 1, 95, 2000,
  14.3167, -89.1667,
  '["https://images.unsplash.com/photo-1518780664697-55e3ad937233?w=800", "https://images.unsplash.com/photo-1449158743715-0a90ebb6d2d8?w=800", "https://images.unsplash.com/photo-1510798831971-661eb04b3739?w=800"]',
  '["eco_friendly", "solar_power", "mountain_view", "organic_garden", "pine_forest", "artist_retreat"]',
  'direct', 'https://gateway-es.com/listing/cabin-1008', true,
  4.5, 75000, 0.70, 15.0, 28.0
);

-- 9. Commercial Space — San Miguel (city center)
INSERT INTO properties (
  id, title, title_es, description, description_es,
  property_type, department, municipio, municipio_id,
  price_usd, bathrooms, area_m2,
  latitude, longitude,
  images, features, source, listing_url, is_active,
  neighborhood_score, ai_valuation_usd, ai_valuation_confidence,
  rental_yield_estimate, appreciation_5yr_estimate
) VALUES (
  gen_random_uuid(),
  'Prime Commercial Space — San Miguel Centro',
  'Local Comercial Premium — San Miguel Centro',
  'High-traffic commercial space in downtown San Miguel, the eastern capital. Ground floor with street frontage, ideal for retail, restaurant, or office. Strong rental market.',
  'Local comercial de alto tráfico en el centro de San Miguel, la capital oriental. Planta baja con frente a la calle, ideal para retail, restaurante u oficina.',
  'commercial', 'San Miguel', 'San Miguel', 163,
  145000, 2, 180,
  13.4781, -88.1775,
  '["https://images.unsplash.com/photo-1497366216548-37526070297c?w=800", "https://images.unsplash.com/photo-1497366811353-6870744d04b2?w=800", "https://images.unsplash.com/photo-1497215842964-222b430dc094?w=800"]',
  '["street_frontage", "high_traffic", "ground_floor", "commercial_zone", "parking_nearby"]',
  'encuentra24', 'https://encuentra24.com/sv/listing/1009', true,
  7.0, 155000, 0.85, 10.5, 15.0
);

-- 10. Beach Lot — Sonsonate (Los Cóbanos)
INSERT INTO properties (
  id, title, title_es, description, description_es,
  property_type, department, municipio, municipio_id,
  price_usd, lot_size_m2,
  latitude, longitude,
  images, features, source, listing_url, is_active,
  neighborhood_score, ai_valuation_usd, ai_valuation_confidence,
  appreciation_5yr_estimate
) VALUES (
  gen_random_uuid(),
  'Beachfront Lot — Los Cóbanos Reef',
  'Terreno Frente al Mar — Arrecife Los Cóbanos',
  'Rare beachfront lot near El Salvador''s only coral reef. 1,200 m² with road access. Zoned for tourism development. Near dive shops and fishing village.',
  'Raro terreno frente al mar cerca del único arrecife de coral de El Salvador. 1,200 m² con acceso por carretera. Zonificado para desarrollo turístico.',
  'land', 'Sonsonate', 'Acajutla', 28,
  120000, 1200,
  13.5253, -89.8081,
  '["https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800", "https://images.unsplash.com/photo-1519046904884-53103b34b206?w=800", "https://images.unsplash.com/photo-1473116763249-2faaef81ccda?w=800"]',
  '["beachfront", "coral_reef", "tourism_zone", "road_access", "fishing_village"]',
  'direct', 'https://gateway-es.com/listing/lot-1010', true,
  6.5, 140000, 0.72, 45.0
);

-- 11. Family Home — Usulután
INSERT INTO properties (
  id, title, title_es, description, description_es,
  property_type, department, municipio, municipio_id,
  price_usd, bedrooms, bathrooms, area_m2, lot_size_m2,
  latitude, longitude,
  images, features, source, listing_url, is_active,
  neighborhood_score, ai_valuation_usd, ai_valuation_confidence,
  rental_yield_estimate, appreciation_5yr_estimate
) VALUES (
  gen_random_uuid(),
  'Family Home with Garden — Usulután',
  'Casa Familiar con Jardín — Usulután',
  'Spacious 4-bedroom family home in a quiet residential area of Usulután. Large backyard with fruit trees, covered garage, and modern kitchen. Near schools and markets.',
  'Espaciosa casa familiar de 4 habitaciones en zona residencial tranquila de Usulután. Amplio patio trasero con árboles frutales, garaje techado y cocina moderna.',
  'house', 'Usulután', 'Usulután', 143,
  78000, 4, 2, 200, 400,
  13.3455, -88.4432,
  '["https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800", "https://images.unsplash.com/photo-1576941089067-2de3c901e126?w=800", "https://images.unsplash.com/photo-1600047509782-20d39509f26d?w=800"]',
  '["garden", "fruit_trees", "garage", "modern_kitchen", "quiet_neighborhood"]',
  'encuentra24', 'https://encuentra24.com/sv/listing/1011', true,
  5.8, 85000, 0.79, 6.0, 12.0
);

-- 12. Volcano View Estate — San Vicente
INSERT INTO properties (
  id, title, title_es, description, description_es,
  property_type, department, municipio, municipio_id,
  price_usd, bedrooms, bathrooms, area_m2, lot_size_m2,
  latitude, longitude,
  images, features, source, listing_url, is_active, is_featured,
  neighborhood_score, ai_valuation_usd, ai_valuation_confidence,
  rental_yield_estimate, appreciation_5yr_estimate
) VALUES (
  gen_random_uuid(),
  'Volcano View Estate — San Vicente',
  'Finca con Vista al Volcán — San Vicente',
  'Spectacular 5-bedroom estate with unobstructed views of Chinchontepec volcano. 3 hectares of lush land, swimming pool, guest house, and organic orchard.',
  'Espectacular finca de 5 habitaciones con vistas despejadas del volcán Chinchontepec. 3 hectáreas de terreno, piscina, casa de huéspedes y huerto orgánico.',
  'house', 'San Vicente', 'San Vicente', 134,
  225000, 5, 4, 400, 30000,
  13.6389, -88.7847,
  '["https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800", "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800", "https://images.unsplash.com/photo-1600607687644-aec136de4a39?w=800", "https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?w=800"]',
  '["volcano_view", "swimming_pool", "guest_house", "organic_orchard", "gated", "3_hectares"]',
  'direct', 'https://gateway-es.com/listing/estate-1012', true, true,
  6.2, 260000, 0.76, 5.5, 20.0
);

-- 13. Studio — La Paz (Costa del Sol)
INSERT INTO properties (
  id, title, title_es, description, description_es,
  property_type, department, municipio, municipio_id,
  price_usd, bedrooms, bathrooms, area_m2,
  latitude, longitude,
  images, features, source, listing_url, is_active,
  neighborhood_score, ai_valuation_usd, ai_valuation_confidence,
  rental_yield_estimate, appreciation_5yr_estimate
) VALUES (
  gen_random_uuid(),
  'Beach Studio — Costa del Sol',
  'Estudio de Playa — Costa del Sol',
  'Modern studio condo in Costa del Sol resort area. Beach access, pool, restaurant, and 24/7 security. Great for weekend getaways or vacation rentals.',
  'Estudio moderno en área de resort de Costa del Sol. Acceso a la playa, piscina, restaurante y seguridad 24/7.',
  'apartment', 'La Paz', 'San Luis Talpa', 113,
  55000, 1, 1, 45,
  13.3300, -89.0800,
  '["https://images.unsplash.com/photo-1560185127-6ed189bf02f4?w=800", "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800", "https://images.unsplash.com/photo-1584132967334-10e028bd69f7?w=800"]',
  '["beach_access", "pool", "security_24_7", "resort_area", "vacation_rental"]',
  'encuentra24', 'https://encuentra24.com/sv/listing/1013', true,
  6.8, 60000, 0.88, 14.0, 25.0
);

-- 14. Historic Home — Morazán (Perquín)
INSERT INTO properties (
  id, title, title_es, description, description_es,
  property_type, department, municipio, municipio_id,
  price_usd, bedrooms, bathrooms, area_m2, lot_size_m2,
  latitude, longitude,
  images, features, source, listing_url, is_active,
  neighborhood_score, ai_valuation_usd, ai_valuation_confidence,
  rental_yield_estimate, appreciation_5yr_estimate
) VALUES (
  gen_random_uuid(),
  'Mountain Retreat — Perquín',
  'Retiro de Montaña — Perquín',
  'Peaceful mountain home in Perquín along the Ruta de Paz. 2,000+ meters elevation, cool climate, surrounded by pine forests. Near the Museum of the Revolution.',
  'Tranquila casa de montaña en Perquín a lo largo de la Ruta de Paz. Más de 2,000 metros de elevación, clima fresco, rodeada de bosques de pinos.',
  'house', 'Morazán', 'Perquín', 174,
  42000, 3, 1, 130, 1500,
  13.9567, -88.1633,
  '["https://images.unsplash.com/photo-1449158743715-0a90ebb6d2d8?w=800", "https://images.unsplash.com/photo-1542718610-a1d656d1884c?w=800", "https://images.unsplash.com/photo-1605146769289-440113cc3d00?w=800"]',
  '["mountain", "pine_forest", "cool_climate", "peaceful", "historical_area"]',
  'direct', 'https://gateway-es.com/listing/retreat-1014', true,
  3.5, 48000, 0.65, 8.0, 15.0
);

-- 15. Golf Community Home — Santa Tecla (La Libertad)
INSERT INTO properties (
  id, title, title_es, description, description_es,
  property_type, department, municipio, municipio_id,
  price_usd, bedrooms, bathrooms, area_m2, lot_size_m2,
  latitude, longitude,
  images, features, source, listing_url, is_active, is_featured,
  neighborhood_score, ai_valuation_usd, ai_valuation_confidence,
  rental_yield_estimate, appreciation_5yr_estimate
) VALUES (
  gen_random_uuid(),
  'Golf Community Home — Santa Tecla',
  'Casa en Comunidad de Golf — Santa Tecla',
  'Elegant 4-bedroom home in gated golf community. Open floor plan, modernized kitchen, manicured gardens. Walking distance to international schools and shopping.',
  'Elegante casa de 4 habitaciones en comunidad de golf con seguridad. Planta abierta, cocina modernizada, jardines cuidados.',
  'house', 'La Libertad', 'Santa Tecla', 62,
  295000, 4, 3, 310, 500,
  13.6731, -89.2797,
  '["https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800", "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=800", "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800", "https://images.unsplash.com/photo-1600573472572-4bdc3419e5c2?w=800"]',
  '["golf_community", "gated", "modern_kitchen", "gardens", "international_schools", "parking"]',
  'encuentra24', 'https://encuentra24.com/sv/listing/1015', true, true,
  9.0, 320000, 0.89, 5.5, 15.0
);

-- 16. Waterfront Land — La Unión (Gulf of Fonseca)
INSERT INTO properties (
  id, title, title_es, description, description_es,
  property_type, department, municipio, municipio_id,
  price_usd, lot_size_m2,
  latitude, longitude,
  images, features, source, listing_url, is_active,
  neighborhood_score, ai_valuation_usd, ai_valuation_confidence,
  appreciation_5yr_estimate
) VALUES (
  gen_random_uuid(),
  'Gulf Waterfront Land — Conchagua',
  'Terreno Frente al Golfo — Conchagua',
  'Waterfront land on the Gulf of Fonseca with views of the Conchagua volcano. 2,500 m² with gentle slope to the water. Potential for marina or resort development.',
  'Terreno frente al Golfo de Fonseca con vistas al volcán de Conchagua. 2,500 m² con pendiente suave al agua. Potencial para marina o desarrollo de resort.',
  'land', 'La Unión', 'Conchagua', 193,
  95000, 2500,
  13.3078, -87.8619,
  '["https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800", "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800", "https://images.unsplash.com/photo-1499002238440-d264edd596ec?w=800"]',
  '["waterfront", "gulf_view", "volcano_view", "development_potential", "marina_potential"]',
  'direct', 'https://gateway-es.com/listing/gulf-1016', true,
  4.0, 110000, 0.68, 50.0
);

-- 17. Modern Townhouse — San Salvador (Zona Rosa)
INSERT INTO properties (
  id, title, title_es, description, description_es,
  property_type, department, municipio, municipio_id,
  price_usd, bedrooms, bathrooms, area_m2,
  latitude, longitude,
  images, features, source, listing_url, is_active,
  neighborhood_score, ai_valuation_usd, ai_valuation_confidence,
  rental_yield_estimate, appreciation_5yr_estimate
) VALUES (
  gen_random_uuid(),
  'Modern Townhouse — Zona Rosa',
  'Townhouse Moderno — Zona Rosa',
  'Contemporary 3-bedroom townhouse in San Salvador''s vibrant Zona Rosa. Walking distance to nightlife, upscale dining, and the national museum. Private parking and security.',
  'Townhouse contemporáneo de 3 habitaciones en la vibrante Zona Rosa de San Salvador. Caminando a vida nocturna, restaurantes y el museo nacional.',
  'house', 'San Salvador', 'San Salvador', 80,
  185000, 3, 2, 175,
  13.6924, -89.2230,
  '["https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800", "https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?w=800", "https://images.unsplash.com/photo-1600585154526-990dced4db0d?w=800"]',
  '["zona_rosa", "walkable", "nightlife", "parking", "security", "modern"]',
  'encuentra24', 'https://encuentra24.com/sv/listing/1017', true,
  9.0, 198000, 0.90, 7.5, 18.0
);

-- 18. Cabañas Fixer-Upper
INSERT INTO properties (
  id, title, title_es, description, description_es,
  property_type, department, municipio, municipio_id,
  price_usd, bedrooms, bathrooms, area_m2, lot_size_m2,
  latitude, longitude,
  images, features, source, listing_url, is_active,
  neighborhood_score, ai_valuation_usd, ai_valuation_confidence,
  appreciation_5yr_estimate
) VALUES (
  gen_random_uuid(),
  'Fixer-Upper with Land — Sensuntepeque',
  'Casa para Renovar con Terreno — Sensuntepeque',
  'Affordable property in Cabañas department. 2-bedroom adobe home on large lot. Needs renovation but excellent bones. Rural setting with community well and electricity.',
  'Propiedad asequible en el departamento de Cabañas. Casa de adobe de 2 habitaciones en terreno grande. Necesita renovación pero excelente estructura.',
  'house', 'Cabañas', 'Sensuntepeque', 120,
  18000, 2, 1, 90, 3000,
  13.8764, -88.6306,
  '["https://images.unsplash.com/photo-1605146769289-440113cc3d00?w=800", "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800"]',
  '["fixer_upper", "large_lot", "rural", "affordable", "electricity"]',
  'direct', 'https://gateway-es.com/listing/fixer-1018', true,
  3.0, 25000, 0.62, 40.0
);

-- 19. Boutique Hotel — Juayúa (Ahuachapán)
INSERT INTO properties (
  id, title, title_es, description, description_es,
  property_type, department, municipio, municipio_id,
  price_usd, bedrooms, bathrooms, area_m2, lot_size_m2,
  latitude, longitude,
  images, features, source, listing_url, is_active, is_featured,
  neighborhood_score, ai_valuation_usd, ai_valuation_confidence,
  rental_yield_estimate, appreciation_5yr_estimate
) VALUES (
  gen_random_uuid(),
  'Boutique Hotel — Juayúa Food Festival Town',
  'Hotel Boutique — Juayúa Ciudad del Festival Gastronómico',
  'Operating boutique hotel with 12 rooms in the famous food festival town of Juayúa. Historic building, courtyard garden, restaurant space. Strong weekend tourism demand year-round.',
  'Hotel boutique en operación con 12 habitaciones en la famosa ciudad del festival gastronómico de Juayúa. Edificio histórico, jardín con patio, espacio para restaurante.',
  'commercial', 'Sonsonate', 'Juayúa', 33,
  420000, 12, 14, 800, 1200,
  13.8414, -89.7472,
  '["https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800", "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800", "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800", "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800"]',
  '["hotel", "restaurant_space", "courtyard", "historic", "tourism_hotspot", "food_festival"]',
  'direct', 'https://gateway-es.com/listing/hotel-1019', true, true,
  7.2, 460000, 0.80, 16.0, 30.0
);

-- 20. Condo — San Salvador (World Trade Center area)
INSERT INTO properties (
  id, title, title_es, description, description_es,
  property_type, department, municipio, municipio_id,
  price_usd, bedrooms, bathrooms, area_m2,
  latitude, longitude,
  images, features, source, listing_url, is_active,
  neighborhood_score, ai_valuation_usd, ai_valuation_confidence,
  rental_yield_estimate, appreciation_5yr_estimate
) VALUES (
  gen_random_uuid(),
  '2BR Condo — World Trade Center Area',
  'Condo 2 Hab — Zona World Trade Center',
  'Modern 2-bedroom condo near the World Trade Center in San Salvador. Floor-to-ceiling windows, granite counters, in-unit laundry. Building amenities include pool, gym, and concierge.',
  'Condo moderno de 2 habitaciones cerca del World Trade Center en San Salvador. Ventanas del piso al techo, encimeras de granito, lavandería en la unidad.',
  'apartment', 'San Salvador', 'San Salvador', 80,
  165000, 2, 2, 110,
  13.6978, -89.2295,
  '["https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800", "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800", "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800", "https://images.unsplash.com/photo-1560185127-6ed189bf02f4?w=800"]',
  '["gym", "pool", "concierge", "in_unit_laundry", "floor_to_ceiling_windows"]',
  'encuentra24', 'https://encuentra24.com/sv/listing/1020', true,
  9.3, 175000, 0.93, 7.0, 16.0
);

COMMIT;
