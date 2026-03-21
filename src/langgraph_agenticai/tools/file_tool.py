import os
from langchain.tools import tool

@tool
def file_reader_tool(file_path:str)->str:
    """
    Reads and returns the contents of a text file from the given file path.
    Use this when the user wants to read or view the contents of a file.
    """
    try:
        if not os.path.exists(file_path): #Check if file exists
            return f"Error: File not Found  at path : {file_path}"
        
        if not os.path.isfile(file_path):
            return f"Error : File;{file_path} provided is a Directory and not a file"

        allowed_extensions = [".txt", ".md", ".csv", ".json", ".py", ".yaml", ".yml"]
        _,ext =os.path.splitext(file_path)
        # os.path.splitext splits a filename into two parts:# python os.path.splitext("/home/data.csv")# # returns → ("/home/data", ".csv")  ← a tuple of 2 values# So you need two variables to unpack it:# pythonname, ext = os.path.splitext("/home/data.csv")# # name = "/home/data"# # ext  = ".csv"
        if ext.lower() not in allowed_extensions:
            return f'{ext.lower()} not allowed. Use any of these: {allowed_extensions}'

        with open(file_path,"r",encoding='utf-8') as f:
            content =f.read()

        return f'file contents of {file_path} is;:\n\n {content}'

    except PermissionError:
        return f"Error: Permission denied to read '{file_path}'"
    except Exception as e:
        return f"Error reading file: {str(e)}"


        

    except:
        pass