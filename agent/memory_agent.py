from langchain.agents import create_react_agent, AgentExecutor
from langchain_community.llms import Ollama
from langchain.tools import Tool
from langchain import hub

def build_agent(qa_chain):
    tools = [
        Tool(
            name="Ask_Personal_Assistant",
            func=qa_chain.invoke,
            description="Answer questions about your memory using documents, emails, and calendar data."
        )
    ]
    
    llm = Ollama(model="llama3.2", temperature=0)
    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    return agent_executor
