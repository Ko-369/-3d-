import type { UiDictionary } from "../types";
import { ui as en } from "./en";

export const ui: UiDictionary = {
  ...en,
  brand: { ...en.brand, tagline: 'Entiende el hardware. Ve el sistema.' },
  nav: { explore: 'Explorar', systems: 'Sistemas', lessons: 'Lecciones', library: 'Biblioteca', notes: 'Notas' },
  search: { placeholder: 'Buscar hardware, buses, conceptos…' },
  library: { ...en.library, title: 'Biblioteca de hardware' },
  tools: { ...en.tools, rotate: 'Rotar', zoom: 'Zoom', isolate: 'Aislar', section: 'Sección', layers: 'Malla', compare: 'Comparar', reset: 'Restablecer' },
  info: { ...en.info, keyFacts: 'Datos de ingeniería' },
};
