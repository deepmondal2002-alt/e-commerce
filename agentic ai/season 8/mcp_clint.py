import asyncio
from typing import Annotated, TypedDict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from my_library import tools


class State(TypedDict):
    messages: Annotated[list, add_messages]


def build_app():
    llm = ChatGoogleGenerativeAI(model="gemini-flash-latest")
    llm_with_tools = llm.bind_tools(tools)

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "you are a helpful assistant that uses tools to get the current weather for a location"),
        MessagesPlaceholder("messages"),
    ])

    chat_llm = prompt_template | llm_with_tools

    def chat_node(state: State) -> State:
        return {"messages": [chat_llm.invoke({"messages": state["messages"]})]}

    graph = StateGraph(State)
    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", ToolNode(tools=tools))
    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges(
        "chat_node",
        tools_condition,
        {"tools": "tools", "__end__": END},
    )
    graph.add_edge("tools", "chat_node")

    return graph.compile(checkpointer=MemorySaver())


async def main():
    app = build_app()
    config = {"configurable": {"thread_id": "weather-1"}}

    while True:
        user_input = input("\nAsk about the weather (or type 'exit'): ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break

        result = await app.ainvoke(
            {"messages": [HumanMessage(content=user_input)]}, config
        )
        print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
