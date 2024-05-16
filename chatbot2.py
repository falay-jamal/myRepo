import os
# import openai
from langchain.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate
)
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
# from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

class Chatbot2:
    """Class definition for a single chatbot with memory, created with LangChain."""
    
    def __init__(self, engine):
        """Select backbone large language model, as well as instantiate 
        the memory for creating language chain in LangChain.
        
        Args:
        --------------
        engine: the backbone llm-based chat model.
                "OpenAI" stands for OpenAI chat model;
                Other chat models are also possible in LangChain, 
                see https://python.langchain.com/en/latest/modules/models/chat/integrations.html
        """
        
        # Instantiate llm
        if engine == 'OpenAI':
            # OpenAI key setup
            os.environ["OPENAI_API_KEY"] = "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"
            self.llm = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0.7
            )
        else:
            raise KeyError("Currently unsupported chat model type!")
        
        # Instantiate memory
        self.memory = ConversationBufferMemory(return_messages=True)
        self.conversation = None

    def start_conversation(self):
        """Starts a conversation between the user and the chatbot."""
        
        # Define prompt template
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self._specify_system_message()),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("""{input}""")
        ])
        
        # Create conversation chain
        self.conversation = ConversationChain(memory=self.memory, prompt=prompt, 
                                              llm=self.llm, verbose=False)
        self.conversation.prompt = prompt
        
        # Start the conversation
        # self.conversation.start()



    def _specify_system_message(self):
        """Specify the behavior of the chatbot."""
        
        purpose = "This chatbot is designed to assist users in learning English through conversation. Act as a language teacher, make the answers easy to understand as the user's vocabulary is limited. Give the users different scenarios or exercises to practice. You may ask questions in grammar, conjugation, and vocabulary. Give feedback. Also correct the grammatical or spelling errors if there's any by providing more accurate answers. Give one exercise after the other. Avoid hallucinations and be precise and accurate in your feedbacks."

        system_message = f"{purpose}\n"

        return system_message
# chatbot = Chatbot2('OpenAI')
# chatbot.start_conversation()

# Generate a response
