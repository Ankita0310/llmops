
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage, HumanMessage

from app.config.settings import settings
from app.common.logger import get_logger

logger = get_logger(__name__)


def get_response_from_ai_agents(
    llm_id,
    query,
    allow_search,
    system_prompt
):

    try:
        logger.info(f"Initializing LLM: {llm_id}")

        # Initialize Groq LLM
        llm = ChatGroq(
            model=llm_id,
            api_key=settings.GROQ_API_KEY
        )

        # Configure tools
        tools = []

        if allow_search:
            logger.info("Enabling Tavily web search")
            tools.append(TavilySearch(max_results=2))

        # Create AI agent
        agent = create_react_agent(
            model=llm,
            tools=tools,
            prompt=system_prompt
        )

        # Normalize query
        if isinstance(query, str):
            query_list = [query]
        elif isinstance(query, list):
            query_list = query
        else:
            raise ValueError("Query must be a string or list of strings")

        # Convert queries into HumanMessage objects
        messages = [
            HumanMessage(content=q)
            for q in query_list
            if isinstance(q, str) and q.strip()
        ]

        if not messages:
            raise ValueError("No valid user messages found")

        state = {
            "messages": messages
        }

        logger.info("Invoking AI agent")

        response = agent.invoke(state)

        # Extract AI response
        response_messages = response.get("messages", [])

        ai_messages = [
            message.content
            for message in response_messages
            if isinstance(message, AIMessage)
            and message.content
            and not message.tool_calls
        ]

        if not ai_messages:
            raise ValueError("AI agent returned no final response")

        logger.info("AI agent response generated successfully")

        return ai_messages[-1]

    except Exception:
        logger.exception("Error while executing AI agent")
        raise
