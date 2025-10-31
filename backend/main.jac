"""
Codebase Genius - Main Entry Point
Multi-agent system for automatic code documentation generation
"""
import os;
import json;
import from dotenv { load_dotenv }

# ==================== NODE DEFINITIONS ====================

node Repository {
    has url: str;
    has name: str;
    has local_path: str = "";
    has file_tree: dict = {};
    has readme_summary: str = "";
    has analyzed: bool = False;
    has code_context_graph: dict = {};
    has documentation_path: str = "";
    has documentation_content: str = "";
}

node CodeFile {
    has path: str;
    has language: str;
    has content: str = "";
    has functions: list = [];
    has classes: list = [];
    has imports: list = [];
}

node Documentation {
    has content: str = "";
    has sections: list = [];
    has diagrams: list = [];
    has completed: bool = False;
}

# ==================== WALKER DEFINITIONS ====================

walker CodeGenius {
    """
    Supervisor walker that orchestrates the entire documentation pipeline
    """
    has repo_url: str;
    has output_path: str = "./outputs";
    
    can start with entry {
        print("=" * 50);
        print("CodeGenius Supervisor Started!");
        print("=" * 50);
        print(f"Repository URL: {self.repo_url}");
        print(f"Output path: {self.output_path}");
        
        # Extract repo name from URL
        import from pathlib { Path }
        repo_name = self.repo_url.rstrip('/').split('/')[-1];
        if repo_name.endswith('.git') {
            repo_name = repo_name[:-4];
        }
        print(f"Repository name: {repo_name}");
        
        # Step 1: Spawn RepoMapper to analyze the repository
        print("\n📍 Step 1: Mapping repository structure...");
        here spawn RepoMapper(repo_url=self.repo_url);
        
        # Step 2: Spawn CodeAnalyzer to build CCG
        print("\n📍 Step 2: Analyzing code and building CCG...");
        if here.local_path {
            here spawn CodeAnalyzer(
                local_path=here.local_path,
                max_files=30
            );
        } else {
            print("⚠ Skipping code analysis - no local path available");
        }
        
        # Step 3: Spawn DocGenie to generate documentation
        print("\n📍 Step 3: Generating documentation...");
        here spawn DocGenie(
            repo_name=repo_name,
            repo_url=self.repo_url,
            output_path=self.output_path
        );
        
        print("\n" + "=" * 50);
        print("🎉 CodeGenius Workflow Complete!");
        print("=" * 50);

        # Print final summary
        if here.documentation_path {
            print(f"\n✅ Documentation generated successfully!");
            print(f"📁 Output location: {here.documentation_path}");
            print(f"\n💡 View your documentation:");
            print(f"   cat {here.documentation_path}");
        }
    }
}

walker RepoMapper {
    """
    Agent responsible for repository exploration and mapping
    """
    has repo_url: str;
    
    can map_repository with entry {
        print("\n" + "=" * 50);
        print("RepoMapper Agent Started");
        print("=" * 50);
        print(f"Target Repository: {self.repo_url}");
        
        # Import Python utilities
        import from utils.repo_utils {
            RepoCloner,
            FileTreeGenerator,
            ReadmeAnalyzer
        }

        # Initialize tools
        cloner = RepoCloner();
        tree_gen = FileTreeGenerator();
        readme_analyzer = ReadmeAnalyzer();
        
        # Step 1: Clone repository
        print("\n[1/4] Cloning repository...");
        local_path = cloner.clone_repository(self.repo_url);
        
        if not local_path {
            print("ERROR: Failed to clone repository!");
            return;
        }
        
        print(f"✓ Repository cloned to: {local_path}");
        here.local_path = local_path;
        
        # Step 2: Generate file tree
        print("\n[2/4] Generating file tree...");
        file_tree = tree_gen.generate_tree(local_path);
        here.file_tree = file_tree;
        
        print(f"✓ File tree generated with {len(file_tree.get('children', []))} top-level items");
        
        # Step 3: Find important files
        print("\n[3/4] Identifying important files...");
        important_files = tree_gen.get_important_files(file_tree);
        print(f"✓ Found {len(important_files)} important files:");
        
        i = 0;
        for file in important_files {
            if i >= 5 {
                break;
            }
            print(f"  - {os.path.basename(file)}");
            i += 1;
        }
        
        if len(important_files) > 5 {
            print(f"  ... and {len(important_files) - 5} more");
        }
        
        # Step 4: Analyze README
        print("\n[4/4] Analyzing README...");
        readme_path = readme_analyzer.find_readme(local_path);
        
        if readme_path {
            readme_content = readme_analyzer.read_readme(readme_path);
            readme_summary = readme_analyzer.extract_summary(readme_content);
            here.readme_summary = readme_summary;
            print("✓ README found and summarized");
            print("\nREADME Summary:");
            print("-" * 50);
            
            print(readme_summary[:300] + "..." if len(readme_summary) > 300 else readme_summary);
            
            print("-" * 50);
        } else {
            print("⚠ No README file found");
            here.readme_summary = "No README available";
        }

        here.analyzed = True;
        
        print("\n" + "=" * 50);
        print("RepoMapper Complete!");
        print("=" * 50);
    }
}

