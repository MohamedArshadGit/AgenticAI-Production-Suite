from typing import TypedDict,Annotated,List

from langgraph.graph.message import add_messages

class State(TypedDict):
    """
    Represents the Structure of the State Used in Graph
    """
    messages:Annotated[List,add_messages]