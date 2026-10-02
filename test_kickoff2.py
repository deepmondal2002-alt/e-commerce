import os
from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv

load_dotenv(r'D:\vector_databse\.env')

llm = LLM(
    model="openai/gemini-1.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY"),
    api_base="https://generativelanguage.googleapis.com/v1beta/openai/"
)

agent = Agent(
    role="Support",
    goal="Help",
    backstory="You are help",
    llm=llm
)

task = Task(
    description="I bought an item and I dont like it. I want to return it. What is your return policy for this case?",
    expected_output="Return policy details",
    agent=agent
)

crew = Crew(
    agents=[agent],
    tasks=[task],
    verbose=True
)

crew.kickoff()
print("Success!")
