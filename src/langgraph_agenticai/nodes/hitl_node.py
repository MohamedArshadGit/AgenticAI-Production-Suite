

from langgraph_agenticai.state.state import State
from langgraph_agenticai.utils.logger import logger


class HITLNode:
    def process(self, state: State) -> dict:
        """
        This node does NOT execute anything.
        It just pauses the graph and returns state as-is.
        The actual user decision (approve/reject/select)
        happens in the Streamlit UI — not here.
        LangGraph will interrupt BEFORE this node runs
        via interrupt_before=["hitl"] in graph compile.
        """
        logger.info("HITLNode", "Graph paused for human input",
                    {"pattern": state.get("hitl_pattern"),
                     "message": state.get("hitl_message")})

        return {}  # return empty — state unchanged, just a pause point