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
                    if not isinstance(node_output, dict):  # safety check
                        continue
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
                                content = message.content
                                if isinstance(content, list): content = content[0].get("text", str(content))
                                st.success(f"✅ Tool result: {content}")

                        # final answer — show to user
                        elif isinstance(message, AIMessage) and message.content:
                            with st.chat_message("assistant"):
                                st.write(message.content)

        elif usecase == "Tools + ReAct + HITL":
            # only show user message when a new message comes in
            # on st.rerun() user_message is None — skip it
            if user_message:
                with st.chat_message("user"):
                    st.write(user_message)

            # ── Session state setup ──────────────────────────────────
            # hitl_pending  : True = graph is paused, waiting for user decision
            # hitl_graph    : saved graph object — survives st.rerun()
            # hitl_config   : saved config with thread_id — survives st.rerun()
            # hitl_state    : saved HITL state values — survives st.rerun()
            if "hitl_pending" not in st.session_state:
                st.session_state.hitl_pending = False

            # only update graph and config when a real graph is passed in
            # on rerun graph=None → keep old stored graph
            if graph is not None:
                # generate unique thread_id per conversation session
                # generate unique thread_id per browser session using uuid
                # prevents old conversation history leaking into new conversations
                # same session = same uuid = consistent memory across reruns
                # new browser session = new uuid = fresh clean memory
                # see down below in code after last block of code
                if "hitl_thread_id" not in st.session_state:
                    import uuid
                    st.session_state.hitl_thread_id = str(uuid.uuid4())
                st.session_state.hitl_graph = graph
                st.session_state.hitl_config = {
                    **self.config,
                    "configurable": {"thread_id": st.session_state.hitl_thread_id}
                }

            hitl_graph = st.session_state.hitl_graph
            hitl_config = st.session_state.hitl_config

            # ── STEP 1: Run graph only if no HITL is pending ────────
            # and only if a new user message exists
            # if hitl_pending=True → skip streaming, go straight to STEP 2
            if not st.session_state.hitl_pending and user_message:
                for event in hitl_graph.stream(
                    {"messages": [HumanMessage(content=user_message)]},
                    hitl_config
                ):
                    for node_name, node_output in event.items():
                        if not isinstance(node_output, dict):
                            continue
                        messages = node_output.get("messages", [])
                        for message in messages:
                            # tool call — show which tool is being used
                            if isinstance(message, AIMessage) and message.tool_calls:
                                for tool_call in message.tool_calls:
                                    with st.chat_message("assistant"):
                                        st.info(f"🔧 Using tool: `{tool_call['name']}` "
                                                f"with args: `{tool_call['args']}`")
                            # tool result
                            elif isinstance(message, ToolMessage):
                                content = message.content
                                if isinstance(content, list):
                                    content = content[0].get("text", str(content))
                                with st.chat_message("assistant"):
                                    st.success(f"✅ Tool result: {content}")
                            # final answer
                            elif isinstance(message, AIMessage) and message.content:
                                with st.chat_message("assistant"):
                                    st.write(message.content)

                # after stream finishes — check if graph paused for HITL
                current_state = hitl_graph.get_state(hitl_config)
                if current_state.values.get("hitl_required", False):
                    st.session_state.hitl_pending = True
                    st.session_state.hitl_state = current_state.values
                    st.rerun()  # rerun to show HITL UI in STEP 2

            # ── STEP 2: Show HITL UI if pending ─────────────────────
            # this block runs on every rerun when hitl_pending=True
            # shows approve/reject buttons OR ambiguity options
            if st.session_state.hitl_pending:
                state = st.session_state.hitl_state
                pattern = state.get("hitl_pattern")       # "sensitive_tool" or "ambiguity"
                hitl_message = state.get("hitl_message")  # message shown to user
                hitl_options = state.get("hitl_options")  # ambiguity options list

                st.warning(f"⚠️ {hitl_message}")

                # ── Pattern: sensitive_tool ─────────────────────────
                # agent wants to use location_tool or search_tool
                # user must approve or reject
                if pattern == "sensitive_tool":
                    col1, col2 = st.columns(2)
                    with col1:  # approve block
                        if st.button("✅ Approve"):
                            hitl_graph.update_state(
                                hitl_config,
                                {"hitl_approved": True, "hitl_required": False},
                                as_node="hitl"
                            )
                            st.session_state.hitl_pending = False
                            # resume graph after approval
                            for event in hitl_graph.stream(None, hitl_config):
                                for node_name, node_output in event.items():
                                    if not isinstance(node_output, dict):
                                        continue
                                    messages = node_output.get("messages", [])
                                    for message in messages:
                                        # tool result
                                        if isinstance(message, ToolMessage):
                                            content = message.content
                                            if isinstance(content, list):
                                                content = content[0].get("text", str(content))
                                            with st.chat_message("assistant"):
                                                st.success(f"✅ Tool result: {content}")
                                        # final answer
                                        elif isinstance(message, AIMessage) and message.content:
                                            with st.chat_message("assistant"):
                                                st.write(message.content)
                            # after stream finishes — check if graph paused AGAIN
                            # e.g. sensitive_tool after ambiguity resolution
                            new_state = hitl_graph.get_state(hitl_config)
                            if new_state.values.get("hitl_required", False):
                                st.session_state.hitl_pending = True
                                st.session_state.hitl_state = new_state.values
                                st.rerun()

                    with col2:  # reject block
                        if st.button("❌ Reject"):
                            hitl_graph.update_state(
                                hitl_config,
                                {"hitl_approved": False, "hitl_required": False},
                                as_node="hitl"
                            )
                            st.session_state.hitl_pending = False
                            with st.chat_message("assistant"):
                                st.write("Tool use was rejected. How else can I help you?")

                # ── Pattern: ambiguity ──────────────────────────────
                # agent detected message is ambiguous
                # user must select one of 3 interpretations
                elif pattern == "ambiguity" and hitl_options:
                    if st.button("⏭️ Skip — Just answer directly", key="opt_skip"):
                        hitl_graph.update_state(
                            hitl_config,
                            {"hitl_approved": False, "hitl_required": False},
                            as_node="hitl"
                        )
                        st.session_state.hitl_pending = False
                        for event in hitl_graph.stream(None, hitl_config):
                            for node_name, node_output in event.items():
                                if not isinstance(node_output, dict):
                                    continue
                                messages = node_output.get("messages", [])
                                for message in messages:
                                    if isinstance(message, AIMessage) and message.content:
                                        with st.chat_message("assistant"):
                                            st.write(message.content)
                    for i, option in enumerate(hitl_options):
                        #if st.button(f"Option {i+1}: {option}", key=f"opt_{i}"):
                        if st.button(f"Option {i+1}: {option}", key=f"opt_{id(hitl_options)}_{i}"):#id(hitl_options) generates a unique number based on the current options object — so every new HITL pause gets unique button keys
                            hitl_graph.update_state(
                                hitl_config,
                                {
                                    "hitl_approved": True,
                                    "hitl_required": False,
                                    "messages": [HumanMessage(content=option)]
                                    # inject selected option as new human message
                                    # agent will re-run with this clarified message
                                },
                                as_node="hitl"
                            )
                            st.session_state.hitl_pending = False
                            # resume graph after ambiguity resolved
                            for event in hitl_graph.stream(None, hitl_config):
                                for node_name, node_output in event.items():
                                    if not isinstance(node_output, dict):
                                        continue
                                    messages = node_output.get("messages", [])
                                    for message in messages:
                                        # tool result
                                        if isinstance(message, ToolMessage):
                                            content = message.content
                                            if isinstance(content, list):
                                                content = content[0].get("text", str(content))
                                            with st.chat_message("assistant"):
                                                st.success(f"✅ Tool result: {content}")
                                        # final answer
                                        elif isinstance(message, AIMessage) and message.content:
                                            with st.chat_message("assistant"):
                                                st.write(message.content)
                            # after stream finishes — check if graph paused AGAIN
                            # e.g. sensitive_tool triggered after ambiguity resolved
                            new_state = hitl_graph.get_state(hitl_config)
                            if new_state.values.get("hitl_required", False):
                                st.session_state.hitl_pending = True
                                st.session_state.hitl_state = new_state.values
                                st.rerun()

# Every new message → same thread_id "hitl-thread-1"
#                   → LangGraph MemorySaver sees same thread
#                   → appends to OLD conversation history
#                   → LLM gets confused with mixed context
# What uuid does:
# First time app loads → generates "a3f9b2c1-..." (random unique id)
# stores in session_state → survives reruns
# every message in same session → uses SAME uuid → consistent memory ✅

# Next browser session → generates new uuid → fresh memory ✅
# In simple words:

# Before: every conversation shared same memory slot "hitl-thread-1" → old messages leaked into new conversations
# After: each browser session gets its own unique memory slot → conversations are isolated

# Think of it like hotel room keys:
# Before: everyone gets key "101" → walk into wrong room ❌
# After:  each guest gets unique key → own private room ✅