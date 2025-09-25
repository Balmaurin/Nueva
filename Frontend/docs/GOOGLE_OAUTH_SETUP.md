# Configuración de Credenciales de Google OAuth para Sheily

## Requisitos Previos
- Cuenta de Google
- Proyecto en Google Cloud Console
- Aplicación Next.js configurada

## Pasos Detallados

### 1. Crear Proyecto en Google Cloud Console
1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Hacer clic en "Seleccionar un proyecto" en la parte superior
3. Hacer clic en "Nuevo proyecto"
4. Asignar un nombre (por ejemplo, "Sheily-OAuth")
5. Hacer clic en "Crear"

### 2. Configurar Pantalla de Consentimiento OAuth
1. En el menú de navegación, ir a "APIs y servicios" > "Pantalla de consentimiento OAuth"
2. Seleccionar "Externo"
3. Completar los campos obligatorios:
   - Nombre de la aplicación
   - Correo electrónico de soporte
   - Información de desarrollador

### 3. Crear Credenciales de OAuth
1. Ir a "APIs y servicios" > "Credenciales"
2. Hacer clic en "Crear credenciales" > "ID de cliente de OAuth"
3. Seleccionar "Aplicación web" como tipo de aplicación
4. Configurar URIs de redireccionamiento:
   ```
   http://localhost:3004/api/auth/callback/google
   https://tu-dominio-produccion.com/api/auth/callback/google
   ```
5. Hacer clic en "Crear"
6. Copiar el "ID de cliente" y "Secreto de cliente"

### 4. Configurar Variables de Entorno
Editar el archivo `.env.local` en tu proyecto Frontend:
```bash
GOOGLE_CLIENT_ID=tu_client_id_copiado_aquí
GOOGLE_CLIENT_SECRET=tu_client_secret_copiado_aquí
```

### 5. Verificaciones Adicionales
- Asegurarse de que el dominio de la aplicación esté configurado
- Verificar que las URIs de redireccionamiento sean exactamente iguales
- Comprobar que la pantalla de consentimiento esté completamente configurada

## Solución de Problemas Comunes
- **Error 401: invalid_client**
  - Verificar que el client ID y client secret sean correctos
  - Comprobar que las URIs de redireccionamiento coincidan exactamente
  - Regenerar credenciales si es necesario

## Recursos Adicionales
- [Documentación de OAuth de Google](https://developers.google.com/identity/protocols/oauth2)
- [Guía de Configuración de NextAuth](https://next-auth.js.org/providers/google)

## Notas de Seguridad
- Nunca compartir las credenciales públicamente
- Usar variables de entorno para manejar credenciales
- Tener credenciales separadas para desarrollo y producción
