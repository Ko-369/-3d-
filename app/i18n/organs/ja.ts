import type { OrganContentDictionary } from "../types";
import { organs as en } from "./en";

export const organs: OrganContentDictionary = {
  motherboard: { ...en.motherboard, name: 'マザーボード', system: 'プラットフォームと相互接続', poetic: 'システムの信号地図' },
  cpu: { ...en.cpu, name: 'CPU', system: '処理', poetic: '命令実行エンジン' },
  gpu: { ...en.gpu, name: 'グラフィックスカード / GPU', system: '並列計算とグラフィックス', poetic: '並列ワークホース' },
  memory: { ...en.memory, name: 'メモリ RAM', system: '作業メモリ', poetic: 'アクティブな作業領域' },
  storage: { ...en.storage, name: 'NVMe SSD', system: '永続ストレージ', poetic: '永続する記憶' },
  power: { ...en.power, name: '電源ユニット PSU', system: '電力供給', poetic: 'エネルギー変換器' },
  cooling: { ...en.cooling, name: 'CPU クーラー', system: '熱管理', poetic: '熱のハイウェイ' },
  network: { ...en.network, name: 'ネットワークアダプター', system: '通信と I/O', poetic: 'データゲートウェイ' },
  case: { ...en.case, name: 'コンピュータシステム', system: '統合システム', poetic: '完全なマシン' },
};
