// Decimate the Hi3D CPU scan to ~400k triangles (matching the motherboard's
// weight class) while preserving UVs, then repack as a clean glb.
import fs from 'node:fs';
import { MeshoptSimplifier } from 'meshoptimizer';

const SRC = 'D:/陈铭志/新建文件夹/v3/模型图片/Hi3D_Untitled_allparts_20260916_142208.glb';
const OUT = 'D:/陈铭志/新建文件夹/v3/public/models/cpu.glb';

const TARGET_INDEX_COUNT = 1_200_000; // 400k triangles
const TARGET_ERROR = 0.05;

await MeshoptSimplifier.ready;

const data = fs.readFileSync(SRC);
const jsonLen = data.readUInt32LE(12);
const json = JSON.parse(data.toString('utf8', 20, 20 + jsonLen));
const binStart = 20 + jsonLen + 8; // BIN chunk data begins here

// --- read a bufferView as a fresh little-endian typed array (no alignment risk)
function readTyped(bvIndex, Ctor, bytesPerElem) {
  const bv = json.bufferViews[bvIndex];
  const count = bv.byteLength / bytesPerElem;
  const src = data.subarray(binStart + bv.byteOffset, binStart + bv.byteOffset + bv.byteLength);
  const dst = new Ctor(count);
  new Uint8Array(dst.buffer).set(src);
  return dst;
}

const prim = json.meshes[0].primitives[0];
const accPos = json.accessors[prim.attributes.POSITION];
const accUv = json.accessors[prim.attributes.TEXCOORD_0];
const accIdx = json.accessors[prim.indices];

const positions = readTyped(accPos.bufferView, Float32Array, 4); // interleaved xyz
const uvs = readTyped(accUv.bufferView, Float32Array, 4);        // interleaved uv
const indices = readTyped(accIdx.bufferView, Uint32Array, 4);    // triangle list
const image0 = data.subarray(binStart + json.bufferViews[4].byteOffset, binStart + json.bufferViews[4].byteOffset + json.bufferViews[4].byteLength);
const image1 = data.subarray(binStart + json.bufferViews[5].byteOffset, binStart + json.bufferViews[5].byteOffset + json.bufferViews[5].byteLength);

const vertexCount = positions.length / 3;
console.log('input: vertices', vertexCount, 'triangles', indices.length / 3, 'uv floats', uvs.length);

// --- simplify (preserve UV seams via attribute weights)
const [simplifiedIndices, error] = MeshoptSimplifier.simplifyWithAttributes(
  indices, positions, 3, uvs, 2, [0.5, 0.5], null, TARGET_INDEX_COUNT, TARGET_ERROR
);
console.log('simplified: indices', simplifiedIndices.length, 'triangles', simplifiedIndices.length / 3, 'error', error);

// --- compact the vertex buffer (meshopt leaves indices referencing original vertices)
const remap = new Map();
const newPos = [];
const newUv = [];
let vertexIndex = 0;
for (const oldIdx of simplifiedIndices) {
  if (!remap.has(oldIdx)) {
    remap.set(oldIdx, vertexIndex++);
    newPos.push(positions[oldIdx * 3], positions[oldIdx * 3 + 1], positions[oldIdx * 3 + 2]);
    newUv.push(uvs[oldIdx * 2], uvs[oldIdx * 2 + 1]);
  }
}
const newIndexCount = simplifiedIndices.length;
const newVertexCount = newPos.length / 3;
const compactIndices = new Uint32Array(newIndexCount);
for (let i = 0; i < newIndexCount; i++) compactIndices[i] = remap.get(simplifiedIndices[i]);

// --- recompute smooth normals
const normals = new Float32Array(newVertexCount * 3);
for (let i = 0; i < newIndexCount; i += 3) {
  const a = compactIndices[i], b = compactIndices[i + 1], c = compactIndices[i + 2];
  const ax = newPos[a * 3], ay = newPos[a * 3 + 1], az = newPos[a * 3 + 2];
  const bx = newPos[b * 3], by = newPos[b * 3 + 1], bz = newPos[b * 3 + 2];
  const cx = newPos[c * 3], cy = newPos[c * 3 + 1], cz = newPos[c * 3 + 2];
  const ux = bx - ax, uy = by - ay, uz = bz - az;
  const vx = cx - ax, vy = cy - ay, vz = cz - az;
  const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
  for (const v of [a, b, c]) {
    normals[v * 3] += nx; normals[v * 3 + 1] += ny; normals[v * 3 + 2] += nz;
  }
}
for (let i = 0; i < newVertexCount; i++) {
  const x = normals[i * 3], y = normals[i * 3 + 1], z = normals[i * 3 + 2];
  const len = Math.hypot(x, y, z) || 1;
  normals[i * 3] = x / len; normals[i * 3 + 1] = y / len; normals[i * 3 + 2] = z / len;
}

