import type { UiDictionary } from "../types";

export const ui: UiDictionary = {
  meta: {
    title: "Computer Architecture Lab — Explore the machine in 3D",
    description:
      "Explore nine interactive 3D computer hardware specimens — motherboard, CPU, GPU, memory, storage, power, cooling, networking and the complete system.",
    ogTitle: "Computer Architecture Lab — Explore the machine in 3D",
    ogDescription: "Learn computer hardware and system architecture through interactive 3D specimens, structure hotspots, comparisons, quizzes and system views.",
    imageAlt: "A premium interactive computer hardware laboratory showing a 3D motherboard and system architecture controls",
  },
  brand: { tagline: "Understand hardware. See the system.", home: "Computer Architecture Lab home" },
  nav: { explore: "Explore", systems: "Systems", lessons: "Lessons", library: "Library", notes: "Notes" },
  search: { placeholder: "Search hardware, buses, concepts…" },
  profile: { open: "Open learner profile" },
  language: { label: "Language", choose: "Choose a language" },
  library: {
    title: "Hardware library", open: "Open hardware library", close: "Close library", saved: "Saved components",
    viewAll: "View all components",
    quoteLine1: "A computer is", quoteLine2: "a system of systems.", quoteSign: "Trace every connection.",
  },
  tools: {
    label: "3D hardware viewer tools", rotate: "Rotate", zoom: "Zoom", isolate: "Isolate",
    section: "Cross-section", layers: "Wireframe", compare: "Compare", reset: "Reset",
  },
  viewer: {
    title: "{organ} interactive viewer",
    canvas: "Interactive 3D computer hardware model. Drag to rotate, scroll to zoom, and click a marker to inspect that structure.",
    tip: "Controls", tipDrag: "Drag to rotate", tipScroll: "Scroll to zoom", tipClick: "Click a marker to inspect",
    loading: "Preparing the {organ}", autoRotate: "Auto rotate",
    caption: "3D hardware specimen · click a marker to explore", structures: "Structures in this component",
  },
  info: {
    kicker: "Inspecting {organ}", keyFacts: "Engineering facts", size: "Form factor", weight: "Mass", daily: "Throughput",
    location: "System position", bloodSupply: "Interfaces / power", function: "Primary function",
    medical: "Engineering significance", didYouKnow: "Architecture note", viewLesson: "Open guided lesson",
    animate: "Animate", quiz: "Quiz", compare: "Compare",
  },
  compare: {
    title: "Hardware comparison", comparing: "Selected component", reference: "Reference",
    primaryRole: "Primary role", scale: "Physical scale", vs: "vs.", close: "Close comparison",
  },
  cards: {
    resources: "{organ} learning resources",
    microscopic: "Inside the hardware", compareOrgans: "Compare components", functionAnimation: "Data / energy flow",
    clinicalNotes: "Diagnostics", whereItWorks: "System context", commonConditions: "Common failure modes & bottlenecks",
    exploreTissue: "Inspect internals", openComparison: "Open comparison", playAnimation: "Play flow animation",
    seeAll: "Review all", seeSystem: "See system context",
    playAria: "Play the {organ} function animation", systemAria: "See where the {organ} sits in the computer system",
  },
  quiz: {
    start: "Start the labelling quiz", find: "Find the", progress: "{current} of {total}",
    correct: "Correct", wrong: "Not quite", reveal: "That marker is {label}", answer: "{label} is highlighted in green",
    done: "Quiz complete", score: "{score} of {total} correct", retry: "Try again",
    exit: "Exit quiz", hint: "Click the matching marker on the 3D model",
  },
  modal: {
    guided: "Guided architecture lab", close: "Close", continueExploring: "Continue exploring",
    quizTitle: "{organ} quick quiz", motionTitle: "{organ} data / energy flow",
    bodyTitle: "{organ} in the computer system", insideTitle: "Inside the {organ}",
    quizPrompt: "Which statement best describes the {organ}?",
    quizA: "It performs a specialized role while exchanging data or power with other subsystems",
    quizB: "It works completely independently of the rest of the computer",
    quizC: "It is only active while the computer is starting",
    lessonBody:
      "Follow the highlighted structures, rotate the 3D specimen and connect physical design with signal flow, power, thermal behavior and system-level function.",
    systemIntro: "Located {location}. Trace how the {organ} connects to firmware, the operating system and the rest of the hardware platform.",
    system: "Subsystem", primaryRole: "Primary role", bloodSupply: "Interfaces / power",
  },
};
