from autogen_core import CancellationToken
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from tools.llm import GroqLLMClient
from tools.search import WebSearchTool
from dotenv import load_dotenv
import asyncio
import json

load_dotenv()

#model_client = GroqLLMClient(model="llama3-8b-8192")
model_client = GroqLLMClient()
search_tool = WebSearchTool()

_agent = AssistantAgent(
    name="executor_agent",
    model_client=model_client,
    system_message=(
        "You are ORCHA's execution agent.\n"
        "You receive a search plan and web search results.\n"
        "Return ONLY a valid JSON object with these keys:\n"
        "- executed_queries: list of queries searched\n"
        "- total_results: integer count\n"
        "- key_findings: list of 3 to 5 findings\n"
        "- summary: one paragraph summary\n"
        "Return raw JSON only, no markdown or explanation."
    )
)


def _fallback(queries: list, results: list) -> dict:
    return {
        "executed_queries": queries,
        "total_results": len(results),
        "key_findings": [],
        "summary": "Could not generate summary due to a parsing error."
    }


class ExecutorAgent:
    async def execute(self, plan: dict) -> dict:
        queries = plan.get("search_queries", [])

        # run searches
        results = []
        for query in queries:
            try:
                results.extend(search_tool.query(query, "duckduckgo"))
            except Exception as e:
                print(f"[Executor] Search error for '{query}': {e}")

        print(f"[Executor] Fetched {len(results)} results across {len(queries)} queries")

        # send plan + results to LLM
        prompt = (
            f"Plan: {json.dumps(plan)}\n\n"
            f"Search Results: {json.dumps(results[:10])}"
        )

        response = await _agent.on_messages(
            messages=[TextMessage(content=prompt, source="user")],
            cancellation_token=CancellationToken(),
        )

        raw = response.chat_message.content

        if raw.startswith("```"):
            raw = raw.strip("`").removeprefix("json").strip()

        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"[Executor] Parse failed: {e}, using fallback")
            return _fallback(queries, results)


async def main():
    product_name = input("Enter product name: ").strip()

    if not product_name:
        print("[Executor] No product name provided.")
        return

    plan = {
        "product_name": product_name,
        "search_queries": [
            f"{product_name} reviews",
            f"{product_name} complaints",
            f"{product_name} user feedback"
        ]
    }

    result = await ExecutorAgent().execute(plan)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())