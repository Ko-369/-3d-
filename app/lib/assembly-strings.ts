// Self-contained copy for the assembly lab. It sits outside the 12-locale
// organ dictionary so the feature ships for zh/en without touching every locale
// file; anything unmapped falls back to English.

export type AssemblyStrings = {
  title: string;
  subtitle: string;
  back: string;
  hint: string;
  hintDrag: string;
  hintScroll: string;
  progress: (placed: number, total: number) => string;
  modeFree: string;
  modeGuided: string;
  modeHintFree: string;
  modeHintGuided: string;
  reset: string;
  loading: string;
  next: (part: string) => string;
  doneTitle: string;
  doneBody: string;
  doneAgain: string;
  partNames: Record<string, string>;
  calib: {
    title: string;
    hint: string;
    active: (part: string) => string;
    copy: string;
    copied: string;
    keys: string[];
  };
};

const en: AssemblyStrings = {
  title: "PC Assembly Lab",
  subtitle: "Drag each component into the case to build a PC",
  back: "Back to explore",
  hint: "Assembly",
  hintDrag: "Drag a component to move it",
  hintScroll: "Scroll to zoom, drag empty space to rotate",
  progress: (placed, total) => `${placed} / ${total} installed`,
  modeFree: "Free build",
  modeGuided: "Guided",
  modeHintFree: "Assemble in any order",
  modeHintGuided: "Follow the recommended order",
  reset: "Reset",
  loading: "Loading components",
  next: (part) => `Next: install the ${part}`,
  doneTitle: "Build complete",
  doneBody: "Every component is in place. Nice work.",
  doneAgain: "Build again",
  partNames: {
    motherboard: "Motherboard",
    cpu: "CPU",
    memory: "Memory",
    cooling: "CPU Cooler",
    gpu: "Graphics Card",
    network: "Network Card",
    storage: "SSD",
    power: "Power Supply",
  },
  calib: {
    title: "Calibration",
    hint: "Drag a part, fine-tune with the keys below, then copy the snippet into assembly-data.ts.",
    active: (part) => `Adjusting: ${part}`,
    copy: "Copy slot",
    copied: "Copied",
    keys: ["Drag — position", "← → — rotate Y", "↑ ↓ — rotate X", ", . — rotate Z", "[ ] — size"],
  },
};

const zh: AssemblyStrings = {
  title: "组装机箱",
  subtitle: "把每个硬件拖进机箱里，组装一台电脑",
  back: "返回浏览",
  hint: "装机",
  hintDrag: "拖动硬件进行安装",
  hintScroll: "滚轮缩放，拖动空白处旋转视角",
  progress: (placed, total) => `已装 ${placed} / ${total}`,
  modeFree: "自由组装",
  modeGuided: "分步引导",
  modeHintFree: "任意顺序安装",
  modeHintGuided: "按推荐顺序安装",
  reset: "重置",
  loading: "正在加载硬件",
  next: (part) => `下一步：安装${part}`,
  doneTitle: "组装完成",
  doneBody: "所有硬件都已就位，干得漂亮。",
  doneAgain: "重新组装",
  partNames: {
    motherboard: "主板",
    cpu: "CPU",
    memory: "内存",
    cooling: "散热器",
    gpu: "显卡",
    network: "网卡",
    storage: "固态硬盘",
    power: "电源",
  },
  calib: {
    title: "标定模式",
    hint: "拖动硬件到目标位置，用下方按键微调，然后复制片段粘回 assembly-data.ts。",
    active: (part) => `正在调整：${part}`,
    copy: "复制安装位",
    copied: "已复制",
    keys: ["拖动 — 位置", "← → — 绕 Y 旋转", "↑ ↓ — 绕 X 旋转", ", . — 绕 Z 旋转", "[ ] — 尺寸"],
  },
};

export function getAssemblyStrings(locale: string): AssemblyStrings {
  return locale === "zh" ? zh : en;
}
