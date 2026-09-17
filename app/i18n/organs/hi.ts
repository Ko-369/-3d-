import type { OrganContentDictionary } from "../types";
import { organs as en } from "./en";

export const organs: OrganContentDictionary = {
  motherboard: { ...en.motherboard, name: 'मदरबोर्ड', system: 'प्लेटफ़ॉर्म और इंटरकनेक्ट', poetic: 'सिस्टम का सिग्नल मानचित्र' },
  cpu: { ...en.cpu, name: 'CPU', system: 'प्रोसेसिंग', poetic: 'निर्देश इंजन' },
  gpu: { ...en.gpu, name: 'ग्राफ़िक्स कार्ड / GPU', system: 'समानांतर कम्प्यूट और ग्राफ़िक्स', poetic: 'समानांतर कार्य इंजन' },
  memory: { ...en.memory, name: 'मेमोरी RAM', system: 'कार्यशील मेमोरी', poetic: 'सक्रिय कार्यक्षेत्र' },
  storage: { ...en.storage, name: 'NVMe SSD', system: 'स्थायी स्टोरेज', poetic: 'स्थायी स्मृति' },
  power: { ...en.power, name: 'पावर सप्लाई PSU', system: 'पावर डिलीवरी', poetic: 'ऊर्जा कनवर्टर' },
  cooling: { ...en.cooling, name: 'CPU कूलिंग', system: 'थर्मल प्रबंधन', poetic: 'ऊष्मा मार्ग' },
  network: { ...en.network, name: 'नेटवर्क अडैप्टर', system: 'संचार और I/O', poetic: 'डेटा गेटवे' },
  case: { ...en.case, name: 'कंप्यूटर सिस्टम', system: 'एकीकृत सिस्टम', poetic: 'पूर्ण मशीन' },
};
