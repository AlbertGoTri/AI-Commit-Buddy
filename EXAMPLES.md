# Ejemplos de Uso - Kiro Commit Buddy

Esta guía contiene ejemplos prácticos de cómo usar Kiro Commit Buddy en diferentes escenarios.

## 🚀 Uso básico

### Ejemplo 1: Primer commit

```bash
# 1. Crear un nuevo archivo
echo "print('Hello, World!')" > hello.py

# 2. Añadir al staging
git add hello.py

# 3. Generar commit con IA
kiro commit --from-diff
```

**Salida esperada:**
```
🔍 Analizando cambios staged...
🤖 Generando mensaje con IA...

📝 Mensaje propuesto:
feat: add hello world script

¿Usar este mensaje? (y/n/e para editar): y

✅ Commit creado exitosamente: a1b2c3d
```

### Ejemplo 2: Corrección de bug

```bash
# 1. Corregir un bug en el código
# Cambiar: result = x / y
# Por: result = x / y if y != 0 else 0

# 2. Añadir cambios
git add calculator.py

# 3. Generar commit
kiro commit --from-diff
```

**Salida esperada:**
```
📝 Mensaje propuesto:
fix: prevent division by zero in calculator

¿Usar este mensaje? (y/n/e para editar): y
```

## 📝 Tipos de commit automáticos

### feat: Nuevas funcionalidades

```bash
# Añadir nueva función de autenticación
git add auth.py login.html
kiro commit --from-diff
# Resultado: "feat: add user authentication system"

# Añadir API endpoint
git add api/users.py
kiro commit --from-diff
# Resultado: "feat: add users API endpoint"
```

### fix: Correcciones

```bash
# Corregir error de validación
git add validation.py
kiro commit --from-diff
# Resultado: "fix: correct email validation regex"

# Arreglar problema de memoria
git add memory_manager.py
kiro commit --from-diff
# Resultado: "fix: resolve memory leak in cache"
```

### docs: Documentación

```bash
# Actualizar README
git add README.md
kiro commit --from-diff
# Resultado: "docs: update installation instructions"

# Añadir comentarios al código
git add complex_algorithm.py
kiro commit --from-diff
# Resultado: "docs: add comments to sorting algorithm"
```

### refactor: Refactorización

```bash
# Reorganizar código
git add utils.py helpers.py
kiro commit --from-diff
# Resultado: "refactor: extract utility functions to separate module"

# Mejorar estructura de clases
git add models/user.py
kiro commit --from-diff
# Resultado: "refactor: simplify user model structure"
```

### test: Pruebas

```bash
# Añadir tests unitarios
git add test_calculator.py
kiro commit --from-diff
# Resultado: "test: add unit tests for calculator functions"

# Actualizar tests existentes
git add test_auth.py
kiro commit --from-diff
# Resultado: "test: update authentication test cases"
```

### chore: Tareas de mantenimiento

```bash
# Actualizar dependencias
git add requirements.txt
kiro commit --from-diff
# Resultado: "chore: update project dependencies"

# Configuración de build
git add .github/workflows/ci.yml
kiro commit --from-diff
# Resultado: "chore: configure CI/CD pipeline"
```

## 🎛️ Opciones de interacción

### Confirmar mensaje (y)

```bash
kiro commit --from-diff
# Mensaje propuesto: "feat: add user dashboard"
# ¿Usar este mensaje? (y/n/e para editar): y
# ✅ Commit creado exitosamente
```

### Rechazar mensaje (n)

```bash
kiro commit --from-diff
# Mensaje propuesto: "chore: update files"
# ¿Usar este mensaje? (y/n/e para editar): n
# ❌ Commit cancelado
```

### Editar mensaje (e)

```bash
kiro commit --from-diff
# Mensaje propuesto: "feat: add login"
# ¿Usar este mensaje? (y/n/e para editar): e
# Edita el mensaje: feat: implement secure user login system
# ✅ Commit creado con mensaje editado
```

## 🔄 Escenarios de fallback

### Sin conexión a internet

```bash
git add multiple_files.py config.json
kiro commit --from-diff
```

**Salida:**
```
🔍 Analizando cambios staged...
⚠️  API no disponible, generando mensaje básico...

📝 Mensaje propuesto:
chore: update multiple_files.py, config.json

¿Usar este mensaje? (y/n/e para editar): e
Edita el mensaje: feat: add configuration management system
```

### API key no configurada

```bash
# Sin GROQ_API_KEY configurada
kiro commit --from-diff
```

**Salida:**
```
⚠️  GROQ_API_KEY no configurada. Usando mensaje básico...
Configura tu API key para obtener mensajes más inteligentes.

📝 Mensaje propuesto:
chore: update 3 files
```

## 🛠️ Flujos de trabajo avanzados

### Workflow de desarrollo de features

```bash
# 1. Crear rama para feature
git checkout -b feature/user-profile

# 2. Implementar funcionalidad básica
echo "class UserProfile: pass" > user_profile.py
git add user_profile.py
kiro commit --from-diff
# "feat: add user profile model"

# 3. Añadir validaciones
# Editar user_profile.py para añadir validaciones
git add user_profile.py
kiro commit --from-diff
# "feat: add validation to user profile"

# 4. Añadir tests
echo "def test_user_profile(): pass" > test_user_profile.py
git add test_user_profile.py
kiro commit --from-diff
# "test: add user profile tests"

# 5. Documentar
echo "# User Profile\n\nManages user profiles..." > docs/user_profile.md
git add docs/user_profile.md
kiro commit --from-diff
# "docs: add user profile documentation"
```

