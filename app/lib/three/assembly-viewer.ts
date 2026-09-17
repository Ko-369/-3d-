import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { MeshoptDecoder } from "three/examples/jsm/libs/meshopt_decoder.module.js";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";
import gsap from "gsap";
import {
  ASSEMBLY_SLOTS,
  CASE_OPEN_Z,
  type AssemblyPartId,
  type AssemblySlot,
} from "../assembly-data";
import { disposeObject } from "./dispose";

/** A calibrated slot pose, in the same case-unit / radian space as assembly-data. */
export type CalibrationPose = {
  id: AssemblyPartId;
  position: [number, number, number];
  rotation: [number, number, number]; // radians
  size: [number, number, number];
};

type AssemblyCallbacks = {
  onLoading: (loading: boolean, progress: number) => void;
  onPlace: (id: AssemblyPartId) => void;
  onComplete: () => void;
  onDragState: (id: AssemblyPartId | null) => void;
  onPoseChange?: (pose: CalibrationPose) => void;
};

/** A loaded, placeable hardware part. */
type PartHandle = {
  slot: AssemblySlot;
  /** Model scaled so its baked bbox == slot.size and centred at the pivot origin. */
  pivot: THREE.Group;
  meshes: THREE.Mesh[];
  /** Slot mount pose in case-local (baked) units. */
  slotPos: THREE.Vector3;
  slotQuat: THREE.Quaternion;
  /** Staging pose in case units (child of the staging group). */
  homePos: THREE.Vector3;
  homeScale: number;
  /** Ghost box shown at the slot while the part is being dragged. */
  ghost: THREE.Mesh;
  placed: boolean;
};

const CAMERA_FOV = 34;
const TARGET_CASE_SIZE = 3.0; // world units of the case's longest edge
const STAGE_SCALE = 0.68; // uniform shrink of parts while resting on the bench
const STAGE_COLS = 3;
const GAP_X = 0.1;
const GAP_Y = 0.12;
const SNAP_PIXELS = 70; // screen-space snap threshold
/** World-centre x for the case (left) and the parts bench (right). */
const CASE_WORLD_X = -2.3;
const STAGE_WORLD_X = 2.3;

export class AssemblyViewer {
  private renderer: THREE.WebGLRenderer;
  private scene = new THREE.Scene();
  private camera = new THREE.PerspectiveCamera(CAMERA_FOV, 1, 0.1, 200);
  private controls: OrbitControls;
  private loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
  private callbacks: AssemblyCallbacks;
  private container: HTMLElement;

  private world = new THREE.Group();
  private caseGroup = new THREE.Group();
  private stageGroup = new THREE.Group();
  private caseScale = 1;

  private parts = new Map<AssemblyPartId, PartHandle>();
  private raycaster = new THREE.Raycaster();
  private clipPlane = new THREE.Plane(new THREE.Vector3(0, 0, -1), 0);

  private guidedNext: AssemblyPartId | null = null;
  private calibration = false;
  private activeId: AssemblyPartId | null = null;
  private dragging: PartHandle | null = null;
  private dragPlane = new THREE.Plane();
  private dragOffset = new THREE.Vector3();
  private pointerId: number | null = null;
  private pointerStart = { x: 0, y: 0 };
  private dragged = false;

  private width = 1;
  private height = 1;
  private clock = new THREE.Clock();
  private resizeObserver: ResizeObserver;
  private intersectionObserver: IntersectionObserver;
  private isVisible = true;
  private isPageVisible = true;
  private dirty = true;
  private disposed = false;

  constructor(container: HTMLElement, callbacks: AssemblyCallbacks) {
    this.container = container;
    this.callbacks = callbacks;

    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 0.55;
    this.renderer.localClippingEnabled = true;
    this.renderer.domElement.tabIndex = 0;
    container.appendChild(this.renderer.domElement);

    this.camera.position.set(0, 0.4, 12);
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.06;
    this.controls.enablePan = false;
    this.controls.minDistance = 4;
    this.controls.maxDistance = 30;
    this.controls.target.set(0, 0, 0);

    this.scene.add(this.world);
    this.world.add(this.caseGroup);
    this.world.add(this.stageGroup);
    this.buildLights();

    this.resizeObserver = new ResizeObserver(() => this.resize());
    this.resizeObserver.observe(container);
    this.intersectionObserver = new IntersectionObserver(
      ([entry]) => {
        this.isVisible = entry.isIntersecting;
        if (this.isVisible) this.dirty = true;
      },
      { rootMargin: "120px" },
    );
    this.intersectionObserver.observe(container);
    document.addEventListener("visibilitychange", this.onVisibilityChange);

    const canvas = this.renderer.domElement;
    canvas.addEventListener("pointerdown", this.onPointerDown);
    canvas.addEventListener("pointermove", this.onPointerMove);
    canvas.addEventListener("pointerup", this.onPointerUp);
    canvas.addEventListener("pointercancel", this.onPointerCancel);
    canvas.addEventListener("pointerleave", this.onPointerLeave);

    this.resize();
    this.animate();
  }

