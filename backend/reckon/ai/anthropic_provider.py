import json
from typing import Dict

import anthropic
from django.conf import settings

from reckon.ai.base import AIProvider
from reckon.ai.prompts import (
    ADVISOR_SCHEMA,
    ADVISOR_SYSTEM_PROMPT,
    CHALLENGE_SCHEMA,
    CHALLENGE_SYSTEM_PROMPT,
    build_challenge_prompt,
)

MAX_TOKENS = 16000
# Routes the request to another Claude model if a safety classifier declines it,
# so a single refusal never surfaces as a broken feature. Safe to remove.
FALLBACK_BETA = "server-side-fallback-2026-07-01"


class AnthropicProvider(AIProvider):
    """Real provider. Needs ANTHROPIC_API_KEY and network access."""

    name = "anthropic"

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY or None)
        self.model = settings.AI_MODEL

    def challenge(self, decision: Dict) -> Dict:
        response = self.client.beta.messages.create(
            model=self.model,
            max_tokens=MAX_TOKENS,
            betas=[FALLBACK_BETA],
            fallbacks="default",
            system=CHALLENGE_SYSTEM_PROMPT,
            thinking={"type": "adaptive"},
            output_config={
                "effort": "medium",
                "format": {"type": "json_schema", "schema": CHALLENGE_SCHEMA},
            },
            messages=[{"role": "user", "content": build_challenge_prompt(decision)}],
        )
        text = next(block.text for block in response.content if block.type == "text")
        return json.loads(text)

    def advise(self, question, topic, profile, track_record, assessment, history):
        messages = [{"role": message["role"], "content": message["content"]} for message in history]
        messages.append(
            {
                "role": "user",
                "content": (
                    f"Topic: {topic}\n\n"
                    f"My profile:\n{json.dumps(profile, indent=2)}\n\n"
                    f"My track record on past decisions:\n{json.dumps(track_record, indent=2)}\n\n"
                    + (
                        f"Arithmetic already computed from my profile — use these figures verbatim, "
                        f"do not recalculate:\n{json.dumps(assessment, indent=2)}\n\n"
                        if assessment
                        else "No purchase arithmetic applies to this question.\n\n"
                    )
                    + f"My question: {question}"
                ),
            }
        )

        response = self.client.beta.messages.create(
            model=self.model,
            max_tokens=MAX_TOKENS,
            betas=[FALLBACK_BETA],
            fallbacks="default",
            system=ADVISOR_SYSTEM_PROMPT,
            thinking={"type": "adaptive"},
            output_config={
                "effort": "medium",
                "format": {"type": "json_schema", "schema": ADVISOR_SCHEMA},
            },
            messages=messages,
        )
        text = next(block.text for block in response.content if block.type == "text")
        return json.loads(text)
