# Guía de Solución de Problemas - Kiro Commit Buddy

Esta guía te ayudará a resolver los problemas más comunes que puedes encontrar al usar Kiro Commit Buddy.

## 🔍 Diagnóstico rápido

Antes de revisar problemas específicos, ejecuta estos comandos para verificar tu configuración:

```bash
# Verificar que estás en un repositorio Git
git status

# Verificar que tienes cambios staged
git diff --staged

# Verificar tu API key (Windows PowerShell)
echo $env:GROQ_API_KEY

# Verificar tu API key (Linux/Mac)
echo $GROQ_API_KEY

# Verificar que Python puede importar las dependencias
python -c "import requests, colorama; print('Dependencias OK')"
```

## 🚨 Problemas comunes

### 1. Error: "No estás en un repositorio Git"

**Síntomas:**
```
Error: No estás en un repositorio Git
Asegúrate de ejecutar este comando desde un directorio que contenga un repositorio Git.
```

**Causas posibles:**
- Ejecutando el comando fuera de un repositorio Git
- El directorio `.git` está corrupto o no existe

**Soluciones:**
1. Navega a tu repositorio Git:
   ```bash
   cd /ruta/a/tu/proyecto
   ```

2. Verifica que es un repositorio Git válido:
   ```bash
   git status
   ```

3. Si no es un repositorio, inicialízalo:
   ```bash
   git init
   ```

### 2. Error: "No hay cambios staged para commit"

**Síntomas:**
```
No hay cambios staged para commit.
Usa 'git add <archivo>' para añadir cambios al área de staging.
```

**Causas posibles:**
- No has añadido archivos al área de staging
- Todos los cambios ya están committed

**Soluciones:**
1. Verifica el estado de tu repositorio:
   ```bash
   git status
   ```

2. Añade archivos al staging:
   ```bash
   git add archivo1.py archivo2.js
   # o para añadir todos los cambios:
   git add .
   ```

3. Verifica que tienes cambios staged:
   ```bash
   git diff --staged
   ```

### 3. Error: "GROQ_API_KEY no configurada"

**Síntomas:**
```
GROQ_API_KEY no está configurada.
Para configurarla:
  Windows: set GROQ_API_KEY=tu_api_key
  Linux/Mac: export GROQ_API_KEY=tu_api_key
```

**Soluciones:**

#### Windows (PowerShell):
```powershell
# Temporal (solo para la sesión actual)
$env:GROQ_API_KEY = "gsk_tu_api_key_aqui"

# Permanente (para el usuario actual)
[Environment]::SetEnvironmentVariable("GROQ_API_KEY", "gsk_tu_api_key_aqui", "User")

# Verificar
echo $env:GROQ_API_KEY
```

#### Windows (CMD):
```cmd
# Temporal
set GROQ_API_KEY=gsk_tu_api_key_aqui

# Permanente: Panel de Control > Sistema > Configuración avanzada > Variables de entorno
```

#### Linux/macOS:
```bash
# Temporal
export GROQ_API_KEY="gsk_tu_api_key_aqui"

# Permanente (añadir a ~/.bashrc o ~/.zshrc)
echo 'export GROQ_API_KEY="gsk_tu_api_key_aqui"' >> ~/.bashrc
source ~/.bashrc

# Verificar
echo $GROQ_API_KEY
```

### 4. Error: "API key inválida"

**Síntomas:**
```
Error de autenticación con Groq API
Verifica que tu GROQ_API_KEY sea correcta
```

**Causas posibles:**
- API key incorrecta o expirada
- API key con formato incorrecto
- Espacios extra en la API key

**Soluciones:**
1. Verifica el formato de tu API key:
   - Debe comenzar con `gsk_`
   - No debe contener espacios
   - Debe tener al menos 40 caracteres

