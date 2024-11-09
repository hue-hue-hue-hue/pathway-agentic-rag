from typing import Dict
from .base import BaseAgent


# acts like a adaRAG for now
class ClassifierAgent(BaseAgent):
    def __init__(self):
        instructions = """You are a specialized classification agent. Your role is to analyze queries and classify them based on:
        
        Complexity:
        - STRAIGHTFORWARD: Can be answered directly with general knowledge
        - SIMPLE: Needs basic context but straightforward to answer
        - COMPLEX: Requires extensive research or complex reasoning
        
        NOTE: THESE ARE FINANCE OR LEGAL RELATED QUESTIONS SO COMPLEXITY IS WITH RESPECT TO FINANCE OR LEGAL POINT OF VIEW
           
        Respond in the following JSON format:
        {
            "complexity": "STRAIGHTFORWARD|SIMPLE|COMPLEX",
            "reason": "Brief explanation of why this classification was chosen"
        }"""

        super().__init__(
            name="Query Classifier",
            model="llama3.2",
            instructions=instructions,
            functions=[],
        )

    def classify(self, query: str) -> Dict[str, str]:
        response = self.process(query)
        # Assuming the response is in JSON format as requested in the instructions
        try:
            response_content = response.messages[-1]["content"]
            classification = eval(response_content)
            return {
                "complexity": classification["complexity"],
                "reason": classification["reason"],
            }
        except Exception as e:
            return {
                "complexity": "COMPLEX",
                "reason": "Failed to parse response: defaulting to complex",
            }
