import asyncio
from src.tools.web_search import search_web

def main():
    print("--- Testing Web Search Tool ---")
    query = "Microsoft Agent Framework October 2025 update"
    print(f"Query: {query}")
    
    result = search_web(query)
    print(f"\nResult:\n{result}")
    
    if "No results found" not in result and "Error" not in result:
        print("\nSUCCESS: Web search returned results.")
    else:
        print("\nFAILURE: Web search failed.")

if __name__ == "__main__":
    main()
