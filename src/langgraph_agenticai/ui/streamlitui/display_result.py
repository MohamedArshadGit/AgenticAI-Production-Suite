import streamlit as st
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage

class DisplayResultStreamlit:
    def __init__(self,usecase,graph,user_message,config={}) :
        self.usecase =usecase #They store values inside the object.
        self.graph =graph
        self.user_message =user_message
        self.config =config
    # A constructor runs automatically when you create an object.
    # example : obj = DisplayResultStreamlit("Basic Chatbot", graph, "Hi")
    # When this runs → Python automatically calls
    # __init__()
    # Purpose of constructor:
    # initialize variables
    # store values inside the object

    # Now internally:
    # obj.usecase = "Basic Chatbot"
    # obj.graph = graph
    # obj.user_message = "Hi"
    # So the object remembers these values.
    
    def display_result_on_ui(self):
        usecase =self.usecase
        # here just we are assigning varibales (usecase =,graph=,user_message =) for easy coding or everything we have to write like self.usecase, self.graph etc
        graph =self.graph
        user_message =self.user_message
        print(user_message)
        config =self.config

        if usecase =="Basic Chatbot":
            for event in graph.stream({'messages':("user",user_message)},config):
                    print(event.values())
                    for value in event.values():
                        print(value['messages'])
                        with st.chat_message("user"):
                            st.write(user_message)
                        with st.chat_message("assistant"):
                            st.write(value["messages"].content)
        elif usecase == "Tools + ReAct":
            with st.chat_message("user"):
                st.write(user_message)

            # stream through all graph events
            for event in graph.stream(
                {'messages': [HumanMessage(content=user_message)]},
                config
            ):
                print(f"DEBUG event: {event}")

                for node_name, node_output in event.items():
                    messages = node_output.get("messages", [])

                    for message in messages:

                        # tool call — show which tool is being used
                        if isinstance(message, AIMessage) and message.tool_calls:
                            for tool_call in message.tool_calls:
                                with st.chat_message("assistant"):
                                    st.info(f"🔧 Using tool: `{tool_call['name']}` "
                                            f"with args: `{tool_call['args']}`")

                        # tool result — show raw result
                        elif isinstance(message, ToolMessage):
                            with st.chat_message("assistant"):
                                st.success(f"✅ Tool result: {message.content}")

                        # final answer — show to user
                        elif isinstance(message, AIMessage) and message.content:
                            with st.chat_message("assistant"):
                                st.write(message.content)