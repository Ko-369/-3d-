import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { MeshoptDecoder } from "three/examples/jsm/libs/meshopt_decoder.module.js";
import { disposeObject } from "./dispose";

/** Accent materials glow softly so the hardware reads as "powered" and the
 *  emissive cues pop against the light studio backdrop. */
const ACCENT_EMISSIVE: Record<string, number> = {
  "cyan accent": 0x55d8e8,
  "teal accent": 0x2bb7a9,
  "amber accent": 0xefb54a,
  "blue accent": 0x5a8dee,
  "violet accent": 0x9f7aea,
  "green accent": 0x6fcf97,
  "red accent": 0xef6b6b,
};

const RIM_COLOR = new THREE.Color(0xbfeefc);

/**
 * Adds a view-dependent fresnel rim to a standard material. The rim brightens
 * grazing-angle edges, which is what the eye reads as "solid and three
 * dimensional" — especially on the rounded, bevelled hardware silhouettes.
 * Uniforms are constant across every material, so the shared program cache is
 * safe and no per-material plumbing is needed.
 */
function enableFresnelRim(material: THREE.MeshStandardMaterial) {
  material.onBeforeCompile = (shader) => {
    shader.uniforms.uRimColor = { value: RIM_COLOR };
    shader.uniforms.uRimPower = { value: 3.0 };
    shader.uniforms.uRimStrength = { value: 0.25 };
    shader.fragmentShader =
      "uniform vec3 uRimColor;\nuniform float uRimPower;\nuniform float uRimStrength;\n" +
      shader.fragmentShader;
    shader.fragmentShader = shader.fragmentShader.replace(
      "#include <emissivemap_fragment>",
      `#include <emissivemap_fragment>
       vec3 vn = normalize( normal );
       float rim = pow( 1.0 - clamp( dot( vn, normalize( vViewPosition ) ), 0.0, 1.0 ), uRimPower );
       totalEmissiveRadiance += uRimColor * rim * uRimStrength;`,
    );
  };
  material.needsUpdate = true;
}

/** Edge length of the cube every organ is normalised into, so hotspot
 *  coordinates authored in `anatomy-data` mean the same thing for each model. */
export const FIT_SIZE = 3.8;

const CACHE_LIMIT = 3;

export type LoadedOrgan = {
  url: string;
  /** Hotspot space: the fitted model, centred on the origin, spanning FIT_SIZE. */
  pivot: THREE.Group;
  meshes: THREE.Mesh[];
  mixer: THREE.AnimationMixer | null;
};

export class AnatomyAssetManager {
  private loader: GLTFLoader;
  private cache = new Map<string, LoadedOrgan>();
  private inflight = new Map<string, Promise<LoadedOrgan>>();
  private current: LoadedOrgan | null = null;
  private maxAnisotropy: number;

  constructor(renderer: THREE.WebGLRenderer) {
    // Anisotropy is what stops the texture detail from crawling at grazing
    // angles, which is most of the shimmer on a rotating organ.
    this.maxAnisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
    this.loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
  }

  get hasAnimation() {
    return Boolean(this.current?.mixer);
  }

  /** Warms the HTTP cache so switching organs feels instant. */
  prefetch(url: string) {
    if (this.cache.has(url) || this.inflight.has(url)) return;
    void fetch(url, { priority: "low" } as RequestInit).catch(() => {});
  }

  async load(url: string, onProgress?: (progress: number) => void): Promise<LoadedOrgan> {
    const cached = this.cache.get(url);
    if (cached) {
      this.cache.delete(url);
      this.cache.set(url, cached);
      this.resetMaterials(cached);
      onProgress?.(1);
      this.current = cached;
      return cached;
    }

    const pending = this.inflight.get(url) ?? this.parse(url, onProgress);
    this.inflight.set(url, pending);
    try {
      const organ = await pending;
      this.cache.set(url, organ);
      this.evict();
      this.current = organ;
      return organ;
    } finally {
      this.inflight.delete(url);
    }
  }

  private async parse(url: string, onProgress?: (progress: number) => void): Promise<LoadedOrgan> {
    const gltf = await this.loader.loadAsync(url, (event) => {
      if (event.total > 0) onProgress?.(event.loaded / event.total);
    });

    const model = gltf.scene;
    const box = new THREE.Box3().setFromObject(model);
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());
    const scale = FIT_SIZE / Math.max(size.x, size.y, size.z, 0.001);
    model.scale.setScalar(scale);
    model.position.copy(center.multiplyScalar(-scale));

    // The pivot is what the viewer animates and what hotspots are parented to,
    // so hotspot coordinates stay in the normalised FIT_SIZE space.
    const pivot = new THREE.Group();
    pivot.name = "organ-pivot";
    pivot.add(model);
    pivot.rotation.set(0.05, -0.28, 0);

