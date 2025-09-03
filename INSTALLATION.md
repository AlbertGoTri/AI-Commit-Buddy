# Guía de Instalación - Kiro Commit Buddy

Esta guía te llevará paso a paso por el proceso de instalación y configuración de Kiro Commit Buddy.

## ❓ Preguntas Frecuentes sobre Instalación

### ¿Necesito crear un repositorio en GitHub?
**No es necesario.** El código ya funciona perfectamente en tu máquina local. Si quieres compartirlo o hacer backup:
- Puedes crear tu propio repositorio: `https://github.com/TU_USUARIO/kiro-commit-buddy.git`
- O simplemente usarlo localmente

### ¿Qué es un workspace de Kiro?
Un **workspace de Kiro** es cualquier directorio que contenga una carpeta `.kiro/`. Es como `.git/` para Git - simplemente marca que ese directorio usa Kiro.

### ¿Solo funciona en proyectos Kiro?
**¡No!** Funciona en **cualquier repositorio Git**, tenga o no Kiro:
- **Con Kiro**: `kiro commit --from-diff` (comando nativo)
- **Sin Kiro**: `python .kiro/scripts/commit_buddy.py --from-diff` (funciona igual)

### ¿Cómo usar en otros proyectos?
Simplemente copia la carpeta `.kiro/` a cualquier otro repositorio Git y ya funcionará allí también.

## 📋 Prerrequisitos

Antes de comenzar, asegúrate de tener instalado:

