from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence, RunnableParallel
from config.settings import get_settings
from config.system_prompts import SYSTEM_PROMPTS
from llms import Models
from utils.parsers import parse_json_output

class RAGChains:
    def __init__(self):
        pass