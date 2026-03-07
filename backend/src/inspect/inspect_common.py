from inspect_ai.model import get_model, modelapi, GenerateConfig
from inspect_ai.model._providers.openai_compatible import OpenAICompatibleAPI
from src.utils.logger import logger

class AICustomAPI(OpenAICompatibleAPI):
    def __init__(self, model_name, base_url, api_key, original_model_name=None, config=GenerateConfig(), service_name=None, **model_args):
        if service_name is None:
            service_name = "Custom"
        # Store the original model name for API requests (e.g., "qwen/qwen3-14b")
        # model_name from alias will be used for inspect_ai, but API requests need the original name
        self.original_model_name = original_model_name or model_name
        super().__init__(
            model_name=self.original_model_name,  # Pass original model name for API requests
            base_url=base_url,
            api_key=api_key,
            config=config,
            service=service_name,
            service_base_url=base_url,
            **model_args
        )

def register_in_inspect_ai(model_name: str, api_url: str, api_key: str):
    """
    Register models in inspect_ai with unique alias.
    Stores the original model_name for later use in API requests.
    """
    if '/' in model_name:
        model_name_str = model_name.rsplit('/', 1)
        alias = f"custom-model-{model_name_str[1]}"
    else:
        alias = f"custom-model-{model_name}"

    # Store original_model_name in closure for use in wrapper
    original_model_name = model_name

    @modelapi(name=alias)
    def _factory():
        def wrapper(model_name, config=GenerateConfig(), **model_args):
            model_args.pop("base_url", None)
            model_args.pop("api_key", None)
            _api_key = api_key
            if _api_key == "":
                logger.warning(
                    "API_KEY is empty."
                )
                _api_key = None
            return AICustomAPI(
                model_name=alias,  # Pass alias for inspect_ai registration
                base_url=api_url,
                api_key=_api_key,
                original_model_name=original_model_name,  # Pass original model name for API requests
                config=config,
                **model_args
            )
        return wrapper
    return alias