### Requisitos obligatorios
- **Python 3.7 o superior** ([Descargar Python](https://www.python.org/downloads/))
- **Git** ([Descargar Git](https://git-scm.com/downloads))
- **Kiro IDE** (debe estar instalado y funcionando)

### Requisitos opcionales
- **Cuenta en Groq** para funcionalidad IA ([Registrarse en Groq](https://console.groq.com))

## 🚀 Instalación paso a paso

### Paso 1: Verificar prerrequisitos

Abre tu terminal y verifica que tienes todo instalado:

```bash
# Verificar Python
python --version
# Debe mostrar: Python 3.7.x o superior

# Verificar Git
git --version
# Debe mostrar: git version x.x.x

# Verificar pip
pip --version
# Debe mostrar: pip x.x.x
```

### Paso 2: Preparar el proyecto

1. **Navega a tu workspace de Kiro:**
   ```bash
   cd /ruta/a/tu/workspace
   ```

2. **Verifica que estás en un repositorio Git:**
   ```bash
   git status
   ```
   
   Si no es un repositorio Git, inicialízalo:
   ```bash
   git init
   ```

### Paso 3: Instalar Kiro Commit Buddy

#### Opción A: Ya tienes el código

**¡Si ya tienes estos archivos en tu proyecto, no necesitas hacer nada más!** 
El Kiro Commit Buddy ya está instalado y listo para usar.

```bash
# Verificar que tienes los archivos
ls .kiro/hooks/commit.yml
ls .kiro/scripts/commit_buddy.py

# Instalar dependencias si no lo has hecho
pip install -r .kiro/scripts/requirements.txt
```

#### Opción B: Clonar desde repositorio

Si quieres obtener el código desde un repositorio:

```bash
# Si el repositorio existe (puedes crear el tuyo propio)
git clone https://github.com/TU_USUARIO/kiro-commit-buddy.git
cd kiro-commit-buddy

# Instalar usando setup.py
pip install -e .
```

#### Opción C: Instalación manual

Si tienes los archivos del proyecto:

1. **Crear la estructura de directorios:**
   ```bash
   mkdir -p .kiro/hooks
   mkdir -p .kiro/scripts
   ```

2. **Copiar los archivos del proyecto** a las ubicaciones correctas:
   - Archivos Python → `.kiro/scripts/`
   - Archivo de hook → `.kiro/hooks/commit.yml`

3. **Instalar dependencias:**
   ```bash
   pip install -r .kiro/scripts/requirements.txt
   ```

### Paso 4: Configurar Groq API

#### 4.1 Obtener API Key

1. Ve a [console.groq.com](https://console.groq.com)
2. Crea una cuenta o inicia sesión
3. Navega a "API Keys" en el panel lateral
4. Haz clic en "Create API Key"
5. Dale un nombre a tu key (ej: "Kiro Commit Buddy")
6. Copia la API key generada (empieza con `gsk_`)

#### 4.2 Configurar la API Key

**Windows (PowerShell):**
```powershell
# Configuración temporal (solo para esta sesión)
$env:GROQ_API_KEY = "gsk_tu_api_key_aqui"

# Configuración permanente
[Environment]::SetEnvironmentVariable("GROQ_API_KEY", "gsk_tu_api_key_aqui", "User")

# Verificar configuración
echo $env:GROQ_API_KEY
```

**Windows (CMD):**
```cmd
# Configuración temporal
set GROQ_API_KEY=gsk_tu_api_key_aqui

# Para configuración permanente:
# 1. Panel de Control > Sistema > Configuración avanzada del sistema
# 2. Variables de entorno > Variables de usuario > Nueva
# 3. Nombre: GROQ_API_KEY
# 4. Valor: gsk_tu_api_key_aqui
```

**macOS/Linux:**
```bash
# Configuración temporal
export GROQ_API_KEY="gsk_tu_api_key_aqui"

# Configuración permanente
echo 'export GROQ_API_KEY="gsk_tu_api_key_aqui"' >> ~/.bashrc
source ~/.bashrc

# Para zsh users
echo 'export GROQ_API_KEY="gsk_tu_api_key_aqui"' >> ~/.zshrc
source ~/.zshrc

# Verificar configuración
echo $GROQ_API_KEY
```

### Paso 5: Verificar la instalación

1. **Verificar que los archivos están en su lugar:**
   ```bash
   ls .kiro/hooks/commit.yml
   ls .kiro/scripts/commit_buddy.py
   ls .kiro/scripts/requirements.txt
   ```

2. **Probar el script directamente:**
   ```bash
   python .kiro/scripts/commit_buddy.py --help
   ```
   
   Deberías ver la ayuda del comando.

3. **Probar con Kiro:**
   ```bash
   # Hacer algunos cambios y añadirlos al staging
   echo "test" > test.txt
   git add test.txt
   
   # Probar el comando
   kiro commit --from-diff
   ```

### Paso 6: Configuración avanzada (Opcional)

#### Personalizar configuración

Puedes crear un archivo `.env` en la raíz de tu proyecto para configuraciones adicionales:

```bash
# .env
GROQ_API_KEY=gsk_tu_api_key_aqui
GROQ_MODEL=llama3-70b-8192
MAX_DIFF_SIZE=8000
TIMEOUT=10
```

#### Configurar para múltiples proyectos

Si quieres usar Kiro Commit Buddy en múltiples proyectos:

1. **Instala globalmente:**
   ```bash
   pip install -e . --user
   ```

2. **Copia la configuración a cada proyecto:**
   ```bash
   cp .kiro/hooks/commit.yml /otro/proyecto/.kiro/hooks/
   cp -r .kiro/scripts /otro/proyecto/.kiro/
   ```

## 🔧 Configuraciones específicas por sistema

### Windows con WSL

Si usas Windows Subsystem for Linux:

```bash
# En WSL
export GROQ_API_KEY="gsk_tu_api_key_aqui"

# Para que persista entre sesiones
echo 'export GROQ_API_KEY="gsk_tu_api_key_aqui"' >> ~/.bashrc
```

### macOS con Homebrew

Si instalaste Python con Homebrew:

```bash
# Usar python3 explícitamente
python3 -m pip install -r .kiro/scripts/requirements.txt

# Verificar que usa la versión correcta
which python3
python3 --version
```

### Linux con múltiples versiones de Python

```bash
# Usar una versión específica
python3.9 -m pip install -r .kiro/scripts/requirements.txt

# Crear un alias si es necesario
echo 'alias python=python3.9' >> ~/.bashrc
```

## 🧪 Verificación completa

Ejecuta este script de verificación para asegurarte de que todo está configurado correctamente:

```bash
# Crear script de verificación
cat > verify_installation.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

def verify_installation():
    print("🔍 Verificando instalación de Kiro Commit Buddy...\n")
    
    # Verificar Python
    print(f"✅ Python: {sys.version}")
    
    # Verificar Git
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        print(f"✅ Git: {result.stdout.strip()}")
    except:
        print("❌ Git: No encontrado")
        return False
    
    # Verificar archivos
    files = [
        '.kiro/hooks/commit.yml',
        '.kiro/scripts/commit_buddy.py',
        '.kiro/scripts/requirements.txt'
    ]
    
    for file in files:
        if Path(file).exists():
            print(f"✅ {file}: Existe")
        else:
            print(f"❌ {file}: No encontrado")
            return False
    
    # Verificar dependencias
    try:
        import requests
        import colorama
        print("✅ Dependencias: Instaladas")
    except ImportError as e:
        print(f"❌ Dependencias: {e}")
        return False
    
    # Verificar API key
    api_key = os.getenv('GROQ_API_KEY')
    if api_key and api_key.startswith('gsk_'):
        print("✅ GROQ_API_KEY: Configurada")
    else:
        print("⚠️  GROQ_API_KEY: No configurada (funcionalidad IA limitada)")
    
    # Verificar que el script funciona
    try:
        result = subprocess.run([
            sys.executable, '.kiro/scripts/commit_buddy.py', '--help'
        ], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Script: Funcional")
        else:
            print("❌ Script: Error al ejecutar")
            return False
    except:
        print("❌ Script: No se puede ejecutar")
        return False
    
    print("\n🎉 ¡Instalación completada exitosamente!")
    print("\nPróximos pasos:")
    print("1. Haz algunos cambios en tu código")
    print("2. Añádelos al staging: git add .")
    print("3. Ejecuta: kiro commit --from-diff")
    
    return True

if __name__ == "__main__":
    verify_installation()
EOF

# Ejecutar verificación
python verify_installation.py
```

## 🆘 Solución de problemas de instalación

### Error: "pip no encontrado"

```bash
# Windows
python -m ensurepip --upgrade

# macOS
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py

# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install python3-pip
```

### Error: "Permission denied"

```bash
# Usar --user para instalar solo para tu usuario
pip install --user -r .kiro/scripts/requirements.txt

# O usar un entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
pip install -r .kiro/scripts/requirements.txt
```

### Error: "Command not found: kiro"

1. Verifica que Kiro IDE está instalado y funcionando
2. Reinicia Kiro IDE
3. Verifica que el archivo `.kiro/hooks/commit.yml` existe
4. Prueba ejecutar directamente: `python .kiro/scripts/commit_buddy.py --from-diff`

## 📞 Obtener ayuda

Si encuentras problemas durante la instalación:

1. Revisa la [Guía de Solución de Problemas](TROUBLESHOOTING.md)
2. Ejecuta el script de verificación de arriba
3. Busca en los issues del repositorio
4. Crea un nuevo issue con:
   - Tu sistema operativo
   - Versión de Python
   - Mensaje de error completo
   - Pasos que seguiste

¡Bienvenido a Kiro Commit Buddy! 🎉