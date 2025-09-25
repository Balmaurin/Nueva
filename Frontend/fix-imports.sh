#!/bin/bash

# Script para arreglar todos los imports del Frontend

echo "🔧 Arreglando imports del Frontend..."

# Limpiar paths duplicados
find . -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|\.\./\.\./\.\./\.\./|../../|g'
find . -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|\.\./\.\./\.\./|../../|g'
find . -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|\.\./\.\./\.\./|../../|g'

# Arreglar paths específicos para app/page.tsx
sed -i 's|\.\./contexts/|../contexts/|g' app/page.tsx
sed -i 's|\.\./components/|../components/|g' app/page.tsx

# Arreglar paths específicos para app/dashboard/page.tsx
sed -i 's|\.\./contexts/|../../contexts/|g' app/dashboard/page.tsx
sed -i 's|\.\./components/|../../components/|g' app/dashboard/page.tsx

# Arreglar paths para componentes en components/
find components/ -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|\.\./components/ui/|./components/ui/|g'
find components/ -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|\.\./lib/|./lib/|g'

echo "✅ Imports arreglados"
