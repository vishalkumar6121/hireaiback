from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, ValidationError
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize LangChain with Groq
llm = ChatGroq(
    model="llama3-70b-8192", # Use a suitable Groq model
    api_key=os.getenv("GROQ_API_KEY")
)

# Log a partial API key to confirm it's loaded (for debugging only)
logger.debug(f"GROQ_API_KEY (first 5 chars): {os.getenv('GROQ_API_KEY')[:5] if os.getenv('GROQ_API_KEY') else 'None'}")

class SearchCriteria(BaseModel):
    """Schema for extracted search criteria from natural language query"""
    # keywords: List[str] = Field(default=[], description="General keywords to search for (e.g., job titles, technologies)")
    skills: List[str] = Field(default=[], description="Specific technical or soft skills mentioned")
    location: Optional[str] = Field(default=None, description="Location mentioned (city, state, country)")
    min_experience_years: Optional[float] = Field(default=None, description="Minimum years of experience mentioned")
    # Add other relevant fields as needed (e.g., job titles, industries)

async def parse_nl_search_query(query: str) -> SearchCriteria:
    """
    Parses a natural language search query using an LLM to extract structured criteria.
    """
    logger.debug(f"Entering parse_nl_search_query with query: '{query}'")
    # Create prompt for the LLM
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a highly accurate search query parser for candidate information. Your task is to extract structured criteria from a natural language query. You MUST output ONLY a JSON object that strictly follows the provided `SearchCriteria` schema, with no additional text, explanations, or formatting. Your response should be raw JSON.

        Extract the following:
        - **skills**: Specific technical or soft skills (e.g., "Python", "SQL", "Project Management"). IMPORTANT: If a job title implies a technical skill (e.g., "PHP Developer", "Java Engineer"), extract only the core technology (e.g., "php", "java") as a skill. All skills should be lowercase.
        - **location**: City, state, or country.
        - **min_experience_years**: Minimum years of experience, converted to a single floating-point number. For "8+ years" or "at least 8 years", it should be `8.0`. For "5 years", it should be `5.0`. Be precise.

        If information is not mentioned, use the schema's default (empty list, null). If no criteria are found, return: {{"skills": [], "location": null, "min_experience_years": null}}.

        **EXAMPLE:**
        Query: "PHP Developer, 8+ year experience"
        Output: {{"skills": ["php"], "location": null, "min_experience_years": 8.0}}

        Ensure all keys match the schema exactly."""),
        ("user", "Natural language query: {query}\n\n{format_instructions}")
    ])

    # Create output parser
    parser = PydanticOutputParser(pydantic_object=SearchCriteria)

    # Create a chain
    chain = prompt | llm | parser

    # Get format instructions from the parser
    format_instructions = parser.get_format_instructions()

    try:
        # Invoke the chain to parse the query
        messages_to_send = prompt.format_prompt(query=query, format_instructions=format_instructions).to_messages()
        logger.debug(f"Sending messages to LLM: {messages_to_send}")
        logger.debug("Attempting to invoke LLM...")
        llm_output = await llm.ainvoke(messages_to_send)
        print(f"Raw LLM output: {llm_output.content}")
        search_criteria = parser.parse(llm_output.content)
        return search_criteria
    except ValidationError as e:
        # If Pydantic validation fails, log the error and return an empty SearchCriteria
        print(f"Validation error parsing natural language search query: {e.errors()}")
        return SearchCriteria() # Return a default empty object
    except Exception as e:
        logger.exception("An unexpected error occurred during natural language search query parsing.")
        return SearchCriteria() # Return a default empty object 