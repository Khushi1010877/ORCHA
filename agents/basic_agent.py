from dotenv import load_dotenv
from tools.llm import GroqLLMClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
import json
import asyncio

load_dotenv()

model_client = GroqLLMClient(model="llama3-8b-8192")

agent = AssistantAgent(
    name="ORCHA_agent",
    model_client=model_client,
    system_message=(
        "You are ORCHA, an AI product feedback analyst.\n"
        "Analyze the following product and return ONLY a valid JSON object with these exact keys:\n"
        "- product\n"
        "- category\n"
        "- top_3_insights (list of 3 strings)\n"
        "- sentiment_summary (string)\n"
        "- severity_score (integer 1-10)\n"
        "- recommendations (list of strings)\n"
        "Do NOT include markdown, code fences, or explanation. Return raw JSON only."
    )
)


def build_prompt(product_name: str) -> str:
    return f"Analyze feedback for this product and return structured JSON. Product: {product_name}"


async def analyze(product_name: str) -> dict:
    prompt = build_prompt(product_name)

    response = await agent.on_messages(
        messages=[TextMessage(content=prompt, source="user")],
        cancellation_token=CancellationToken(),
    )

    raw = response.chat_message.content

    if raw.startswith("```"):
        raw = raw.strip("`").removeprefix("json").strip()

    try:
        result = json.loads(raw)
        print("[ORCHA] Parsed successfully")
    except json.JSONDecodeError as e:
        print(f"[ORCHA] Parse failed: {e}")
        result = {"raw_output": raw, "error": str(e)}

    return result


async def main():
    product_name = input("Enter product name: ").strip()

    if not product_name:
        print("[ORCHA] No product name provided.")
        return

    result = await analyze(product_name)

    print("\n[ORCHA] Result:")
    print(json.dumps(result, indent=2))


asyncio.run(main())