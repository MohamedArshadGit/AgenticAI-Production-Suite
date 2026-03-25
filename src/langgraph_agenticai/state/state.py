from typing import TypedDict,Annotated,List,Optional

from langgraph.graph.message import add_messages

class State(TypedDict):
    """
    Represents the Structure of the State Used in Graph

    Fields:
    ─────────────────────────────────────────────────
    messages           : full conversation history
    
    ─────────────────────────── HITL fields ───────────────────────────
    hitl_required      : True if HITL pause needed
    hitl_pattern       : which pattern triggered
                         "sensitive_tool" / "ambiguity"
    hitl_approved      : True=approved, False=rejected, None=pending
    hitl_message       : message shown to user in approval UI
    hitl_options       : list of options for ambiguity resolution
    confidence_score   : final confidence score 
    sensitive_tools    : list of sensitive tools agent wants to call 
    """
    messages:Annotated[List,add_messages]

    #HITL(Human in the loop) Fields
    hitl_required      : Optional[bool]          # is HITL needed?
    hitl_pattern       : Optional[str]           # which pattern triggered
    hitl_approved      : Optional[bool]          # user decision
    hitl_message       : Optional[str]           # shown in UI
    hitl_options       : Optional[List[str]]     # ambiguity options (Pattern 6)
    #confidence_score   : Optional[float]         # 0-100 (Pattern 4)
    sensitive_tools    : Optional[List[str]]     # tools needing approval (Pattern 1)

