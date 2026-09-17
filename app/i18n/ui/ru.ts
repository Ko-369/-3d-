import type { UiDictionary } from "../types";
import { ui as en } from "./en";

export const ui: UiDictionary = {
  ...en,
  brand: { ...en.brand, tagline: 'Поймите железо. Увидьте систему.' },
  nav: { explore: 'Обзор', systems: 'Системы', lessons: 'Уроки', library: 'Библиотека', notes: 'Заметки' },
  search: { placeholder: 'Поиск оборудования, шин, понятий…' },
  library: { ...en.library, title: 'Библиотека компонентов' },
  tools: { ...en.tools, rotate: 'Вращать', zoom: 'Масштаб', isolate: 'Изолировать', section: 'Сечение', layers: 'Каркас', compare: 'Сравнить', reset: 'Сбросить' },
  info: { ...en.info, keyFacts: 'Инженерные данные' },
};
