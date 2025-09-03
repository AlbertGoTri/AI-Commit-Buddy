"""
Git operations module for Kiro Commit Buddy
Handles all Git repository interactions
"""

from typing import List, Optional, Tuple
import subprocess
import os

class GitOperationError(Exception):
    """Custom exception for Git operation errors"""
    pass

class GitOperations:
    """Handles Git repository operations"""

    def __init__(self):
        pass

    def is_git_repository(self) -> bool:
        """Check if current directory is a Git repository"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except FileNotFoundError:
            return False
        except PermissionError:
            return False
        except Exception:
            return False

    def validate_git_environment(self) -> Tuple[bool, str]:
        """
        Validate Git environment and provide detailed error information
        Returns: (is_valid, error_message)
        """
        try:
            # Check if git command is available
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                return False, "Git no está instalado o no está disponible en el PATH"
        except FileNotFoundError:
            return False, "Git no está instalado. Por favor instala Git para continuar."
        except subprocess.TimeoutExpired:
            return False, "Timeout verificando la instalación de Git"
        except Exception as e:
            return False, f"Error verificando Git: {str(e)}"

        try:
            # Check if we're in a Git repository
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                # Try to get more specific error information
                if "not a git repository" in result.stderr.lower():
                    return False, "No estás en un repositorio Git. Ejecuta 'git init' o navega a un repositorio existente."
                else:
                    return False, f"Error de Git: {result.stderr.strip() or 'Repositorio Git inválido'}"
        except subprocess.TimeoutExpired:
            return False, "Timeout verificando el repositorio Git"
        except PermissionError:
            return False, "Sin permisos para acceder al repositorio Git"
        except Exception as e:
            return False, f"Error verificando repositorio Git: {str(e)}"

        try:
            # Check if we can access the working directory
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                return False, f"No se puede acceder al estado del repositorio: {result.stderr.strip()}"
        except subprocess.TimeoutExpired:
            return False, "Timeout verificando el estado del repositorio"
        except Exception as e:
            return False, f"Error verificando estado del repositorio: {str(e)}"

        return True, ""

    def get_staged_diff(self) -> str:
        """Get the diff of staged changes"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--staged'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout
            else:
                raise GitOperationError(f"Error obteniendo diff: {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            raise GitOperationError("Timeout obteniendo diff de cambios staged")
        except FileNotFoundError:
            raise GitOperationError("Git no está disponible")
        except Exception as e:
            raise GitOperationError(f"Error inesperado obteniendo diff: {str(e)}")

    def check_staged_changes(self) -> Tuple[bool, str, List[str]]:
        """
        Check for staged changes and provide detailed information
        Returns: (has_changes, status_message, changed_files)
        """
        try:
            # Get staged files
            result = subprocess.run(
                ['git', 'diff', '--staged', '--name-only'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return False, f"Error verificando cambios staged: {result.stderr.strip()}", []

            staged_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]

            if not staged_files:
                # Check if there are unstaged changes
                unstaged_result = subprocess.run(
                    ['git', 'diff', '--name-only'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if unstaged_result.returncode == 0:
                    unstaged_files = [f.strip() for f in unstaged_result.stdout.split('\n') if f.strip()]
                    if unstaged_files:
                        return False, f"No hay cambios staged. Hay {len(unstaged_files)} archivo(s) modificado(s) sin stage. Usa 'git add' para stagear los cambios.", unstaged_files
                    else:
                        return False, "No hay cambios para commit. El directorio de trabajo está limpio.", []
                else:
                    return False, "No hay cambios staged para commit. Usa 'git add <archivo>' para stagear cambios.", []

            return True, f"Encontrados {len(staged_files)} archivo(s) staged para commit", staged_files

        except subprocess.TimeoutExpired:
            return False, "Timeout verificando cambios staged", []
        except Exception as e:
            return False, f"Error verificando cambios: {str(e)}", []

    def get_changed_files(self) -> List[str]:
        """Get list of changed files"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--staged', '--name-only'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                return [f for f in files if f]  # Filter out empty strings
            return []
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def commit_with_message(self, message: str) -> Tuple[bool, str]:
        """
        Execute git commit with the provided message
        Returns: (success, error_message_or_commit_hash)
        """
        if not message or not message.strip():
            return False, "El mensaje de commit no puede estar vacío"

        try:
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                capture_output=True,
                text=True,
                timeout=15
            )

            if result.returncode == 0:
                # Try to get the commit hash
                try:
                    hash_result = subprocess.run(
                        ['git', 'rev-parse', 'HEAD'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if hash_result.returncode == 0:
                        commit_hash = hash_result.stdout.strip()[:8]  # Short hash
                        return True, commit_hash
                    else:
                        return True, "commit creado exitosamente"
                except:
                    return True, "commit creado exitosamente"
            else:
                # Parse common Git commit errors
                error_msg = result.stderr.strip()
                if "nothing to commit" in error_msg.lower():
                    return False, "No hay cambios staged para commit"
                elif "please tell me who you are" in error_msg.lower():
                    return False, "Configuración de Git incompleta. Ejecuta:\ngit config --global user.email 'tu@email.com'\ngit config --global user.name 'Tu Nombre'"
                elif "pathspec" in error_msg.lower():
                    return False, "Error en los archivos especificados para commit"
                elif "lock" in error_msg.lower():
                    return False, "El repositorio está bloqueado. Intenta de nuevo en unos segundos."
                else:
                    return False, f"Error ejecutando commit: {error_msg}"

        except subprocess.TimeoutExpired:
            return False, "Timeout ejecutando commit. El proceso tomó demasiado tiempo."
        except FileNotFoundError:
            return False, "Git no está disponible"
        except Exception as e:
            return False, f"Error inesperado ejecutando commit: {str(e)}"
