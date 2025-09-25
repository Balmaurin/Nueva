# Sistema de Audio del Láser - Sheily AI

## Descripción General

El sistema de audio del láser implementa un efecto de sonido que simula la carga progresiva de un arma láser, desde el inicio de la carga hasta el momento de la explosión.

## Características Principales

### 1. **Duración Completa**
- **Inicio**: Cuando comienza a cargar el núcleo
- **Fin**: En el flash de la explosión
- **Duración Total**: 7 segundos exactos

### 2. **Sin Repetición**
- El sonido se reproduce **UNA SOLA VEZ** por ciclo
- No hay loops ni repeticiones automáticas
- Se detiene automáticamente al finalizar la carga

### 3. **Aceleración Progresiva**
- **Velocidad Inicial**: 0.5x (más lento)
- **Velocidad Final**: 2.0x (más rápido)
- **Transición**: Suave y progresiva durante los 7 segundos
- **Actualización**: Cada 100ms para transición fluida

## Implementación Técnica

### Sonido MP3 (Principal)
```typescript
// Archivo: /sounds/062708_laser-charging-81968.mp3
// Aceleración progresiva del playbackRate
const playbackRate = 0.5 + (progress * 1.5);
source.playbackRate.setValueAtTime(playbackRate, audioContext.currentTime);

// Ganancia progresiva para compensar la aceleración
const gainValue = 0.4 + (progress * 0.3);
gainNode.gain.setValueAtTime(gainValue, audioContext.currentTime);
```

### Sonido Sintético (Fallback)
```typescript
// Frecuencia progresiva: 150Hz → 400Hz
const targetFreq = 150 + (progress * 250);

// Modulación progresiva: 8Hz → 20Hz
const modFreq = 8 + (progress * 12);

// Ganancia progresiva: 0.08 → 0.20
const gainValue = 0.08 + (progress * 0.12);
```

## Flujo de Audio

```
1. Click en el orbe
   ↓
2. Inicio de carga (sonido comienza a 0.5x velocidad)
   ↓
3. Progresión de 7 segundos con aceleración constante
   ↓
4. Velocidad máxima (2.0x) al final de la carga
   ↓
5. Sonido se detiene automáticamente
   ↓
6. Explosión con sonido separado
```

## Parámetros de Configuración

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `totalDuration` | 7000ms | Duración total de la carga |
| `updateInterval` | 100ms | Frecuencia de actualización |
| `playbackRate.min` | 0.5x | Velocidad inicial |
| `playbackRate.max` | 2.0x | Velocidad final |
| `gain.min` | 0.4 | Ganancia inicial |
| `gain.max` | 0.7 | Ganancia final |

## Archivos de Sonido

- **Carga del Láser**: `/sounds/062708_laser-charging-81968.mp3`
- **Explosión**: `/sounds/whoosh-drum-hits-169007.mp3`

## Compatibilidad

- **Navegadores Modernos**: Web Audio API completa
- **Fallback**: Generación sintética de audio
- **Móviles**: Soporte completo para dispositivos táctiles

## Debug y Logging

El sistema incluye logs detallados en la consola:
```
🎵 Iniciando sonido de carga del láser (duración completa)
📡 Cargando archivo: /sounds/062708_laser-charging-81968.mp3
▶️ Reproduciendo sonido de carga del láser (sin loop)
🎵 Aceleración del láser: 0.75x, Ganancia: 0.55
🎵 Aceleración del láser: 1.25x, Ganancia: 0.65
🎵 Aceleración del láser: 1.75x, Ganancia: 0.70
```

## Notas de Implementación

- El sistema utiliza `setInterval` para la aceleración progresiva
- Se limpia automáticamente al finalizar o al detener manualmente
- Compatible con el sistema de explosión existente
- No interfiere con otros sonidos del sistema
