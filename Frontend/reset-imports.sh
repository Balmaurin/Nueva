#!/bin/bash

echo "🔄 Reiniciando sistema de imports..."

# 1. Desactivar paths absolutos temporalmente
sed -i 's|"@/\*": \["./\*"\],||g' tsconfig.json
sed -i 's|"@/components/\*": \["components/\*"\],||g' tsconfig.json
sed -i 's|"@/lib/\*": \["lib/\*"\],||g' tsconfig.json
sed -i 's|"@/contexts/\*": \["contexts/\*"\],||g' tsconfig.json
sed -i 's|"@/services/\*": \["services/\*"\],||g' tsconfig.json
sed -i 's|"@/hooks/\*": \["hooks/\*"\],||g' tsconfig.json
sed -i 's|"@/types/\*": \["types/\*"\],||g' tsconfig.json
sed -i 's|"@/app/\*": \["app/\*"\],||g' tsconfig.json

# 2. Convertir TODOS los imports absolutos a relativos
find . -name "*.tsx" -o -name "*.ts" | grep -v node_modules | xargs sed -i 's|@/contexts/|./contexts/|g'
find . -name "*.tsx" -o -name "*.ts" | grep -v node_modules | xargs sed -i 's|@/components/|./components/|g'
find . -name "*.tsx" -o -name "*.ts" | grep -v node_modules | xargs sed -i 's|@/lib/|./lib/|g'
find . -name "*.tsx" -o -name "*.ts" | grep -v node_modules | xargs sed -i 's|@/services/|./services/|g'
find . -name "*.tsx" -o -name "*.ts" | grep -v node_modules | xargs sed -i 's|@/hooks/|./hooks/|g'
find . -name "*.tsx" -o -name "*.ts" | grep -v node_modules | xargs sed -i 's|@/types/|./types/|g'

# 3. Arreglar imports desde app/ (que necesitan ../ para salir de app/)
find app/ -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|./contexts/|../contexts/|g'
find app/ -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|./components/|../components/|g'
find app/ -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|./lib/|../lib/|g'
find app/ -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|./services/|../services/|g'
find app/ -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|./hooks/|../hooks/|g'
find app/ -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|./types/|../types/|g'

# 4. Arreglar imports desde components/ (que necesitan ../ para salir de components/)
find components/ -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|./contexts/|../contexts/|g'
find components/ -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|./components/|.|g'  # dentro de components/
find components/ -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|./lib/|../lib/|g'
find components/ -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|./services/|../services/|g'

# 5. Limpiar paths duplicados
find . -name "*.tsx" -o -name "*.ts" | grep -v node_modules | xargs sed -i 's|\.\./\.\./\.\./|\.\./\.\./|g'
find . -name "*.tsx" -o -name "*.ts" | grep -v node_modules | xargs sed -i 's|\.\./\.\./\.\./|\.\./\.\./|g'
find . -name "*.tsx" -o -name "*.ts" | grep -v node_modules | xargs sed -i 's|\.\./\.\./|\.\./|g'

echo "✅ Sistema de imports reiniciado"
