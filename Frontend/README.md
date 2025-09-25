# 🚀 Sheily AI - Frontend Next.js

Frontend moderno y responsivo para el sistema de inteligencia artificial Sheily AI.

## 📁 Estructura del Proyecto

```
Frontend/
├── 📚 docs/                    # Documentación del proyecto
│   ├── CHAT_SYSTEM.md         # Sistema de chat con Phi-3 Mini
│   ├── CSS_OPTIMIZATION.md    # Optimizaciones CSS
│   ├── GOOGLE_OAUTH_SETUP.md  # Configuración OAuth de Google
│   └── QUICK_START.md         # Guía de inicio rápido
├── 🔧 scripts/                 # Scripts de inicio y utilidades
│   ├── start.sh               # Script principal de inicio (Linux/macOS)
│   ├── start.py               # Script de inicio en Python
│   ├── start.js               # Script de inicio en JavaScript
│   └── test_startup.py        # Diagnóstico del sistema
├── ⚙️ config/                  # Configuraciones adicionales
├── 🧪 e2e/                    # Pruebas end-to-end
├── 🎨 components/             # Componentes React
├── 📱 app/                    # Páginas de la aplicación
└── [archivos de configuración en raíz]
```

## 🚀 Inicio Rápido

### Opción 1: Script Bash (Recomendado para Linux/macOS)
```bash
cd Frontend
./scripts/start.sh
```

### Opción 2: Script Python
```bash
cd Frontend
python3 scripts/start.py
```

### Opción 3: Script JavaScript
```bash
cd Frontend
node scripts/start.js
```

## 🌐 Acceso

Una vez iniciado, el frontend estará disponible en:
- **URL**: http://127.0.0.1:3000
- **Puerto**: 3000

## 📚 Documentación

- **📖 [Guía de Inicio Rápido](docs/QUICK_START.md)** - Instrucciones básicas
- **🤖 [Sistema de Chat](docs/CHAT_SYSTEM.md)** - Documentación del chat con Phi-3 Mini
- **🎨 [Optimización CSS](docs/CSS_OPTIMIZATION.md)** - Guía de optimización CSS
- **🔐 [OAuth Google](docs/GOOGLE_OAUTH_SETUP.md)** - Configuración de autenticación

## 🛠️ Tecnologías

- **Next.js 15.5.2** - Framework React
- **TypeScript** - Tipado estático
- **Tailwind CSS** - Framework CSS
- **PostCSS** - Procesamiento CSS
- **Playwright** - Testing E2E

## 🔧 Scripts Disponibles

```bash
npm run dev          # Desarrollo
npm run build        # Build de producción
npm run start        # Servidor de producción
npm run test:e2e     # Pruebas E2E
```

## 🚨 Solución de Problemas

Si encuentras problemas al iniciar:

1. **Ejecuta el diagnóstico**: `python3 scripts/test_startup.py`
2. **Verifica dependencias**: `npm install`
3. **Limpia caché**: `rm -rf .next`
4. **Revisa puertos**: Asegúrate de que el puerto 3000 esté libre

---

**Desarrollado con ❤️ para el proyecto Sheily AI**
