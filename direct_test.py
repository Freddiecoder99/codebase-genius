#!/usr/bin/env python3
"""
Direct test without API server - calls Jac directly
"""
import subprocess
import json

def generate_docs_direct(repo_url, max_files=30):
    """Generate documentation by calling jac run directly"""
    print(f"\n🚀 Generating documentation for: {repo_url}")
    print("=" * 60)
    
    # Create a temporary test file in backend directory
    test_jac = f"""
import from main {{ 
    Repository,
    CodeGenius
}}
import from dotenv {{ load_dotenv }}

with entry {{
    load_dotenv();
    
    repo_node = Repository(
        url="{repo_url}",
        name="{repo_url.split('/')[-1].replace('.git', '')}"
    );
    
    repo_node spawn CodeGenius(
        repo_url="{repo_url}",
        output_path="../outputs"
    );
}}
"""
    
    # Write the test file to backend directory
    import os
    os.makedirs("backend", exist_ok=True)
    with open("backend/temp_test.jac", "w") as f:
        f.write(test_jac)
    
    # Run it from backend directory
    try:
        result = subprocess.run(
            ["jac", "run", "temp_test.jac"],
            cwd="backend",
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        print("\n" + "=" * 60)
        if result.returncode == 0:
            print("✅ Documentation generated successfully!")
            print("📁 Check: ./outputs/")
        else:
            print(f"❌ Process failed with code {result.returncode}")
            
    except subprocess.TimeoutExpired:
        print("❌ Process timed out (took longer than 5 minutes)")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Clean up temp file
        try:
            os.remove("backend/temp_test.jac")
        except:
            pass

if __name__ == "__main__":
    print("=" * 60)
    print("CODEBASE GENIUS - DIRECT EXECUTION TEST")
    print("=" * 60)
    
    # Test with Hello-World
    generate_docs_direct("https://github.com/octocat/Hello-World")
    
    print("\n" + "=" * 60)
    print("✅ Test complete! Check outputs/ directory")
    print("=" * 60)
