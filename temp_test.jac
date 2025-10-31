
import from backend.main { 
    Repository,
    CodeGenius
}
import from dotenv { load_dotenv }

with entry {
    load_dotenv();
    
    repo_node = Repository(
        url="https://github.com/octocat/Hello-World",
        name="Hello-World"
    );
    
    repo_node spawn CodeGenius(
        repo_url="https://github.com/octocat/Hello-World",
        output_path="./outputs"
    );
}
