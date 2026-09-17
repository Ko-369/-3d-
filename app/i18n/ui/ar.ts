import type { UiDictionary } from "../types";
import { ui as en } from "./en";

export const ui: UiDictionary = {
  ...en,
  brand: { ...en.brand, tagline: 'افهم العتاد. شاهد النظام.' },
  nav: { explore: 'استكشاف', systems: 'الأنظمة', lessons: 'الدروس', library: 'المكتبة', notes: 'ملاحظات' },
  search: { placeholder: 'ابحث عن العتاد والحافلات والمفاهيم…' },
  library: { ...en.library, title: 'مكتبة العتاد' },
  tools: { ...en.tools, rotate: 'تدوير', zoom: 'تكبير', isolate: 'عزل', section: 'مقطع', layers: 'هيكل شبكي', compare: 'مقارنة', reset: 'إعادة ضبط' },
  info: { ...en.info, keyFacts: 'حقائق هندسية' },
};
