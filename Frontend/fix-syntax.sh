#!/bin/bash

echo "🔧 Arreglando errores de sintaxis..."

# Arreglar fetch calls
find components/ -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|"/api/|"/api/|g'
find components/ -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|"/api/|"/api/|g'

# Arreglar template literals
find components/ -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|"/api/datasets/\${|`/api/datasets/${|g'
find components/ -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|"/api/vault/|`/api/vault/|g'
find components/ -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|"/api/security/|`/api/security/|g'
find components/ -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|"/api/auth/|`/api/auth/|g'

# Arreglar imports problemáticos
find . -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|../ui/use-toast|../components/ui/use-toast|g'

echo "✅ Errores de sintaxis arreglados"
