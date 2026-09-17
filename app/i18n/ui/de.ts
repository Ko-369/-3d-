import type { UiDictionary } from "../types";
import { ui as en } from "./en";

export const ui: UiDictionary = {
  ...en,
  brand: { ...en.brand, tagline: 'Hardware verstehen. System sehen.' },
  nav: { explore: 'Erkunden', systems: 'Systeme', lessons: 'Lektionen', library: 'Bibliothek', notes: 'Notizen' },
  search: { placeholder: 'Hardware, Busse, Konzepte suchen…' },
  library: { ...en.library, title: 'Hardware-Bibliothek' },
  tools: { ...en.tools, rotate: 'Drehen', zoom: 'Zoom', isolate: 'Isolieren', section: 'Querschnitt', layers: 'Drahtmodell', compare: 'Vergleichen', reset: 'Zurücksetzen' },
  info: { ...en.info, keyFacts: 'Technische Daten' },
};
