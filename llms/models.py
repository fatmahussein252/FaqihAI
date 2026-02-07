from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import Settings, get_settings

class Models:
    def __init__(self):
        self.settings = get_settings()

    def create_llms(self):
        return {
            "llm_master": ChatGoogleGenerativeAI(
                model=self.settings.MODEL_NAME,
                temperature=0.7,
                google_api_key=self.settings.MASTER_API_KEY
            ),
            "llm_formatter": ChatGoogleGenerativeAI(
                model=self.settings.MODEL_NAME,
                temperature=0.7,
                google_api_key=self.settings.RAG_FORMATTER_API_KEY
            ),
            "llm_rag": ChatGoogleGenerativeAI(
                model=self.settings.MODEL_NAME,
                temperature=0.7,
                google_api_key=self.settings.RAG_AGENT_API_KEY
            ),
            "llm_filter": ChatGoogleGenerativeAI(
                model=self.settings.MODEL_NAME,
                temperature=0.7,
                google_api_key=self.settings.FILTER_API_KEY
            ),
            "llm_fiqh": ChatGoogleGenerativeAI(
                model=self.settings.MODEL_NAME,
                temperature=0.7,
                google_api_key=self.settings.FIQH_API_KEY
            ),
            "llm_mazhab": ChatGoogleGenerativeAI(
                model=self.settings.MODEL_NAME,
                temperature=0.7,
                google_api_key=self.settings.MAZHAB_API_KEY
            ),
            "llm_fatwa": ChatGoogleGenerativeAI(
                model=self.settings.MODEL_NAME,
                temperature=0.7,
                google_api_key=self.settings.FATWA_API_KEY
            ),
            "llm_thread_classifier": ChatGoogleGenerativeAI(
                model=self.settings.MODEL_NAME,
                temperature=0.7,
                google_api_key=self.settings.THREAD_CLASSIFIER_API_KEY
            ),
            "llm_command_preprocessor": ChatGoogleGenerativeAI(
                model=self.settings.MODEL_NAME,
                temperature=0.7,
                google_api_key=self.settings.COMMAND_PREPROCESSOR_API_KEY
            ),
        }