walker CodeAnalyzer {
    """
    Agent responsible for deep code analysis and CCG construction
    """
    has local_path: str;
    has max_files: int = 30;
    
    can analyze_code with entry {
        print("\n" + "=" * 50);
        print("CodeAnalyzer Agent Started");
        print("=" * 50);
        print(f"Analyzing repository at: {self.local_path}");
        
        # Import analysis utilities
        import from utils.code_analyzer {
            CodeParser,
            PythonAnalyzer,
            CodeContextGraph,
            FileSelector
        }
        
        import from pathlib { Path }
        
        # Step 1: Select files to analyze
        print(f"\n[1/4] Selecting files to analyze (max: {self.max_files})...");
        files_to_analyze = FileSelector.get_code_files(self.local_path, self.max_files);
        print(f"✓ Selected {len(files_to_analyze)} files");
        
        # Show some files
        print("\nFiles to analyze:");
        i = 0;
        for file in files_to_analyze {
            if i >= 5 {
                break;
            }
            print(f"  {i+1}. {Path(file).name}");
            i += 1;
        }
        
        if len(files_to_analyze) > 5 {
            print(f"  ... and {len(files_to_analyze) - 5} more");
        }
        
        # Step 2: Initialize parser and analyzer
        print("\n[2/4] Initializing code parser...");
        parser = CodeParser();
        py_analyzer = PythonAnalyzer();
        ccg = CodeContextGraph();
        
        # Step 3: Parse and analyze files
        print("\n[3/4] Parsing and analyzing files...");
        analyzed_count = 0;
        
        for file_path in files_to_analyze {
            # Parse the file
            parsed = parser.parse_file(file_path);
            
            if parsed and parsed['language'] == 'python' {
                # Analyze Python code
                analysis = py_analyzer.analyze(parsed);
                
                if analysis {
                    ccg.add_file_analysis(analysis);
                    analyzed_count += 1;
                }
            }
        }
        
        print(f"✓ Successfully analyzed {analyzed_count} files");
        
        # Step 4: Build and store CCG
        print("\n[4/4] Building Code Context Graph...");
        ccg_data = ccg.export_to_dict();
        stats = ccg.get_statistics();
        
        print(f"✓ CCG constructed with:");
        print(f"  - {stats['total_nodes']} nodes");
        print(f"  - {stats['total_edges']} edges");
        print(f"  - {stats['functions']} functions");
        print(f"  - {stats['classes']} classes");
        
        # Store CCG in the node
        here.code_context_graph = ccg_data;
        
        # Show sample of what was found
        if stats['functions'] > 0 {
            print("\nSample functions found:");
            i = 0;
            for node in ccg_data['nodes'] {
                if i >= 5 {
                    break;
                }
                if node['type'] == 'function' {
                    print(f"  - {node['name']}() in {os.path.basename(node['file'])}");
                    i += 1;
                }
            }
        }
        
        print("\n" + "=" * 50);
        print("CodeAnalyzer Complete!");
        print("=" * 50);
    }
}

