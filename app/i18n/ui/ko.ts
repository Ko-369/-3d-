import type { UiDictionary } from "../types";
import { ui as en } from "./en";

export const ui: UiDictionary = {
  ...en,
  brand: { ...en.brand, tagline: '하드웨어를 이해하고 시스템을 보세요.' },
  nav: { explore: '탐색', systems: '시스템', lessons: '레슨', library: '라이브러리', notes: '노트' },
  search: { placeholder: '하드웨어, 버스, 개념 검색…' },
  library: { ...en.library, title: '하드웨어 라이브러리' },
  tools: { ...en.tools, rotate: '회전', zoom: '확대', isolate: '분리', section: '단면', layers: '와이어프레임', compare: '비교', reset: '초기화' },
  info: { ...en.info, keyFacts: '엔지니어링 정보' },
};
