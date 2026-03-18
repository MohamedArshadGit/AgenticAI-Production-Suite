import logging,json,os # to format logs as json
from datetime import datetime # add timestamp 
from langchain_core.callbacks.base import BaseCallbackHandler #inbuilt  BaseCallbackHandler = LangChain's built in class lets you "hook into" LangGraph and listen to events automatically

os.makedirs("logs",exist_ok=True) # creates "logs" folder if it doesn't exist
# exist_ok=True means no error if folder already exists

class JSONLogger:
    def __init__(self,name='app'):
        self.logger =logging.getLogger(name)
        # getLogger creates a logger with this "app" name
        # name="app" means this logger is called "app"
        self.logger.setLevel(logging.DEBUG)
        # DEBUG = log everything
        # other levels: INFO, WARNING, ERROR, CRITICAL
        # DEBUG is lowest = captures all messages
        # only add handlers if none exist yet
        if not self.logger.handlers:
            fh =logging.FileHandler("logs/app.log")
            # fh = file handler
            # saves all logs to logs/app.log file
            ch=logging.StreamHandler()
            # ch = console handler
            # prints logs to your terminal
            self.logger.addHandler(fh)
            self.logger.addHandler(ch)
            # now logs go to BOTH file and terminal simultaneously

    def _fmt(self,level,node,msg,data={}):# _ prefix means private method — only used inside this class
        return json.dumps(
            {
                "time":datetime.utcnow().isoformat(),  # current timestamp
                "level":level,     # INFO or ERROR
                "node":node,      # which node is logging e.g. "BasicChatbotNode"
                "msg":msg,     # what happened e.g. "Node started"
                "data":data   # extra details e.g. {"input": "Hello"}


            }
        )
        # json.dumps converts Python dict → JSON string

    def info(self,node,msg,data={}):
        self.logger.info(self._fmt("INFO",node,msg,data))
        # calls _fmt to build JSON string
        # then logs it as INFO level
    
    def error(self, node, msg, data={}):
        self.logger.error(self._fmt("ERROR", node, msg, data))
        # calls _fmt to build JSON string and logs as ERROR level

class LangGraphCallbackHandler(BaseCallbackHandler):
    def __init__(self,logger=JSONLogger): #JSONLogger usage here is not inheritance ,it is-> Composition  = class RECEIVES another class → access through self.x and not inheritance
        # INHERITANCE: handler.info("node", "msg")       # direct access 
        # COMPOSITION : handler.logger.info("node", "msg") # through self.logger 
        self.logger =logger
    
    # ── Chain/Node events ──────────────────────────

    def on_chain_start(self, serialized, inputs,**kwargs): #on_chain_start,on_chain_end,on_chain_error comes from BaseCallbackHandler
        self.logger.info("Graph", "Node started", {"inputs": str(inputs)[:200]})
        # on_chain_start = LangChain calls this AUTOMATICALLY
        # every time a node/chain starts running
        # str(inputs)[:200] = convert to string, take first 200 chars only
    
    def on_chain_end(self, outputs, **kwargs):
        self.logger.info("Graph", "Node finished", {"outputs": str(outputs)[:200]})
        # called AUTOMATICALLY when node finishes
    
    def on_chain_error(self, error, **kwargs):
        self.logger.error("Graph", "Node error", {"error": str(error)})
        # called AUTOMATICALLY when node throws an errors

    # ── LLM events ─────────────────────────────────
    def on_llm_start(self, serialized, prompts, **kwargs):
        self.logger.info("LLM", "LLM call started", {
            "model": serialized.get("name", "unknown"),
            "prompt_preview": str(prompts)#[:200]
        })

    def on_llm_end(self, response, **kwargs):
        try:
            # get final answer
            content = response.generations[0][0].message.content

            # get reasoning if exists
            reasoning = response.generations[0][0].message.additional_kwargs.get('reasoning_content', 'No reasoning')

            # get token usage
            usage = response.llm_output.get('token_usage', {})

            self.logger.info("LLM", "LLM call finished", {
                "reasoning": reasoning[:300],        # thinking
                "answer":    content[:300],          # final answer
                "tokens":    usage.get('total_tokens', 0),
                "time_taken": usage.get('total_time', 0)
            })
        except Exception as e:
            self.logger.error("LLM", "Log parse failed", {"error": str(e)})

    def on_llm_error(self, error, **kwargs):
        self.logger.error("LLM", "LLM failed", {
            "error": str(error)
        })

    # ── Tool events ────────────────────────────────
    def on_tool_start(self, serialized, input_str, **kwargs):
        self.logger.info("Tool", "Tool started", {
            "tool": serialized.get("name", "unknown"),
            "input": str(input_str)[:200]
        })

    def on_tool_end(self, output, **kwargs):
        self.logger.info("Tool", "Tool finished", {
            "output": str(output)[:200]
        })

    def on_tool_error(self, error, **kwargs):
        self.logger.error("Tool", "Tool failed", {
            "error": str(error)
        })

    # ── Agent events ───────────────────────────────
    def on_agent_action(self, action, **kwargs):
        self.logger.info("Agent", "Agent action", {
            "tool": action.tool,
            "input": str(action.tool_input)[:200]
        })

    def on_agent_finish(self, finish, **kwargs):
        self.logger.info("Agent", "Agent finished", {
            "output": str(finish.return_values)[:200]
        })

    # ── Retriever events ───────────────────────────
    def on_retriever_start(self, serialized, query, **kwargs):
        self.logger.info("Retriever", "Retrieval started", {
            "query": str(query)[:200]
        })

    def on_retriever_end(self, documents, **kwargs):
        self.logger.info("Retriever", "Retrieval finished", {
            "docs_count": len(documents)
        })

    def on_retriever_error(self, error, **kwargs):
        self.logger.error("Retriever", "Retrieval failed", {
            "error": str(error)
        })

    # ── Chat model events ──────────────────────────
    def on_chat_model_start(self, serialized, messages, **kwargs):
        self.logger.info("ChatModel", "Chat model started", {
            "model": serialized.get("name", "unknown"),
            "messages_count": len(messages)
        })

    # ── Retry events ───────────────────────────────
    def on_retry(self, retry_state, **kwargs):
        self.logger.warning("Retry", "Retrying", {
            "attempt": str(retry_state)[:200]
        })

    
logger = JSONLogger()
# creates ONE logger instance(or object) for the whole app
# any file that imports logger gets this same instance

callback_handler = LangGraphCallbackHandler(logger)
# creates ONE callback handler instance
# passed to graph.stream() in main.py via config
# LangGraph then calls its methods automatically

#NOTES:

# BaseCallbackHandler has pre-defined methods for every possible event that can happen in LangChain/LangGraph.

# Full List of What They Listen To
# python# LLM events
# on_llm_start()       # when LLM starts generating
# on_llm_end()         # when LLM finishes
# on_llm_error()       # when LLM fails

# # Chain/Node events
# on_chain_start()     # when a node/chain starts
# on_chain_end()       # when a node/chain finishes
# on_chain_error()     # when a node/chain fails

# # Agent events
# on_agent_action()    # when agent decides an action
# on_agent_finish()    # when agent finishes

# # Tool events
# on_tool_start()      # when a tool starts
# on_tool_end()        # when tool finishes
# on_tool_error()      # when tool fails

# # Retriever events
# on_retriever_start()  # when RAG retrieval starts
# on_retriever_end()    # when retrieval finishes
# ```

# ---

