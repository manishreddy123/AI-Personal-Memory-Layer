def run_chat(agent):
    print("📥 AI Personal Memory Assistant ready. Ask anything or type 'exit'.\n")
    while True:
        query = input("You: ")
        if query.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        try:
            response = agent.invoke({"input": query})
            print("AI:", response["output"])
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again or type 'exit' to quit.")
