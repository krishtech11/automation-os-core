# backend/app/core/llm_planner_free.py

"""
LLM-based workflow planner using FREE local models (Ollama)
No API costs, runs completely offline!
"""

import json
import logging
import re
import requests
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


# -----------------------------
# SAFE JSON PARSER (LLM REPAIR)
# -----------------------------

def safe_parse_json(response_text: str) -> Dict:
    """
    Safely parse LLM JSON output.
    Repairs common formatting issues.
    """

    try:
        return json.loads(response_text)

    except json.JSONDecodeError:

        cleaned = response_text.strip()

        # remove trailing commas
        cleaned = re.sub(r',\s*}', '}', cleaned)
        cleaned = re.sub(r',\s*]', ']', cleaned)

        # remove newlines that break JSON
        cleaned = cleaned.replace("\n", " ")

        try:
            return json.loads(cleaned)

        except Exception:
            raise ValueError("LLM returned invalid JSON even after repair")


# -----------------------------
# LLM PLANNER
# -----------------------------

class FreeLLMPlanner:
    """
    Uses FREE local LLM via Ollama for workflow planning
    """

    def __init__(self):

        self.ollama_url = "http://localhost:11434/api/generate"

        # fast and small model
        self.model = "llama3.2:3b"

        self.available_workflows = {
            "NEWS_DIGEST": {
                "description": "Fetch news from NewsAPI and send via email",
                "params": ["email", "category", "country", "limit"],
            },
            "FILE_CLEANUP": {
                "description": "Scan, rename, and organize files",
                "params": ["folder", "file_pattern", "action", "rename_pattern"],
            },
            "INVOICE_SYNC": {
                "description": "Extract invoices from Gmail and upload to Drive",
                "params": ["gmail_filter", "drive_folder", "organize_by_date"],
            },
        }

    # -----------------------------
    # CHECK OLLAMA
    # -----------------------------

    def check_ollama_available(self) -> bool:

        try:

            response = requests.get(
                "http://localhost:11434/api/tags",
                timeout=3
            )

            if response.status_code != 200:
                return False

            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]

            if self.model in model_names:

                logger.info(f"Ollama is running with model: {self.model}")
                return True

            logger.warning(
                f"Model {self.model} not found. Available models: {model_names}"
            )

            return False

        except Exception as e:

            logger.warning(f"Ollama not available: {str(e)}")
            return False

    # -----------------------------
    # PROMPT CREATION
    # -----------------------------

    def create_planning_prompt(self, user_input: str) -> str:

        workflows_desc = json.dumps(self.available_workflows, indent=2)

        prompt = f"""
You are a workflow planning assistant.

Available workflows:
{workflows_desc}

User request:
"{user_input}"

Return ONLY valid JSON with this format:

{{
 "analysis": "...",
 "steps": [
   {{
     "step_number": 1,
     "workflow_type": "WORKFLOW_NAME",
     "description": "...",
     "config": {{}},
     "depends_on": []
   }}
 ],
 "schedule": "schedule",
 "confidence": 0.95
}}

User request:
"""

        return prompt

    # -----------------------------
    # OLLAMA CALL
    # -----------------------------

    def call_ollama(self, prompt: str) -> str:

        try:

            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 500,
                },
            }

            logger.info(f"Calling Ollama with model: {self.model}")

            # --- TIMEOUT PROTECTION ---
            response = requests.post(
                self.ollama_url,
                json=data,
                timeout=90
            )

            response.raise_for_status()

            result = response.json()

            generated_text = result.get("response", "").strip()

            if not generated_text:
                raise ValueError("Empty response from Ollama")

            logger.info(
                f"Ollama response received ({len(generated_text)} chars)"
            )

            return generated_text

        except requests.exceptions.ConnectionError:

            raise ConnectionError(
                "Cannot connect to Ollama. Start with: ollama serve"
            )

        except requests.exceptions.Timeout:

            raise TimeoutError(
                "Ollama request timed out (model too slow)"
            )

        except Exception as e:

            logger.error(f"Ollama API error: {str(e)}")
            raise

    # -----------------------------
    # RESPONSE PARSER
    # -----------------------------

    def parse_llm_response(self, response_text: str) -> Dict:

        try:

            text = response_text.strip()

            # remove markdown blocks
            if "```" in text:

                text = text.replace("```json", "")
                text = text.replace("```", "")

            # extract JSON region
            start = text.find("{")
            end = text.rfind("}")

            if start != -1 and end != -1:
                text = text[start:end + 1]

            plan = safe_parse_json(text)

            # basic validation
            required_keys = [
                "analysis",
                "steps",
                "schedule",
                "confidence",
            ]

            for key in required_keys:
                if key not in plan:
                    raise ValueError(f"Missing key: {key}")

            if not isinstance(plan["steps"], list) or not plan["steps"]:
                raise ValueError("Invalid steps format")

            return plan

        except Exception as e:

            logger.error(
                f"Failed to parse JSON from Ollama: {str(e)}"
            )

            raise

    # -----------------------------
    # MAIN PLANNER
    # -----------------------------

    def plan_workflow(self, user_input: str) -> Tuple[Dict, float]:

        if not self.check_ollama_available():

            raise ConnectionError(
                "Ollama not running. Run: ollama serve"
            )

        logger.info(
            f"Planning workflow with FREE LLM for: {user_input}"
        )

        prompt = self.create_planning_prompt(user_input)

        response = self.call_ollama(prompt)

        plan = self.parse_llm_response(response)

        confidence = plan.get("confidence", 0.5)

        logger.info(
            f"Plan created with {len(plan['steps'])} steps (confidence {confidence})"
        )

        return plan, confidence

    # -----------------------------
    # CONVERT TO TASK
    # -----------------------------

    def simplify_plan_for_single_task(
        self, plan: Dict
    ) -> Tuple[str, Dict, str]:

        if not plan["steps"]:
            raise ValueError("Plan has no steps")

        step = plan["steps"][0]

        workflow_type = step["workflow_type"]
        config = step["config"]
        schedule = plan["schedule"]

        return workflow_type, config, schedule


# -----------------------------
# SINGLETON
# -----------------------------

free_llm_planner = None


def init_free_llm_planner():

    global free_llm_planner

    free_llm_planner = FreeLLMPlanner()

    return free_llm_planner


def get_free_llm_planner():

    return free_llm_planner