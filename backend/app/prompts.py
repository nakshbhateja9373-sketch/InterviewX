import re
from pathlib import Path
from typing import Dict, Any
from backend.app.config import PROMPTS_DIR

class PromptManager:
    def __init__(self, prompts_base_dir: Path = PROMPTS_DIR):
        self.base_dir = prompts_base_dir
        self.final_dir = self.base_dir / "final"
        self.v1_dir = self.base_dir / "v1"
        self.v2_dir = self.base_dir / "v2"
        self.v3_dir = self.base_dir / "v3"

    def _read_file(self, path: Path) -> str:
        if not path.exists():
            raise FileNotFoundError(f"Prompt template file not found: {path}")
        return path.read_text(encoding="utf-8")

    def get_prompt_text(self, version: str, name: str) -> str:
        """Retrieve raw prompt text by version ('v1', 'v2', 'v3', 'final') and filename."""
        target_dir = self.base_dir / version
        file_path = target_dir / name
        return self._read_file(file_path)

    def render(self, template: str, variables: Dict[str, Any]) -> str:
        """Safely format prompt template with variables, preserving JSON brackets."""
        # Replace only tokens matching {var_name} where var_name is in variables
        def replace_token(match):
            key = match.group(1)
            if key in variables:
                val = variables[key]
                if isinstance(val, (list, tuple)):
                    return "\n- " + "\n- ".join(str(v) for v in val) if val else "None"
                return str(val)
            return match.group(0)

        # Regex for {word}
        return re.sub(r"\{([a-zA-Z0-9_]+)\}", replace_token, template)

    def get_question_generation_prompt(self, variables: Dict[str, Any]) -> str:
        template = self._read_file(self.final_dir / "question_generation.txt")
        return self.render(template, variables)

    def get_answer_evaluation_prompt(self, variables: Dict[str, Any]) -> str:
        template = self._read_file(self.final_dir / "answer_evaluation.txt")
        return self.render(template, variables)

    def get_follow_up_prompt(self, variables: Dict[str, Any]) -> str:
        template = self._read_file(self.final_dir / "follow_up_generation.txt")
        return self.render(template, variables)

    def get_final_summary_prompt(self, variables: Dict[str, Any]) -> str:
        template = self._read_file(self.final_dir / "final_interview_summary.txt")
        return self.render(template, variables)

prompt_manager = PromptManager()
