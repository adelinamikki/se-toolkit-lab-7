import json
import sys
from typing import Any

import httpx
from config import BotConfig
from services.lms_client import LMSClient


TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "List labs and tasks from the LMS backend.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get enrolled students and their groups.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution buckets for a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, for example lab-04.",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, for example lab-04.",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submissions per day for a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, for example lab-04.",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group average scores and student counts for a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, for example lab-04.",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get the top learners for a lab, optionally limited by count.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, for example lab-04.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of learners to return.",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get the completion percentage for a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, for example lab-04.",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Refresh LMS data by triggering the ETL sync pipeline.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


class IntentRouter:
    """Natural-language router skeleton for Task 3."""

    def __init__(self, config: BotConfig):
        self.config = config
        self.lms_client = LMSClient(config)
        if not config.LLM_API_BASE_URL or not config.LLM_API_KEY or not config.LLM_API_MODEL:
            raise ValueError(
                "LLM_API_BASE_URL, LLM_API_KEY, and LLM_API_MODEL must be set in .env.bot.secret"
            )

    def _llm_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.LLM_API_KEY}",
            "Content-Type": "application/json",
        }

    def _call_llm(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        payload = {
            "model": self.config.LLM_API_MODEL,
            "messages": messages,
            "tools": TOOLS,
            "tool_choice": "auto",
        }
        with httpx.Client(trust_env=False, timeout=30.0) as client:
            response = client.post(
                f"{self.config.LLM_API_BASE_URL}/chat/completions",
                headers=self._llm_headers(),
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    def _backend_get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        with httpx.Client(trust_env=False, timeout=10.0) as client:
            response = client.get(
                f"{self.config.LMS_API_BASE_URL}{path}",
                headers={
                    "Authorization": f"Bearer {self.config.LMS_API_KEY}",
                    "Content-Type": "application/json",
                },
                params=params,
            )
            response.raise_for_status()
            return response.json()

    def _backend_post(self, path: str, body: dict[str, Any] | None = None) -> Any:
        with httpx.Client(trust_env=False, timeout=10.0) as client:
            response = client.post(
                f"{self.config.LMS_API_BASE_URL}{path}",
                headers={
                    "Authorization": f"Bearer {self.config.LMS_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=body or {},
            )
            response.raise_for_status()
            return response.json()

    def _run_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        if tool_name == "get_items":
            return self._backend_get("/items/")
        if tool_name == "get_learners":
            return self._backend_get("/learners/")
        if tool_name == "get_scores":
            return self._backend_get("/analytics/scores", params={"lab": arguments["lab"]})
        if tool_name == "get_pass_rates":
            return self._backend_get("/analytics/pass-rates", params={"lab": arguments["lab"]})
        if tool_name == "get_timeline":
            return self._backend_get("/analytics/timeline", params={"lab": arguments["lab"]})
        if tool_name == "get_groups":
            return self._backend_get("/analytics/groups", params={"lab": arguments["lab"]})
        if tool_name == "get_top_learners":
            params = {"lab": arguments["lab"]}
            if "limit" in arguments:
                params["limit"] = arguments["limit"]
            return self._backend_get("/analytics/top-learners", params=params)
        if tool_name == "get_completion_rate":
            return self._backend_get("/analytics/completion-rate", params={"lab": arguments["lab"]})
        if tool_name == "trigger_sync":
            return self._backend_post("/pipeline/sync")
        raise ValueError(f"Unknown tool: {tool_name}")

    def route(self, message_text: str) -> str:
        """Route natural-language queries through the LLM tool-calling loop."""
        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": (
                    "You are an LMS bot assistant. Use the provided tools to answer questions "
                    "with real backend data. Do not guess numbers. If the user is greeting you, "
                    "reply briefly and mention what you can do. If the query is ambiguous, ask a "
                    "clarifying question. Prefer tool calls over unsupported assumptions."
                ),
            },
            {"role": "user", "content": message_text},
        ]

        try:
            for _ in range(6):
                llm_response = self._call_llm(messages)
                message = llm_response["choices"][0]["message"]
                tool_calls = message.get("tool_calls", [])

                if not tool_calls:
                    return message.get("content", "I couldn't produce a response.")

                messages.append(
                    {
                        "role": "assistant",
                        "content": message.get("content") or "",
                        "tool_calls": tool_calls,
                    }
                )

                for tool_call in tool_calls:
                    tool_name = tool_call["function"]["name"]
                    raw_arguments = tool_call["function"].get("arguments") or "{}"
                    arguments = json.loads(raw_arguments)
                    print(
                        f"[tool] LLM called: {tool_name}({json.dumps(arguments, ensure_ascii=True)})",
                        file=sys.stderr,
                    )
                    result = self._run_tool(tool_name, arguments)
                    result_summary = len(result) if isinstance(result, list) else "1 object"
                    print(f"[tool] Result: {result_summary}", file=sys.stderr)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": json.dumps(result, ensure_ascii=False),
                        }
                    )

                print("[summary] Feeding tool results back to LLM", file=sys.stderr)

            return "I couldn't finish the tool-calling loop."
        except Exception as error:
            return f"LLM error: {error}"
