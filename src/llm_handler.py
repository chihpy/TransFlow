"""
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai  import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain.schema import BaseMessage
from typing import List

class LLMHandler:
    def __init__(self, model_provider: str = "ollama", model_name: str = "gpt-4.1", temperature: float = 0, json_mode=False):
        if model_provider == 'ollama':
            if json_mode:
                self.llm = ChatOllama(
                    model=model_name, 
                    temperature=temperature,
                    model_kwargs={"response_format": {"type": "json_object"}}
                )
            else:
                self.llm = ChatOllama(
                    model=model_name, 
                    temperature=temperature
                )
        elif model_provider == 'openai':
            if json_mode:
                self.llm = ChatOpenAI(
                    model_name=model_name,
                    temperature=temperature,
                    model_kwargs={"response_format": {"type": "json_object"}}
                )
            else:
                self.llm = ChatOpenAI(
                    model_name=model_name,
                    temperature=temperature
                )
        else:
            print(f'unknown model provider: {model_provider}.\n must be openai or ollama')
        self.model_name = model_name
        self.model_provider = model_provider

    def invoke(self, messages: List[BaseMessage]) -> str:
        response = self.llm.invoke(messages)
        return response.content

def get_messages():
    prompt = ChatPromptTemplate.from_messages([
        'system', 'you are a helpful assistant',
        'human', 'hi, who are you?'
    ])
    return prompt.format_messages()

def get_json_messages():
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Return ONLY valid JSON with keys: answer, reasoning."),
        ("human", "{question}")
    ])
    return prompt

if __name__ == "__main__":
    import json
    #####
    from dotenv import load_dotenv, find_dotenv
    _ = load_dotenv(find_dotenv())
    #####
    # case1: openai chat
    model_provider = 'openai'
    model_name = 'gpt-4.1-mini'
    json_mode = False
    llm = LLMHandler(model_provider=model_provider,
                     model_name=model_name,
                     json_mode=json_mode)
    message = get_messages()
    response = llm.invoke(message)
    print(f"# case1: openai chat\nresponse: {response}")
    # case2: openai json
    model_provider = 'openai'
    model_name = 'gpt-4.1-mini'
    json_mode = True
    llm = LLMHandler(model_provider=model_provider,
                     model_name=model_name,
                     json_mode=json_mode)
    message = get_json_messages()
    prompt = message.invoke({'question': 'hi, who are you?'})
    print(prompt)
    print(type(prompt))
    response = json.loads(llm.invoke(prompt))
    print(f"# case2: openai json\nresponse: {response}")
    # case3: ollama chat
    model_provider = 'ollama'
    model_name = "gpt-oss:20b"
    json_mode = False
    llm = LLMHandler(model_provider=model_provider,
                     model_name=model_name,
                     json_mode=json_mode)
    message = get_messages()
    response = llm.invoke(message)
    print(f"# case3: ollama chat\nresponse: {response}")
    # case4: ollama json
    model_provider = 'ollama'
    model_name = "gpt-oss:20b"
    json_mode = True
    llm = LLMHandler(model_provider=model_provider,
                     model_name=model_name,
                     json_mode=json_mode)
    message = get_json_messages()
    prompt = message.invoke({'question': 'hi, who are you?'})
    response = json.loads(llm.invoke(prompt))
    print(f"# case4: ollama json\nresponse: {response}")