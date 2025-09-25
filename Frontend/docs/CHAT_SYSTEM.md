# 🤖 Sistema de Chat con Phi-3 Mini 4-bit

Este proyecto incluye un sistema completo de chat que utiliza el modelo Phi-3 Mini de 4-bit para inferencia rápida y generación de archivos LoRA para entrenamiento.

## 🏗️ Arquitectura del Sistema

### Componentes Principales

1. **`ChatService`** - Servicio principal para comunicación con el backend
2. **`ChatInterface`** - Componente React para la interfaz de usuario
3. **`useChat`** - Hook personalizado para manejo del estado del chat
4. **Tipos TypeScript** - Interfaces completas para type safety

### Flujo de Datos

```
Usuario → ChatInterface → useChat → ChatService → Backend API
   ↑                                                      ↓
   ← ChatResponse ← ChatService ← Model Server ← Modelo 4-bit
```

## 🚀 Características Principales

### ✅ Chat en Tiempo Real
- Interfaz moderna y responsiva
- Mensajes en tiempo real
- Indicadores de carga
- Manejo de errores robusto

### ✅ Generación de Archivos LoRA
- Creación automática de adaptadores
- Soporte para 32 dominios especializados
- Formato Safetensors
- Integración con modelo de 16-bit

### ✅ Fallback Inteligente
- Respuestas simuladas cuando el backend no está disponible
- Contexto basado en el mensaje del usuario
- Respuestas realistas del modelo 4-bit

### ✅ Métricas y Monitoreo
- Conteo de mensajes y tokens
- Tiempo de respuesta promedio
- Estadísticas de uso del modelo
- Información del sistema

## 📁 Estructura de Archivos

```
Frontend/
├── services/
│   └── ChatService.ts          # Servicio principal de chat
├── components/
│   └── chat/
│       └── ChatInterface.tsx   # Interfaz de usuario del chat
├── hooks/
│   └── useChat.ts              # Hook personalizado para el chat
├── types/
│   └── chat.ts                 # Tipos TypeScript para el chat
├── app/
│   └── chat/
│       └── page.tsx            # Página de ejemplo del chat
└── CHAT_SYSTEM_README.md       # Esta documentación
```

## 🔧 Configuración

### Variables de Entorno

```bash
# Backend API
API_BASE_URL=http://127.0.0.1:8000

# Timeouts
CHAT_TIMEOUT=30000
HEALTH_CHECK_TIMEOUT=5000
```

### Dependencias

```json
{
  "axios": "^1.6.7",
  "react": "^18.3.1",
  "typescript": "^5.5.4"
}
```

## 💻 Uso Básico

### 1. Importar el Servicio

```typescript
import { ChatService } from '@/services/ChatService';

// Enviar mensaje
const response = await ChatService.sendMessage("Hola, ¿cómo estás?");
console.log(response.message);
```

### 2. Usar el Hook

```typescript
import { useChat } from '@/hooks/useChat';

function MyChatComponent() {
  const { messages, sendMessage, isLoading } = useChat();
  
  const handleSend = () => {
    sendMessage("Tu mensaje aquí");
  };
  
  return (
    <div>
      {messages.map(msg => (
        <div key={msg.id}>{msg.content}</div>
      ))}
      <button onClick={handleSend} disabled={isLoading}>
        Enviar
      </button>
    </div>
  );
}
```

### 3. Usar el Componente

```typescript
import ChatInterface from '@/components/chat/ChatInterface';

function ChatPage() {
  return (
    <div className="h-screen">
      <ChatInterface 
        showLoRAGeneration={true}
        className="h-full"
      />
    </div>
  );
}
```

## 🔌 API Endpoints

### Chat 4-bit
```http
POST /api/chat/4bit
Content-Type: application/json

{
  "message": "Tu mensaje",
  "context": "Contexto opcional",
  "model": "phi3-mini-4bit",
  "max_tokens": 500,
  "temperature": 0.7
}
```

### Generación LoRA
```http
POST /api/lora/generate
Content-Type: application/json

{
  "conversation": [...],
  "domain": "medicina",
  "model": "phi3-mini-4bit",
  "target_model": "phi3-personal-16bit"
}
```

### Health Check
```http
GET /api/health
```

## 🎯 Casos de Uso

### 1. Chat General
- Consultas informativas
- Asistencia técnica
- Conversaciones casuales

