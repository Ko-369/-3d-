import type { OrganContentDictionary } from "../types";
import { organs as en } from "./en";

export const organs: OrganContentDictionary = {
  motherboard: { ...en.motherboard, name: '메인보드', system: '플랫폼 및 인터커넥트', poetic: '시스템의 신호 지도' },
  cpu: { ...en.cpu, name: 'CPU', system: '처리', poetic: '명령 실행 엔진' },
  gpu: { ...en.gpu, name: '그래픽 카드 / GPU', system: '병렬 연산 및 그래픽', poetic: '병렬 작업 엔진' },
  memory: { ...en.memory, name: '메모리 RAM', system: '작업 메모리', poetic: '활성 작업 공간' },
  storage: { ...en.storage, name: 'NVMe SSD', system: '영구 저장장치', poetic: '지속되는 메모리' },
  power: { ...en.power, name: '전원공급장치 PSU', system: '전력 공급', poetic: '에너지 변환기' },
  cooling: { ...en.cooling, name: 'CPU 쿨링', system: '열 관리', poetic: '열 이동 경로' },
  network: { ...en.network, name: '네트워크 어댑터', system: '통신 및 I/O', poetic: '데이터 게이트웨이' },
  case: { ...en.case, name: '컴퓨터 시스템', system: '통합 시스템', poetic: '완전한 머신' },
};
