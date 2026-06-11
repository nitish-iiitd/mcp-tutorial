from __future__ import annotations

import json
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastmcp import Client
from pydantic import BaseModel, Field

from app.mcp_server import mcp

mcp_app = mcp.http_app(path="/mcp")

app = FastAPI(
    title="MCP Tutorial",
    description="A FastMCP server with a dashboard for learning and testing MCP primitives.",
    version="0.1.0",
    lifespan=mcp_app.lifespan,
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/mcp", mcp_app)


class ToolCallRequest(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ResourceReadRequest(BaseModel):
    uri: str


class PromptGetRequest(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


def normalize_result(value: Any) -> Any:
    encoded = jsonable_encoder(value)
    if isinstance(encoded, dict) and "content" in encoded:
        return encoded
    return encoded


@app.get("/", response_class=HTMLResponse)
async def dashboard(_: Request) -> str:
    with open("app/static/index.html", "r", encoding="utf-8") as file:
        return file.read()


@app.get("/api/mcp/catalog")
async def mcp_catalog() -> dict[str, Any]:
    async with Client(mcp) as client:
        return {
            "server": client.initialize_result.serverInfo.name,
            "instructions": client.initialize_result.instructions,
            "tools": normalize_result(await client.list_tools()),
            "resources": normalize_result(await client.list_resources()),
            "resource_templates": normalize_result(await client.list_resource_templates()),
            "prompts": normalize_result(await client.list_prompts()),
        }


@app.post("/api/mcp/tools/call")
async def call_tool(payload: ToolCallRequest) -> Any:
    try:
        async with Client(mcp) as client:
            result = await client.call_tool(payload.name, payload.arguments)
            return normalize_result(result)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/mcp/resources/read")
async def read_resource(payload: ResourceReadRequest) -> Any:
    try:
        async with Client(mcp) as client:
            result = await client.read_resource(payload.uri)
            return normalize_result(result)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/mcp/prompts/get")
async def get_prompt(payload: PromptGetRequest) -> Any:
    try:
        async with Client(mcp) as client:
            result = await client.get_prompt(payload.name, payload.arguments)
            return normalize_result(result)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/examples/json-rpc")
async def json_rpc_examples() -> dict[str, Any]:
    return {
        "endpoint": "/mcp",
        "note": "Real MCP clients manage initialization, sessions, and protocol headers. These examples show the method names conceptually.",
        "examples": [
            {"method": "tools/list", "params": {}},
            {"method": "tools/call", "params": {"name": "get_current_weather", "arguments": {"city": "Bengaluru"}}},
            {"method": "resources/read", "params": {"uri": "weather://supported-cities"}},
            {"method": "prompts/get", "params": {"name": "weather_report_prompt", "arguments": {"city": "Delhi"}}},
        ],
    }
