from concurrent.futures import ThreadPoolExecutor

from loguru import logger
from mem0 import AsyncMemoryClient

from src.agent.setting import settings

CLIENT = AsyncMemoryClient(api_key=settings.MEM0_API_KEY)
memory_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="memory_")


def search_memory(query: str, user_id: str) -> str:
    """
    Search the memory database for a given query and user.

    Args:
        query (str): The search query.
        user_id (str): The user identifier.

    Returns:
        str: Formatted search results or a message if nothing found.
    """
    logger.info(f"Searching memory for query: '{query}' (user: {user_id})")
    try:
        memories = CLIENT.search(query=query, user_id=user_id, top_k=10)
        if not memories:
            return "No relevant memories found."
        context = "\n".join(f"- {memory['memory']}" for memory in memories)
        return context
    except Exception as e:
        logger.error(f"Error searching memory for user {user_id}: {e}")
        return "Error occurred while searching memory."


def save_memory_sync(conversation: str, user_id: str, metadata: dict) -> dict:
    """
    Synchronously save a conversation to memory.

    Args:
        conversation (str): The conversation text.
        user_id (str): The user identifier.
        metadata (dict): Additional metadata.

    Returns:
        dict: The result from the memory client.
    """
    try:
        result = CLIENT.add(
            conversation,
            user_id=user_id,
            metadata=metadata,
            output_format="v1.1",
        )
        logger.success(f"Memory saved successfully for user {user_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to save memory for user {user_id}: {e}")
