from src.langgraph_agenticai.state.state import State
from src.langgraph_agenticai.utils.logger import logger

class BasicChatbotNode:
    
    def __init__(self,model):  
        self.llm =model
        
    def process(self,state:State)->dict:
        """
        Processes the input state and generates a chatbot response
        """
        logger.info("BasicChatbotNode","Started",{"input": str(state['messages'])[:200]})
        response = self.llm.invoke(state['messages'])
        logger.info("BasicChatbotNode", "Finished")  # add
        return {"messages": response}
        