// --- lay out the new BIN buffer
const align4 = (n) => (n + 3) & ~3;
const posBuf = Buffer.from(new Float32Array(newPos).buffer);
const uvBuf = Buffer.from(new Float32Array(newUv).buffer);
const nrmBuf = Buffer.from(normals.buffer, normals.byteOffset, normals.byteLength);
const idxBuf = Buffer.from(compactIndices.buffer, compactIndices.byteOffset, compactIndices.byteLength);
const img0Buf = Buffer.from(image0);
const img1Buf = Buffer.from(image1);

const offPos = 0;
const offUv = offPos + posBuf.length;
const offNrm = offUv + uvBuf.length;
const offIdx = offNrm + nrmBuf.length;
const offImg0 = offIdx + idxBuf.length;
const offImg1 = align4(offImg0 + img0Buf.length);
const binLength = offImg1 + img1Buf.length;

const bin = Buffer.alloc(binLength);
posBuf.copy(bin, offPos);
uvBuf.copy(bin, offUv);
nrmBuf.copy(bin, offNrm);
idxBuf.copy(bin, offIdx);
img0Buf.copy(bin, offImg0);
img1Buf.copy(bin, offImg1);

// --- rebuild JSON
const bufferViews = [
  { buffer: 0, byteOffset: offPos, byteLength: posBuf.length, target: 34962, byteStride: 12 },
  { buffer: 0, byteOffset: offUv, byteLength: uvBuf.length, target: 34962, byteStride: 8 },
  { buffer: 0, byteOffset: offNrm, byteLength: nrmBuf.length, target: 34962, byteStride: 12 },
  { buffer: 0, byteOffset: offIdx, byteLength: idxBuf.length, target: 34963 },
  { buffer: 0, byteOffset: offImg0, byteLength: img0Buf.length },
  { buffer: 0, byteOffset: offImg1, byteLength: img1Buf.length },
];
const accessors = [
  { bufferView: 0, componentType: 5126, count: newVertexCount, type: 'VEC3' },
  { bufferView: 1, componentType: 5126, count: newVertexCount, type: 'VEC2' },
  { bufferView: 2, componentType: 5126, count: newVertexCount, type: 'VEC3' },
  { bufferView: 3, componentType: 5125, count: newIndexCount, type: 'SCALAR' },
];
const outJson = {
  asset: { version: '2.0', generator: json.asset?.generator || 'THREE.GLTFExporter' },
  scene: 0,
  scenes: json.scenes,
  nodes: json.nodes,
  meshes: [{
    primitives: [{
      mode: 4,
      attributes: { POSITION: 0, TEXCOORD_0: 1, NORMAL: 2 },
      indices: 3,
      material: 0,
    }],
  }],
  materials: json.materials,
  textures: json.textures,
  images: json.images,
  samplers: json.samplers,
  accessors,
  bufferViews,
  buffers: [{ byteLength: binLength }],
};

// --- assemble glb
const jsonStr = JSON.stringify(outJson);
const jsonBuf = Buffer.from(jsonStr, 'utf8');
const jsonPadded = Buffer.alloc(align4(jsonBuf.length), 0x20);
jsonBuf.copy(jsonPadded);

const totalLen = 12 + 8 + jsonPadded.length + 8 + bin.length;
const glb = Buffer.alloc(totalLen);
glb.writeUInt32LE(0x46546c67, 0);
glb.writeUInt32LE(2, 4);
glb.writeUInt32LE(totalLen, 8);
glb.writeUInt32LE(jsonPadded.length, 12);
glb.writeUInt32LE(0x4e4f534a, 16);
jsonPadded.copy(glb, 20);
glb.writeUInt32LE(bin.length, 20 + jsonPadded.length);
glb.writeUInt32LE(0x004e4942, 24 + jsonPadded.length);
bin.copy(glb, 28 + jsonPadded.length);

fs.writeFileSync(OUT, glb);
console.log('wrote', OUT, 'bytes', glb.length, '| vertices', newVertexCount, '| triangles', newIndexCount / 3);
