from configparser import ConfigParser # this will read config from uni file 
import os 
class Config:
    # def __init__(self,config_file=r"CHATBOT\src\langgraph_agenticai\ui\uiconfigfile.ini"):
    #     self.config =ConfigParser()
    #     self.config.read(config_file)
    #above is not working due to directory hierarchy 
    
    def __init__(self):
        # Get the directory where uiconfigfile.py is located
        #Find where (uiconfigfile.py) am located, then look for uiconfigfile.ini in that same folder
        base_dir = os.path.dirname(os.path.abspath(__file__)) # this line gives folder path not point to file,,, __file__ gives the current file's full path, os.path.abspath(__file__) ensures it's always the absolute full path:
        config_file = os.path.join(base_dir, "uiconfigfile.ini") #here is it joining gthe folder given by base_dir and adding the uiconfigfile.ini (is where this file is located)
        
        self.config = ConfigParser()
        self.config.read(config_file)

    def get_llm_options(self):
        return self.config['DEFAULT'].get('LLM_OPTIONS').split(', ')
    
    def get_usecase_options(self):
        return self.config['DEFAULT'].get('USECASE_OPTIONS').split(', ')
    
    def get_groq_model_options(self):
        return self.config['DEFAULT'].get('GROQ_MODEL_OPTIONS').split(', ')
    
    def get_page_title(self):
        return self.config['DEFAULT'].get('PAGE_TITLE')
    

    