  // ------------------------------------------------------------- environment

  private buildLights() {
    const pmrem = new THREE.PMREMGenerator(this.renderer);
    this.scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    pmrem.dispose();

    this.scene.add(new THREE.HemisphereLight(0xffffff, 0x14181c, 0.75));
    const key = new THREE.DirectionalLight(0xfff3e6, 2.4);
    key.position.set(5, 6, 7);
    this.scene.add(key);
    const fill = new THREE.DirectionalLight(0xeef1f3, 1.0);
    fill.position.set(-5, 1, 5);
    this.scene.add(fill);
    const rim = new THREE.DirectionalLight(0xf2f5f7, 1.4);
    rim.position.set(-4, 3, -6);
    this.scene.add(rim);
  }

  // ----------------------------------------------------------------- loading

  async loadAll() {
    this.callbacks.onLoading(true, 0);
    let caseLoaded = false;
    const total = ASSEMBLY_SLOTS.length;
    let done = 0;

    try {
      await this.loadCase();
      caseLoaded = true;
      this.callbacks.onLoading(true, 0.08);

      await Promise.all(
        ASSEMBLY_SLOTS.map(async (slot) => {
          const handle = await this.loadPart(slot);
          this.parts.set(slot.id, handle);
          done += 1;
          this.callbacks.onLoading(true, 0.08 + (done / total) * 0.92);
        }),
      );
    } finally {
      this.callbacks.onLoading(false, 1);
    }

    if (!caseLoaded) return;
    if (this.calibration) this.placeAllForCalibration();
    else this.layoutStaging();
    this.frameCamera();
    this.dirty = true;
  }

  private async loadCase() {
    const scene = await this.loadScene("/models/case.glb");
    const box = new THREE.Box3().setFromObject(scene);
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());
    this.caseScale = TARGET_CASE_SIZE / Math.max(size.x, size.y, size.z, 0.001);

    // Case (open side +z) sits on the left; the bench shares the case's scale.
    this.caseGroup.scale.setScalar(this.caseScale);
    this.caseGroup.position.set(
      CASE_WORLD_X - center.x * this.caseScale,
      -center.y * this.caseScale,
      -center.z * this.caseScale,
    );
    this.stageGroup.scale.setScalar(this.caseScale);
    this.stageGroup.position.set(STAGE_WORLD_X, 0, 0);

    // Clip away the front mesh/grill so the interior is open for assembly while
    // the solid back stays opaque. The plane lives in world space.
    this.clipPlane.constant = CASE_OPEN_Z * this.caseScale + this.caseGroup.position.z;
    scene.traverse((child) => {
      if (!(child instanceof THREE.Mesh)) return;
      child.frustumCulled = false;
      this.configureMaterial(child, { clip: true });
    });
    this.caseGroup.add(scene);

