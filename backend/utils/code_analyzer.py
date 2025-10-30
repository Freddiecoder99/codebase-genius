"""
Code analysis utilities using Tree-sitter for parsing
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set
from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript

class CodeParser:
    """Parse source code files using Tree-sitter"""
    
    def __init__(self):
        """Initialize parsers for different languages"""
        self.parsers = {}
        self.languages = {}
        
        try:
            self.languages['python'] = Language(tspython.language())
            self.parsers['python'] = Parser(self.languages['python'])
            print("✓ Python parser initialized")
        except Exception as e:
            print(f"⚠ Python parser initialization failed: {e}")
        
        try:
            self.languages['javascript'] = Language(tsjavascript.language())
            self.parsers['javascript'] = Parser(self.languages['javascript'])
            print("✓ JavaScript parser initialized")
        except Exception as e:
            print(f"⚠ JavaScript parser initialization failed: {e}")
    
    def detect_language(self, file_path: str) -> Optional[str]:
        """Detect programming language from file extension"""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'javascript',  # TypeScript uses JS parser
            '.jsx': 'javascript',
            '.jac': 'python',  # Jac is Python-like
        }
        
        ext = Path(file_path).suffix.lower()
        return ext_map.get(ext)
    
    def parse_file(self, file_path: str) -> Optional[Dict]:
        """
        Parse a source code file
        
        Returns:
            Dict with parsed information or None if failed
        """
        language = self.detect_language(file_path)
        
        if not language or language not in self.parsers:
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            parser = self.parsers[language]
            tree = parser.parse(bytes(code, 'utf8'))
            
            return {
                'file_path': file_path,
                'language': language,
                'tree': tree,
                'code': code,
                'root_node': tree.root_node
            }
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None


class PythonAnalyzer:
    """Extract information from Python code"""
    
    def __init__(self):
        self.functions = []
        self.classes = []
        self.imports = []
    
    def analyze(self, parsed_data: Dict) -> Dict:
        """
        Analyze parsed Python code
        
        Returns:
            Dict with extracted functions, classes, imports
        """
        if not parsed_data or parsed_data['language'] != 'python':
            return {}
        
        root_node = parsed_data['root_node']
        code = parsed_data['code']
        
        self.functions = []
        self.classes = []
        self.imports = []
        
        self._traverse_node(root_node, code)
        
        return {
            'functions': self.functions,
            'classes': self.classes,
            'imports': self.imports,
            'file_path': parsed_data['file_path']
        }
    
    def _traverse_node(self, node, code: str):
        """Recursively traverse syntax tree nodes"""
        
        if node.type == 'function_definition':
            self._extract_function(node, code)
        
        elif node.type == 'class_definition':
            self._extract_class(node, code)
        
        elif node.type == 'import_statement' or node.type == 'import_from_statement':
            self._extract_import(node, code)
        
        for child in node.children:
            self._traverse_node(child, code)
    
    def _extract_function(self, node, code: str):
        """Extract function information"""
        func_info = {
            'type': 'function',
            'name': '',
            'params': [],
            'line_start': node.start_point[0] + 1,
            'line_end': node.end_point[0] + 1,
            'calls': []
        }
        
        for child in node.children:
            if child.type == 'identifier':
                func_info['name'] = code[child.start_byte:child.end_byte]
                break
        
        for child in node.children:
            if child.type == 'parameters':
                func_info['params'] = self._extract_params(child, code)
                break
        
        func_info['calls'] = self._find_function_calls(node, code)
        
        self.functions.append(func_info)
    
    def _extract_class(self, node, code: str):
        """Extract class information"""
        class_info = {
            'type': 'class',
            'name': '',
            'methods': [],
            'bases': [],
            'line_start': node.start_point[0] + 1,
            'line_end': node.end_point[0] + 1
        }
        
        for child in node.children:
            if child.type == 'identifier':
                class_info['name'] = code[child.start_byte:child.end_byte]
                break
        
        for child in node.children:
            if child.type == 'argument_list':
                class_info['bases'] = self._extract_bases(child, code)
                break
        
        class_info['methods'] = self._extract_methods(node, code)
        
        self.classes.append(class_info)
    
    def _extract_import(self, node, code: str):
        """Extract import information"""
        import_text = code[node.start_byte:node.end_byte]
        self.imports.append({
            'type': 'import',
            'statement': import_text,
            'line': node.start_point[0] + 1
        })
    
    def _extract_params(self, params_node, code: str) -> List[str]:
        """Extract function parameters"""
        params = []
        for child in params_node.children:
            if child.type == 'identifier':
                params.append(code[child.start_byte:child.end_byte])
        return params
    
    def _extract_bases(self, arg_list_node, code: str) -> List[str]:
        """Extract base classes"""
        bases = []
        for child in arg_list_node.children:
            if child.type == 'identifier':
                bases.append(code[child.start_byte:child.end_byte])
        return bases
    
    def _extract_methods(self, class_node, code: str) -> List[Dict]:
        """Extract methods from a class"""
        methods = []
        
        for child in class_node.children:
            if child.type == 'block':
                for stmt in child.children:
                    if stmt.type == 'function_definition':
                        method_name = ''
                        for node in stmt.children:
                            if node.type == 'identifier':
                                method_name = code[node.start_byte:node.end_byte]
                                break
                        
                        methods.append({
                            'name': method_name,
                            'line': stmt.start_point[0] + 1
                        })
        
        return methods
    
    def _find_function_calls(self, node, code: str) -> List[str]:
        """Find function calls within a node"""
        calls = []
        
        def traverse(n):
            if n.type == 'call':
                for child in n.children:
                    if child.type == 'identifier' or child.type == 'attribute':
                        call_name = code[child.start_byte:child.end_byte]
                        calls.append(call_name)
                        break
            
            for child in n.children:
                traverse(child)
        
        traverse(node)
        return calls


class CodeContextGraph:
    """Build and manage Code Context Graph (CCG)"""
    
    def __init__(self):
        self.nodes = []  # All code entities (functions, classes)
        self.edges = []  # Relationships (calls, inheritance, etc.)
        self.file_map = {}  # Map files to their entities
    
    def add_file_analysis(self, analysis: Dict):
        """Add analysis results for a file to the CCG"""
        file_path = analysis.get('file_path', 'unknown')
       
        for func in analysis.get('functions', []):
            node_id = f"{file_path}::{func['name']}"
            node = {
                'id': node_id,
                'type': 'function',
                'name': func['name'],
                'file': file_path,
                'line_start': func['line_start'],
                'line_end': func['line_end'],
                'params': func['params'],
                'calls': func['calls']
            }
            self.nodes.append(node)
           
            for call in func['calls']:
                edge = {
                    'from': node_id,
                    'to': call,
                    'type': 'calls',
                    'file': file_path
                }
                self.edges.append(edge)
        
        for cls in analysis.get('classes', []):
            node_id = f"{file_path}::{cls['name']}"
            node = {
                'id': node_id,
                'type': 'class',
                'name': cls['name'],
                'file': file_path,
                'line_start': cls['line_start'],
                'line_end': cls['line_end'],
                'methods': cls['methods'],
                'bases': cls['bases']
            }
            self.nodes.append(node)
            
            for base in cls['bases']:
                edge = {
                    'from': node_id,
                    'to': base,
                    'type': 'inherits',
                    'file': file_path
                }
                self.edges.append(edge)
        
        self.file_map[file_path] = {
            'functions': [f['name'] for f in analysis.get('functions', [])],
            'classes': [c['name'] for c in analysis.get('classes', [])]
        }
    
    def get_statistics(self) -> Dict:
        """Get CCG statistics"""
        return {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'functions': len([n for n in self.nodes if n['type'] == 'function']),
            'classes': len([n for n in self.nodes if n['type'] == 'class']),
            'files_analyzed': len(self.file_map)
        }
    
    def find_callers(self, function_name: str) -> List[str]:
        """Find all functions that call a specific function"""
        callers = []
        for edge in self.edges:
            if edge['type'] == 'calls' and edge['to'] == function_name:
                callers.append(edge['from'])
        return callers
    
    def find_callees(self, function_name: str) -> List[str]:
        """Find all functions called by a specific function"""
        callees = []
        for node in self.nodes:
            if node.get('name') == function_name:
                callees = node.get('calls', [])
                break
        return callees
    
    def export_to_dict(self) -> Dict:
        """Export CCG as dictionary"""
        return {
            'nodes': self.nodes,
            'edges': self.edges,
            'file_map': self.file_map,
            'statistics': self.get_statistics()
        }


class FileSelector:
    """Select important files to analyze"""
    
    @staticmethod
    def get_code_files(root_path: str, max_files: int = 50) -> List[str]:
        """
        Get list of source code files to analyze
        
        Prioritizes: entry points, then important modules
        """
        root_path = Path(root_path)
        code_files = []
        
        priority_patterns = [
            'main.py', 'app.py', '__main__.py', '__init__.py',
            'main.jac', 'server.py', 'run.py', 'start.py'
        ]
        
        code_extensions = {'.py', '.jac', '.js', '.ts'}
        
        skip_dirs = {
            '.git', '__pycache__', 'node_modules', 'venv', 
            'env', '.venv', 'dist', 'build', 'tests', 'test'
        }
        
        # First pass: Find priority files
        priority_files = []
        for pattern in priority_patterns:
            for file in root_path.rglob(pattern):
                if not any(skip in file.parts for skip in skip_dirs):
                    priority_files.append(str(file))
        
        code_files.extend(priority_files[:10])  # Max 10 priority files
        
        # Second pass: Find other code files
        if len(code_files) < max_files:
            for ext in code_extensions:
                for file in root_path.rglob(f'*{ext}'):
                    if str(file) not in code_files:
                        if not any(skip in file.parts for skip in skip_dirs):
                            code_files.append(str(file))
                            if len(code_files) >= max_files:
                                break
                if len(code_files) >= max_files:
                    break
        
        return code_files[:max_files]
