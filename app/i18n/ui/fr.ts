import type { UiDictionary } from "../types";
import { ui as en } from "./en";

export const ui: UiDictionary = {
  ...en,
  brand: { ...en.brand, tagline: 'Comprendre le matériel. Voir le système.' },
  nav: { explore: 'Explorer', systems: 'Systèmes', lessons: 'Leçons', library: 'Bibliothèque', notes: 'Notes' },
  search: { placeholder: 'Rechercher matériel, bus, concepts…' },
  library: { ...en.library, title: 'Bibliothèque matérielle' },
  tools: { ...en.tools, rotate: 'Pivoter', zoom: 'Zoom', isolate: 'Isoler', section: 'Coupe', layers: 'Filaire', compare: 'Comparer', reset: 'Réinitialiser' },
  info: { ...en.info, keyFacts: 'Données techniques' },
};
