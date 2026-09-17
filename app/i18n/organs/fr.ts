import type { OrganContentDictionary } from "../types";
import { organs as en } from "./en";

export const organs: OrganContentDictionary = {
  motherboard: { ...en.motherboard, name: 'Carte mère', system: 'Plateforme et interconnexion', poetic: 'La carte des signaux' },
  cpu: { ...en.cpu, name: 'CPU', system: 'Traitement', poetic: 'Le moteur d’instructions' },
  gpu: { ...en.gpu, name: 'Carte graphique / GPU', system: 'Calcul parallèle et graphisme', poetic: 'Le moteur parallèle' },
  memory: { ...en.memory, name: 'Mémoire RAM', system: 'Mémoire de travail', poetic: 'L’espace de travail actif' },
  storage: { ...en.storage, name: 'SSD NVMe', system: 'Stockage persistant', poetic: 'La mémoire persistante' },
  power: { ...en.power, name: 'Bloc d’alimentation', system: 'Distribution électrique', poetic: 'Le convertisseur d’énergie' },
  cooling: { ...en.cooling, name: 'Refroidissement CPU', system: 'Gestion thermique', poetic: 'La voie thermique' },
  network: { ...en.network, name: 'Carte réseau', system: 'Communication et E/S', poetic: 'La passerelle de données' },
  case: { ...en.case, name: 'Système informatique', system: 'Système intégré', poetic: 'La machine complète' },
};
