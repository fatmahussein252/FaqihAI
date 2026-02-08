from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from config.system_prompts import SYSTEM_PROMPTS
from llms import Models
from utils.parsers import parse_json_output

class RAGChains:
    def __init__(self):
        self.models = Models.create_llms()
        self._init_prompts()
        self._init_chains()

    def __init_prompts(self):
        # Initialize all prompt templates
        self.rag_formatter_prompt = PromptTemplate(
            input_variables=["input", "related_threads"],
            template=f"""{SYSTEM_PROMPTS["rag_formatter_prompt"]}
                        Input: {{input}}
                        Related Threads: {{related_threads}}"""
        )
        
        self.rag_agent_prompt = PromptTemplate(
            input_variables=["category", "question"],
            template="""Simulate an islamic fiqh RAG agent response for category: 
                        {category} and question: {question}.
                        Provide a concise fiqh answer with one or more citation in formal Arabic 
                        from a proper book or group of books related to the {category}.
                        No English text nor side comments allowed. Mention book name clearly and 
                        leave two empty lines at the end of your response."""
        )
        
        self.rag_output_formatter_prompt = PromptTemplate(
            input_variables=["rag_output", "chat_history"],
            template=f"""{SYSTEM_PROMPTS["rag_output_formatter_prompt"]}
                        Input:
                        - RAG Output: {{rag_output}}
                        - Chat History: {{chat_history}}
                        """
        )
        
    def _init_chains(self):
        # Initialize all classifier chains
        # Single classifier chains
        self.rag_formatter_chain = RunnableSequence(
            self.rag_formatter_prompt | 
            self.models["llm_formatter"] | 
            (lambda x: parse_json_output(x.content, is_formatter=True))
        )

        self.rag_agent_chain = RunnableSequence(
            self.rag_agent_prompt | 
            self.models["llm_rag"] | 
            (lambda x: parse_json_output(x.content))
        )

        self.rag_output_formatter_chain =RunnableSequence(
            self.rag_output_formatter_prompt | 
            self.models["llm_rag_output_formatter"] | 
            (lambda x: parse_json_output(x.content))
        )
        
        
    def format_rag_input(self, user_input: str, related_threads: list):
        # Classify user input intent
        return self.rag_formatter_chain.invoke({
            "input": user_input,
            "related_threads": related_threads
            })

    def retrieve(self, category: str, question: str):
        # Run parallel classification for fiqh, mazhab, and fatwa
        return self.rag_agent_chain.invoke({
            "category": category,
            "question": question
            })
    
    def format_rag_output(self, rag_output: str, chat_history: list):
        # Classify thread type and relations
        return self.rag_output_formatter_chain.invoke({
            "rag_output": rag_output,
            "chat_history": chat_history
        })
    
   