walker DocGenie {
    """
    Agent responsible for documentation synthesis
    """
    has repo_name: str;
    has repo_url: str;
    has output_path: str = "./outputs";
    
    can generate_docs with entry {
        print("\n" + "=" * 50);
        print("DocGenie Agent Started");
        print("=" * 50);
        print(f"Generating documentation for: {self.repo_name}");
        
        # Import documentation utilities
        import from utils.doc_generator {
            MarkdownGenerator,
            DocumentationSaver
        }
        
        # Get data from the repository node
        file_tree = here.file_tree if here.file_tree else {};
        readme_summary = here.readme_summary if here.readme_summary else "";
        ccg_data = here.code_context_graph if here.code_context_graph else {};
        local_path = here.local_path if here.local_path else "";
        
        # Step 1: Initialize markdown generator
        print("\n[1/3] Initializing markdown generator...");
        md_gen = MarkdownGenerator(self.repo_name, self.repo_url);
        print("✓ Markdown generator ready");
        
        # Step 2: Generate documentation
        print("\n[2/3] Generating comprehensive documentation...");
        print("  - Creating header and overview");
        print("  - Formatting repository structure");
        print("  - Building API reference");
        print("  - Generating relationship diagrams");
        
        markdown_doc = md_gen.generate_full_documentation(
            file_tree=file_tree,
            readme_summary=readme_summary,
            ccg_data=ccg_data,
            local_path=local_path
        );
        
        print(f"✓ Generated {len(markdown_doc)} characters of documentation");
        
        # Step 3: Save documentation
        print("\n[3/3] Saving documentation to disk...");
        doc_saver = DocumentationSaver(self.output_path);
        doc_path = doc_saver.save_documentation(self.repo_name, markdown_doc);
        
        # Also save CCG data
        if ccg_data {
            doc_saver.save_ccg_json(self.repo_name, ccg_data);
        }
        
        # Store the documentation path
        here.documentation_path = doc_path;
        here.documentation_content = markdown_doc;
        
        print("\n" + "=" * 50);
        print("DocGenie Complete!");
        print("=" * 50);
        print(f"\n📄 Documentation available at: {doc_path}");
    }
}

# ==================== API WALKER ====================

