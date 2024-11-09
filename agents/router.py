from .classifier import ClassifierAgent
import json
from typing import Dict, Any
from rich.panel import Panel
from rich.console import Console


class AgentRouter:
    def __init__(self):
        self.classifier = ClassifierAgent()
        self.console = Console()

    def _log_agent_execution(
        self, agent_name: str, purpose: str, output: Dict[str, Any]
    ) -> None:
        """Pretty print agent execution details"""
        self.console.print(
            Panel(
                f"[bold blue]Agent:[/bold blue] {agent_name}\n"
                f"[bold green]Purpose:[/bold green] {purpose}\n"
                f"[bold yellow]Output:[/bold yellow] {json.dumps(output, indent=2)}",
                title="🤖 Agent Execution Log",
                border_style="cyan",
            )
        )

    def route_query(self, query: str):
        """Route the query to the finance agent after classification"""

        classification = self.classifier.classify(query)
        self._log_agent_execution(
            agent_name="Classifier Agent",
            purpose="Determine query complexity and routing",
            output=classification,
        )

        # TODO: result me final result aayega pipeline khtm hone ke baad
        result = None

        return result
