from typing import Optional, List, Dict, Any, Union
from swarm import Agent, Swarm

# from openai import OpenAI


class BaseAgent:
    def __init__(
        self,
        name: str,
        model: str = "llama3.2",
        instructions: Optional[str] = None,
        functions: Optional[List] = None,
    ):
        self.name = name
        self.model = model
        self.instructions = instructions or "You are a helpful agent."
        self.functions = functions or []
        self.agent = self._initialize_agent()

    def _initialize_agent(self) -> Agent:
        return Agent(
            name=self.name,
            model=self.model,
            instructions=self.instructions,
            functions=self.functions,
        )

    def process(
        self, query: str, context_variables: Optional[Dict[str, Any]] = None
    ) -> Union[Dict[str, Any], Any]:
        # ollama_client = OpenAI(base_url="http://localhost:11434/v1", api_key="fake_key")
        # client = Swarm(client=ollama_client)
        client = Swarm()
        messages = [{"role": "user", "content": query}]
        response = client.run(
            agent=self.agent,
            messages=messages,
            context_variables=context_variables or {},
        )
        return response
