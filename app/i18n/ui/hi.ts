import type { UiDictionary } from "../types";
import { ui as en } from "./en";

export const ui: UiDictionary = {
  ...en,
  brand: { ...en.brand, tagline: 'हार्डवेयर समझें। सिस्टम देखें।' },
  nav: { explore: 'खोजें', systems: 'सिस्टम', lessons: 'पाठ', library: 'लाइब्रेरी', notes: 'नोट्स' },
  search: { placeholder: 'हार्डवेयर, बस, अवधारणाएँ खोजें…' },
  library: { ...en.library, title: 'हार्डवेयर लाइब्रेरी' },
  tools: { ...en.tools, rotate: 'घुमाएँ', zoom: 'ज़ूम', isolate: 'अलग करें', section: 'क्रॉस-सेक्शन', layers: 'वायरफ्रेम', compare: 'तुलना', reset: 'रीसेट' },
  info: { ...en.info, keyFacts: 'इंजीनियरिंग तथ्य' },
};
