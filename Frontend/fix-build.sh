#!/bin/bash

echo "🔧 Reparando build del Frontend..."

# Arreglar errores de sintaxis en fetch calls
echo "🔧 Arreglando fetch calls..."
find . -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|fetch("/api/|fetch(\'/api/|g'
find . -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|fetch(\`/api/|fetch(\'/api/|g'

# Arreglar template literals malformados
echo "🔧 Arreglando template literals..."
find . -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|`/api/|/api/|g'
find . -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|/api/datasets/\${|/api/datasets/${|g'

# Arreglar imports
echo "🔧 Arreglando imports..."
find . -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|.../providers/|../providers/|g'
find . -name "*.tsx" -o -name "*.ts" | xargs sed -i 's|../components/providers/|../providers/|g'

echo "✅ Build del Frontend reparado"
