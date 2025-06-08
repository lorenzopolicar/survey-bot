from langchain_openai import ChatOpenAI

mini_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

llm = ChatOpenAI(model="gpt-4o", temperature=0)
