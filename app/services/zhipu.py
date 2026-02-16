
from .openai import OpenAIProvider

class ZhipuProvider(OpenAIProvider):
    """
    Zhipu AI Provider.
    Currently inherits seamlessly from OpenAIProvider as Zhipu supports OpenAI format.
    Kept as a separate class for future extensibility or specific quirks.
    """
    pass
