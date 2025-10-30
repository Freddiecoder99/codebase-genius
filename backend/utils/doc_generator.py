"""
Documentation generation utilities
Converts analyzed code data into structured markdown documentation
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class MarkdownGenerator:
    """Generate markdown documentation from analysis results"""
    
    def __init__(self, repo_name: str, repo_url: str):
        self.repo_name = repo_name
        self.repo_url = repo_url
        self.sections = []
    
    def generate_full_documentation(
        self, 
        file_tree: Dict,
        readme_summary: str,
        ccg_data: Dict,
        local_path: str
    ) -> str:
        """
        Generate complete documentation
        
        Args:
            file_tree: Repository file tree structure
            readme_summary: Summary of README file
            ccg_data: Code Context Graph data
            local_path: Local path to repository
            
        Returns:
            Complete markdown documentation as string
        """
        doc_parts = []
        
        # Title and metadata
        doc_parts.append(self._generate_header())
        
        # Table of contents
        doc_parts.append(self._generate_toc())
        
        # Overview section
        doc_parts.append(self._generate_overview(readme_summary))
        
        # Repository structure
        doc_parts.append(self._generate_structure_section(file_tree))
        
        # Code analysis section
        if ccg_data and ccg_data.get('statistics', {}).get('total_nodes', 0) > 0:
            doc_parts.append(self._generate_code_analysis(ccg_data))
            doc_parts.append(self._generate_api_reference(ccg_data))
            doc_parts.append(self._generate_relationship_diagram(ccg_data))
        else:
            doc_parts.append("\n## 📊 Code Analysis\n\n")
            doc_parts.append("*No code files were analyzed in this repository.*\n")
        
        # Installation and usage (if available)
        doc_parts.append(self._generate_usage_section(local_path))
        
        # Footer
        doc_parts.append(self._generate_footer())
        
        return "\n".join(doc_parts)
    
    def _generate_header(self) -> str:
        """Generate documentation header"""
        return f"""# 📚 {self.repo_name} - Documentation

**Repository:** [{self.repo_url}]({self.repo_url})

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Generator:** Codebase Genius - AI-Powered Documentation System

---
"""
    
    def _generate_toc(self) -> str:
        """Generate table of contents"""
        return """## 📑 Table of Contents

