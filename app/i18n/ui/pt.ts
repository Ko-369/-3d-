import type { UiDictionary } from "../types";
import { ui as en } from "./en";

export const ui: UiDictionary = {
  ...en,
  brand: { ...en.brand, tagline: 'Entenda o hardware. Veja o sistema.' },
  nav: { explore: 'Explorar', systems: 'Sistemas', lessons: 'Lições', library: 'Biblioteca', notes: 'Notas' },
  search: { placeholder: 'Buscar hardware, barramentos, conceitos…' },
  library: { ...en.library, title: 'Biblioteca de hardware' },
  tools: { ...en.tools, rotate: 'Girar', zoom: 'Zoom', isolate: 'Isolar', section: 'Corte', layers: 'Malha', compare: 'Comparar', reset: 'Redefinir' },
  info: { ...en.info, keyFacts: 'Dados de engenharia' },
};
