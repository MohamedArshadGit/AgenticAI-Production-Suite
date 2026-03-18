import os
import streamlit as st
from langchain_groq import ChatGroq

#Rules for modular coding
# - Add `self` as first parameter
# - Move external dependencies (llm etc) into `__init__`
# NOTEBOOK thinking:
# "I write code top to bottom, run it once"

# MODULAR thinking:
# "I build lego pieces, then connect them"

class GroqLLM:
    def __init__(self,user_controls_input):
        self.user_controls_input =user_controls_input
        # stores the dictionary
        # {
        #   "GROQ_API_KEY": "gsk_abc123...",
        #   "selected_groq_model": "llama3-8b-8192"
        # }s

    def get_llm_model(self):
        try:
            # pulls values OUT of the dictionary
            groq_api_key =self.user_controls_input['GROQ_API_KEY']
            # groq_api_key = "abc123"
            selected_groq_model=self.user_controls_input['selected_groq_model']
            # selected_groq_model = "llama3-8b-8192"
            if groq_api_key=="" and os.environ['GROQ_API_KEY'] =="":
                st.error("Please Enter Groq API Key to use it")
            # creates the actual LLM object
            llm =ChatGroq(api_key=groq_api_key,model=selected_groq_model)
            # llm = ChatGroq object — ready to talk to Groq API
        
        except Exception as e:
            raise ValueError(f"Error Occured with :{e}")

        return llm #sends this object back to main.py
