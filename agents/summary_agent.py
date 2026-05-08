#summary agent
# READS ANALYSIS RESULTS AND GENERATES A FINAL SUMMARY REPORT
# STRUCTURED JSON WITH FINAL VERDICT, KEY POINTS, AND ACTION ITEMS

from autogen_core import CancellationToken
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from tools.llm import GroqLLMClient
from tools.search import WebSearchTool
from agents.analyzer_agent import AnalyzerAgent
from dotenv import load_dotenv
import asyncio
import json

load_dotenv()

model_client = GroqLLMClient()
search_tool = WebSearchTool()

_agent = AssistantAgent(
    name="summary_agent",
    model_client=model_client,
    system_message=(
        "You are ORCHA's summary agent.\n"
        "You receive a full product analysis and generate a final executive summary report.\n"
        "Return ONLY a valid JSON object with these exact keys:\n"
        "- product: product name\n"
        "- verdict: one sentence final verdict on the product\n"
        "- overall_sentiment: positive, negative, or mixed\n"
        "- severity_score: integer 1-10\n"
        "- key_points: list of 3 to 5 most important points\n"
        "- action_items: list of 3 to 5 recommended actions for the product team\n"
        "- final_summary: two to three paragraph executive summary\n"
        "Return raw JSON only, no markdown or explanation."
    )
)


def _fallback(product_name: str) -> dict:
    return {
        "product": product_name,
        "verdict": "Could not generate verdict due to a parsing error.",
        "overall_sentiment": "mixed",
        "severity_score": 5,
        "key_points": [],
        "action_items": [],
        "final_summary": "Could not generate summary due to a parsing error."
    }


class SummaryAgent:
    async def summarize(self, analysis: dict) -> dict:
        prompt = (
            f"Generate a final executive summary for this product analysis:\n\n"
            f"{json.dumps(analysis)}"
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
            print(f"[Summary] Parse failed: {e}, using fallback")
            return _fallback(analysis.get("product", "unknown"))


async def main():
    product_name = input("Enter product name: ").strip()

    if not product_name:
        print("[Summary] No product name provided.")
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

    print(f"[Summary] Fetched {len(search_results)} results for '{product_name}'")

    analysis = await AnalyzerAgent().analyze(product_name, search_results)
    result = await SummaryAgent().summarize(analysis)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())