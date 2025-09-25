# 🤖 Bugbot - Gestión Automática de Issues

Bugbot es un sistema automatizado que ayuda a gestionar issues y pull requests en el repositorio Sheily AI.

## 🚀 Funciones Principales

### Etiquetado Automático
Bugbot analiza automáticamente el título y contenido de las issues para asignar etiquetas relevantes:

- **🐛 bug**: Issues relacionadas con errores y bugs
- **✨ enhancement**: Solicitudes de nuevas funcionalidades
- **📚 documentation**: Issues de documentación
- **🚨 critical**: Issues críticas que requieren atención inmediata
- **🎨 frontend**: Issues relacionadas con la interfaz de usuario
- **⚙️ backend**: Issues del lado del servidor
- **🤖 ai/ml**: Issues de inteligencia artificial y machine learning
- **⛓️ blockchain**: Issues relacionados con blockchain y criptomonedas

### Priorización Automática
- **🔴 high-priority**: Bugs críticos, errores de seguridad
- **🟡 medium-priority**: Mejoras y nuevas funcionalidades
- **🟢 low-priority**: Documentación y tareas menores

### Gestión de Estado
- **📋 triage-needed**: Issues que necesitan revisión inicial
- **👀 under-review**: Issues en proceso de revisión
- **✅ ready-to-work**: Issues listas para desarrollo

## 📝 Cómo Usar Bugbot

### Reportar un Bug
1. Ve a [Issues](https://github.com/Balmaurin/Sheily/issues)
2. Haz clic en "New Issue"
3. Selecciona "🐛 Bug Report"
4. Completa el template con toda la información necesaria
5. Bugbot etiquetará automáticamente la issue

### Solicitar una Funcionalidad
1. Ve a [Issues](https://github.com/Balmaurin/Sheily/issues)
2. Haz clic en "New Issue"
3. Selecciona "✨ Feature Request"
4. Describe claramente la funcionalidad deseada
5. Bugbot asignará las etiquetas apropiadas

### Palabras Clave para Etiquetado Automático

Incluye estas palabras en el título o descripción para activar etiquetas específicas:

| Palabra Clave | Etiqueta Asignada |
|---------------|-------------------|
| `[BUG]`, `bug:`, `error` | 🐛 bug |
| `[FEATURE]`, `feature:` | ✨ enhancement |
| `[DOCS]`, `documentation` | 📚 documentation |
| `[URGENT]`, `critical` | 🚨 critical |
| `frontend`, `react`, `ui` | 🎨 frontend |
| `backend`, `api`, `server` | ⚙️ backend |
| `ai`, `ml`, `model` | 🤖 ai/ml |
| `blockchain`, `solana` | ⛓️ blockchain |

## ⚙️ Configuración

La configuración de Bugbot se encuentra en:
- `.github/workflows/bugbot.yml` - Workflow de GitHub Actions
- `.github/bugbot-config.json` - Configuración detallada
- `.github/ISSUE_TEMPLATE/` - Templates para issues

## 🤖 Comportamiento de Bugbot

Cuando creas una issue:

1. **Análisis automático**: Bugbot lee el título y contenido
2. **Etiquetado inteligente**: Asigna etiquetas basadas en patrones
3. **Priorización**: Determina la urgencia del issue
4. **Comentario automático**: Explica qué etiquetas asignó
5. **Notificaciones**: Puede enviar alertas para issues críticos

## 📊 Estadísticas y Reportes

Bugbot puede generar reportes automáticos sobre:
- Número de bugs abiertos
- Tiempo promedio de resolución
- Issues por componente
- Tendencias de bugs por semana/mes

## 🔧 Personalización

Para modificar el comportamiento de Bugbot, edita los archivos en `.github/`:
- Añade nuevas reglas de etiquetado en `bugbot-config.json`
- Modifica los templates en `ISSUE_TEMPLATE/`
- Actualiza el workflow en `workflows/bugbot.yml`

## 📞 Soporte

Si Bugbot no funciona correctamente:
1. Verifica que el issue tenga suficiente información
2. Revisa las etiquetas asignadas automáticamente
3. Si es incorrecto, edita manualmente las etiquetas
4. Reporta problemas con Bugbot como cualquier otro bug

---

**Bugbot mantiene el repositorio organizado y asegura que los issues sean manejados eficientemente.** 🎯
