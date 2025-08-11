from typing_extensions import TypedDict
from typing import Any, Callable, List, Annotated

from langgraph.graph import StateGraph, START
from langgraph.prebuilt import tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import AnyMessage, add_messages

from src.agent.base_agent import Agent
from src.agent.llm import LLM
from src.agent.prompt import patient_agent_prompt
from src.agent.tools import (
    # knowledge_base_tool,
    get_doctor_schedule_appointments,
    get_event_by_id,
    create_doctor_appointment,
    update_doctor_appointment,
    cancel_doctor_appointment,
)
from src.agent.utils import create_tool_node_with_fallback


class State(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        messages: The list of messages that the agent has seen.
                  It is appended to by the `add_messages` function.
    """
    messages: Annotated[list[AnyMessage], add_messages]


class AgentGraph:
    """
    Encapsulates the creation and compilation of the conversational agent graph.

    This class handles the setup of the language model, tools, and the graph
    structure, providing a compiled, runnable graph instance.
    """

    def __init__(self):
        self.llm = LLM
        self.tools = self._get_tools()
        self.agent_runnable = self._create_agent_runnable()

    @staticmethod
    def _get_tools() -> List[Callable[..., Any]]:
        """Returns a list of all tools available to the agent."""
        return [
            get_doctor_schedule_appointments,
            get_event_by_id,
            # knowledge_base_tool,
            # Sensitive tools that modify state
            create_doctor_appointment,
            update_doctor_appointment,
            cancel_doctor_appointment,
        ]

    def _create_agent_runnable(self):
        """Binds the tools to the LLM via the agent prompt."""
        return patient_agent_prompt | self.llm.bind_tools(self.tools)

    def compile_graph(self):
        """
        Builds and compiles the StateGraph for the agent.

        The graph defines the flow of control:
        1. Start with the 'agent' node.
        2. The 'agent' decides whether to call a tool.
        3. If a tool is called, the 'tools' node is executed.
        4. The output of the 'tools' node is fed back to the 'agent'.
        5. The process repeats until the agent generates a final response.

        Returns:
            A compiled, runnable graph with a memory checkpointer.
        """
        builder = StateGraph(State)

        # Define nodes
        builder.add_node("agent", Agent(self.agent_runnable))
        builder.add_node("tools", create_tool_node_with_fallback(self.tools))

        # Define edges
        builder.add_edge(START, "agent")
        builder.add_conditional_edges("agent", tools_condition)
        builder.add_edge("tools", "agent")

        # The checkpointer allows the graph to persist its state,
        # creating a memory for the conversation.
        # memory = MemorySaver()
        return builder.compile()


# Create a single, globally accessible instance of the compiled graph.
# This follows the singleton pattern at the module level, which is efficient
# as the graph is compiled only once when the module is first imported.
graph = AgentGraph().compile_graph()