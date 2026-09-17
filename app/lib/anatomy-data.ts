// STRUCTURE ONLY — translatable prose lives in app/i18n/organs/*.ts.
// The original project exposed nine interactive specimens and 35 hotspots.
// This computer-systems edition keeps that exact interaction density while
// replacing the anatomy content with real hardware architecture concepts.

export type OrganId =
  | "motherboard"
  | "cpu"
  | "gpu"
  | "memory"
  | "storage"
  | "power"
  | "cooling"
  | "network"
  | "case";

export type HotspotStructure = {
  id: string;
  /** Stable technical term used as the cross-locale identity. */
  ta: string;
  position: [number, number, number];
  color: string;
};

export type OrganStructure = {
  id: OrganId;
  model: string;
  icon: string;
  accent: string;
  illustrated: boolean;
  /** Canonical hardware / standards name. */
  scientificName: string;
  hotspots: HotspotStructure[];
};

export const organStructures: OrganStructure[] = [
  {
    id: "motherboard",
    model: "/models/motherboard.glb",
    icon: "▣",
    accent: "#55d8e8",
    illustrated: true,
    scientificName: "ASUS ROG Strix B660",
    hotspots: [
      { id: "socket", ta: "CPU socket", position: [-0.5, 0.5, 0.26], color: "#55d8e8" },
      { id: "dimm", ta: "DIMM slots", position: [0.8, 0.65, 0.26], color: "#9f7aea" },
      { id: "pcie", ta: "PCIe slots", position: [0.3, -1.0, 0.26], color: "#5a8dee" },
      { id: "chipset", ta: "Chipset", position: [1.0, -0.7, 0.26], color: "#efb54a" },
      { id: "vrm", ta: "VRM", position: [-1.3, 0.85, 0.26], color: "#ef6b6b" },
      { id: "m2", ta: "M.2 slot", position: [0.0, -0.1, 0.26], color: "#6fcf97" },
    ],
  },
  {
    id: "cpu",
    model: "/models/cpu.glb",
    icon: "⌘",
    accent: "#efb54a",
    illustrated: true,
    scientificName: "Central Processing Unit",
    hotspots: [
      { id: "cores", ta: "CPU cores", position: [-0.48, -0.46, 0.54], color: "#55d8e8" },
      { id: "cache", ta: "Last-level cache", position: [0.93, 0.0, 0.52], color: "#efb54a" },
      { id: "memory-controller", ta: "Integrated memory controller", position: [0.46, 0.46, 0.54], color: "#9f7aea" },
      { id: "interconnect", ta: "On-die interconnect", position: [0.0, -0.92, 0.52], color: "#5a8dee" },
    ],
  },
  {
    id: "gpu",
    model: "/models/gpu.glb",
    icon: "◫",
    accent: "#5a8dee",
    illustrated: true,
    scientificName: "Graphics Processing Unit",
    hotspots: [
      { id: "fans", ta: "Cooling fans", position: [0, 0.55, 0.33], color: "#55d8e8" },
      { id: "heatsink", ta: "Heatsink", position: [-0.6, 0.1, 0.33], color: "#2bb7a9" },
      { id: "gpu-die", ta: "GPU package", position: [0, -0.1, 0.33], color: "#efb54a" },
      { id: "vram", ta: "VRAM", position: [0.8, -0.45, 0.33], color: "#9f7aea" },
      { id: "pcie-edge", ta: "PCIe connector", position: [0, -0.95, 0.1], color: "#5a8dee" },
    ],
  },
  {
    id: "memory",
    model: "/models/memory.glb",
    icon: "▥",
    accent: "#9f7aea",
    illustrated: true,
    scientificName: "DDR SDRAM DIMM",
    hotspots: [
      { id: "dram", ta: "DRAM chips", position: [0, 0, 0.18], color: "#9f7aea" },
      { id: "spd", ta: "SPD / profile data", position: [1.55, 0, 0.18], color: "#efb54a" },
      { id: "contacts", ta: "Edge contacts", position: [0, -0.66, 0.0], color: "#5a8dee" },
    ],
  },
  {
    id: "storage",
    model: "/models/storage.glb",
    icon: "▰",
    accent: "#6fcf97",
    illustrated: true,
    scientificName: "NVMe Solid-State Drive",
    hotspots: [
      { id: "controller", ta: "NVMe controller", position: [1.1, 0, 0.08], color: "#efb54a" },
      { id: "nand", ta: "NAND flash", position: [0, 0, 0.08], color: "#6fcf97" },
      { id: "connector", ta: "M.2 connector", position: [1.75, 0.35, 0.0], color: "#5a8dee" },
    ],
  },
  {
    id: "power",
    model: "/models/power.glb",
    icon: "ϟ",
    accent: "#e9894a",
    illustrated: true,
    scientificName: "ATX Power Supply Unit",
    hotspots: [
      { id: "fan", ta: "Cooling fan", position: [0, 1.05, 0], color: "#55d8e8" },
      { id: "transformer", ta: "Switching transformer", position: [-0.3, -0.3, -0.3], color: "#efb54a" },
      { id: "modular", ta: "Modular outputs", position: [0, -0.2, 1.52], color: "#2bb7a9" },
    ],
  },
  {
    id: "cooling",
    model: "/models/cooling.glb",
    icon: "❄",
    accent: "#2bb7a9",
    illustrated: true,
    scientificName: "CPU Thermal Solution",
    hotspots: [
      { id: "fan", ta: "PWM fan", position: [0, 0, -1.6], color: "#55d8e8" },
      { id: "fins", ta: "Fin stack", position: [0, 0, 0], color: "#2bb7a9" },
      { id: "heatpipes", ta: "Heat pipes", position: [0, -0.55, -0.3], color: "#efb54a" },
    ],
  },
  {
    id: "network",
    model: "/models/network.glb",
    icon: "⌁",
    accent: "#2bb7a9",
    illustrated: true,
    scientificName: "PCIe Network Interface Controller",
    hotspots: [
      { id: "port", ta: "Ethernet port", position: [1.8, 0.5, 0.21], color: "#2bb7a9" },
      { id: "controller", ta: "NIC controller", position: [0, 0.2, 0.21], color: "#efb54a" },
      { id: "phy", ta: "PHY transceiver", position: [1.1, 0.2, 0.21], color: "#6fcf97" },
      { id: "pcie", ta: "PCIe interface", position: [0, -1.55, 0.0], color: "#5a8dee" },
    ],
  },
  {
    id: "case",
    model: "/models/case.glb",
    icon: "▤",
    accent: "#7b8992",
    illustrated: true,
    scientificName: "Personal Computer System Unit",
    hotspots: [
      { id: "mainboard", ta: "Motherboard", position: [-1.1, 0.3, -0.5], color: "#55d8e8" },
      { id: "graphics", ta: "Graphics subsystem", position: [0, -0.7, -0.3], color: "#5a8dee" },
      { id: "psu", ta: "Power subsystem", position: [0, -1.6, -0.5], color: "#ef6b6b" },
      { id: "airflow", ta: "System airflow", position: [0, 1.2, 0.4], color: "#2bb7a9" },
    ],
  },
];

export const organIds = organStructures.map((organ) => organ.id);
export const structureById = Object.fromEntries(
  organStructures.map((organ) => [organ.id, organ]),
) as Record<OrganId, OrganStructure>;
