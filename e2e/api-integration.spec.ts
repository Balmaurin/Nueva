import { test, expect } from '@playwright/test';

test.describe('API Integration Tests', () => {
  const baseUrl = 'http://127.0.0.1:3000';
  const apiUrl = 'http://127.0.0.1:8000';

  test.beforeEach(async ({ page }) => {
    await page.goto(baseUrl);
  });

  test('should register and login user through API', async ({ page }) => {
    // Navegar a la página de registro
    await page.click('text=Registrarse');
    
    // Llenar formulario de registro
    await page.fill('input[name="username"]', 'testuser_e2e');
    await page.fill('input[name="email"]', 'test_e2e@example.com');
    await page.fill('input[name="password"]', 'testpassword123');
    
    // Enviar formulario
    await page.click('button[type="submit"]');
    
    // Verificar que se registró correctamente
    await expect(page).toHaveURL(/.*dashboard/);
    
    // Verificar que el usuario está autenticado
    await expect(page.locator('text=testuser_e2e')).toBeVisible();
  });

  test('should handle chat interaction with API', async ({ page }) => {
    // Login primero
    await page.click('text=Iniciar Sesión');
    await page.fill('input[name="username"]', 'testuser_e2e');
    await page.fill('input[name="password"]', 'testpassword123');
    await page.click('button[type="submit"]');
    
    // Navegar al chat
    await page.click('text=Chat IA');
    
    // Enviar mensaje
    await page.fill('textarea[placeholder*="mensaje"]', 'Hola, ¿cómo estás?');
    await page.click('button:has-text("Enviar")');
    
    // Verificar que se envió el mensaje
    await expect(page.locator('text=Hola, ¿cómo estás?')).toBeVisible();
    
    // Verificar que se recibió respuesta
    await expect(page.locator('.message-response')).toBeVisible();
  });

  test('should start training session through API', async ({ page }) => {
    // Login primero
    await page.click('text=Iniciar Sesión');
    await page.fill('input[name="username"]', 'testuser_e2e');
    await page.fill('input[name="password"]', 'testpassword123');
    await page.click('button[type="submit"]');
    
    // Navegar al entrenamiento
    await page.click('text=Train AI');
    
    // Verificar que se muestra la interfaz de entrenamiento
    await expect(page.locator('text=Train AI')).toBeVisible();
    await expect(page.locator('text=Precisión')).toBeVisible();
    await expect(page.locator('text=Velocidad')).toBeVisible();
    
    // Verificar que hay un ejercicio disponible
    await expect(page.locator('.exercise-question')).toBeVisible();
  });

  test('should display vault statistics from API', async ({ page }) => {
    // Login primero
    await page.click('text=Iniciar Sesión');
    await page.fill('input[name="username"]', 'testuser_e2e');
    await page.fill('input[name="password"]', 'testpassword123');
    await page.click('button[type="submit"]');
    
    // Navegar al vault
    await page.click('text=Caja Fuerte');
    
    // Verificar que se muestran las estadísticas
    await expect(page.locator('text=Balance')).toBeVisible();
    await expect(page.locator('text=Experiencia')).toBeVisible();
    await expect(page.locator('text=Nivel')).toBeVisible();
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Intentar login con credenciales incorrectas
    await page.click('text=Iniciar Sesión');
    await page.fill('input[name="username"]', 'nonexistent');
    await page.fill('input[name="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');
    
    // Verificar que se muestra error
    await expect(page.locator('.error-message')).toBeVisible();
  });

  test('should maintain session across page reloads', async ({ page }) => {
    // Login
    await page.click('text=Iniciar Sesión');
    await page.fill('input[name="username"]', 'testuser_e2e');
    await page.fill('input[name="password"]', 'testpassword123');
    await page.click('button[type="submit"]');
    
    // Verificar que está en dashboard
    await expect(page).toHaveURL(/.*dashboard/);
    
    // Recargar página
    await page.reload();
    
    // Verificar que sigue autenticado
    await expect(page.locator('text=testuser_e2e')).toBeVisible();
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test('should handle network connectivity issues', async ({ page }) => {
    // Simular desconexión de red
    await page.route('**/*', route => route.abort());
    
    // Intentar navegar
    await page.goto(baseUrl);
    
    // Verificar que se muestra mensaje de error de conexión
    await expect(page.locator('text=Error de conexión')).toBeVisible();
  });

  test('should validate form inputs properly', async ({ page }) => {
    // Navegar a registro
    await page.click('text=Registrarse');
    
    // Intentar enviar formulario vacío
    await page.click('button[type="submit"]');
    
    // Verificar que se muestran errores de validación
    await expect(page.locator('.validation-error')).toBeVisible();
    
    // Intentar con email inválido
    await page.fill('input[name="email"]', 'invalid-email');
    await page.click('button[type="submit"]');
    
    // Verificar error de email
    await expect(page.locator('text=Email inválido')).toBeVisible();
  });

  test('should handle concurrent API requests', async ({ page }) => {
    // Login
    await page.click('text=Iniciar Sesión');
    await page.fill('input[name="username"]', 'testuser_e2e');
    await page.fill('input[name="password"]', 'testpassword123');
    await page.click('button[type="submit"]');
    
    // Hacer múltiples requests simultáneos
    await Promise.all([
      page.click('text=Chat IA'),
      page.click('text=Train AI'),
      page.click('text=Caja Fuerte')
    ]);
    
    // Verificar que todas las páginas cargan correctamente
    await expect(page.locator('text=Chat IA')).toBeVisible();
  });

  test('should handle API rate limiting', async ({ page }) => {
    // Login
    await page.click('text=Iniciar Sesión');
    await page.fill('input[name="username"]', 'testuser_e2e');
    await page.fill('input[name="password"]', 'testpassword123');
    await page.click('button[type="submit"]');
    
    // Navegar al chat
    await page.click('text=Chat IA');
    
    // Enviar múltiples mensajes rápidamente
    for (let i = 0; i < 10; i++) {
      await page.fill('textarea[placeholder*="mensaje"]', `Mensaje ${i}`);
      await page.click('button:has-text("Enviar")');
    }
    
    // Verificar que se maneja el rate limiting
    await expect(page.locator('.rate-limit-message')).toBeVisible();
  });
});