### Workflow de bugfix

```bash
# 1. Crear rama para bugfix
git checkout -b fix/login-error

# 2. Identificar y corregir el problema
# Editar auth.py para corregir el bug
git add auth.py
kiro commit --from-diff
# "fix: resolve login timeout issue"

# 3. Añadir test para prevenir regresión
git add test_auth.py
kiro commit --from-diff
# "test: add test for login timeout scenario"

# 4. Actualizar documentación si es necesario
git add README.md
kiro commit --from-diff
# "docs: update troubleshooting section"
```

### Workflow de refactoring

```bash
# 1. Extraer funciones comunes
git add utils.py
kiro commit --from-diff
# "refactor: extract common utilities"

# 2. Actualizar imports en archivos existentes
git add main.py auth.py
kiro commit --from-diff
# "refactor: update imports to use new utilities"

# 3. Eliminar código duplicado
git add legacy_utils.py
kiro commit --from-diff
# "refactor: remove duplicate utility functions"
```

## 🎯 Mejores prácticas

### 1. Commits atómicos

```bash
# ✅ Bueno: Un cambio lógico por commit
git add user_model.py
kiro commit --from-diff
# "feat: add user model"

git add user_controller.py
kiro commit --from-diff
# "feat: add user controller"

# ❌ Evitar: Múltiples cambios no relacionados
# git add user_model.py payment_system.py bug_fix.py
```

### 2. Staging selectivo

```bash
# Añadir solo partes específicas de un archivo
git add -p complex_file.py
kiro commit --from-diff

# Añadir archivos específicos
git add src/models/user.py src/controllers/user.py
kiro commit --from-diff
```

### 3. Revisar cambios antes del commit

```bash
# Revisar qué está staged
git diff --staged

# Generar commit
kiro commit --from-diff
```

### 4. Usar edición cuando sea necesario

```bash
kiro commit --from-diff
# Si el mensaje generado es: "chore: update files"
# Usar 'e' para editarlo a algo más descriptivo:
# "feat: implement user authentication middleware"
```

## 🔍 Casos de uso específicos

### Proyecto Python

```bash
# Añadir nueva clase
git add models/product.py
kiro commit --from-diff
# "feat: add product model with validation"

# Actualizar requirements
git add requirements.txt
kiro commit --from-diff
# "chore: update dependencies to latest versions"

# Corregir import
git add __init__.py
kiro commit --from-diff
# "fix: correct module imports in package"
```

### Proyecto JavaScript/Node.js

```bash
# Nuevo componente React
git add components/UserCard.jsx
kiro commit --from-diff
# "feat: add user card component"

# Actualizar package.json
git add package.json package-lock.json
kiro commit --from-diff
# "chore: update npm dependencies"

# Corregir bug en async function
git add api/users.js
kiro commit --from-diff
# "fix: handle async errors in user API"
```

### Configuración y DevOps

```bash
# Docker configuration
git add Dockerfile docker-compose.yml
kiro commit --from-diff
# "chore: add Docker configuration"

# CI/CD pipeline
git add .github/workflows/deploy.yml
kiro commit --from-diff
# "chore: configure deployment pipeline"

# Environment variables
git add .env.example
kiro commit --from-diff
# "chore: add environment variables template"
```

## 📊 Estadísticas y análisis

### Analizar patrones de commit

```bash
# Ver historial de commits generados
git log --oneline --grep="feat:"
git log --oneline --grep="fix:"
git log --oneline --grep="docs:"

# Estadísticas por tipo
git log --pretty=format:"%s" | grep -E "^(feat|fix|docs|refactor|test|chore):" | sort | uniq -c
```

### Comparar con commits manuales

```bash
# Commits antes de usar Kiro Commit Buddy
git log --before="2024-01-01" --oneline

# Commits después de usar Kiro Commit Buddy
git log --after="2024-01-01" --oneline
```

## 🎓 Consejos avanzados

### 1. Personalizar mensajes según el contexto

Si trabajas en diferentes tipos de proyectos, puedes editar los mensajes para que se adapten mejor:

```bash
# Para proyectos de API
kiro commit --from-diff
# Editar: "feat: add user endpoint" → "feat: add GET /api/users endpoint"

# Para proyectos de frontend
kiro commit --from-diff
# Editar: "feat: add component" → "feat: add responsive user profile component"
```

### 2. Usar con hooks de Git

Puedes integrar Kiro Commit Buddy con hooks de Git para automatizar aún más el proceso:

```bash
# .git/hooks/prepare-commit-msg
#!/bin/sh
if [ -z "$2" ]; then
    python .kiro/scripts/commit_buddy.py --from-diff --auto > "$1"
fi
```

### 3. Combinar con herramientas de linting

```bash
# Ejecutar linter antes del commit
npm run lint
git add .
kiro commit --from-diff
# "style: fix linting issues in components"
```

¡Estos ejemplos te ayudarán a aprovechar al máximo Kiro Commit Buddy en tu flujo de trabajo diario! 🚀