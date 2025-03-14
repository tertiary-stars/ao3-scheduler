#!/usr/bin/env python3
import sys
import json
from auth import ao3_login

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"status": "error", "message": "Missing credentials"}))
        sys.exit(1)
    username = sys.argv[1]
    password = sys.argv[2]
    
    result = ao3_login(username, password)
    print(json.dumps(result))
