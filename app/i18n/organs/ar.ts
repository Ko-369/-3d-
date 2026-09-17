import type { OrganContentDictionary } from "../types";
import { organs as en } from "./en";

export const organs: OrganContentDictionary = {
  motherboard: { ...en.motherboard, name: 'اللوحة الأم', system: 'المنصة والترابط', poetic: 'خريطة إشارات النظام' },
  cpu: { ...en.cpu, name: 'المعالج CPU', system: 'المعالجة', poetic: 'محرك التعليمات' },
  gpu: { ...en.gpu, name: 'بطاقة الرسوميات / GPU', system: 'الحوسبة المتوازية والرسوميات', poetic: 'محرك العمل المتوازي' },
  memory: { ...en.memory, name: 'ذاكرة RAM', system: 'الذاكرة العاملة', poetic: 'مساحة العمل النشطة' },
  storage: { ...en.storage, name: 'وحدة NVMe SSD', system: 'التخزين الدائم', poetic: 'الذاكرة الدائمة' },
  power: { ...en.power, name: 'مزود الطاقة PSU', system: 'توصيل الطاقة', poetic: 'محوّل الطاقة' },
  cooling: { ...en.cooling, name: 'تبريد المعالج', system: 'الإدارة الحرارية', poetic: 'مسار الحرارة' },
  network: { ...en.network, name: 'مهايئ الشبكة', system: 'الاتصال والإدخال/الإخراج', poetic: 'بوابة البيانات' },
  case: { ...en.case, name: 'نظام الحاسوب', system: 'النظام المتكامل', poetic: 'الآلة الكاملة' },
};
