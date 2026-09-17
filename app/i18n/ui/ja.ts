import type { UiDictionary } from "../types";
import { ui as en } from "./en";

export const ui: UiDictionary = {
  ...en,
  brand: { ...en.brand, tagline: 'ハードウェアを理解し、システムを見る。' },
  nav: { explore: '探索', systems: 'システム', lessons: 'レッスン', library: 'ライブラリ', notes: 'ノート' },
  search: { placeholder: 'ハードウェア、バス、概念を検索…' },
  library: { ...en.library, title: 'ハードウェアライブラリ' },
  tools: { ...en.tools, rotate: '回転', zoom: 'ズーム', isolate: '分離', section: '断面', layers: 'ワイヤー', compare: '比較', reset: 'リセット' },
  info: { ...en.info, keyFacts: 'エンジニアリング情報' },
};
