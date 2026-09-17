import type { OrganContentDictionary } from "../types";
import { organs as en } from "./en";

export const organs: OrganContentDictionary = {
  motherboard: { ...en.motherboard, name: 'Материнская плата', system: 'Платформа и межсоединения', poetic: 'Карта сигналов системы' },
  cpu: { ...en.cpu, name: 'ЦП', system: 'Обработка', poetic: 'Двигатель инструкций' },
  gpu: { ...en.gpu, name: 'Видеокарта / GPU', system: 'Параллельные вычисления и графика', poetic: 'Параллельный двигатель' },
  memory: { ...en.memory, name: 'Оперативная память', system: 'Рабочая память', poetic: 'Активное рабочее пространство' },
  storage: { ...en.storage, name: 'NVMe SSD', system: 'Постоянное хранилище', poetic: 'Постоянная память' },
  power: { ...en.power, name: 'Блок питания', system: 'Электропитание', poetic: 'Преобразователь энергии' },
  cooling: { ...en.cooling, name: 'Охлаждение ЦП', system: 'Термоуправление', poetic: 'Тепловая магистраль' },
  network: { ...en.network, name: 'Сетевой адаптер', system: 'Связь и ввод-вывод', poetic: 'Шлюз данных' },
  case: { ...en.case, name: 'Компьютерная система', system: 'Интегрированная система', poetic: 'Полная машина' },
};
