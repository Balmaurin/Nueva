# Tests End-to-End (E2E)

Este directorio contiene tests de integración end-to-end reales para el sistema Sheily AI.

## Estructura

```
e2e/
├── README.md                    # Este archivo
└── api-integration.spec.ts      # Tests de integración de API
```

## Tests Disponibles

### 1. API Integration Tests (`api-integration.spec.ts`)

Tests de integración completa que verifican:

#### **✅ Autenticación y Registro**
- Registro de nuevos usuarios
- Login con credenciales válidas
- Manejo de credenciales incorrectas
- Persistencia de sesión

#### **✅ Interacción con Chat IA**
- Envío de mensajes al chat
- Recepción de respuestas del modelo
- Verificación de respuestas reales

#### **✅ Sistema de Entrenamiento**
- Acceso a ejercicios de entrenamiento
- Verificación de interfaz de entrenamiento
- Validación de métricas (precisión, velocidad)

#### **✅ Caja Fuerte (Vault)**
- Visualización de estadísticas reales
- Verificación de balance y experiencia
- Control de nivel del usuario

#### **✅ Manejo de Errores**
- Respuesta a errores de API
- Manejo de problemas de conectividad
- Validación de formularios

## Configuración

### **Requisitos**
- Node.js 18+
- Playwright
- Servidor backend ejecutándose en puerto 8000
- Servidor frontend ejecutándose en puerto 3000

### **Instalación**
```bash
# Instalar dependencias
npm install

# Instalar Playwright
npx playwright install
```

### **Ejecución**
```bash
# Ejecutar todos los tests
npx playwright test

# Ejecutar tests específicos
npx playwright test api-integration.spec.ts

# Ejecutar en modo UI
npx playwright test --ui

# Ejecutar en modo headed
npx playwright test --headed
```

## Configuración de Entorno

### **Variables de Entorno**
```bash
# URLs de los servicios
BASE_URL=http://127.0.0.1:3000
API_URL=http://127.0.0.1:8000

# Credenciales de prueba
TEST_USER=testuser_e2e
TEST_EMAIL=test_e2e@example.com
TEST_PASSWORD=testpassword123
```

### **Configuración de Playwright**
```typescript
// playwright.config.ts
export default defineConfig({
  testDir: './e2e',
  timeout: 30000,
  expect: {
    timeout: 5000
  },
  use: {
    baseURL: 'http://127.0.0.1:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
});
```

## Casos de Prueba

### **1. Flujo de Usuario Completo**
```typescript
test('complete user journey', async ({ page }) => {
  // 1. Registro
  await page.goto('/register');
  await page.fill('[name="username"]', 'newuser');
  await page.fill('[name="email"]', 'newuser@test.com');
  await page.fill('[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  
  // 2. Login
  await expect(page).toHaveURL(/.*dashboard/);
  
  // 3. Chat
  await page.click('text=Chat IA');
  await page.fill('textarea[placeholder*="mensaje"]', 'Hola');
  await page.click('button:has-text("Enviar")');
  await expect(page.locator('.message-response')).toBeVisible();
  
  // 4. Entrenamiento
  await page.click('text=Train AI');
  await expect(page.locator('.exercise-question')).toBeVisible();
  
  // 5. Vault
  await page.click('text=Caja Fuerte');
  await expect(page.locator('text=Balance')).toBeVisible();
});
```

### **2. Manejo de Errores**
```typescript
test('error handling', async ({ page }) => {
  // Login con credenciales incorrectas
  await page.fill('[name="username"]', 'wrong');
  await page.fill('[name="password"]', 'wrong');
  await page.click('button[type="submit"]');
  
  // Verificar mensaje de error
  await expect(page.locator('.error-message')).toBeVisible();
});
```

### **3. Validación de Formularios**
```typescript
test('form validation', async ({ page }) => {
  // Enviar formulario vacío
  await page.click('button[type="submit"]');
  await expect(page.locator('.validation-error')).toBeVisible();
  
  // Email inválido
  await page.fill('[name="email"]', 'invalid-email');
  await page.click('button[type="submit"]');
  await expect(page.locator('text=Email inválido')).toBeVisible();
});
```

## Integración Continua

### **GitHub Actions**
```yaml
name: E2E Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npx playwright install
      - run: npx playwright test
```

### **Docker**
```dockerfile
FROM mcr.microsoft.com/playwright:v1.40.0
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
CMD ["npx", "playwright", "test"]
```

## Monitoreo y Reportes

### **Reportes Automáticos**
```bash
# Generar reporte HTML
npx playwright show-report

# Generar reporte JUnit
npx playwright test --reporter=junit

# Generar reporte JSON
npx playwright test --reporter=json
```

### **Métricas de Calidad**
- **Cobertura de funcionalidades**: 100%
- **Tiempo de ejecución**: < 5 minutos
- **Tasa de éxito**: > 95%
- **Casos de prueba**: 10+ escenarios

## Mantenimiento

### **Actualización de Tests**
- Revisar tests mensualmente
- Actualizar selectores si cambia la UI
- Agregar nuevos casos de uso
- Optimizar tiempos de ejecución

### **Debugging**
```bash
# Modo debug
npx playwright test --debug

# Generar traces
npx playwright test --trace on

# Ver screenshots en fallos
npx playwright test --screenshot on
```

## Contacto

Para reportar problemas o sugerir mejoras:
- **Issues**: GitHub repository
- **Email**: testing@sheily-ai.com
- **Documentación**: docs/testing/e2e/
