from agent.conversation import ConversationAgent
from agent.llm import GeminiLLM

print("TikTok AI Agent booting...")

llm = GeminiLLM()
agent = ConversationAgent(llm)

print("Agent ready. Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    response = agent.ask(user_input)
    print("\nAgent:", response, "\n")
