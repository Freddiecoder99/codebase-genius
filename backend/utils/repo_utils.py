"""
Repository utilities for cloning and analyzing Git repositories
"""

import os
import shutil
from pathlib import Path
from git import Repo, GitCommandError
from typing import Dict, List, Optional

class RepoCloner:
    """Handles cloning and managing repositories"""
    
    def __init__(self, base_path: str = "./temp_repos"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
    
    def clone_repository(self, repo_url: str) -> Optional[str]:
        """
        Clone a repository from GitHub
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Local path to cloned repository, or None if failed
        """
        try:
            # Extract repo name from URL
            repo_name = repo_url.rstrip('/').split('/')[-1]
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]
            
            # Create local path
            local_path = self.base_path / repo_name
            
            # Remove if already exists
            if local_path.exists():
                shutil.rmtree(local_path)
            
            # Clone the repository
            print(f"Cloning {repo_url}...")
            Repo.clone_from(repo_url, local_path, depth=1)
            print(f"Successfully cloned to {local_path}")
            
            return str(local_path)
            
        except GitCommandError as e:
            print(f"Error cloning repository: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    def cleanup(self, local_path: str):
        """Remove cloned repository"""
        try:
            if os.path.exists(local_path):
                shutil.rmtree(local_path)
                print(f"Cleaned up {local_path}")
        except Exception as e:
            print(f"Error during cleanup: {e}")


class FileTreeGenerator:
    """Generates file tree representations of repositories"""
    
    # Directories to ignore
    IGNORE_DIRS = {
        '.git', '__pycache__', 'node_modules', 'venv', 'env',
        '.venv', '.env', 'dist', 'build', '.idea', '.vscode',
        'coverage', '.pytest_cache', '.mypy_cache', 'target'
    }
    
    # File extensions to prioritize
    PRIORITY_EXTENSIONS = {
        '.py', '.jac', '.js', '.ts', '.java', '.cpp', '.c', '.rs'
    }
    
    def generate_tree(self, root_path: str, max_depth: int = 5) -> Dict:
        """
        Generate a hierarchical file tree
        
        Args:
            root_path: Root directory path
            max_depth: Maximum depth to traverse
            
        Returns:
            Dictionary representing file tree structure
        """
        root_path = Path(root_path)
        
        if not root_path.exists():
            return {}
        
        tree = {
            'name': root_path.name,
            'type': 'directory',
            'path': str(root_path),
            'children': []
        }
        
        self._build_tree(root_path, tree, 0, max_depth)
        return tree
    
    def _build_tree(self, path: Path, node: Dict, depth: int, max_depth: int):
        """Recursively build file tree"""
        if depth >= max_depth:
            return
        
        try:
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
            
            for item in items:
                # Skip ignored directories
                if item.is_dir() and item.name in self.IGNORE_DIRS:
                    continue
                
                # Skip hidden files (except important ones)
                if item.name.startswith('.') and item.name not in {'.env.example', '.gitignore'}:
                    continue
                
                child = {
                    'name': item.name,
                    'type': 'directory' if item.is_dir() else 'file',
                    'path': str(item),
                    'extension': item.suffix if item.is_file() else None
                }
                
                if item.is_dir():
                    child['children'] = []
                    self._build_tree(item, child, depth + 1, max_depth)
                
                node['children'].append(child)
                
        except PermissionError:
            pass
    
    def get_important_files(self, tree: Dict) -> List[str]:
        """Extract paths to important files (entry points, configs)"""
        important_patterns = {
            'main.py', 'app.py', '__main__.py', 'setup.py',
            'main.jac', 'README.md', 'requirements.txt',
            'package.json', 'Cargo.toml', 'pom.xml'
        }
        
        important_files = []
        self._find_files(tree, important_patterns, important_files)
        return important_files
    
    def _find_files(self, node: Dict, patterns: set, result: List):
        """Recursively find files matching patterns"""
        if node['type'] == 'file' and node['name'] in patterns:
            result.append(node['path'])
        
        if 'children' in node:
            for child in node['children']:
                self._find_files(child, patterns, result)


class ReadmeAnalyzer:
    """Analyzes README files"""
    
    def find_readme(self, root_path: str) -> Optional[str]:
        """Find README file in repository"""
        root_path = Path(root_path)
        
        readme_patterns = ['README.md', 'README.MD', 'readme.md', 'README', 'README.txt']
        
        for pattern in readme_patterns:
            readme_path = root_path / pattern
            if readme_path.exists():
                return str(readme_path)
        
        return None
    
    def read_readme(self, readme_path: str) -> str:
        """Read README content"""
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            print(f"Error reading README: {e}")
            return ""
    
    def extract_summary(self, content: str, max_length: int = 500) -> str:
        """Extract a summary from README"""
        if not content:
            return "No README found"
        
        # Take first few lines or first paragraph
        lines = content.split('\n')
        summary_lines = []
        char_count = 0
        
        for line in lines:
            # Skip title lines
            if line.startswith('#'):
                continue
            
            # Skip empty lines at start
            if not line.strip() and not summary_lines:
                continue
            
            summary_lines.append(line)
            char_count += len(line)
            
            if char_count >= max_length:
                break
        
        summary = '\n'.join(summary_lines[:10])  # Max 10 lines
        
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        
        return summary.strip()