    // The scan's -y bottom is an open gap; close it so the only open face is
    // the clipped front. A thin slab at the floor seals the underside.
    const floorMaterial = new THREE.MeshStandardMaterial({ color: 0x14171a, roughness: 0.85, metalness: 0.25 });
    floorMaterial.clippingPlanes = [this.clipPlane];
    const floor = new THREE.Mesh(
      new THREE.BoxGeometry(size.x + 0.02, 0.03, size.z + 0.02),
      floorMaterial,
    );
    floor.position.set(center.x, -0.015, center.z);
    this.caseGroup.add(floor);
  }

  private async loadPart(slot: AssemblySlot): Promise<PartHandle> {
    const scene = await this.loadScene(slot.model);
    const box = new THREE.Box3().setFromObject(scene);
    const bakedSize = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());

    // Non-uniform scale so the baked bbox matches slot.size, centred at origin.
    const scale = new THREE.Vector3(
      slot.size[0] / Math.max(bakedSize.x, 0.001),
      slot.size[1] / Math.max(bakedSize.y, 0.001),
      slot.size[2] / Math.max(bakedSize.z, 0.001),
    );
    scene.scale.copy(scale);
    scene.position.set(-center.x * scale.x, -center.y * scale.y, -center.z * scale.z);

    const meshes: THREE.Mesh[] = [];
    scene.traverse((child) => {
      if (!(child instanceof THREE.Mesh)) return;
      child.frustumCulled = false;
      meshes.push(child);
      this.configureMaterial(child);
    });

    const pivot = new THREE.Group();
    pivot.name = `part-${slot.id}`;
    pivot.add(scene);

    const ghost = new THREE.Mesh(
      new THREE.BoxGeometry(slot.size[0], slot.size[1], slot.size[2]),
      new THREE.MeshBasicMaterial({ color: new THREE.Color(slot.accent), wireframe: true, transparent: true, opacity: 0.5 }),
    );
    ghost.visible = false;
    ghost.rotation.set(...slot.rotation);
    ghost.position.set(...slot.position);
    this.caseGroup.add(ghost);

    return {
      slot,
      pivot,
      meshes,
      slotPos: new THREE.Vector3(...slot.position),
      slotQuat: new THREE.Quaternion().setFromEuler(new THREE.Euler(...slot.rotation)),
      homePos: new THREE.Vector3(),
      homeScale: STAGE_SCALE,
      ghost,
      placed: false,
    };
  }

  private async loadScene(url: string) {
    const gltf = await this.loader.loadAsync(url);
    return gltf.scene;
  }

  private configureMaterial(mesh: THREE.Mesh, opts?: { clip?: boolean }) {
    const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
    materials.forEach((material) => {
      if (material instanceof THREE.MeshStandardMaterial) {
        material.envMapIntensity = 1.0;
        if (material.map) material.map.colorSpace = THREE.SRGBColorSpace;
      }
      material.clippingPlanes = opts?.clip ? [this.clipPlane] : null;
      material.needsUpdate = true;
    });
  }

  // ------------------------------------------------------------------ layout

  /** Lay the parts out on a bench to the right of the case, in a grid. */
  private layoutStaging() {
    const handles = [...this.parts.values()];
    let maxW = 0;
    let maxH = 0;
    handles.forEach((p) => {
      maxW = Math.max(maxW, p.slot.size[0] * STAGE_SCALE);
      maxH = Math.max(maxH, p.slot.size[1] * STAGE_SCALE);
    });

    const cellW = maxW + GAP_X;
    const cellH = maxH + GAP_Y;
    const rows = Math.ceil(handles.length / STAGE_COLS);
    const gridW = STAGE_COLS * cellW;
    const gridH = rows * cellH;

    handles.forEach((p, i) => {
      const col = i % STAGE_COLS;
      const row = Math.floor(i / STAGE_COLS);
      p.homePos.set(
        -gridW / 2 + col * cellW + cellW / 2,
        gridH / 2 - row * cellH - cellH / 2,
        0,
      );
      this.stageGroup.add(p.pivot);
      p.pivot.scale.setScalar(p.homeScale);
      p.pivot.position.copy(p.homePos);
      p.pivot.quaternion.identity();
    });
    this.dirty = true;
  }

  private frameCamera() {
    this.caseGroup.updateWorldMatrix(true, true);
    this.stageGroup.updateWorldMatrix(true, true);
    const box = new THREE.Box3().setFromObject(this.caseGroup);
    box.expandByObject(this.stageGroup);
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());

    // Frame by the horizontal + vertical extents (with a little margin) so the
    // whole bench + case fills the view, rather than the over-wide sphere fit.
    const aspect = Math.max(this.camera.aspect, 1);
    const fit = Math.max(size.y, size.x / aspect) * 1.12;
    const dist = fit / 2 / Math.tan((CAMERA_FOV / 2) * (Math.PI / 180)) + 0.5;

    this.camera.position.set(center.x, center.y, center.z + dist);
    this.camera.near = Math.max(0.05, dist / 200);
    this.camera.far = dist * 6;
    this.camera.updateProjectionMatrix();
    this.controls.target.copy(center);
    this.controls.update();
    this.dirty = true;
  }

  // ------------------------------------------------------------------- loop

  private animate = () => {
    requestAnimationFrame(this.animate);
    if (!this.isVisible || !this.isPageVisible || this.disposed) return;
    const delta = Math.min(this.clock.getDelta(), 0.05);
    if (this.controls.update(delta)) this.dirty = true;
    if (!this.dirty && !this.dragging) return;
    this.dirty = false;
    this.renderer.render(this.scene, this.camera);
  };

  private onVisibilityChange = () => {
    this.isPageVisible = !document.hidden;
    if (this.isPageVisible) this.dirty = true;
  };

  private resize() {
    this.width = Math.max(this.container.clientWidth, 1);
    this.height = Math.max(this.container.clientHeight, 1);
    this.camera.aspect = this.width / this.height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(this.width, this.height, false);
    this.dirty = true;
  }

  // ------------------------------------------------------------------ input

  private pickPart(x: number, y: number): PartHandle | null {
    const rect = this.renderer.domElement.getBoundingClientRect();
    const ndc = new THREE.Vector2(
      ((x - rect.left) / rect.width) * 2 - 1,
      -((y - rect.top) / rect.height) * 2 + 1,
    );
    this.raycaster.setFromCamera(ndc, this.camera);
    const targets = [...this.parts.values()].flatMap((p) => p.meshes);
    const hit = this.raycaster.intersectObjects(targets, false)[0];
    if (!hit) return null;
    return [...this.parts.values()].find((p) => p.meshes.includes(hit.object as THREE.Mesh)) ?? null;
  }

  private isDraggable(part: PartHandle) {
    if (this.calibration) return true;
    return this.guidedNext === null || part.slot.id === this.guidedNext;
  }

  private onPointerDown = (event: PointerEvent) => {
    this.pointerId = event.pointerId;
    this.pointerStart = { x: event.clientX, y: event.clientY };
    this.dragged = false;
    const part = this.pickPart(event.clientX, event.clientY);
    if (part && this.isDraggable(part)) this.startDrag(part, event);
  };

  private onPointerMove = (event: PointerEvent) => {
    if (this.dragging) {
      this.moveDrag(event);
      return;
    }
    if (this.pointerId !== null) {
      if (!this.dragged && Math.hypot(event.clientX - this.pointerStart.x, event.clientY - this.pointerStart.y) > 5) {
        this.dragged = true;
      }
      return; // orbiting on empty space (OrbitControls handles it)
    }
    this.updateHover(event.clientX, event.clientY);
  };

  private onPointerUp = () => {
    this.pointerId = null;
    const wasDragging = this.dragging;
    this.dragged = false;
    if (wasDragging) this.endDrag();
  };

  private onPointerCancel = () => {
    this.pointerId = null;
    this.dragged = false;
    if (this.dragging) this.cancelDrag();
  };

  private onPointerLeave = () => {
    this.pointerId = null;
    this.dragged = false;
    if (this.dragging) this.cancelDrag();
    else this.updateHover(-1, -1);
  };

  private updateHover(x: number, y: number) {
    if (this.dragging) return;
    const part = this.pickPart(x, y);
    const over = part && this.isDraggable(part) ? part : null;
    if (over) {
      this.controls.enabled = false;
      this.renderer.domElement.style.cursor = "grab";
    } else {
      this.controls.enabled = true;
      this.renderer.domElement.style.cursor = "";
    }
    this.dirty = true;
  }

  // -------------------------------------------------------------------- drag

  private startDrag(part: PartHandle, event: PointerEvent) {
    this.dragging = part;
    this.controls.enabled = false;
    this.renderer.domElement.style.cursor = "grabbing";
    try {
      this.renderer.domElement.setPointerCapture(event.pointerId);
    } catch {
      /* ignore — capture is a best-effort */
    }
    part.ghost.visible = !this.calibration;
    this.setPartDragOpacity(part, true);

    // A plane facing the camera through the part, so it follows the pointer.
    const worldPos = part.pivot.getWorldPosition(new THREE.Vector3());
    const normal = this.camera.getWorldDirection(new THREE.Vector3());
    this.dragPlane.setFromNormalAndCoplanarPoint(normal, worldPos);
    const hit = this.raycastPlane(event.clientX, event.clientY);
    if (hit) this.dragOffset.copy(worldPos).sub(hit);

    this.callbacks.onDragState(part.slot.id);
    this.dirty = true;
  }

  private moveDrag(event: PointerEvent) {
    if (!this.dragging) return;
    const hit = this.raycastPlane(event.clientX, event.clientY);
    if (!hit) return;
    const target = hit.add(this.dragOffset);
    const parent = this.dragging.pivot.parent!;
    this.dragging.pivot.position.copy(parent.worldToLocal(target.clone()));
    this.dirty = true;
  }

  private endDrag() {
    if (!this.dragging) return;
    const part = this.dragging;
    const slotWorld = this.caseGroup.localToWorld(part.slotPos.clone());
    const posWorld = part.pivot.getWorldPosition(new THREE.Vector3());
    const near = this.screenDistance(posWorld, slotWorld) < SNAP_PIXELS;

    part.ghost.visible = false;
    this.setPartDragOpacity(part, false);
    this.dragging = null;
    this.renderer.domElement.style.cursor = "";
    this.controls.enabled = true;

    if (this.calibration) {
      this.activeId = part.slot.id;
      this.reportPose(part);
    } else if (near || part.placed) {
      this.snapToSlot(part);
    } else {
      this.returnHome(part);
    }
    this.callbacks.onDragState(null);
  }

  private cancelDrag() {
    if (!this.dragging) return;
    const part = this.dragging;
    part.ghost.visible = false;
    this.setPartDragOpacity(part, false);
    this.dragging = null;
    this.renderer.domElement.style.cursor = "";
    this.controls.enabled = true;
    if (this.calibration) {
      this.activeId = part.slot.id;
      this.reportPose(part);
    } else if (part.placed) {
      this.snapToSlot(part);
    } else {
      this.returnHome(part);
    }
    this.callbacks.onDragState(null);
  }

  private raycastPlane(x: number, y: number): THREE.Vector3 | null {
    const rect = this.renderer.domElement.getBoundingClientRect();
    const ndc = new THREE.Vector2(
      ((x - rect.left) / rect.width) * 2 - 1,
      -((y - rect.top) / rect.height) * 2 + 1,
    );
    this.raycaster.setFromCamera(ndc, this.camera);
    const out = new THREE.Vector3();
    if (!this.raycaster.ray.intersectPlane(this.dragPlane, out)) return null;
    return out;
  }

  /** Pixel distance between two world points projected onto the screen. */
  private screenDistance(a: THREE.Vector3, b: THREE.Vector3): number {
    const pa = a.clone().project(this.camera);
    const pb = b.clone().project(this.camera);
    const dx = (pa.x - pb.x) * this.width * 0.5;
    const dy = (pa.y - pb.y) * this.height * 0.5;
    return Math.hypot(dx, dy);
  }

  /** Fades the carried part so it reads as "in hand", not "already mounted". */
  private setPartDragOpacity(part: PartHandle, dragging: boolean) {
    part.meshes.forEach((mesh) => {
      const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
      materials.forEach((material) => {
        material.transparent = dragging;
        material.opacity = dragging ? 0.6 : 1;
        material.depthWrite = !dragging;
        material.needsUpdate = true;
      });
    });
  }

  // -------------------------------------------------------------------- snap

  private snapToSlot(part: PartHandle) {
    this.caseGroup.attach(part.pivot);
    const wasPlaced = part.placed;
    part.placed = true;
    gsap.to(part.pivot.position, {
      x: part.slotPos.x, y: part.slotPos.y, z: part.slotPos.z,
      duration: 0.28, ease: "back.out(1.6)", onUpdate: () => (this.dirty = true),
    });
    gsap.to(part.pivot.scale, { x: 1, y: 1, z: 1, duration: 0.28, ease: "back.out(1.6)", onUpdate: () => (this.dirty = true) });
    gsap.to(part.pivot.quaternion, {
      x: part.slotQuat.x, y: part.slotQuat.y, z: part.slotQuat.z, w: part.slotQuat.w,
      duration: 0.28, onUpdate: () => (this.dirty = true),
    });
    if (!wasPlaced) {
      this.callbacks.onPlace(part.slot.id);
      if ([...this.parts.values()].every((p) => p.placed)) this.callbacks.onComplete();
    }
  }

  private returnHome(part: PartHandle) {
    this.stageGroup.attach(part.pivot);
    gsap.to(part.pivot.position, {
      x: part.homePos.x, y: part.homePos.y, z: part.homePos.z,
      duration: 0.3, ease: "power3.out", onUpdate: () => (this.dirty = true),
    });
    gsap.to(part.pivot.scale, { x: part.homeScale, y: part.homeScale, z: part.homeScale, duration: 0.3, ease: "power3.out", onUpdate: () => (this.dirty = true) });
    gsap.to(part.pivot.quaternion, { x: 0, y: 0, z: 0, w: 1, duration: 0.3, onUpdate: () => (this.dirty = true) });
  }

  // -------------------------------------------------------------------- API

  /** Guided mode: pass the next part id, or null for freeform. */
  setGuided(next: AssemblyPartId | null) {
    this.guidedNext = next;
    this.dirty = true;
  }

  reset() {
    this.dragging = null;
    this.parts.forEach((part) => {
      part.placed = false;
      part.ghost.visible = false;
      this.setPartDragOpacity(part, false);
      this.stageGroup.attach(part.pivot);
      part.pivot.position.copy(part.homePos);
      part.pivot.scale.setScalar(part.homeScale);
      part.pivot.quaternion.identity();
    });
    this.dirty = true;
  }

  /** Calibration mode: free placement with no snapping; prints poses to the UI. */
  setCalibration(enabled: boolean) {
    this.calibration = enabled;
    if (enabled) document.addEventListener("keydown", this.onKeyDown);
    else document.removeEventListener("keydown", this.onKeyDown);
    this.dirty = true;
  }

  private placeAllForCalibration() {
    this.parts.forEach((part) => {
      this.caseGroup.attach(part.pivot);
      part.pivot.position.copy(part.slotPos);
      part.pivot.quaternion.copy(part.slotQuat);
      part.pivot.scale.setScalar(1);
    });
  }

  private reportPose(part: PartHandle) {
    const r = (n: number) => Math.round(n * 100) / 100;
    this.callbacks.onPoseChange?.({
      id: part.slot.id,
      position: [r(part.pivot.position.x), r(part.pivot.position.y), r(part.pivot.position.z)],
      rotation: [r(part.pivot.rotation.x), r(part.pivot.rotation.y), r(part.pivot.rotation.z)],
      size: [
        r(part.slot.size[0] * part.pivot.scale.x),
        r(part.slot.size[1] * part.pivot.scale.y),
        r(part.slot.size[2] * part.pivot.scale.z),
      ],
    });
  }

  private onKeyDown = (event: KeyboardEvent) => {
    if (!this.calibration || !this.activeId) return;
    const part = this.parts.get(this.activeId);
    if (!part) return;
    const step = THREE.MathUtils.degToRad(5);
    let changed = false;
    switch (event.key) {
      case "ArrowLeft": part.pivot.rotation.y += step; changed = true; break;
      case "ArrowRight": part.pivot.rotation.y -= step; changed = true; break;
      case "ArrowUp": part.pivot.rotation.x -= step; changed = true; break;
      case "ArrowDown": part.pivot.rotation.x += step; changed = true; break;
      case ",": part.pivot.rotation.z += step; changed = true; break;
      case ".": part.pivot.rotation.z -= step; changed = true; break;
      case "[": part.pivot.scale.setScalar(part.pivot.scale.x * 0.95); changed = true; break;
      case "]": part.pivot.scale.setScalar(part.pivot.scale.x / 0.95); changed = true; break;
      default: return;
    }
    if (changed) {
      event.preventDefault();
      this.dirty = true;
      this.reportPose(part);
    }
  };

  dispose() {
    this.disposed = true;
    this.resizeObserver.disconnect();
    this.intersectionObserver.disconnect();
    document.removeEventListener("visibilitychange", this.onVisibilityChange);
    document.removeEventListener("keydown", this.onKeyDown);
    const canvas = this.renderer.domElement;
    canvas.removeEventListener("pointerdown", this.onPointerDown);
    canvas.removeEventListener("pointermove", this.onPointerMove);
    canvas.removeEventListener("pointerup", this.onPointerUp);
    canvas.removeEventListener("pointercancel", this.onPointerCancel);
    canvas.removeEventListener("pointerleave", this.onPointerLeave);
    this.controls.dispose();
    this.scene.environment?.dispose();
    disposeObject(this.world);
    this.renderer.dispose();
    canvas.remove();
  }
}
