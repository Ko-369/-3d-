import type { OrganContentDictionary } from "../types";
import { organs as en } from "./en";

export const organs: OrganContentDictionary = {
  motherboard: { ...en.motherboard, name: 'Placa-mãe', system: 'Plataforma e interconexão', poetic: 'O mapa de sinais' },
  cpu: { ...en.cpu, name: 'CPU', system: 'Processamento', poetic: 'O motor de instruções' },
  gpu: { ...en.gpu, name: 'Placa de vídeo / GPU', system: 'Computação paralela e gráficos', poetic: 'O motor paralelo' },
  memory: { ...en.memory, name: 'Memória RAM', system: 'Memória de trabalho', poetic: 'O espaço de trabalho ativo' },
  storage: { ...en.storage, name: 'SSD NVMe', system: 'Armazenamento persistente', poetic: 'A memória persistente' },
  power: { ...en.power, name: 'Fonte de alimentação', system: 'Distribuição de energia', poetic: 'O conversor de energia' },
  cooling: { ...en.cooling, name: 'Refrigeração da CPU', system: 'Gerenciamento térmico', poetic: 'A rota térmica' },
  network: { ...en.network, name: 'Adaptador de rede', system: 'Comunicação e E/S', poetic: 'O gateway de dados' },
  case: { ...en.case, name: 'Sistema de computador', system: 'Sistema integrado', poetic: 'A máquina completa' },
};
