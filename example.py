from agents.router import AgentRouter
from dotenv import load_dotenv

load_dotenv()
# Initialize the router
router = AgentRouter()

# Test some queries
queries = [
    "What is compound interest?",
    "Can you explain the implications of insider trading?",
    "What are the legal requirements for starting a hedge fund?",
    "How do I calculate my tax deductions?",
]

for query in queries:
    print("\nProcessing query:", query)
    result = router.route_query(query)
    # print("Result:", result)