2. Genera una nueva API key:
   - Ve a [console.groq.com](https://console.groq.com)
   - Navega a "API Keys"
   - Crea una nueva key
   - Reemplaza la anterior

3. Verifica que no hay espacios extra:
   ```bash
   # Linux/Mac
   export GROQ_API_KEY="$(echo $GROQ_API_KEY | tr -d ' ')"
   ```

### 5. Error: "Timeout de conexión"

**Síntomas:**
```
⚠️ API no disponible, generando mensaje básico...
Error: Connection timeout
```

**Causas posibles:**
- Problemas de conectividad a internet
- Firewall bloqueando la conexión
- Servidor de Groq temporalmente no disponible

**Soluciones:**
1. Verifica tu conexión a internet:
   ```bash
   ping google.com
   ```

2. Verifica que puedes acceder a Groq:
   ```bash
   curl -I https://api.groq.com
   ```

3. Si estás detrás de un firewall corporativo, contacta a tu administrador de sistemas

4. La herramienta automáticamente usará el modo fallback, que sigue funcionando

### 6. Error: "ModuleNotFoundError"

**Síntomas:**
```
ModuleNotFoundError: No module named 'requests'
ModuleNotFoundError: No module named 'colorama'
```

**Causas posibles:**
- Dependencias no instaladas
- Usando el Python incorrecto (múltiples versiones)
- Entorno virtual no activado

**Soluciones:**
1. Instala las dependencias:
   ```bash
   pip install -r .kiro/scripts/requirements.txt
   ```

2. Si usas múltiples versiones de Python:
   ```bash
   python3 -m pip install -r .kiro/scripts/requirements.txt
   ```

3. Si usas un entorno virtual:
   ```bash
   # Activar el entorno virtual primero
   source venv/bin/activate  # Linux/Mac
   # o
   venv\Scripts\activate     # Windows
   
   # Luego instalar
   pip install -r .kiro/scripts/requirements.txt
   ```

### 7. Error: "Permission denied"

**Síntomas (Windows):**
```
cannot be loaded because running scripts is disabled on this system
```

**Solución:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 8. El mensaje generado no es apropiado

**Síntomas:**
- El mensaje no refleja los cambios
- El prefijo de tipo es incorrecto
- El mensaje está en inglés en lugar de español

**Soluciones:**
1. Usa la opción de edición:
   ```
   ¿Usar este mensaje? (y/n/e para editar): e
   ```

2. Verifica que tus cambios staged son claros:
   ```bash
   git diff --staged
   ```

3. Si el problema persiste, reporta el issue con:
   - El diff que causó el problema
   - El mensaje generado
   - El mensaje esperado

### 9. Kiro no reconoce el comando

**Síntomas:**
```
Command not found: commit
```

**Causas posibles:**
- El archivo de hook no está en el lugar correcto
- Kiro no ha recargado la configuración

**Soluciones:**
1. Verifica que existe el archivo de hook:
   ```bash
   ls .kiro/hooks/commit.yml
   ```

2. Verifica el contenido del hook:
   ```bash
   cat .kiro/hooks/commit.yml
   ```

3. Reinicia Kiro o recarga la configuración

4. Verifica que el archivo Python es ejecutable:
   ```bash
   python .kiro/scripts/commit_buddy.py --help
   ```

## 🔧 Herramientas de diagnóstico

### Script de diagnóstico

Crea este script para diagnosticar problemas automáticamente:

```python
#!/usr/bin/env python3
"""Diagnóstico de Kiro Commit Buddy"""

import os
import sys
import subprocess
from pathlib import Path

def check_git():
    try:
        subprocess.run(['git', 'status'], capture_output=True, check=True)
        print("✅ Git repository: OK")
        return True
    except:
        print("❌ Git repository: No encontrado")
        return False

def check_staged_changes():
    try:
        result = subprocess.run(['git', 'diff', '--staged'], capture_output=True, text=True)
        if result.stdout.strip():
            print("✅ Staged changes: OK")
            return True
        else:
            print("⚠️  Staged changes: No hay cambios staged")
            return False
    except:
        print("❌ Staged changes: Error al verificar")
        return False

def check_api_key():
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ GROQ_API_KEY: No configurada")
        return False
    
    if not api_key.startswith('gsk_'):
        print("❌ GROQ_API_KEY: Formato incorrecto (debe empezar con 'gsk_')")
        return False
    
    if len(api_key) < 40:
        print("❌ GROQ_API_KEY: Muy corta")
        return False
    
    print("✅ GROQ_API_KEY: OK")
    return True

def check_dependencies():
    try:
        import requests
        import colorama
        print("✅ Dependencies: OK")
        return True
    except ImportError as e:
        print(f"❌ Dependencies: {e}")
        return False

def check_files():
    files = [
        '.kiro/hooks/commit.yml',
        '.kiro/scripts/commit_buddy.py',
        '.kiro/scripts/requirements.txt'
    ]
    
    all_ok = True
    for file in files:
        if Path(file).exists():
            print(f"✅ {file}: OK")
        else:
            print(f"❌ {file}: No encontrado")
            all_ok = False
    
    return all_ok

if __name__ == "__main__":
    print("🔍 Diagnóstico de Kiro Commit Buddy\n")
    
    checks = [
        check_git(),
        check_staged_changes(),
        check_api_key(),
        check_dependencies(),
        check_files()
    ]
    
    if all(checks):
        print("\n🎉 Todo parece estar configurado correctamente!")
    else:
        print("\n⚠️  Se encontraron algunos problemas. Revisa los errores arriba.")
```

### Logs de debug

Para obtener más información sobre errores, puedes modificar temporalmente el archivo de configuración para habilitar logs detallados.

## 📞 Obtener ayuda adicional

Si ninguna de estas soluciones funciona:

1. **Ejecuta el diagnóstico** usando el script de arriba
2. **Recopila información**:
   - Sistema operativo y versión
   - Versión de Python (`python --version`)
   - Versión de Git (`git --version`)
   - Contenido de `.kiro/hooks/commit.yml`
   - Mensaje de error completo

3. **Busca en issues existentes** en el repositorio del proyecto

4. **Crea un nuevo issue** con toda la información recopilada

## 🔄 Reinstalación completa

Si todo lo demás falla, puedes hacer una reinstalación completa:

```bash
# 1. Respaldar configuración actual
cp .kiro/hooks/commit.yml commit.yml.backup

# 2. Limpiar instalación anterior
rm -rf .kiro/scripts/__pycache__

# 3. Reinstalar dependencias
pip uninstall -y requests colorama
pip install -r .kiro/scripts/requirements.txt

# 4. Verificar instalación
python .kiro/scripts/commit_buddy.py --help

# 5. Restaurar configuración
cp commit.yml.backup .kiro/hooks/commit.yml
```