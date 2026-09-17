import type { UiDictionary } from "../types";
import { ui as en } from "./en";

export const ui: UiDictionary = {
  ...en,
  brand: { ...en.brand, tagline: 'Pahami hardware. Lihat sistem.' },
  nav: { explore: 'Jelajahi', systems: 'Sistem', lessons: 'Pelajaran', library: 'Pustaka', notes: 'Catatan' },
  search: { placeholder: 'Cari hardware, bus, konsep…' },
  library: { ...en.library, title: 'Pustaka hardware' },
  tools: { ...en.tools, rotate: 'Putar', zoom: 'Zoom', isolate: 'Isolasi', section: 'Penampang', layers: 'Wireframe', compare: 'Bandingkan', reset: 'Reset' },
  info: { ...en.info, keyFacts: 'Fakta rekayasa' },
};
