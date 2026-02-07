// Official GeoJSON outline of El Salvador
// Source: Natural Earth via github.com/johan/world.geo.json
export const EL_SALVADOR_BORDER: GeoJSON.Feature = {
  type: "Feature",
  properties: { name: "El Salvador" },
  geometry: {
    type: "Polygon",
    coordinates: [
      [
        [-87.793111, 13.38448],
        [-87.904112, 13.149017],
        [-88.483302, 13.163951],
        [-88.843228, 13.259734],
        [-89.256743, 13.458533],
        [-89.812394, 13.520622],
        [-90.095555, 13.735338],
        [-90.064678, 13.88197],
        [-89.721934, 14.134228],
        [-89.534219, 14.244816],
        [-89.587343, 14.362586],
        [-89.353326, 14.424133],
        [-89.058512, 14.340029],
        [-88.843073, 14.140507],
        [-88.541231, 13.980155],
        [-88.503998, 13.845486],
        [-88.065343, 13.964626],
        [-87.859515, 13.893312],
        [-87.723503, 13.78505],
        [-87.793111, 13.38448],
      ],
    ],
  },
};

// Detailed department boundaries for El Salvador (14 departments)
export const DEPARTMENT_LABELS: { name: string; center: [number, number] }[] = [
  { name: "Ahuachapán", center: [-89.84, 13.92] },
  { name: "Santa Ana", center: [-89.56, 14.03] },
  { name: "Sonsonate", center: [-89.72, 13.72] },
  { name: "Chalatenango", center: [-88.94, 14.17] },
  { name: "La Libertad", center: [-89.32, 13.60] },
  { name: "San Salvador", center: [-89.19, 13.70] },
  { name: "Cuscatlán", center: [-88.93, 13.73] },
  { name: "La Paz", center: [-88.93, 13.44] },
  { name: "Cabañas", center: [-88.74, 13.96] },
  { name: "San Vicente", center: [-88.72, 13.63] },
  { name: "Usulután", center: [-88.46, 13.44] },
  { name: "San Miguel", center: [-88.20, 13.58] },
  { name: "Morazán", center: [-88.10, 13.82] },
  { name: "La Unión", center: [-87.84, 13.55] },
];
