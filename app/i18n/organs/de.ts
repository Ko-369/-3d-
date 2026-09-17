import type { OrganContentDictionary } from "../types";
import { organs as en } from "./en";

export const organs: OrganContentDictionary = {
  motherboard: { ...en.motherboard, name: 'Mainboard', system: 'Plattform & Interconnect', poetic: 'Die Signalkarte' },
  cpu: { ...en.cpu, name: 'CPU', system: 'Verarbeitung', poetic: 'Die Befehlsmaschine' },
  gpu: { ...en.gpu, name: 'Grafikkarte / GPU', system: 'Paralleles Rechnen & Grafik', poetic: 'Die Parallelmaschine' },
  memory: { ...en.memory, name: 'Arbeitsspeicher', system: 'Arbeitsgedächtnis', poetic: 'Der aktive Arbeitsbereich' },
  storage: { ...en.storage, name: 'NVMe-SSD', system: 'Permanenter Speicher', poetic: 'Das dauerhafte Gedächtnis' },
  power: { ...en.power, name: 'Netzteil', system: 'Stromversorgung', poetic: 'Der Energiewandler' },
  cooling: { ...en.cooling, name: 'CPU-Kühlung', system: 'Thermomanagement', poetic: 'Der Wärmeweg' },
  network: { ...en.network, name: 'Netzwerkadapter', system: 'Kommunikation & E/A', poetic: 'Das Datentor' },
  case: { ...en.case, name: 'Computersystem', system: 'Integriertes System', poetic: 'Die vollständige Maschine' },
};
