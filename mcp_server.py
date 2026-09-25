import logging
import os

import uvicorn
from fastmcp import FastMCP
from starlette.responses import RedirectResponse
from starlette.routing import Route

from src.pipeline import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("tesla_rag_mcp")

mcp = FastMCP("tesla-rag")


def build_http_app():
    """Create the streamable HTTP app and redirect the browser root to /mcp."""
    app = mcp.http_app(path="/mcp", transport="streamable-http")

    async def redirect_root(request):
        return RedirectResponse(url="/mcp", status_code=307)

    app.router.routes.insert(0, Route("/", redirect_root, methods=["GET", "HEAD"]))
    return app


@mcp.tool()
def ask_tesla_report(question: str) -> dict:
    """Answer a question using the local Tesla annual report RAG pipeline."""
    logger.info("Received MCP tool call: question=%s", question)
    result = run_pipeline(question)

    if result.get("error"):
        logger.error("RAG pipeline error: %s", result["error"])
        return {
            "success": False,
            "error": result["error"],
        }

    logger.info(
        "Completed MCP tool call: route=%s sources=%d",
        result.get("route", "unknown"),
        len(result.get("sources", [])),
    )
    return {
        "success": True,
        "answer": result.get("answer", ""),
        "sources": result.get("sources", []),
        "route": result.get("route", "unknown"),
        "diagnostics": result.get("diagnostics", {}),
    }


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()
    if transport == "http":
        host = os.getenv("MCP_HOST", "127.0.0.1")
        port = int(os.getenv("MCP_PORT", "8501"))
        logger.info("Starting Tesla RAG MCP server on http://%s:%s/mcp", host, port)
        uvicorn.run(build_http_app(), host=host, port=port, log_level="info")
    else:
        logger.info("Starting Tesla RAG MCP server with stdio transport")
        mcp.run(transport="stdio", show_banner=True)
