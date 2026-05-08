from autogen_core import CancellationToken
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from tools.llm import GroqLLMClient
from dotenv import load_dotenv
import asyncio
import json
import config

load_dotenv()

#model_client = GroqLLMClient(model="llama3-8b-8192")
model_client = GroqLLMClient()

_agent = AssistantAgent(
    name="planner_agent",
    model_client=model_client,
    system_message=(
        "You are a planner agent that creates a DuckDuckGo search plan for a given product.\n"
        "Return a valid JSON object with these exact keys:\n"
        "- search_queries: list of 3 to 5 search queries\n"
        "- top_5_insights: list of 3 to 5 insights\n"
        "- sources: list of source URLs or domains\n"
        "- feedback_types: list of feedback categories like reviews, social media, news, complaints\n"
        "- sentiment_summary: positive, negative, or mixed\n"
        "- severity_score: integer 1-10\n"
        "- recommendations: list of 3 to 5 recommendations\n"
        "Return only JSON and nothing else."
    )
)


def _fallback(product_name: str) -> dict:
    return {
        "product_name": product_name,
        "search_queries": [
            f"{product_name} reviews",
            f"{product_name} complaints",
            f"{product_name} user feedback"
        ],
        "top_5_insights": [],
        "sources": [],
        "feedback_types": ["reviews", "social_media", "news"],
        "sentiment_summary": "mixed",
        "severity_score": 5,
        "recommendations": []
    }


class PlannerAgent:
    async def plan(self, product_name: str) -> dict:
        if config.MOCK_MODE:
            print("[Planner] Mock mode enabled, skipping LLM call.")
            return _fallback(product_name)

        prompt = f"Create a DuckDuckGo search plan for analyzing feedback on: {product_name}"

        response = await _agent.on_messages(
            messages=[TextMessage(content=prompt, source="user")],
            cancellation_token=CancellationToken(),
        )

        raw = response.chat_message.content

        if raw.startswith("```"):
            raw = raw.strip("`").removeprefix("json").strip()

        try:
            result = json.loads(raw)
            result["product_name"] = product_name
            print("[Planner] Plan parsed successfully")
            return result
        except json.JSONDecodeError as e:
            print(f"[Planner] Parse failed: {e}, using fallback")
            return _fallback(product_name)


async def main():
    product_name = input("Enter product name: ").strip()
    if not product_name:
        print("[Planner] No product name provided.")
        return
    result = await PlannerAgent().plan(product_name)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())