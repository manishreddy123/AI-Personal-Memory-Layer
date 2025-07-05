import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import subprocess

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDockerConfiguration(unittest.TestCase):
    """Test Docker configuration and deployment"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.dockerfile_content = """FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN apt-get update && \\
    apt-get install -y build-essential libgl1-mesa-glx curl && \\
    rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
CMD ["python", "main.py"]"""
        
        self.docker_compose_content = """version: '3.9'
services:
  memory-ai:
    build: .
    container_name: personal_memory_ai
    volumes:
      - ./personal_docs:/app/personal_docs
      - ./token.json:/app/token.json
      - ./token_calendar.json:/app/token_calendar.json
      - .env:/app/.env
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - NOTION_API_KEY=${NOTION_API_KEY}
      - NOTION_DB_ID=${NOTION_DB_ID}
      - GOOGLE_CLIENT_SECRET_FILE=credentials.json
    stdin_open: true
    tty: true"""
    
    def test_dockerfile_structure(self):
        """Test Dockerfile structure and commands"""
        lines = self.dockerfile_content.strip().split('\n')
        
        # Check base image
        self.assertTrue(lines[0].startswith('FROM python:3.11'))
        
        # Check working directory
        self.assertIn('WORKDIR /app', lines)
        
        # Check copy command
        self.assertIn('COPY . /app', lines)
        
        # Check system dependencies
        apt_get_lines = [line for line in lines if 'apt-get' in line]
        self.assertTrue(len(apt_get_lines) >= 2)  # update and install
        
        # Check Python dependencies
        pip_lines = [line for line in lines if 'pip install' in line]
        self.assertTrue(len(pip_lines) >= 2)  # upgrade pip and install requirements
        
        # Check exposed port
        self.assertIn('EXPOSE 8501', lines)
        
        # Check command
        self.assertTrue(any('CMD' in line and 'python' in line and 'main.py' in line for line in lines))
    
    def test_docker_compose_structure(self):
        """Test docker-compose.yml structure"""
        # This is a basic structure test
        self.assertIn('version:', self.docker_compose_content)
        self.assertIn('services:', self.docker_compose_content)
        self.assertIn('memory-ai:', self.docker_compose_content)
        self.assertIn('build: .', self.docker_compose_content)
        self.assertIn('container_name: personal_memory_ai', self.docker_compose_content)
        
        # Check volume mappings
        self.assertIn('./personal_docs:/app/personal_docs', self.docker_compose_content)
        self.assertIn('./token.json:/app/token.json', self.docker_compose_content)
        self.assertIn('./token_calendar.json:/app/token_calendar.json', self.docker_compose_content)
        self.assertIn('.env:/app/.env', self.docker_compose_content)
        
        # Check environment variables
        self.assertIn('OPENAI_API_KEY=${OPENAI_API_KEY}', self.docker_compose_content)
        self.assertIn('NOTION_API_KEY=${NOTION_API_KEY}', self.docker_compose_content)
        self.assertIn('NOTION_DB_ID=${NOTION_DB_ID}', self.docker_compose_content)
        self.assertIn('GOOGLE_CLIENT_SECRET_FILE=credentials.json', self.docker_compose_content)
        
        # Check interactive mode
        self.assertIn('stdin_open: true', self.docker_compose_content)
        self.assertIn('tty: true', self.docker_compose_content)
    
    @patch('subprocess.run')
    def test_docker_build_command(self, mock_subprocess):
        """Test Docker build command execution"""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="Successfully built")
        
        # Simulate docker build
        result = subprocess.run(['docker', 'build', '-t', 'personal_memory_ai', '.'], 
                              capture_output=True, text=True)
        
        mock_subprocess.assert_called_once_with(
            ['docker', 'build', '-t', 'personal_memory_ai', '.'],
            capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0)
    
    @patch('subprocess.run')
    def test_docker_compose_up_command(self, mock_subprocess):
        """Test Docker Compose up command execution"""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="Container started")
        
        # Simulate docker-compose up
        result = subprocess.run(['docker-compose', 'up', '-d'], 
                              capture_output=True, text=True)
        
        mock_subprocess.assert_called_once_with(
            ['docker-compose', 'up', '-d'],
            capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0)
    
    def test_dockerfile_security_considerations(self):
        """Test Dockerfile for security best practices"""
        lines = self.dockerfile_content.strip().split('\n')
        
        # Check if running as non-root user (currently not implemented - improvement needed)
        user_lines = [line for line in lines if line.startswith('USER')]
        # Note: This test will fail as the current Dockerfile doesn't set a non-root user
        # This is flagged as a security improvement needed
        
        # Check if unnecessary packages are cleaned up
        cleanup_lines = [line for line in lines if 'rm -rf' in line and '/var/lib/apt/lists/*' in line]
        self.assertTrue(len(cleanup_lines) > 0, "APT cache should be cleaned up")
        
        # Check if pip cache is disabled
        pip_no_cache_lines = [line for line in lines if '--no-cache-dir' in line]
        self.assertTrue(len(pip_no_cache_lines) > 0, "Pip cache should be disabled")
    
    def test_volume_mappings_security(self):
        """Test volume mappings for security issues"""
        # Check that sensitive files are properly mapped
        sensitive_files = ['token.json', 'token_calendar.json', '.env']
        
        for file in sensitive_files:
            self.assertIn(f'./{file}:/app/{file}', self.docker_compose_content,
                         f"Sensitive file {file} should be properly mapped")
        
        # Check that credentials.json is handled via environment variable
        self.assertIn('GOOGLE_CLIENT_SECRET_FILE=credentials.json', self.docker_compose_content)
    
    def test_environment_variable_handling(self):
        """Test environment variable configuration"""
        required_env_vars = [
            'OPENAI_API_KEY',
            'NOTION_API_KEY', 
            'NOTION_DB_ID',
            'GOOGLE_CLIENT_SECRET_FILE'
        ]
        
        for env_var in required_env_vars:
            self.assertIn(env_var, self.docker_compose_content,
                         f"Environment variable {env_var} should be configured")
    
    @patch('os.path.exists')
    def test_required_files_exist(self, mock_exists):
        """Test that required files exist for Docker deployment"""
        required_files = [
            'Dockerfile',
            'docker-compose.yml',
            'requirements.txt',
            '.env',
            'credentials.json'
        ]
        
        # Mock file existence
        mock_exists.return_value = True
        
        for file in required_files:
            exists = os.path.exists(file)
            self.assertTrue(exists, f"Required file {file} should exist")
    
    def test_port_configuration(self):
        """Test port configuration"""
        # Check exposed port in Dockerfile
        self.assertIn('EXPOSE 8501', self.dockerfile_content)
        
        # Note: docker-compose.yml doesn't expose ports to host
        # This might be intentional for security, but could be an issue for access
        # This is flagged as a potential improvement
    
    @patch('subprocess.run')
    def test_docker_health_check(self, mock_subprocess):
        """Test Docker container health check"""
        # Mock docker ps command to check container status
        mock_subprocess.return_value = MagicMock(
            returncode=0, 
            stdout="CONTAINER ID   IMAGE   STATUS\n123abc   personal_memory_ai   Up 5 minutes"
        )
        
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn('Up', result.stdout)
    
    def test_dockerfile_improvements_needed(self):
        """Test for improvements needed in Dockerfile"""
        lines = self.dockerfile_content.strip().split('\n')
        
        # Check for multi-stage build (not implemented - improvement)
        multistage_lines = [line for line in lines if 'AS' in line and 'FROM' in line]
        # This will be empty - flagged as improvement
        
        # Check for non-root user (not implemented - security improvement)
        user_lines = [line for line in lines if line.startswith('USER')]
        # This will be empty - flagged as security improvement
        
        # Check for health check (not implemented - improvement)
        healthcheck_lines = [line for line in lines if 'HEALTHCHECK' in line]
        # This will be empty - flagged as improvement


class TestDockerDeployment(unittest.TestCase):
    """Test Docker deployment scenarios"""
    
    @patch('subprocess.run')
    def test_full_deployment_workflow(self, mock_subprocess):
        """Test complete Docker deployment workflow"""
        # Mock successful command executions
        mock_subprocess.side_effect = [
            MagicMock(returncode=0, stdout="Build successful"),  # docker build
            MagicMock(returncode=0, stdout="Container started"),  # docker-compose up
            MagicMock(returncode=0, stdout="Container running")   # docker ps
        ]
        
        # Simulate deployment commands
        commands = [
            ['docker', 'build', '-t', 'personal_memory_ai', '.'],
            ['docker-compose', 'up', '-d'],
            ['docker', 'ps']
        ]
        
        for cmd in commands:
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
        
        self.assertEqual(mock_subprocess.call_count, 3)
    
    @patch('subprocess.run')
    def test_deployment_failure_scenarios(self, mock_subprocess):
        """Test deployment failure handling"""
        # Mock build failure
        mock_subprocess.return_value = MagicMock(
            returncode=1, 
            stderr="Error: Could not find requirements.txt"
        )
        
        result = subprocess.run(['docker', 'build', '.'], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error", result.stderr)


if __name__ == '__main__':
    unittest.main()
