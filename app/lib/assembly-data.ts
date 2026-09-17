// The PC-assembly lab. All spatial values are expressed in the CASE's own
// baked units (see CASE_BBOX below). The engine scales the case group up to
// fill the viewport, so these numbers never change when the camera or world
// scale does.

export type AssemblyPartId =
  | "motherboard"
  | "cpu"
  | "memory"
  | "cooling"
  | "gpu"
  | "network"
  | "storage"
  | "power";

export type AssemblySlot = {
  id: AssemblyPartId;
  model: string;
  accent: string;
  /**
   * Desired bounding-box size in case units, per axis [x, y, z]. The loader
   * non-uniformly scales each part so its baked bounding box matches this, which
   * also corrects the independently-baked aspect ratios (e.g. the square
   * motherboard scan becomes the rectangular ATX footprint it really is).
   */
  size: [number, number, number];
  /** Mount position (the part's bbox centre) in case units. */
  position: [number, number, number];
  /** Extra Euler rotation (radians) applied after centring. Parts keep identity
   *  here; if a part's textured front ends up facing the back wall, add
   *  [0, Math.PI, 0] to flip it toward the open side. */
  rotation: [number, number, number];
  /** Snap radius in case units — drop within this of the slot and it locks in. */
  snap: number;
};

/**
 * Bounding box of `case.glb` in its own baked units, measured from the raw
 * vertex positions:
 *
 *   x: -0.462 ..  0.374   (left .. right, 0.836 wide)
 *   y:  0.000 ..  0.771   (bottom .. top, 0.771 tall)
 *   z: -0.267 ..  0.139   (back wall .. front panel, 0.407 deep)
 *
 * Voxel analysis of the scan shows a fully-closed tower: a solid back (-z), a
 * dense front mesh/grill panel (+z), solid sides/top, and a floor with a PSU
 * vent. The interior cavity is genuinely empty. To turn it into an "assemble
 * into the open front" view, the engine clips away the front grill (z beyond
 * CASE_OPEN_Z) and closes the -y floor gap — leaving one open side and nothing
 * inside until parts are dropped in.
 */
export const CASE_BBOX = {
  min: [-0.462, 0, -0.267] as [number, number, number],
  max: [0.374, 0.771, 0.139] as [number, number, number],
  size: [0.836, 0.771, 0.407] as [number, number, number],
};

/** The front grill is clipped past this z so the interior is open for assembly. */
export const CASE_OPEN_Z = 0.02;

/** Recommended real-world assembly order for guided mode. */
export const BUILD_ORDER: AssemblyPartId[] = [
  "motherboard",
  "cpu",
  "memory",
  "cooling",
  "storage",
  "gpu",
  "network",
  "power",
];

/**
 * Mount slots. Every value is in the case's baked units (see CASE_BBOX): x runs
 * left→right, y bottom→top, z back wall→open front. A slot's `size` is the
 * part's bounding box BEFORE its `rotation` is applied — the loader scales each
 * part's baked bbox onto `size`, then rotates it about that bbox centre. So for
 * a part rotated 90° about x (the GPU and NIC, which the scans bake standing on
 * edge but which must sit flat/horizontal in the case), `size` lists the
 * pre-rotation axes: [x, depth→z, thickness→y].
 *
 * Layout (standard ATX tower, open front):
 *   motherboard  vertical, flush against the back wall
 *   cpu          on the board's socket, upper-middle
 *   memory       DIMMs right of the socket, standing on the board
 *   cooling      tower cooler in front of the CPU, extending toward the front
 *   storage      M.2 SSD flat on the board, below-left of the socket
 *   gpu          horizontal card in the x16 slot, lower-middle
 *   network      horizontal NIC in the slot below the GPU
 *   power        PSU box in the bottom-rear corner
 */
export const ASSEMBLY_SLOTS: AssemblySlot[] = [
  {
    id: "motherboard",
    model: "/models/motherboard.glb",
    accent: "#55d8e8",
    // Vertical ATX board against the back (-z) wall, facing the open front.
    size: [0.66, 0.58, 0.05],
    position: [-0.06, 0.46, -0.235],
    rotation: [0, 0, 0],
    snap: 0.16,
  },
  {
    id: "cpu",
    model: "/models/cpu.glb",
    accent: "#efb54a",
    // Square chip in the socket, upper-middle of the board, flush against it.
    size: [0.13, 0.13, 0.035],
    position: [-0.14, 0.6, -0.18],
    rotation: [0, 0, 0],
    snap: 0.08,
  },
  {
    id: "memory",
    model: "/models/memory.glb",
    accent: "#9f7aea",
    // DIMM sticks right of the socket, standing upright off the board. The scan
    // is baked lying flat (thin in z, face parallel to the board), so it is
    // rolled 90° about x to stand up, then yawed 90° about z so its length runs
    // top→bottom along the board's vertical DIMM slots. Pre-rotation size is
    // [len, height, thickness].
    size: [0.22, 0.16, 0.035],
    position: [0.1, 0.56, -0.13],
    rotation: [Math.PI / 2, -Math.PI / 2, 0],
    snap: 0.1,
  },
  {
    id: "cooling",
    model: "/models/cooling.glb",
    accent: "#2bb7a9",
    // Tower cooler in front of the CPU, its fin stack extending toward the front.
    size: [0.2, 0.12, 0.28],
    position: [-0.13, 0.6, -0.02],
    rotation: [0, 0, 0],
    snap: 0.1,
  },
  {
    id: "storage",
    model: "/models/storage.glb",
    accent: "#6fcf97",
    // M.2 SSD flat on the board, below-left of the socket.
    size: [0.2, 0.045, 0.02],
    position: [-0.14, 0.27, -0.19],
    rotation: [0, 0, 0],
    snap: 0.08,
  },
  {
    id: "gpu",
    model: "/models/gpu.glb",
    accent: "#5a8dee",
    // Horizontal graphics card in the x16 slot, lower-middle. The scan is baked
    // standing on edge (thin in z), so it is rolled 90° about x to lie flat with
    // its width running back→front: pre-rotation size is [len, depth, thickness].
    size: [0.55, 0.28, 0.08],
    position: [-0.02, 0.36, -0.07],
    rotation: [Math.PI / 2, 0, 0],
    snap: 0.16,
  },
  {
    id: "network",
    model: "/models/network.glb",
    accent: "#2bb7a9",
    // Horizontal NIC in the PCIe slot below the graphics card (same edge-on scan
    // orientation, rolled 90° about x to lie flat).
    size: [0.3, 0.2, 0.04],
    position: [-0.02, 0.2, -0.1],
    rotation: [Math.PI / 2, 0, 0],
    snap: 0.1,
  },
  {
    id: "power",
    model: "/models/power.glb",
    accent: "#e9894a",
    // PSU box in the bottom-rear corner, below the motherboard.
    size: [0.24, 0.14, 0.26],
    position: [0.16, 0.075, -0.13],
    rotation: [0, 0, 0],
    snap: 0.14,
  },
];

export const slotById = Object.fromEntries(ASSEMBLY_SLOTS.map((slot) => [slot.id, slot])) as Record<
  AssemblyPartId,
  AssemblySlot
>;