walker DocumentRepositoryAPI {
    """
    API walker for handling documentation generation requests
    """
    has repo_url: str = "";
    has max_files: int = 30;
    has output_path: str = "./outputs";
    
    can process_request with entry {
        print("\n" + "🌐 " * 25);
        print("API Request Received");
        print("🌐 " * 25);
        
        # Get parameters from the node context if available
        if hasattr(here, 'repo_url') and here.repo_url {
            self.repo_url = here.repo_url;
        }
        if hasattr(here, 'max_files') and here.max_files {
            self.max_files = here.max_files;
        }
        if hasattr(here, 'output_path') and here.output_path {
            self.output_path = here.output_path;
        }
        
        print(f"Repository URL: {self.repo_url}");
        print(f"Max files to analyze: {self.max_files}");
        
        # Validate URL
        if not self.repo_url or not self.repo_url.startswith('http') {
            report {
                "success": False,
                "error": "Invalid repository URL. Must start with http:// or https://",
                "repo_url": self.repo_url
            };
            return;
        }
        
        # Extract repo name
        import from pathlib { Path }
        repo_name = self.repo_url.rstrip('/').split('/')[-1];
        if repo_name.endswith('.git') {
            repo_name = repo_name[:-4];
        }
        
        # Create a fresh repository node for this request
        repo_node = Repository(
            url=self.repo_url,
            name=repo_name
        );
        
        try {
            # Step 1: Map repository
            print("\n📍 Step 1/3: Mapping repository...");
            repo_node spawn RepoMapper(repo_url=self.repo_url);
            
            # Step 2: Analyze code
            print("\n📍 Step 2/3: Analyzing code...");
            if repo_node.local_path {
                repo_node spawn CodeAnalyzer(
                    local_path=repo_node.local_path,
                    max_files=self.max_files
                );
            }
            
            # Step 3: Generate documentation
            print("\n📍 Step 3/3: Generating documentation...");
            repo_node spawn DocGenie(
                repo_name=repo_name,
                repo_url=self.repo_url,
                output_path=self.output_path
            );
            
            # Prepare response
            stats = {};
            if repo_node.code_context_graph {
                ccg = repo_node.code_context_graph;
                stats = ccg.get('statistics', {}) if isinstance(ccg, dict) else {};
            }
            
            print("\n✅ API Request Complete!");
            
            # Report success with detailed information
            report {
                "success": True,
                "repo_name": repo_name,
                "repo_url": self.repo_url,
                "documentation_path": repo_node.documentation_path if repo_node.documentation_path else "",
                "statistics": {
                    "functions": stats.get('functions', 0),
                    "classes": stats.get('classes', 0),
                    "files_analyzed": stats.get('files_analyzed', 0),
                    "total_nodes": stats.get('total_nodes', 0),
                    "total_edges": stats.get('total_edges', 0)
                },
                "readme_summary": repo_node.readme_summary if repo_node.readme_summary else "",
                "message": "Documentation generated successfully!"
            };
            
        } except Exception as e {
            print(f"\n❌ Error processing request: {e}");
            report {
                "success": False,
                "error": str(e),
                "repo_url": self.repo_url
            };
        }
    }
}

walker GetDocumentationAPI {
    """
    API walker to retrieve generated documentation
    """
    has repo_name: str;
    has output_path: str = "./outputs";
    
    can get_documentation with entry {
        print(f"\n📖 Retrieving documentation for: {self.repo_name}");
        
        import from pathlib { Path }
        import os;
        
        # Check if documentation exists
        doc_path = Path(self.output_path) / self.repo_name / "DOCUMENTATION.md";
        
        if not os.path.exists(doc_path) {
            report {
                "success": False,
                "error": f"Documentation not found for repository: {self.repo_name}",
                "repo_name": self.repo_name
            };
            return;
        }
        
        # Read documentation
        try {
            with open(doc_path, 'r', encoding='utf-8') as f {
                content = f.read();
            }
            
            print(f"✅ Documentation retrieved ({len(content)} chars)");
            
            report {
                "success": True,
                "repo_name": self.repo_name,
                "documentation": content,
                "path": str(doc_path)
            };
            
        } except Exception as e {
            report {
                "success": False,
                "error": str(e),
                "repo_name": self.repo_name
            };
        }
    }
}

walker ListDocumentationsAPI {
    """
    API walker to list all generated documentations
    """
    has output_path: str = "./outputs";
    
    can list_docs with entry {
        print("\n📚 Listing all generated documentations...");
        
        import from pathlib { Path }
        import os;
        
        output_dir = Path(self.output_path);
        
        if not output_dir.exists() {
            report {
                "success": True,
                "documentations": [],
                "count": 0
            };
            return;
        }
        
        # Find all documentation directories
        docs = [];
        for item in output_dir.iterdir() {
            if item.is_dir() {
                doc_file = item / "DOCUMENTATION.md";
                if doc_file.exists() {
                    docs.append({
                        "repo_name": item.name,
                        "path": str(doc_file),
                        "size": os.path.getsize(doc_file)
                    });
                }
            }
        }
        
        print(f"✅ Found {len(docs)} documentations");
        
        report {
            "success": True,
            "documentations": docs,
            "count": len(docs)
        };
    }
}

# ==================== MAIN ENTRY ====================

with entry {
    # Just load environment variables when serving
    load_dotenv();
    
    # The API walkers will be available at:
    # POST /walker/DocumentRepositoryAPI
    # POST /walker/GetDocumentationAPI
    # POST /walker/ListDocumentationsAPI
}
