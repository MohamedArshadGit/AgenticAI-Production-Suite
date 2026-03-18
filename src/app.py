# main.py contains the core function that loads your LangGraph + Streamlit UI.
# app.py is just a launcher script

import sys,os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.langgraph_agenticai.main import load_langgraph_agenticai_app

if __name__=="__main__":
    load_langgraph_agenticai_app()