# Computer Architecture Lab

A 3D interactive learning project for **computer hardware composition and computer systems**, rebuilt on top of the original Anatomy Atelier interaction architecture.

## What is preserved from the original project

- 9 interactive 3D specimens
- 35 clickable 3D hotspots, with hover/selection callouts
- 7 3D tools: rotate, zoom, isolate, cross-section, wireframe/layers, compare, reset
- Auto-rotation, orbit controls, zoom, model transition animation, loading progress and hotspot occlusion
- Structure-labelling quiz with randomized questions, feedback, score and retry
- Comparison strip
- Guided lesson, function-flow animation and system-context modal
- 6 learning/resource cards beneath the main workspace
- Search, responsive mobile component library and language switcher
- 12 locale entries
- The original responsive layouts, GSAP reveal transitions and accessibility structure

## Hardware specimens

1. Motherboard
2. CPU
3. Graphics card / GPU
4. Memory / RAM
5. NVMe SSD
6. Power supply / PSU
7. CPU cooling
8. Network adapter
9. Complete computer system

Each specimen ships with its own procedural GLB model and five supporting visual assets (thumbnail, component view, internal view, comparison view and system-location view).

## Run locally

Requires Node.js 22.13+.

```bash
npm install
npm run dev
```

Open the local URL printed by the development server. Use `/zh` for Chinese or `/en` for English.

## Main source locations

- `app/components/AnatomyApp.tsx` — main application shell and learning interactions
- `app/components/OrganViewer.tsx` — 3D viewer UI, labelling quiz and tool controls
- `app/lib/anatomy-data.ts` — hardware specimen structure, model paths and hotspot coordinates
- `app/lib/three/` — Three.js renderer, asset loader and hotspot engine
- `app/i18n/` — UI and component content
- `public/models/` — 9 hardware GLB models
- `public/hardware/` — 45 supporting WebP learning assets
- `scripts/generate_hardware_assets.py` — reproducible model/asset generator

Internal filenames such as `AnatomyApp`, `OrganViewer` and `anatomy-data.ts` are retained to minimize structural changes to the original codebase; the user-facing project is entirely computer-hardware focused.