    const meshes: THREE.Mesh[] = [];
    model.traverse((child) => {
      if (!(child instanceof THREE.Mesh)) return;
      meshes.push(child);
      // One mesh per organ, always centred in frame — culling can only ever
      // cost a wrong answer here, never save work.
      child.frustumCulled = false;
      // Soft contact shadows ground each part against its neighbours — the
      // single biggest realism cue for assembled hardware. Transparent parts
      // (e.g. the tempered-glass panel) stay shadow-cast-free so they don't
      // throw a solid shadow.
      child.receiveShadow = true;
      let castsShadow = true;
      this.forEachMaterial(child, (material) => {
        // Preserve GLB-declared transparency (e.g. the tempered-glass panel);
        // everything else stays opaque. Captured here so resetMaterials can
        // restore it after the wireframe / fade tools run.
        const isTransparent = material.transparent;
        if (isTransparent) castsShadow = false;
        const baseOpacity = material.opacity;
        material.userData.organTransparent = isTransparent;
        material.userData.organOpacity = isTransparent ? Math.min(baseOpacity, 1) : 1;
        material.transparent = isTransparent;
        material.opacity = isTransparent ? Math.min(baseOpacity, 1) : 1;
        material.depthWrite = !isTransparent;
        material.depthTest = true;
        material.side = isTransparent ? THREE.DoubleSide : THREE.FrontSide;
        if (material instanceof THREE.MeshStandardMaterial) {
          // A tighter specular lobe sparkles on any surface with normal detail;
          // holding roughness a little higher keeps highlights stable while the
          // model turns.
          material.roughness = THREE.MathUtils.clamp(material.roughness ?? 0.45, 0.18, 0.72);
          material.metalness = THREE.MathUtils.clamp(material.metalness ?? 0.15, 0, 0.9);
          material.envMapIntensity = 1.0;
          const imported = material.emissive;
          const importedGlow = imported.r + imported.g + imported.b > 0.02;
          if (/accent/i.test(material.name)) {
            material.emissive.setHex(ACCENT_EMISSIVE[material.name.toLowerCase()] ?? 0x55d8e8);
            material.emissiveIntensity = 1.0;
          } else if (importedGlow) {
            material.emissiveIntensity = 1.0;
          } else {
            material.emissive.set(0x000000);
            material.emissiveIntensity = 0;
          }
          if ("clearcoat" in material) {
            const physical = material as THREE.MeshPhysicalMaterial;
            // A second, sharper specular lobe is the main source of crawling
            // highlights, so keep it faint and broad.
            physical.clearcoat = Math.min(Math.max(physical.clearcoat, 0.08), 0.12);
            physical.clearcoatRoughness = 0.62;
            // Volume/transmission are per-pixel expensive and invisible here.
            physical.transmission = 0;
            physical.thickness = 0;
          }
          if (material.map) material.map.colorSpace = THREE.SRGBColorSpace;
          if (material.normalMap) material.normalScale.set(0.9, 0.9);
          enableFresnelRim(material);
          // Every sampled map needs anisotropy, not just the base colour —
          // an aliasing normal or roughness map shimmers just as badly.
          for (const map of [
            material.map,
            material.normalMap,
            material.roughnessMap,
            material.metalnessMap,
            material.aoMap,
            material.emissiveMap,
          ]) {
            if (!map) continue;
            map.anisotropy = this.maxAnisotropy;
            map.generateMipmaps = true;
            map.minFilter = THREE.LinearMipmapLinearFilter;
            map.magFilter = THREE.LinearFilter;
            map.needsUpdate = true;
          }
        }
        material.needsUpdate = true;
      });
      child.castShadow = castsShadow;
    });

    let mixer: THREE.AnimationMixer | null = null;
    if (gltf.animations.length) {
      mixer = new THREE.AnimationMixer(model);
      gltf.animations.forEach((clip) => mixer?.clipAction(clip).play());
    }

    return { url, pivot, meshes, mixer };
  }

  /** Undoes viewer tools (wireframe, clipping, fade) before a cached organ returns. */
  private resetMaterials(organ: LoadedOrgan) {
    organ.pivot.rotation.set(0.05, -0.28, 0);
    organ.pivot.position.set(0, 0, 0);
    organ.meshes.forEach((mesh) => {
      this.forEachMaterial(mesh, (material) => {
        const wasTransparent = material.userData.organTransparent ?? false;
        const wasOpacity = material.userData.organOpacity ?? 1;
        material.transparent = wasTransparent;
        material.opacity = wasOpacity;
        material.depthWrite = !wasTransparent;
        material.clippingPlanes = null;
        material.clipShadows = false;
        material.side = wasTransparent ? THREE.DoubleSide : THREE.FrontSide;
        if (material instanceof THREE.MeshStandardMaterial) material.wireframe = false;
        material.needsUpdate = true;
      });
    });
  }

  private forEachMaterial(mesh: THREE.Mesh, fn: (material: THREE.Material) => void) {
    const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
    materials.forEach(fn);
  }

  private evict() {
    while (this.cache.size > CACHE_LIMIT) {
      const oldest = this.cache.keys().next().value as string | undefined;
      if (!oldest) return;
      const organ = this.cache.get(oldest);
      this.cache.delete(oldest);
      if (organ && organ !== this.current) this.destroy(organ);
    }
  }

  private destroy(organ: LoadedOrgan) {
    organ.mixer?.stopAllAction();
    organ.mixer?.uncacheRoot(organ.pivot);
    organ.pivot.removeFromParent();
    disposeObject(organ.pivot);
  }

  update(delta: number) {
    this.current?.mixer?.update(delta);
  }

  /** Detaches from the scene but keeps the organ warm for the next visit. */
  release(organ: LoadedOrgan | null = this.current) {
    if (!organ) return;
    organ.mixer?.stopAllAction();
    organ.pivot.removeFromParent();
    if (organ === this.current) this.current = null;
  }

  dispose() {
    this.release();
    this.cache.forEach((organ) => this.destroy(organ));
    this.cache.clear();
  }
}
