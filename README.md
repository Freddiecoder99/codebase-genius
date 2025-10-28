# Codebase Genius 🧠

An AI-powered multi-agent system that automatically generates high-quality documentation for any software repository.

## Features

- 🔍 **Automatic Repository Analysis**: Clone and analyze any GitHub repository
- 🗺️ **Smart Code Mapping**: Generate file trees and dependency graphs
- 🧬 **Code Context Graphs**: Build relationships between functions, classes, and modules
- 📄 **Documentation Generation**: Create comprehensive markdown documentation
- 🎯 **Multi-Agent System**: Specialized agents for mapping, analyzing, and documenting

## Architecture

- **Code Genius (Supervisor)**: Orchestrates the entire workflow
- **Repo Mapper**: Explores repository structure and creates file trees
- **Code Analyzer**: Parses code and builds Code Context Graphs (CCG)
- **DocGenie**: Synthesizes documentation from analyzed data

## Setup

1. Clone this repository
2. Create virtual environment: `python3 -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up `.env` with your API keys
6. Run: `jac serve backend/main.jac`

## Usage
```bash
# Start the backend server
jac serve backend/main.jac

# In another terminal, use the API
curl -X POST http://localhost:8000/walker/analyze_repo \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/user/repo"}'
```

## Technology Stack

- **Jac**: Multi-agent orchestration
- **Tree-sitter**: Code parsing
- **FastAPI**: REST API
- **OpenAI/Gemini**: LLM reasoning
- **GitPython**: Repository operations

## License

MIT
