#GroqLLMClient → connects AutoGen to Groq
#without it, AssistantAgent has no model to call
import config
from autogen_ext.models.openai._openai_client import BaseOpenAIChatCompletionClient
from openai import AsyncOpenAI
from autogen_core.models import ModelInfo, ModelFamily

class GroqLLMClient(BaseOpenAIChatCompletionClient):
    def __init__(self, model=None):
        self.model = model or config.GROQ_MODEL
        client = AsyncOpenAI(
            api_key=config.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )
        create_args = {"model": self.model}
        model_info = ModelInfo(
            vision=False,
            function_calling=True,
            json_output=True,
            family=ModelFamily.UNKNOWN,
            structured_output=True,
            multiple_system_messages=False
        )
        super().__init__(client, create_args=create_args, model_info=model_info)