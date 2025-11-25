import sys
import json

def main():
    # Simple JSON-RPC Loop
    for line in sys.stdin:
        try:
            request = json.loads(line)
            msg_id = request.get("id")
            method = request.get("method")
            
            response = {"jsonrpc": "2.0", "id": msg_id}
            
            if method == "tools/list":
                response["result"] = {
                    "tools": [
                        {
                            "name": "add_numbers",
                            "description": "Adds two numbers together.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "a": {"type": "number"},
                                    "b": {"type": "number"}
                                },
                                "required": ["a", "b"]
                            }
                        }
                    ]
                }
            
            elif method == "tools/call":
                params = request.get("params", {})
                name = params.get("name")
                args = params.get("arguments", {})
                
                if name == "add_numbers":
                    a = args.get("a", 0)
                    b = args.get("b", 0)
                    result = a + b
                    response["result"] = {
                        "content": [
                            {"type": "text", "text": str(result)}
                        ]
                    }
                else:
                    response["error"] = {"code": -32601, "message": "Method not found"}
            
            else:
                # Ignore other messages or return error
                pass

            # Write response
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
            
        except Exception as e:
            # Log error to stderr so it doesn't break JSON-RPC
            sys.stderr.write(f"Error: {e}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    main()
