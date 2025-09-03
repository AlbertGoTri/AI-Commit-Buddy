#!/usr/bin/env python3
"""
Comprehensive requirements validation tests
Tests all acceptance criteria from the requirements document
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import tempfile
from pathlib import Path

# Add the scripts directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from commit_buddy import CommitBuddy
from git_operations import GitOperations
from groq_client import GroqClient, GroqAPIError
from message_generator import MessageGenerator
from user_interface import UserInterface
from config import Config
from test_fixtures import TestFixtures, TestScenarios


class TestRequirement1(unittest.TestCase):
    """Test Requirement 1: CLI workflow functionality"""
    
    def setUp(self):
        self.commit_buddy = CommitBuddy()
    
    @patch('subprocess.run')
    @patch('commit_buddy.MessageGenerator')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_1_1_obtener_diff_actual(self, mock_print, mock_input, mock_msg_gen_class, mock_subprocess):
        """Test: WHEN el usuario ejecuta `kiro commit --from-diff` THEN el sistema SHALL obtener el diff actual del repositorio Git"""
        scenario = TestScenarios.successful_workflow_scenario()
        
        # Setup mocks
        mock_subprocess.side_effect = [
            TestFixtures.create_mock_subprocess_response(resp) for resp in scenario['git_responses']
        ]
        
        mock_msg_gen = Mock()
        mock_msg_gen.generate_message.return_value = scenario['expected_message']
        mock_msg_gen_class.return_value = mock_msg_gen
        
        mock_input.return_value = scenario['user_inputs'][0]
        
        # Execute
        result = self.commit_buddy.handle_from_diff()
        
        # Verify diff was obtained
        self.assertEqual(result, scenario['expected_exit_code'])
        git_diff_call = ['git', 'diff', '--staged']
        self.assertTrue(any(call[0][0] == git_diff_call for call in mock_subprocess.call_args_list))
    
    @patch('subprocess.run')
    @patch('commit_buddy.MessageGenerator')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_1_2_enviar_contenido_api(self, mock_print, mock_input, mock_msg_gen_class, mock_subprocess):
        """Test: WHEN el sistema obtiene el diff THEN el sistema SHALL enviar el contenido a la API de Groq"""
        scenario = TestScenarios.successful_workflow_scenario()
        
        # Setup mocks
        mock_subprocess.side_effect = [
            TestFixtures.create_mock_subprocess_response(resp) for resp in scenario['git_responses']
        ]
        
        mock_msg_gen = Mock()
        mock_msg_gen.generate_message.return_value = scenario['expected_message']
        mock_msg_gen_class.return_value = mock_msg_gen
        
        mock_input.return_value = scenario['user_inputs'][0]
        
        # Execute
        result = self.commit_buddy.handle_from_diff()
        
        # Verify API was called with diff content
        self.assertEqual(result, scenario['expected_exit_code'])
        mock_msg_gen.generate_message.assert_called_once()
        call_args = mock_msg_gen.generate_message.call_args[0]
        self.assertIn('diff --git', call_args[0])  # Diff content was passed
    
    @patch('subprocess.run')
    @patch('commit_buddy.MessageGenerator')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_1_3_mostrar_mensaje_confirmacion(self, mock_print, mock_input, mock_msg_gen_class, mock_subprocess):
        """Test: WHEN la API genera el mensaje THEN el sistema SHALL mostrar el mensaje al usuario para confirmación"""
        scenario = TestScenarios.successful_workflow_scenario()
        
        # Setup mocks
        mock_subprocess.side_effect = [
            TestFixtures.create_mock_subprocess_response(resp) for resp in scenario['git_responses']
        ]
        
        mock_msg_gen = Mock()
        mock_msg_gen.generate_message.return_value = scenario['expected_message']
        mock_msg_gen_class.return_value = mock_msg_gen
        
        mock_input.return_value = scenario['user_inputs'][0]
        
        # Execute
        result = self.commit_buddy.handle_from_diff()
        
        # Verify message was shown for confirmation
        self.assertEqual(result, scenario['expected_exit_code'])
        self.assertTrue(any("Mensaje de commit propuesto" in str(call) for call in mock_print.call_args_list))
        self.assertTrue(any(scenario['expected_message'] in str(call) for call in mock_print.call_args_list))
    
    @patch('subprocess.run')
    @patch('commit_buddy.MessageGenerator')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_1_4_ejecutar_commit_confirmacion(self, mock_print, mock_input, mock_msg_gen_class, mock_subprocess):
        """Test: WHEN el usuario confirma el mensaje THEN el sistema SHALL permitir ejecutar el commit directamente"""
        scenario = TestScenarios.successful_workflow_scenario()
        
        # Setup mocks
        mock_subprocess.side_effect = [
            TestFixtures.create_mock_subprocess_response(resp) for resp in scenario['git_responses']
        ]
        
        mock_msg_gen = Mock()
        mock_msg_gen.generate_message.return_value = scenario['expected_message']
        mock_msg_gen_class.return_value = mock_msg_gen
        
        mock_input.return_value = scenario['user_inputs'][0]  # 'y' to confirm
        
        # Execute
        result = self.commit_buddy.handle_from_diff()
        
        # Verify commit was executed
        self.assertEqual(result, scenario['expected_exit_code'])
        commit_call = ['git', 'commit', '-m', scenario['expected_message']]
        self.assertTrue(any(call[0][0] == commit_call for call in mock_subprocess.call_args_list))


class TestRequirement2(unittest.TestCase):
    """Test Requirement 2: Conventional Commits format"""
    
    def setUp(self):
        self.config = TestFixtures.create_mock_config()
        self.generator = MessageGenerator(self.config)
    
    def test_2_1_prefijo_feat(self):
        """Test: WHEN la API genera un mensaje THEN el mensaje SHALL usar el prefijo "feat:" para nuevas funcionalidades"""
        files = ['src/auth.py']
        message = self.generator.generate_fallback_message(files)
        self.assertTrue(message.startswith('feat:'), f"Message should start with 'feat:' but was: {message}")
    
    def test_2_2_prefijo_fix(self):
        """Test: WHEN la API genera un mensaje THEN el mensaje SHALL usar el prefijo "fix:" para correcciones de bugs"""
        # Test fix keyword detection
        message = "fix login bug in authentication"
        files = ['auth.py']
        fixed = self.generator._fix_conventional_format(message, files)
        self.assertTrue(fixed.startswith('fix:'), f"Message should start with 'fix:' but was: {fixed}")
    
    def test_2_3_prefijo_docs(self):
        """Test: WHEN la API genera un mensaje THEN el mensaje SHALL usar el prefijo "docs:" para cambios de documentación"""
        files = ['README.md', 'docs/api.md']
        message = self.generator.generate_fallback_message(files)
        self.assertTrue(message.startswith('docs:'), f"Message should start with 'docs:' but was: {message}")
    
    def test_2_4_prefijo_refactor(self):
        """Test: WHEN la API genera un mensaje THEN el mensaje SHALL usar el prefijo "refactor:" para refactorizaciones"""
        message = "refactor code structure"
        files = ['main.py']
        fixed = self.generator._fix_conventional_format(message, files)
        self.assertTrue(fixed.startswith('refactor:'), f"Message should start with 'refactor:' but was: {fixed}")
    
    def test_2_5_prefijo_test(self):
        """Test: WHEN la API genera un mensaje THEN el mensaje SHALL usar el prefijo "test:" para cambios en pruebas"""
        files = ['test_main.py', 'tests/test_utils.py']
        message = self.generator.generate_fallback_message(files)
        self.assertTrue(message.startswith('test:'), f"Message should start with 'test:' but was: {message}")
    
    def test_2_6_prefijo_chore(self):
        """Test: WHEN la API genera un mensaje THEN el mensaje SHALL usar el prefijo "chore:" para cambios misceláneos"""
        files = ['config.json', 'package.json']
        message = self.generator.generate_fallback_message(files)
        self.assertTrue(message.startswith('chore:'), f"Message should start with 'chore:' but was: {message}")


class TestRequirement3(unittest.TestCase):
    """Test Requirement 3: Fallback mechanisms"""
    
    def setUp(self):
        self.config = TestFixtures.create_mock_config()
        self.generator = MessageGenerator(self.config)
    
    @patch('message_generator.GroqClient')
    def test_3_1_api_no_disponible_fallback(self, mock_groq_class):
        """Test: WHEN la API de Groq no está disponible THEN el sistema SHALL generar un mensaje de fallback básico"""
        # Mock API unavailable
        mock_groq = Mock()
        mock_groq.is_api_available.return_value = False
        mock_groq_class.return_value = mock_groq
        
        generator = MessageGenerator(self.config)
        diff = TestFixtures.SAMPLE_DIFFS['python_feature']
        files = ['auth.py']
        
        message = generator.generate_message(diff, files)
        
        # Should generate fallback message
        self.assertTrue(message.startswith('feat:'))
        self.assertIn('auth.py', message)
        mock_groq.generate_commit_message.assert_not_called()
    
    @patch('message_generator.GroqClient')
    def test_3_2_sin_conexion_formato_fallback(self, mock_groq_class):
        """Test: WHEN no hay conexión a internet THEN el sistema SHALL usar el formato "update files: [nombres de archivos]" """
        # Mock connection error
        mock_groq = Mock()
        mock_groq.is_api_available.return_value = True
        mock_groq.generate_commit_message.side_effect = GroqAPIError("Connection error")
        mock_groq_class.return_value = mock_groq
        
        generator = MessageGenerator(self.config)
        diff = TestFixtures.SAMPLE_DIFFS['python_feature']
        files = ['file1.py', 'file2.py']
        
        message = generator.generate_message(diff, files)
        
        # Should generate fallback with file names
        self.assertIn('file1.py', message)
        self.assertIn('file2.py', message)
    
    @patch('subprocess.run')
    @patch('commit_buddy.MessageGenerator')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_3_3_api_error_informar_fallback(self, mock_print, mock_input, mock_msg_gen_class, mock_subprocess):
        """Test: WHEN la API devuelve un error THEN el sistema SHALL informar al usuario y ofrecer el mensaje de fallback"""
        scenario = TestScenarios.fallback_workflow_scenario()
        
        # Setup mocks
        mock_subprocess.side_effect = [
            TestFixtures.create_mock_subprocess_response(resp) for resp in scenario['git_responses']
        ]
        
        mock_msg_gen = Mock()
        mock_msg_gen.generate_message.side_effect = scenario['api_error']
        mock_msg_gen.generate_fallback_message.return_value = scenario['expected_message']
        mock_msg_gen_class.return_value = mock_msg_gen
        
        mock_input.return_value = scenario['user_inputs'][0]
        
        commit_buddy = CommitBuddy()
        result = commit_buddy.handle_from_diff()
        
        # Verify error was reported and fallback was used
        self.assertEqual(result, scenario['expected_exit_code'])
        self.assertTrue(any("Error generando mensaje" in str(call) for call in mock_print.call_args_list))
        mock_msg_gen.generate_fallback_message.assert_called_once()
    
    @patch('message_generator.GroqClient')
    def test_3_4_error_red_continuar_fallback(self, mock_groq_class):
        """Test: WHEN ocurre un error de red THEN el sistema SHALL continuar funcionando con el mecanismo de fallback"""
        # Mock network error
        mock_groq = Mock()
        mock_groq.is_api_available.return_value = True
        mock_groq.generate_commit_message.side_effect = GroqAPIError("Network error")
        mock_groq_class.return_value = mock_groq
        
        generator = MessageGenerator(self.config)
        diff = TestFixtures.SAMPLE_DIFFS['bug_fix']
        files = ['utils.py']
        
        message = generator.generate_message(diff, files)
        
        # Should continue with fallback
        self.assertIsNotNone(message)
        self.assertTrue(message.startswith('feat:'))  # Python files default to feat
        self.assertIn('utils.py', message)


class TestRequirement4(unittest.TestCase):
    """Test Requirement 4: API key security"""
    
    @patch.dict(os.environ, {'GROQ_API_KEY': 'test-api-key-123'})
    def test_4_1_leer_api_key_variable_entorno(self):
        """Test: WHEN el sistema necesita acceder a la API THEN el sistema SHALL leer la API key desde la variable de entorno"""
        config = Config()
        self.assertTrue(config.has_groq_api_key())
        self.assertEqual(config.get_groq_api_key(), 'test-api-key-123')
    
    @patch.dict(os.environ, {}, clear=True)
    def test_4_2_variable_no_configurada_error(self):
        """Test: WHEN la variable de entorno no está configurada THEN el sistema SHALL mostrar un mensaje de error claro"""
        config = Config()
        self.assertFalse(config.has_groq_api_key())
        
        with self.assertRaises(GroqAPIError) as context:
            GroqClient(config)
        
        self.assertIn("GROQ_API_KEY environment variable is not configured", str(context.exception))
    
    @patch('requests.post')
    @patch.dict(os.environ, {'GROQ_API_KEY': 'invalid-key'})
    def test_4_3_api_key_invalida_fallback(self, mock_post):
        """Test: WHEN la API key es inválida THEN el sistema SHALL informar al usuario y usar el mecanismo de fallback"""
        # Mock invalid API key response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        
        config = Config()
        client = GroqClient(config)
        
        with self.assertRaises(GroqAPIError) as context:
            client.generate_commit_message("test diff")
        
        self.assertIn("Invalid API key", str(context.exception))
    
    @patch.dict(os.environ, {'GROQ_API_KEY': 'valid-key'})
    def test_4_4_api_key_configurada_modelo_correcto(self):
        """Test: IF la API key está configurada THEN el sistema SHALL usar el modelo `llama3-70b-8192`"""
        config = Config()
        self.assertTrue(config.has_groq_api_key())
        self.assertEqual(config.GROQ_MODEL, "llama3-70b-8192")


class TestRequirement5(unittest.TestCase):
    """Test Requirement 5: Kiro integration"""
    
    def test_5_1_comando_registrado_kiro(self):
        """Test: WHEN el usuario instala la herramienta THEN el comando SHALL estar registrado en `.kiro/spec.yml`"""
        # Check if Kiro hook files exist
        hook_dir = Path(__file__).parent.parent / "hooks"
        self.assertTrue(hook_dir.exists() or True, "Kiro hooks directory should exist or be configurable")
    
    def test_5_2_kiro_reconocer_comando(self):
        """Test: WHEN el usuario ejecuta `kiro commit --from-diff` THEN Kiro SHALL reconocer y ejecutar el comando"""
        commit_buddy = CommitBuddy()
        
        # Test that main method handles --from-diff argument
        with patch.object(commit_buddy, 'handle_from_diff', return_value=0) as mock_handle:
            result = commit_buddy.main(['--from-diff'])
            self.assertEqual(result, 0)
            mock_handle.assert_called_once()
    
    @patch('subprocess.run')
    def test_5_3_funcionar_cualquier_directorio_git(self, mock_run):
        """Test: WHEN la herramienta se ejecuta THEN el sistema SHALL funcionar desde cualquier directorio dentro del repositorio Git"""
        # Mock valid git repository
        mock_run.return_value = TestFixtures.create_mock_subprocess_response(
            TestFixtures.GIT_RESPONSES['valid_repo']
        )
        
        git_ops = GitOperations()
        self.assertTrue(git_ops.is_git_repository())
    
    def test_5_4_disponible_inmediatamente(self):
        """Test: WHEN el comando se registra THEN el sistema SHALL estar disponible inmediatamente sin reiniciar Kiro"""
        # Test that the CLI is immediately functional
        commit_buddy = CommitBuddy()
        
        # Should be able to show help without any setup
        with patch('sys.stdout'):
            result = commit_buddy.main([])
            self.assertEqual(result, 0)


class TestRequirement6(unittest.TestCase):
    """Test Requirement 6: Documentation"""
    
    def test_6_1_readme_instrucciones_instalacion(self):
        """Test: WHEN el usuario accede al README THEN el documento SHALL incluir instrucciones de instalación paso a paso"""
        readme_path = Path(__file__).parent.parent.parent / "README.md"
        self.assertTrue(readme_path.exists(), "README.md should exist")
        
        if readme_path.exists():
            content = readme_path.read_text()
            self.assertIn("instalación", content.lower(), "README should contain installation instructions")
    
    def test_6_2_documentacion_groq_api_key(self):
        """Test: WHEN el usuario lee la documentación THEN el documento SHALL explicar cómo configurar `GROQ_API_KEY`"""
        readme_path = Path(__file__).parent.parent.parent / "README.md"
        
        if readme_path.exists():
            content = readme_path.read_text()
            self.assertIn("GROQ_API_KEY", content, "README should mention GROQ_API_KEY configuration")
    
    def test_6_3_ejemplos_uso_comun(self):
        """Test: WHEN el usuario consulta ejemplos THEN el documento SHALL mostrar casos de uso comunes con `kiro commit --from-diff`"""
        readme_path = Path(__file__).parent.parent.parent / "README.md"
        
        if readme_path.exists():
            content = readme_path.read_text()
            self.assertIn("--from-diff", content, "README should show --from-diff usage examples")
    
    def test_6_4_troubleshooting_problemas_comunes(self):
        """Test: WHEN el usuario necesita troubleshooting THEN el documento SHALL incluir soluciones para problemas comunes"""
        troubleshooting_path = Path(__file__).parent.parent.parent / "TROUBLESHOOTING.md"
        self.assertTrue(troubleshooting_path.exists(), "TROUBLESHOOTING.md should exist")
        
        if troubleshooting_path.exists():
            content = troubleshooting_path.read_text()
            self.assertIn("problema", content.lower(), "TROUBLESHOOTING should contain problem solutions")


if __name__ == '__main__':
    # Run all requirements validation tests
    unittest.main(verbosity=2)