import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
from contextlib import AsyncExitStack
from bson import ObjectId

# Add project root to path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession

from langchain_openai import ChatOpenAI
from langchain_classic.agents import create_react_agent, AgentExecutor
from langchain_core.tools import StructuredTool
from langchain_classic import hub

PROJECT_ROOT = project_root
PYTHON_BIN = str((PROJECT_ROOT / ".venv" / "bin" / "python3").absolute())

SERVERS = {
    "storage": str((PROJECT_ROOT / "microservices/storage/mcp_server.py").absolute()),
    "extraction": str((PROJECT_ROOT / "microservices/extraction/mcp_server.py").absolute()),
    "tax_core": str((PROJECT_ROOT / "microservices/tax_core/mcp_server.py").absolute()),
    "advisory": str((PROJECT_ROOT / "microservices/advisory/mcp_server.py").absolute()),
}

class OrchestratorBrain:
    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}
        self.exit_stack = AsyncExitStack()
        self.tools = []
        
        # We will use an advanced LLM as the reasoning engine
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
            
        self.llm = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1" if "OPENROUTER" in os.environ else None,
            model="openai/gpt-4o" if "OPENROUTER" in os.environ else "gpt-4o",
            api_key=api_key,
            temperature=0
        )

    async def initialize(self):
        """Connect to all MCP servers and wrap their tools for the LLM."""
        print("Initializing Orchestrator Brain...")
        env = os.environ.copy()
        env["PYTHONPATH"] = str(PROJECT_ROOT)
        
        for name, script_path in SERVERS.items():
            print(f"Connecting to {name} MCP server...")
            params = StdioServerParameters(command=PYTHON_BIN, args=[script_path], env=env)
            
            # stdio_client is an async context manager
            read_stream, write_stream = await self.exit_stack.enter_async_context(stdio_client(params))
            session = await self.exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
            
            await session.initialize()
            self.sessions[name] = session
            print(f"✅ Connected to {name}")
            
            # Fetch tools from this MCP server
            tools_response = await session.list_tools()
            for mcp_tool in tools_response.tools:
                # Wrap the MCP tool as a LangChain StructuredTool
                self.tools.append(self._create_langchain_tool(name, mcp_tool))
                print(f"  Loaded tool: {mcp_tool.name}")

    def _create_langchain_tool(self, server_name: str, mcp_tool) -> StructuredTool:
        """Dynamically creates a LangChain tool that proxies calls to the MCP server."""
        
        # We need a proxy function that executes the MCP call
        def invoke_mcp_tool(*args, **kwargs):
            # Since LangChain tools are often synchronous or called in a sync event loop,
            # we need to run the async MCP call carefully.
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import nest_asyncio
                nest_asyncio.apply()
            
            # Use asyncio.run to execute the MCP call
            async def _run():
                session = self.sessions[server_name]
                # Pass all kwargs directly to the MCP tool
                result = await session.call_tool(mcp_tool.name, kwargs)
                # mcp.types.CallToolResult has 'content' which is a list
                if hasattr(result, 'content'):
                    return "\n".join([str(c) for c in result.content])
                return str(result)
            
            try:
                if loop.is_running():
                    return loop.run_until_complete(_run())
                return asyncio.run(_run())
            except Exception as e:
                return f"Error executing tool {mcp_tool.name}: {str(e)}"
        
        return StructuredTool.from_function(
            func=invoke_mcp_tool,
            name=mcp_tool.name,
            description=f"[{server_name}] {mcp_tool.description}",
        )

    async def execute_task(self, prompt: str, user_id: str) -> str:
        """
        Runs the reasoning agent to fulfill the user's request using the available tools.
        """
        if not self.tools:
            return "Error: No tools available. Call initialize() first."
            
        system_prompt = (
            "You are the TaxMate Central Orchestrator, an intelligent reasoning engine. "
            "Your job is to coordinate multiple backend microservices (Storage, Extraction, Tax_Core, Advisory) "
            "to assist the user with their tax filing.\n\n"
            f"The user ID is: {user_id}\n\n"
            "Workflow Strategy:\n"
            "1. If the user asks for tax advice or calculation, first check if we have their data using get_user_tax_data.\n"
            "2. If no data exists, tell them to upload documents or attempt to trigger extraction.\n"
            "3. If data exists, you can pass it to compare_regimes or generate_tax_advice.\n"
            "4. For calculations, carefully pass the extracted JSON to the TaxCore server.\n"
            "5. Always synthesize a friendly, clear final answer for the user."
        )
        
        from langchain_core.prompts import PromptTemplate
        # Standard ReAct prompt from Hub 
        base_prompt = hub.pull("hwchase17/react")
        # We prefix our system instructions
        base_prompt.template = system_prompt + "\n\n" + base_prompt.template
        
        agent = create_react_agent(self.llm, self.tools, base_prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True, handle_parsing_errors=True)
        
        try:
            # We run the agent executor which is sync, but we are in an async function.
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, agent_executor.invoke, {"input": prompt})
            return result.get("output", "Task completed without output.")
        except Exception as e:
            return f"Orchestrator failed to complete the task: {str(e)}"

    async def close(self):
        """Clean up MCP connections."""
        await self.exit_stack.aclose()
        print("Orchestrator Brain shut down.")

# Example local test
async def main():
    brain = OrchestratorBrain()
    try:
        await brain.initialize()
        user_id = str(ObjectId())  # Mock ID for testing
        print("\n=== SYSTEM ONLINE ===")
        print("Prompting brain to check what documents exist...")
        
        reply = await brain.execute_task("Do I have any tax documents uploaded?", user_id="test_user")
        print(f"\nResponse:\n{reply}")
    finally:
        await brain.close()

if __name__ == "__main__":
    asyncio.run(main())