- [Overview](#-overview)
- [Repository Structure](#-repository-structure)
- [Code Analysis](#-code-analysis)
- [API Reference](#-api-reference)
- [Relationship Diagram](#-relationship-diagram)
- [Installation & Usage](#-installation--usage)

---
"""
    
    def _generate_overview(self, readme_summary: str) -> str:
        """Generate overview section"""
        return f"""## 🔍 Overview

{readme_summary if readme_summary else "No description available."}

---
"""
    
    def _generate_structure_section(self, file_tree: Dict) -> str:
        """Generate repository structure section"""
        section = "## 📁 Repository Structure\n\n"
        section += "```\n"
        section += self._format_tree(file_tree, "", True)
        section += "```\n\n"
        section += "---\n"
        return section
    
    def _format_tree(self, node: Dict, prefix: str = "", is_last: bool = True) -> str:
        """Recursively format file tree"""
        if not node:
            return ""
        
        lines = []
        
        # Current node
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{node.get('name', 'unknown')}\n")
        
        # Children
        children = node.get('children', [])
        if children:
            extension = "    " if is_last else "│   "
            new_prefix = prefix + extension
            
            for i, child in enumerate(children[:20]):  # Limit to 20 items
                is_last_child = (i == len(children) - 1)
                lines.append(self._format_tree(child, new_prefix, is_last_child))
            
            if len(children) > 20:
                lines.append(f"{new_prefix}└── ... ({len(children) - 20} more items)\n")
        
        return "".join(lines)
    
    def _generate_code_analysis(self, ccg_data: Dict) -> str:
        """Generate code analysis statistics"""
        stats = ccg_data.get('statistics', {})
        
        section = "## 📊 Code Analysis\n\n"
        section += "### Statistics\n\n"
        section += f"- **Total Code Entities:** {stats.get('total_nodes', 0)}\n"
        section += f"- **Functions:** {stats.get('functions', 0)}\n"
        section += f"- **Classes:** {stats.get('classes', 0)}\n"
        section += f"- **Relationships:** {stats.get('total_edges', 0)}\n"
        section += f"- **Files Analyzed:** {stats.get('files_analyzed', 0)}\n\n"
        
        # File breakdown
        file_map = ccg_data.get('file_map', {})
        if file_map:
            section += "### Files Analyzed\n\n"
            section += "| File | Functions | Classes |\n"
            section += "|------|-----------|----------|\n"
            
            for file_path, entities in list(file_map.items())[:10]:
                file_name = os.path.basename(file_path)
                func_count = len(entities.get('functions', []))
                class_count = len(entities.get('classes', []))
                section += f"| `{file_name}` | {func_count} | {class_count} |\n"
            
            if len(file_map) > 10:
                section += f"\n*... and {len(file_map) - 10} more files*\n"
        
        section += "\n---\n"
        return section
    
    def _generate_api_reference(self, ccg_data: Dict) -> str:
        """Generate API reference from CCG"""
        section = "## 📖 API Reference\n\n"
        
        nodes = ccg_data.get('nodes', [])
        
        # Group by file
        files_dict = {}
        for node in nodes:
            file_path = node.get('file', 'unknown')
            if file_path not in files_dict:
                files_dict[file_path] = {'functions': [], 'classes': []}
            
            if node['type'] == 'function':
                files_dict[file_path]['functions'].append(node)
            elif node['type'] == 'class':
                files_dict[file_path]['classes'].append(node)
        
        # Generate documentation for each file
        for file_path, entities in list(files_dict.items())[:5]:  # Top 5 files
            file_name = os.path.basename(file_path)
            section += f"### 📄 `{file_name}`\n\n"
            
            # Document classes
            for cls in entities['classes'][:3]:  # Top 3 classes per file
                section += f"#### `class {cls['name']}`\n\n"
                
                if cls.get('bases'):
                    section += f"**Inherits from:** {', '.join(cls['bases'])}\n\n"
                
                section += f"**Location:** Lines {cls['line_start']}-{cls['line_end']}\n\n"
                
                if cls.get('methods'):
                    section += "**Methods:**\n"
                    for method in cls['methods'][:5]:
                        section += f"- `{method['name']}()` (line {method['line']})\n"
                    section += "\n"
            
            # Document functions
            for func in entities['functions'][:5]:  # Top 5 functions per file
                params_str = ", ".join(func.get('params', []))
                section += f"#### `{func['name']}({params_str})`\n\n"
                section += f"**Location:** Lines {func['line_start']}-{func['line_end']}\n\n"
                
                if func.get('calls'):
                    section += f"**Calls:** {', '.join(func['calls'][:5])}\n\n"
            
            section += "\n"
        
        if len(files_dict) > 5:
            section += f"*... and {len(files_dict) - 5} more files*\n\n"
        
        section += "---\n"
        return section
    
    def _generate_relationship_diagram(self, ccg_data: Dict) -> str:
        """Generate relationship diagram in Mermaid format"""
        section = "## 🔗 Relationship Diagram\n\n"
        section += "### Function Call Graph\n\n"
        
        edges = ccg_data.get('edges', [])
        nodes = ccg_data.get('nodes', [])
        
        if not edges or not nodes:
            section += "*No relationships found to diagram.*\n\n"
            return section
        
        section += "```mermaid\ngraph TD\n"
        
        # Add nodes (limit to prevent overcrowding)
        node_dict = {}
        for i, node in enumerate(nodes[:15]):  # Limit to 15 nodes
            node_id = f"N{i}"
            node_dict[node['id']] = node_id
            section += f"    {node_id}[\"{node['name']}\"]\n"
        
        # Add edges
        edge_count = 0
        for edge in edges:
            if edge['from'] in node_dict and edge_count < 20:  # Limit edges
                from_id = node_dict[edge['from']]
                to_name = edge['to'].split('.')[-1]  # Get simple name
                
                # Create node for 'to' if it doesn't exist
                to_id = None
                for nid, full_id in node_dict.items():
                    if to_name in nid:
                        to_id = full_id
                        break
                
                if to_id:
                    edge_type = "inherits" if edge['type'] == 'inherits' else "calls"
                    arrow = "-.->|inherits|" if edge['type'] == 'inherits' else "-->|calls|"
                    section += f"    {from_id} {arrow} {to_id}\n"
                    edge_count += 1
        
        section += "```\n\n"
        
        if len(edges) > 20:
            section += f"*Showing 20 of {len(edges)} relationships*\n\n"
        
        section += "---\n"
        return section
    
    def _generate_usage_section(self, local_path: str) -> str:
        """Generate installation and usage section"""
        section = "## 🚀 Installation & Usage\n\n"
        
        # Check for requirements.txt
        req_path = os.path.join(local_path, 'requirements.txt')
        if os.path.exists(req_path):
            section += "### Installation\n\n"
            section += "```bash\n"
            section += "# Clone the repository\n"
            section += f"git clone {self.repo_url}\n\n"
            section += "# Install dependencies\n"
            section += "pip install -r requirements.txt\n"
            section += "```\n\n"
        
        # Check for main entry points
        entry_points = ['main.py', 'app.py', '__main__.py']
        for entry in entry_points:
            entry_path = os.path.join(local_path, entry)
            if os.path.exists(entry_path):
                section += "### Usage\n\n"
                section += "```bash\n"
                section += f"python {entry}\n"
                section += "```\n\n"
                break
        
        if "Installation" not in section and "Usage" not in section:
            section += "*Installation and usage instructions not available.*\n\n"
        
        section += "---\n"
        return section
    
    def _generate_footer(self) -> str:
        """Generate documentation footer"""
        return """## 🤖 About This Documentation

This documentation was automatically generated by **Codebase Genius**, an AI-powered multi-agent system for code analysis and documentation.

**Features:**
- 🔍 Automatic repository analysis
- ��️ Code structure mapping
- 🧬 Relationship graph generation
- 📄 Comprehensive API documentation

---

*Generated with ❤️ by Codebase Genius*
"""


class DocumentationSaver:
    """Save generated documentation to files"""
    
    def __init__(self, output_base_path: str = "./outputs"):
        self.output_base_path = Path(output_base_path)
        self.output_base_path.mkdir(exist_ok=True)
    
    def save_documentation(self, repo_name: str, markdown_content: str) -> str:
        """
        Save documentation to file
        
        Returns:
            Path to saved documentation
        """
        # Create repository-specific output directory
        repo_dir = self.output_base_path / repo_name
        repo_dir.mkdir(exist_ok=True)
        
        # Save main documentation
        doc_path = repo_dir / "DOCUMENTATION.md"
        
        try:
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"✓ Documentation saved to: {doc_path}")
            return str(doc_path)
            
        except Exception as e:
            print(f"Error saving documentation: {e}")
            return ""
    
    def save_ccg_json(self, repo_name: str, ccg_data: Dict) -> str:
        """Save CCG as JSON for further analysis"""
        import json
        
        repo_dir = self.output_base_path / repo_name
        repo_dir.mkdir(exist_ok=True)
        
        ccg_path = repo_dir / "code_context_graph.json"
        
        try:
            with open(ccg_path, 'w', encoding='utf-8') as f:
                json.dump(ccg_data, f, indent=2)
            
            print(f"✓ CCG data saved to: {ccg_path}")
            return str(ccg_path)
            
        except Exception as e:
            print(f"Error saving CCG: {e}")
            return ""
