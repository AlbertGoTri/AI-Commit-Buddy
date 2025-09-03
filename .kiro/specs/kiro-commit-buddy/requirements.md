# Requirements Document

## Introduction

Kiro Commit Buddy es una herramienta de CLI que automatiza la generación de mensajes de commit utilizando inteligencia artificial. La herramienta analiza los cambios en el repositorio Git y genera mensajes de commit claros y concisos siguiendo la convención de Conventional Commits, mejorando la consistencia y calidad de los mensajes de commit en el proyecto.

## Requirements

### Requirement 1

**User Story:** Como desarrollador, quiero ejecutar un comando CLI que genere automáticamente mensajes de commit basados en mis cambios, para que pueda mantener un historial de commits consistente y profesional sin perder tiempo escribiendo mensajes manualmente.

#### Acceptance Criteria

1. WHEN el usuario ejecuta `kiro commit --from-diff` THEN el sistema SHALL obtener el diff actual del repositorio Git
2. WHEN el sistema obtiene el diff THEN el sistema SHALL enviar el contenido a la API de Groq para generar un mensaje de commit
3. WHEN la API genera el mensaje THEN el sistema SHALL mostrar el mensaje al usuario para confirmación o edición
4. WHEN el usuario confirma el mensaje THEN el sistema SHALL permitir ejecutar el commit directamente con ese mensaje

### Requirement 2

**User Story:** Como desarrollador, quiero que los mensajes de commit generados sigan la convención de Conventional Commits, para que el historial del proyecto mantenga un formato estándar y sea fácil de entender.

#### Acceptance Criteria

1. WHEN la API genera un mensaje de commit THEN el mensaje SHALL usar el prefijo "feat:" para nuevas funcionalidades
2. WHEN la API genera un mensaje de commit THEN el mensaje SHALL usar el prefijo "fix:" para correcciones de bugs
3. WHEN la API genera un mensaje de commit THEN el mensaje SHALL usar el prefijo "docs:" para cambios de documentación
4. WHEN la API genera un mensaje de commit THEN el mensaje SHALL usar el prefijo "refactor:" para refactorizaciones
5. WHEN la API genera un mensaje de commit THEN el mensaje SHALL usar el prefijo "test:" para cambios en pruebas
6. WHEN la API genera un mensaje de commit THEN el mensaje SHALL usar el prefijo "chore:" para cambios misceláneos

### Requirement 3

**User Story:** Como desarrollador, quiero que la herramienta funcione incluso cuando no hay conexión a internet o la API falla, para que siempre pueda generar un commit aunque sea con un mensaje básico.

#### Acceptance Criteria

1. WHEN la API de Groq no está disponible THEN el sistema SHALL generar un mensaje de fallback básico
2. WHEN no hay conexión a internet THEN el sistema SHALL usar el formato "update files: [nombres de archivos modificados]"
3. WHEN la API devuelve un error THEN el sistema SHALL informar al usuario y ofrecer el mensaje de fallback
4. WHEN ocurre un error de red THEN el sistema SHALL continuar funcionando con el mecanismo de fallback

### Requirement 4

**User Story:** Como desarrollador, quiero configurar mi API key de Groq de forma segura, para que la herramienta pueda acceder al servicio sin exponer credenciales en el código.

#### Acceptance Criteria

1. WHEN el sistema necesita acceder a la API THEN el sistema SHALL leer la API key desde la variable de entorno `GROQ_API_KEY`
2. WHEN la variable de entorno no está configurada THEN el sistema SHALL mostrar un mensaje de error claro con instrucciones
3. WHEN la API key es inválida THEN el sistema SHALL informar al usuario y usar el mecanismo de fallback
4. IF la API key está configurada THEN el sistema SHALL usar el modelo `llama3-70b-8192` para generar mensajes
5. WHEN la API key está configurada correctamente THEN el sistema SHALL usar la API de Groq en lugar del mensaje genérico de fallback
6. WHEN la API de Groq responde exitosamente THEN el sistema SHALL usar el mensaje generado por IA en lugar de "update <archivos>"

### Requirement 5

**User Story:** Como desarrollador, quiero que la herramienta esté integrada con Kiro como un comando nativo, para que pueda usarla de forma consistente con el resto de herramientas del proyecto.

#### Acceptance Criteria

1. WHEN el usuario instala la herramienta THEN el comando SHALL estar registrado correctamente en `.kiro/hooks/commit.yml`
2. WHEN el usuario ejecuta `kiro commit --from-diff` THEN Kiro SHALL reconocer y ejecutar el comando sin mostrar warnings sobre opciones desconocidas
3. WHEN la herramienta se ejecuta THEN el sistema SHALL funcionar desde cualquier directorio dentro del repositorio Git
4. WHEN el comando se registra THEN el sistema SHALL estar disponible inmediatamente sin reiniciar Kiro
5. WHEN el usuario ejecuta el comando THEN el sistema SHALL NOT crear archivos vacíos llamados "commit"

### Requirement 6

**User Story:** Como desarrollador, quiero documentación clara sobre cómo instalar y usar la herramienta, para que pueda configurarla rápidamente y entender todas sus funcionalidades.

#### Acceptance Criteria

1. WHEN el usuario accede al README THEN el documento SHALL incluir instrucciones de instalación paso a paso
2. WHEN el usuario lee la documentación THEN el documento SHALL explicar cómo configurar `GROQ_API_KEY`
3. WHEN el usuario consulta ejemplos THEN el documento SHALL mostrar casos de uso comunes con `kiro commit --from-diff`
4. WHEN el usuario necesita troubleshooting THEN el documento SHALL incluir soluciones para problemas comunes

### Requirement 7

**User Story:** Como desarrollador, quiero que los bugs reportados en el comando `kiro commit --from-diff` sean corregidos, para que la herramienta funcione correctamente sin generar archivos no deseados o mostrar warnings.

#### Acceptance Criteria

1. WHEN el usuario ejecuta `kiro commit --from-diff` THEN el sistema SHALL NOT mostrar el warning "Warning: 'from-diff' is not in the list of known options"
2. WHEN el usuario ejecuta `kiro commit --from-diff` THEN el sistema SHALL NOT crear un archivo vacío llamado "commit"
3. WHEN la API key de Groq está configurada correctamente THEN el sistema SHALL usar la API para generar mensajes inteligentes
4. WHEN la API de Groq está disponible THEN el sistema SHALL NOT usar siempre el mensaje genérico "update <archivos>"
5. WHEN hay un error en la configuración del comando THEN el sistema SHALL mostrar mensajes de error claros para debugging