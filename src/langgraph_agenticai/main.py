# main.py contains the core function that loads your LangGraph + Streamlit UI.
# app.py is just a launcher script

import streamlit as st
from src.langgraph_agenticai.ui.streamlitui.loadui import LoadStreamlitUI
from src.langgraph_agenticai.llms.groqllm import GroqLLM
from src.langgraph_agenticai.graph.graph_builder import GraphBuilder
from src.langgraph_agenticai.ui.streamlitui.display_result import DisplayResultStreamlit
from src.langgraph_agenticai.utils.logger import logger,callback_handler

import os
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_PROJECT'] = 'CHATBOT'

from dotenv import load_dotenv
load_dotenv()


def load_langgraph_agenticai_app():
    """
    Loads and runs the LangGraph AgenticAI application with Streamlit UI.
    This function initializes the UI, handles user input, configures the LLM model,
    sets up the graph based on the selected use case, and displays the output while 
    implementing exception handling for robustness.

    """

    ui =LoadStreamlitUI()
    user_input =ui.load_streamlit_ui()
    # user_input is a dictionary like this:
# {
#     "GROQ_API_KEY": "abc123...",
#     "selected_groq_model": "llama3-8b-8192",
#     "selected_usecase": "Basic Chatbot"
#User fills the sidebar — API key, model, usecase. All stored in user_input dictionary.
# }

    if not user_input:
        st.error("Error: Failed to load user input from the UI.")
        return
    
    user_message = st.chat_input("Enter your message:") 

    if user_message:
        try:
            logger.info("Main", "App started", {"message": user_message}) 
            # configure the LLM's
            obj_llm_config =GroqLLM(user_controls_input=user_input) #this is GroqLLM class
            model =obj_llm_config.get_llm_model() # from groqllm.py's file(get_llm_model method has groq api key,model)

            if not model:
                st.error('Error : LLM model could not be initialized')
                return 

            #Iniitalize and setup the graph based on usecase
            usecase = user_input.get('selected_usecase')
            print(f"DEBUG usecase = '{usecase}'")   # add this line

            if not usecase:
                st.error('Error: No use Case Selected .Please select Any one of the UseCase')
                return

            graph_builder =GraphBuilder(model) #GraphBuilder Class
            try:
                graph =graph_builder.setup_graph(usecase=usecase)
                config = {"callbacks": [callback_handler]} #tells LangGraph:"whenever you run, call these callback methods automatically so on_chain_start, on_llm_start etc all fire automatically
                logger.info("Main", "Graph built", {"usecase": usecase}) 

                #once graph executed and return go to display result code 
                DisplayResultStreamlit(usecase,graph,user_message,config).display_result_on_ui() #use config here to display callback handler
            except Exception as e:
                logger.error("Main", "Graph failed", {"error": str(e)})
                st.error(f"Error:Graph Setup Failed->{e}")
                return



        except Exception as e:
            logger.error("Main", "App failed", {"error": str(e)})
            st.error(f" Error: GroqLLM or usecase or all Failed {e}")
            return



    

