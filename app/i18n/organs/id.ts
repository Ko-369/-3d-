import type { OrganContentDictionary } from "../types";
import { organs as en } from "./en";

export const organs: OrganContentDictionary = {
  motherboard: { ...en.motherboard, name: 'Motherboard', system: 'Platform & interkoneksi', poetic: 'Peta sinyal sistem' },
  cpu: { ...en.cpu, name: 'CPU', system: 'Pemrosesan', poetic: 'Mesin instruksi' },
  gpu: { ...en.gpu, name: 'Kartu grafis / GPU', system: 'Komputasi paralel & grafis', poetic: 'Mesin paralel' },
  memory: { ...en.memory, name: 'Memori RAM', system: 'Memori kerja', poetic: 'Ruang kerja aktif' },
  storage: { ...en.storage, name: 'SSD NVMe', system: 'Penyimpanan persisten', poetic: 'Memori persisten' },
  power: { ...en.power, name: 'Catu daya', system: 'Distribusi daya', poetic: 'Konverter energi' },
  cooling: { ...en.cooling, name: 'Pendingin CPU', system: 'Manajemen termal', poetic: 'Jalur panas' },
  network: { ...en.network, name: 'Adaptor jaringan', system: 'Komunikasi & I/O', poetic: 'Gerbang data' },
  case: { ...en.case, name: 'Sistem komputer', system: 'Sistem terintegrasi', poetic: 'Mesin lengkap' },
};
