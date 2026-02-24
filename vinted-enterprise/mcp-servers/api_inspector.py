#!/usr/bin/env python3
"""
Vinted Optimizer - Custom MCP Server per API Inspection
Uso: python3 scripts/mcp/api_inspector.py
Kilo Code lo usa per testare endpoints FastAPI locali durante sviluppo
"""

import asyncio
import json
import sys
import os
import httpx
from typing import Any

# MCP protocol via stdin/stdout
async def send_response(id: Any, result: Any = None, error: Any = None):
    response = {"jsonrpc": "2.0", "id": id}
    if error:
        response["error"] = {"code": -32000, "message": str(error)}
    else:
        response["result"] = result
    print(json.dumps(response), flush=True)

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "")

TOOLS = [
    {
        "name": "api_health",
        "description": "Controlla lo stato di salute dell'API FastAPI locale",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "api_get",
        "description": "Esegue GET request all'API FastAPI con autenticazione",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path endpoint es. /api/v1/listings"},
                "params": {"type": "object", "description": "Query params opzionali"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "api_post",
        "description": "Esegue POST request all'API FastAPI",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "body": {"type": "object", "description": "Request body JSON"}
            },
            "required": ["path", "body"]
        }
    },
    {
        "name": "api_schema",
        "description": "Recupera OpenAPI schema dell'API (endpoints disponibili)",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "api_list_endpoints",
        "description": "Lista tutti gli endpoints API disponibili con metodi e descrizioni",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

async def execute_tool(name: str, arguments: dict) -> str:
    headers = {}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    headers["Content-Type"] = "application/json"
    
    async with httpx.AsyncClient(base_url=API_BASE, timeout=10.0) as client:
        if name == "api_health":
            try:
                r = await client.get("/api/health", headers=headers)
                return json.dumps({"status": r.status_code, "body": r.json()}, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e), "api_url": API_BASE})
        
        elif name == "api_get":
            r = await client.get(
                arguments["path"],
                params=arguments.get("params", {}),
                headers=headers
            )
            return json.dumps({
                "status": r.status_code,
                "body": r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text
            }, indent=2)
        
        elif name == "api_post":
            r = await client.post(
                arguments["path"],
                json=arguments["body"],
                headers=headers
            )
            return json.dumps({
                "status": r.status_code,
                "body": r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text
            }, indent=2)
        
        elif name in ("api_schema", "api_list_endpoints"):
            r = await client.get("/api/docs", headers=headers)
            schema_r = await client.get("/openapi.json", headers=headers)
            if schema_r.status_code == 200:
                schema = schema_r.json()
                if name == "api_list_endpoints":
                    endpoints = []
                    for path, methods in schema.get("paths", {}).items():
                        for method, info in methods.items():
                            endpoints.append({
                                "path": path,
                                "method": method.upper(),
                                "summary": info.get("summary", ""),
                                "tags": info.get("tags", [])
                            })
                    return json.dumps(endpoints, indent=2)
                return json.dumps(schema, indent=2)
            return json.dumps({"error": "OpenAPI schema non disponibile", "tip": "Avvia API con DEBUG=true"})
        
        return json.dumps({"error": f"Tool non trovato: {name}"})

async def main():
    while True:
        line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
        if not line:
            break
        
        try:
            request = json.loads(line.strip())
        except json.JSONDecodeError:
            continue
        
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "initialize":
            await send_response(req_id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "vinted-api-inspector", "version": "1.0.0"}
            })
        
        elif method == "tools/list":
            await send_response(req_id, {"tools": TOOLS})
        
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            try:
                result = await execute_tool(tool_name, tool_args)
                await send_response(req_id, {
                    "content": [{"type": "text", "text": result}]
                })
            except Exception as e:
                await send_response(req_id, error=str(e))
        
        elif method == "notifications/initialized":
            pass  # No response needed
        
        else:
            await send_response(req_id, error=f"Method not found: {method}")

if __name__ == "__main__":
    asyncio.run(main())
