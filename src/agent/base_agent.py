from langchain_core.runnables import Runnable, RunnableConfig


class Agent:
    """
    A wrapper for a LangChain Runnable that ensures a valid response is generated.

    This class is designed to be used as a node in a LangGraph. It includes a
    retry mechanism to handle cases where the underlying language model fails to
    produce a tool call or meaningful text content, preventing the graph from
    getting stuck.
    """
    def __init__(self, runnable: Runnable):
        """
        Initializes the Agent.

        Args:
            runnable: A LangChain Runnable that represents the core logic of the agent.
        """
        self.runnable = runnable

    def __call__(self, state, config: RunnableConfig):
        """
        Executes the agent's logic.

        This method is called by the LangGraph framework when the agent node is
        active. It invokes the runnable and checks the output. If the output is
        empty or invalid, it appends a corrective message to the state and
        retries the invocation.
        """
        while True:
            result = self.runnable.invoke(state)
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}