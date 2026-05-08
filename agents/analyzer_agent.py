#READ 50 SEARCHES RESULTS AND EXTRACTS:
#KEY THEMES,SENTIMENT,TOP COMPLAINTS AND PRAISES, RETURN STRUCTURED JSON
#autogen
#for any product like {product_name}, read the search results and extract key themes, sentiment, top complaints and praises, return structured JSON

from autogen_core import CancellationToken
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from tools.llm import GroqLLMClient
from tools.search import WebSearchTool
from dotenv import load_dotenv
import asyncio
import json

load_dotenv()

model_client = GroqLLMClient()
search_tool = WebSearchTool()

_agent = AssistantAgent(
    name="analyzer_agent",
    model_client=model_client,
    system_message=(
        "You are ORCHA's analyzer agent.\n"
        "You receive web search results for a product and extract meaningful insights.\n"
        "Return ONLY a valid JSON object with these exact keys:\n"
        "- product: product name\n"
        "- key_themes: list of 3 to 5 recurring themes from the results\n"
        "- sentiment: positive, negative, or mixed\n"
        "- top_complaints: list of 3 to 5 top complaints found\n"
        "- top_praises: list of 3 to 5 top praises found\n"
        "- severity_score: integer 1-10 based on complaint severity\n"
        "- summary: one paragraph overall summary\n"
        "Return raw JSON only, no markdown or explanation."
    )
)


def _fallback(product_name: str) -> dict:
    return {
        "product": product_name,
        "key_themes": [],
        "sentiment": "mixed",
        "top_complaints": [],
        "top_praises": [],
        "severity_score": 5,
        "summary": "Could not generate analysis due to a parsing error."
    }


class AnalyzerAgent:
    async def analyze(self, product_name: str, search_results: list) -> dict:
        prompt = (
            f"Product: {product_name}\n\n"
            f"Search Results: {json.dumps(search_results[:50])}"
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
            print(f"[Analyzer] Parse failed: {e}, using fallback")
            return _fallback(product_name)


async def main():
    product_name = input("Enter product name: ").strip()

    if not product_name:
        print("[Analyzer] No product name provided.")
        return

    queries = [
        f"{product_name} reviews",
        f"{product_name} complaints",
        f"{product_name} user feedback",
        f"{product_name} pros and cons",
        f"{product_name} problems"
    ]

    search_results = []
    for query in queries:
        search_results.extend(search_tool.query(query))

    print(f"[Analyzer] Fetched {len(search_results)} results for '{product_name}'")

    result = await AnalyzerAgent().analyze(product_name, search_results)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())