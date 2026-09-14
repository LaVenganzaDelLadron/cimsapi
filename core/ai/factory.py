from .groq import GroqProvider
from core.config.settings import get_settings


def create_provider():
    return GroqProvider(get_settings())
