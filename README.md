# Weather MCP Demo

A real Python MCP server using FastMCP, with a clean FastAPI dashboard to explain and test MCP tools, resources, and prompts.

## What it provides

- MCP endpoint: `http://localhost:8000/mcp`
- Dashboard: `http://localhost:8000/`
- Tools:
  - `get_current_weather`
  - `get_weather_forecast`
  - `compare_weather`
- Resources:
  - `weather://supported-cities`
  - `weather://city/{city}/profile`
  - `docs://mcp-overview`
- Prompts:
  - `weather_report_prompt`
  - `travel_weather_advisor`

## Run locally

```bash
cd weather-mcp-demo
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8000
```

Then open:

```text
http://localhost:8000/
```

## Test with MCP Inspector

```bash
npx -y @modelcontextprotocol/inspector
```

Connect to:

```text
http://localhost:8000/mcp
```

## Test with Claude Desktop / Cursor style config

For remote Streamable HTTP clients:

```json
{
  "mcpServers": {
    "weather-demo": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

For local stdio style clients, create a separate `server.py` runner if needed and use `fastmcp run`.