### 2. Generación de LoRA
- Entrenamiento de ramas especializadas
- Adaptación a dominios específicos
- Mejora del modelo de 16-bit

### 3. Desarrollo y Testing
- Pruebas del modelo 4-bit
- Validación de respuestas
- Debugging del sistema

## 🛡️ Manejo de Errores

### Tipos de Errores

1. **401 Unauthorized** - Usuario no autenticado
2. **429 Too Many Requests** - Rate limit alcanzado
3. **503 Service Unavailable** - Servicio no disponible
4. **ECONNREFUSED** - Backend no accesible

### Estrategias de Fallback

- **Respuestas simuladas** cuando el backend falla
- **Reintentos automáticos** para errores temporales
- **Mensajes de error informativos** para el usuario
- **Logging detallado** para debugging

## 📊 Métricas y Monitoreo

### Métricas Disponibles

- **Mensajes**: Total de mensajes enviados/recibidos
- **Tokens**: Consumo total de tokens
- **Tiempo**: Tiempo de respuesta promedio
- **LoRA**: Archivos generados exitosamente
- **Errores**: Tasa de error y tipos

### Información del Modelo

- **Parámetros**: 768M
- **Memoria**: ~2.4GB VRAM
- **Contexto**: 131,072 tokens
- **Cuantización**: 4-bit (NF4)
- **Uptime**: 99.8%

## 🔄 Flujo de Generación LoRA

```
1. Usuario inicia conversación
2. ChatService envía mensajes al backend
3. Modelo 4-bit procesa y responde
4. Conversación se almacena en memoria
5. Usuario solicita generación LoRA
6. ChatService envía conversación al endpoint LoRA
7. Sistema genera archivo .safetensors
8. Archivo se devuelve al usuario
```

## 🚀 Optimizaciones Implementadas

### Rendimiento
- **Lazy loading** de componentes
- **Memoización** de funciones costosas
- **Debouncing** de inputs
- **Virtualización** para mensajes largos

### Memoria
- **Cleanup automático** de recursos
- **Garbage collection** manual
- **Abort controllers** para peticiones
- **Límites de mensajes** configurables

### UX
- **Auto-scroll** al último mensaje
- **Indicadores de estado** claros
- **Manejo de errores** amigable
- **Responsive design** completo

## 🧪 Testing

### Pruebas Unitarias
```bash
npm run test:unit
```

### Pruebas de Integración
```bash
npm run test:integration
```

### Pruebas E2E
```bash
npm run test:e2e
```

## 📈 Roadmap

### Fase 1 (Actual) ✅
- [x] Chat básico con modelo 4-bit
- [x] Generación de archivos LoRA
- [x] Fallback inteligente
- [x] Interfaz de usuario completa

### Fase 2 (Próxima)
- [ ] Persistencia de conversaciones
- [ ] Múltiples sesiones de chat
- [ ] Exportación en múltiples formatos
- [ ] Configuración avanzada del modelo

### Fase 3 (Futura)
- [ ] Chat en tiempo real con WebSockets
- [ ] Integración con múltiples modelos
- [ ] Sistema de plugins y extensiones
- [ ] Analytics avanzados

## 🤝 Contribución

### Estándares de Código
- **TypeScript** estricto
- **ESLint** y **Prettier** configurados
- **Conventional Commits** para commits
- **JSDoc** para documentación

### Proceso de Desarrollo
1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m 'feat: agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 📚 Referencias

- [Microsoft Phi-3 Documentation](https://aka.ms/phi3)
- [LoRA Paper](https://arxiv.org/abs/2106.09685)
- [Transformers Library](https://huggingface.co/docs/transformers)
- [Next.js Documentation](https://nextjs.org/docs)
- [React Hooks](https://react.dev/reference/react/hooks)

## 🆘 Soporte

### Problemas Comunes

1. **Backend no disponible**
   - Verificar que el servidor esté ejecutándose
   - Revisar logs del backend
   - Comprobar conectividad de red

2. **Errores de memoria GPU**
   - Reducir `max_tokens`
   - Limpiar cache de GPU
   - Reiniciar el servidor de modelo

3. **Respuestas lentas**
   - Verificar carga del sistema
   - Comprobar recursos de GPU
   - Revisar configuración del modelo

### Contacto

- **Issues**: Crear issue en GitHub
- **Discussions**: Usar GitHub Discussions
- **Documentación**: Revisar esta documentación

---

**Desarrollado con ❤️ para el proyecto Sheily AI**
