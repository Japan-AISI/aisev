import json
import time
from fastapi import requests
from inspect_ai.model import ModelAPI, GenerateConfig, modelapi
from inspect_ai.model._model_output import ModelOutput, ChatCompletionChoice
from inspect_ai.model._model_call import ModelCall
from inspect_ai.model._chat_message import (
    ChatMessage,
    ChatMessageUser,
    ChatMessageAssistant,
)
from inspect_ai.tool import ToolInfo, ToolChoice
from typing import List, Dict
from ..http import request_processor
from ..config import config as app_config


class MairaAPI(ModelAPI):
    def __init__(
        self,
        model_name: str,
        url: str,
        project_key: str,
        api_key: str,
        defaults: Dict | None = None,
        **model_args,
    ):
        # ✅ REQUIRED: initialize ModelAPI properly
        super().__init__(
            model_name=model_name,
            base_url=url,
            api_key=api_key,
            config=model_args.get("config", GenerateConfig()),
        )

        self.project_key = project_key
        self.defaults = defaults or {}

    async def generate(
        self,
        input: List[ChatMessage],
        tools: List[ToolInfo],
        tool_choice: ToolChoice,
        config: GenerateConfig,
    ):
        # ---- Extract last user message ----
        user_messages = [m for m in input if isinstance(m, ChatMessageUser)]
        query = user_messages[-1].content if user_messages else ""

        # ---- Build headers ----
        headers = {
            "project-key": self.project_key,
            "api-key": self.api_key,
            "accept": "application/json",
            "Content-Type": "application/json",
        }

        # ---- Required fields ----
        payload: Dict = {
            "user_id": self.defaults.get("user_id", "aisev-user"),
            "query": query,
            "conversation_type": self.defaults.get("conversation_type", "question"),
            "is_background_task": self.defaults.get("is_background_task", False),
        }

        # ---- Optional MairaAskRequestSchema fields ----
        for k, v in self.defaults.items():
            payload.setdefault(k, v)

        print(
            "MairaAPI Payload::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::",
            payload,
        )

        start_time = time.time()

        # ---- Call Maira (sync) ----
        try:
            # Convert payload dict to JSON string
            payload_str = json.dumps(payload) if payload else None

            response_body, status = request_processor(
                host=app_config.maira_api_hostname,
                port=app_config.maira_api_port,
                method="POST",
                url=self.base_url,  # e.g., "/v1/maira/ask"
                headers=headers,
                payload=payload_str,  # can be defaulted in config
            )

            # Parse JSON response
            try:
                data = json.loads(response_body)
            except json.JSONDecodeError:
                print("⚠️ Maira API response is not valid JSON!")
                data = {"detail": {"response": response_body}}

        except RuntimeError as e:
            print(f"❌ Maira API request failed: {e}")
            data = {"detail": {"response": ""}}  # fallback

        elapsed_time = time.time() - start_time

        print(
            "MairaAPI Response::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::",
            data["detail"]["response"],
        )

        # ---- Background task case ----
        if payload.get("is_background_task"):
            assistant_msg = ChatMessageAssistant(role="assistant", content="")

            choice = ChatCompletionChoice(
                index=0, message=assistant_msg, stop_reason="stop"
            )

            output = ModelOutput(
                model=self.model_name, choices=[choice], time=elapsed_time
            )

            call = ModelCall.create(
                request=payload,
                response=data,
                time=elapsed_time,
            )
            return output, call

        # ---- Extract text ----
        text = (
            data.get("detail", {}).get("response")
            or data.get("answer")
            or data.get("response")
            or data.get("data", {}).get("text", "")
            or ""
        )

        assistant_msg = ChatMessageAssistant(role="assistant", content=text or "")

        choice = ChatCompletionChoice(
            index=0, message=assistant_msg, stop_reason="stop"
        )

        output = ModelOutput(model=self.model_name, choices=[choice], time=elapsed_time)

        call = ModelCall.create(
            request=payload,
            response=data,
            time=elapsed_time,
        )

        return output, call


def register_in_inspect_maira_ai(
    alias: str,
    url: str,
    project_key: str,
    api_key: str,
    defaults: Dict,
):
    @modelapi(name=alias)
    def _factory():
        def wrapper(model_name, config=GenerateConfig(), **kwargs):
            return MairaAPI(
                model_name=model_name,
                url=url,
                project_key=project_key,
                api_key=api_key,
                defaults=defaults,
            )

        return wrapper

    return alias
