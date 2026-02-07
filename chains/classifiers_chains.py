from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence, RunnableParallel
from config.settings import get_settings
from config.system_prompts import SYSTEM_PROMPTS
from llms import Models
from utils.parsers import parse_json_output

class ClassifiersChains:
    def __init__(self):
        self.settings = get_settings()
        self.models = Models.create_llms()
        self._init_prompts()
        self._init_chains()
    
    def _init_prompts(self):
        # Initialize all prompt templates
        self.filter_prompt = PromptTemplate(
            input_variables=["input"],
            template=f"""{SYSTEM_PROMPTS["filter_prompt"]}
                         Text: {{input}}"""
        )
        
        self.fiqh_prompt = PromptTemplate(
            input_variables=["input"],
            template=f"""{SYSTEM_PROMPTS["fiqh_prompt"]}
                         Input: {{input}}"""
        )
        
        self.mazhab_prompt = PromptTemplate(
            input_variables=["input"],
            template=f"""{SYSTEM_PROMPTS["mazhab_prompt"]}
                         Text: {{input}}"""
        )
        
        self.fatwa_prompt = PromptTemplate(
            input_variables=["input"],
            template=f"""{SYSTEM_PROMPTS["fatwa_prompt"]}
                         Input: {{input}}"""
        )
        
        self.thread_classifier_prompt = PromptTemplate(
            input_variables=["input", "thread_history"],
            template=f"""{SYSTEM_PROMPTS["thread_classifier_prompt"]}
                         Input: {{input}}
                         Thread History: {{thread_history}}"""
        )
        
        self.command_preprocessor_prompt = PromptTemplate(
            input_variables=["input"],
            template=f"""{SYSTEM_PROMPTS["command_preprocessor_prompt"]}
                         Input: {{input}}"""
        )
    
    def _init_chains(self):
        """Initialize all classifier chains"""
        # Single classifier chains
        self.filter_chain = RunnableSequence(
            self.filter_prompt | 
            self.models["llm_filter"] | 
            (lambda x: parse_json_output(x.content))
        )

        self.command_preprocessor_chain = RunnableSequence(
            self.command_preprocessor_prompt | 
            self.models["llm_command_preprocessor"] | 
            (lambda x: parse_json_output(x.content))
        )

        self.parallel_classifiers = RunnableParallel(
            fiqh=self.fiqh_prompt | self.models["llm_fiqh"] | (lambda x: parse_json_output(x.content)),
            mazhab=self.mazhab_prompt | self.models["llm_mazhab"] | (lambda x: parse_json_output(x.content)),
            fatwa=self.fatwa_prompt | self.models["llm_fatwa"] | (lambda x: parse_json_output(x.content))
        ) 
    
    def classify_intent(self, user_input: str):
        # Classify user input intent
        return self.filter_chain.invoke({"input": user_input})

    def classify_fiqh_parallel(self, user_input: str):
        # Run parallel classification for fiqh, mazhab, and fatwa
        return self.parallel_classifiers.invoke({"input": user_input})
    
    def classify_thread(self, user_input: str, thread_history: list):
        # Classify thread type and relations
        return self.thread_classifier_chain.invoke({
            "input": user_input,
            "thread_history": thread_history
        })
    
    def preprocess_command(self, user_input: str):
        # Preprocess command-type inputs
        return self.command_preprocessor_chain.invoke({"input": user_input})


        
