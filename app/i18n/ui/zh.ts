import type { UiDictionary } from "../types";

export const ui: UiDictionary = {
  meta: {
    title: "Computer Architecture Lab — 3D 计算机硬件与系统实验室",
    description: "通过九个可交互 3D 硬件标本探索主板、CPU、GPU、内存、存储、电源、散热、网络与完整计算机系统。",
    ogTitle: "Computer Architecture Lab — 3D 计算机硬件与系统实验室",
    ogDescription: "通过 3D 模型、结构热点、对比、测验和系统视图理解计算机硬件组成与计算机系统。",
    imageAlt: "展示 3D 主板、硬件结构热点与系统架构控制面板的交互式计算机硬件实验室",
  },
  brand: { tagline: "看懂硬件，理解系统", home: "Computer Architecture Lab 首页" },
  nav: { explore: "探索", systems: "系统", lessons: "课程", library: "资料库", notes: "笔记" },
  search: { placeholder: "搜索硬件、总线或系统概念…" },
  profile: { open: "打开学习者档案" },
  language: { label: "语言", choose: "选择语言" },
  library: {
    title: "硬件组件库", open: "打开硬件组件库", close: "关闭组件库", saved: "已收藏组件",
    viewAll: "查看全部组件",
    quoteLine1: "一台计算机", quoteLine2: "本质上是系统的系统。", quoteSign: "沿着每一条连接去理解它。",
  },
  tools: {
    label: "3D 硬件查看器工具", rotate: "旋转", zoom: "缩放", isolate: "单独显示",
    section: "剖面", layers: "线框", compare: "对比", reset: "重置",
  },
  viewer: {
    title: "{organ}互动查看器",
    canvas: "可交互的 3D 计算机硬件模型。拖动旋转，滚轮缩放，点击结构标记查看说明。",
    tip: "操作", tipDrag: "拖动：旋转模型", tipScroll: "滚轮：缩放视图", tipClick: "点击标记：查看结构",
    loading: "正在加载{organ}", autoRotate: "自动旋转",
    caption: "3D 硬件标本 · 点击标记探索结构", structures: "该组件中的关键结构",
  },
  info: {
    kicker: "正在查看：{organ}", keyFacts: "工程参数", size: "规格尺寸", weight: "重量", daily: "吞吐 / 活动",
    location: "系统位置", bloodSupply: "接口 / 供电", function: "主要功能",
    medical: "工程意义", didYouKnow: "架构知识", viewLesson: "进入引导课程",
    animate: "动画", quiz: "测验", compare: "对比",
  },
  compare: {
    title: "硬件组件对比", comparing: "当前组件", reference: "参照组件",
    primaryRole: "主要作用", scale: "物理尺度", vs: "对比", close: "关闭对比",
  },
  cards: {
    resources: "{organ}学习资源",
    microscopic: "内部结构", compareOrgans: "组件对比", functionAnimation: "数据 / 能量流",
    clinicalNotes: "诊断与瓶颈", whereItWorks: "系统上下文", commonConditions: "常见故障与性能瓶颈",
    exploreTissue: "查看内部结构", openComparison: "打开对比", playAnimation: "播放流动动画",
    seeAll: "查看全部", seeSystem: "查看系统关系",
    playAria: "播放{organ}的数据或能量流动画", systemAria: "查看{organ}在计算机系统中的位置",
  },
  quiz: {
    start: "开始结构标注测验", find: "找出", progress: "第 {current} / {total} 题",
    correct: "正确", wrong: "还差一点", reveal: "你点击的是{label}", answer: "正确结构 {label} 已用绿色标出",
    done: "测验完成", score: "答对 {score} / {total}", retry: "再试一次",
    exit: "退出测验", hint: "在 3D 模型上点击对应的结构标记",
  },
  modal: {
    guided: "计算机体系结构引导实验", close: "关闭", continueExploring: "继续探索",
    quizTitle: "{organ}快速测验", motionTitle: "{organ}的数据 / 能量流",
    bodyTitle: "{organ}在计算机系统中的位置", insideTitle: "深入{organ}",
    quizPrompt: "以下哪种说法最准确地描述{organ}？",
    quizA: "它承担专门功能，并通过数据、控制信号或电能与其他子系统协作",
    quizB: "它完全独立于计算机中的其他硬件工作",
    quizC: "它只在计算机开机阶段工作",
    lessonBody: "跟随高亮结构，旋转 3D 模型，把物理结构与信号流、供电、散热和系统级功能联系起来，建立完整的计算机硬件心智模型。",
    systemIntro: "位置：{location}。继续追踪{organ}如何与固件、操作系统以及其他硬件子系统连接。",
    system: "所属子系统", primaryRole: "主要作用", bloodSupply: "接口 / 供电",
  },
};
