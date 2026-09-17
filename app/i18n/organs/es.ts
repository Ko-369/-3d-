import type { OrganContentDictionary } from "../types";
import { organs as en } from "./en";

export const organs: OrganContentDictionary = {
  motherboard: { ...en.motherboard, name: 'Placa base', system: 'Plataforma e interconexión', poetic: 'El mapa de señales' },
  cpu: { ...en.cpu, name: 'CPU', system: 'Procesamiento', poetic: 'El motor de instrucciones' },
  gpu: { ...en.gpu, name: 'Tarjeta gráfica / GPU', system: 'Cómputo paralelo y gráficos', poetic: 'El motor paralelo' },
  memory: { ...en.memory, name: 'Memoria RAM', system: 'Memoria de trabajo', poetic: 'El espacio de trabajo activo' },
  storage: { ...en.storage, name: 'SSD NVMe', system: 'Almacenamiento persistente', poetic: 'La memoria persistente' },
  power: { ...en.power, name: 'Fuente de alimentación', system: 'Suministro eléctrico', poetic: 'El convertidor de energía' },
  cooling: { ...en.cooling, name: 'Refrigeración de CPU', system: 'Gestión térmica', poetic: 'La autopista térmica' },
  network: { ...en.network, name: 'Adaptador de red', system: 'Comunicación y E/S', poetic: 'La puerta de enlace de datos' },
  case: { ...en.case, name: 'Sistema informático', system: 'Sistema integrado', poetic: 'La máquina completa' },
};
