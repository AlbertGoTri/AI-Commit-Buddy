# Kiro Commit Buddy

Una herramienta CLI inteligente que automatiza la generación de mensajes de commit utilizando inteligencia artificial. Analiza los cambios en tu repositorio Git y genera mensajes de commit claros y concisos siguiendo la convención de Conventional Commits.

## ✨ Características

- 🤖 **Generación automática de mensajes** usando IA (Groq API)
- 📝 **Formato Conventional Commits** automático (feat, fix, docs, etc.)
- 🔄 **Modo fallback** para funcionamiento offline
- 🎨 **Interfaz colorida** y fácil de usar
- ⚡ **Integración nativa con Kiro**
- 🛡️ **Manejo robusto de errores**

## 🚀 Instalación

### Prerrequisitos

- Python 3.7 o superior
- Git instalado y configurado
- Kiro IDE
- Cuenta en Groq (para funcionalidad IA)

### Pasos de instalación

1. **Clona o descarga el proyecto** en tu workspace de Kiro
2. **Instala las dependencias**:
   ```bash
   pip install -r .kiro/scripts/requirements.txt
   ```
3. **Configura tu API key de Groq** (ver sección de configuración)
4. **¡Listo!** El comando ya está registrado en Kiro

## ⚙️ Configuración

### Configurar GROQ_API_KEY

Para usar la funcionalidad de IA, necesitas configurar tu API key de Groq:

#### Opción 1: Variable de entorno (Recomendado)

**Windows (PowerShell):**
```powershell
$env:GROQ_API_KEY = "tu_api_key_aqui"
# Para hacerlo permanente:
[Environment]::SetEnvironmentVariable("GROQ_API_KEY", "tu_api_key_aqui", "User")
```

**Windows (CMD):**
```cmd
set GROQ_API_KEY=tu_api_key_aqui
# Para hacerlo permanente, usa el Panel de Control > Sistema > Variables de entorno
```

**macOS/Linux:**
```bash
export GROQ_API_KEY="tu_api_key_aqui"
# Para hacerlo permanente, añade la línea anterior a tu ~/.bashrc o ~/.zshrc
```

#### Opción 2: Archivo .env (Alternativo)

Crea un archivo `.env` en la raíz de tu proyecto:
```
GROQ_API_KEY=tu_api_key_aqui
```

### Obtener tu API Key de Groq

1. Ve a [console.groq.com](https://console.groq.com)
2. Crea una cuenta o inicia sesión
3. Navega a "API Keys" en el panel
4. Crea una nueva API key
5. Copia la key y configúrala como se indica arriba

## 📖 Uso

### Comando básico

```bash
kiro commit --from-diff
```

Este comando:
1. Analiza los cambios staged en tu repositorio
2. Genera un mensaje de commit usando IA
3. Te muestra el mensaje propuesto
4. Te permite confirmarlo, editarlo o cancelar
5. Ejecuta el commit automáticamente

### Flujo de trabajo típico

```bash
# 1. Haz tus cambios
git add archivo1.py archivo2.js

# 2. Genera y ejecuta el commit
kiro commit --from-diff
```

### Ejemplo de sesión

```
$ kiro commit --from-diff

🔍 Analizando cambios staged...
🤖 Generando mensaje con IA...

📝 Mensaje propuesto:
feat: add user authentication with JWT tokens

¿Usar este mensaje? (y/n/e para editar): y

✅ Commit creado exitosamente: a1b2c3d
```

## 🎯 Tipos de commit soportados

La herramienta genera automáticamente el prefijo correcto según tus cambios:

- `feat:` - Nuevas funcionalidades
- `fix:` - Corrección de bugs
- `docs:` - Cambios en documentación
- `refactor:` - Refactorización de código
- `test:` - Cambios en pruebas
- `chore:` - Tareas de mantenimiento

## 🔧 Solución de problemas

### Error: "No estás en un repositorio Git"

**Problema:** El comando se ejecuta fuera de un repositorio Git.

**Solución:**
```bash
cd tu-proyecto-git
kiro commit --from-diff
```

### Error: "No hay cambios staged para commit"

**Problema:** No tienes archivos en el área de staging.

**Solución:**
```bash
git add archivo1.py archivo2.js
kiro commit --from-diff
```

### Error: "GROQ_API_KEY no configurada"

**Problema:** La API key no está configurada.

**Solución:**
1. Sigue los pasos de configuración de GROQ_API_KEY
2. Reinicia tu terminal/IDE
3. Verifica con: `echo $GROQ_API_KEY` (Linux/Mac) o `echo $env:GROQ_API_KEY` (Windows PowerShell)

### La IA no está disponible

**Problema:** API de Groq no responde o hay problemas de conexión.

**Comportamiento:** La herramienta automáticamente usa un mensaje de fallback:
```
⚠️  API no disponible, generando mensaje básico...
📝 Mensaje propuesto: chore: update archivo1.py, archivo2.js
```

### Mensaje generado no es apropiado

**Solución:** Usa la opción de edición:
```
¿Usar este mensaje? (y/n/e para editar): e
Edita el mensaje: feat: implement user login system
```

### Problemas de permisos en Windows

**Problema:** Error al ejecutar Python scripts.

**Solución:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Dependencias no instaladas

**Problema:** Error de importación de módulos.

**Solución:**
```bash
pip install -r .kiro/scripts/requirements.txt
```

## 🧪 Testing

Para ejecutar las pruebas:

```bash
# Ejecutar todas las pruebas
python -m pytest .kiro/scripts/test_*.py -v

# Ejecutar pruebas específicas
python -m pytest .kiro/scripts/test_commit_buddy_integration.py -v
```

## 📁 Estructura del proyecto

```
.kiro/
├── hooks/
│   └── commit.yml              # Configuración del comando Kiro
├── scripts/
│   ├── commit_buddy.py         # Punto de entrada principal
│   ├── config.py              # Configuración y variables de entorno
│   ├── git_operations.py      # Operaciones con Git
│   ├── groq_client.py         # Cliente para API de Groq
│   ├── message_generator.py   # Lógica de generación de mensajes
│   ├── user_interface.py      # Interfaz de usuario
│   ├── requirements.txt       # Dependencias Python
│   └── test_*.py             # Archivos de prueba
└── specs/
    └── kiro-commit-buddy/     # Documentación del proyecto
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'feat: add nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si encuentras problemas o tienes preguntas:

1. Revisa la sección de **Solución de problemas**
2. Busca en los issues existentes
3. Crea un nuevo issue con detalles del problema

## 🔄 Changelog

### v1.0.0
- ✅ Generación automática de mensajes con IA
- ✅ Soporte para Conventional Commits
- ✅ Modo fallback offline
- ✅ Integración completa con Kiro
- ✅ Interfaz de usuario interactiva
- ✅ Manejo robusto de errores