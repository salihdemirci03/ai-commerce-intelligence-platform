"""
Base Agent class for all AI agents in the system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import json
import time

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from loguru import logger

from app.core.config import settings


class AgentInput(BaseModel):
    """Base input schema for all agents."""

    request_id: str = Field(..., description="Unique request identifier")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context data")


class AgentOutput(BaseModel):
    """Base output schema for all agents."""

    agent_name: str
    success: bool
    data: Dict[str, Any]
    summary: str
    reasoning_steps: List[str] = Field(default_factory=list)
    confidence_score: float = Field(default=0.0, ge=0.0, le=100.0)
    execution_time_ms: int
    tokens_used: int
    cost_usd: float
    error: Optional[str] = None


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.

    Each agent:
    1. Receives structured input
    2. Performs AI-powered analysis
    3. Returns structured output with reasoning
    4. Logs execution metrics
    """

    def __init__(
        self,
        name: str,
        description: str,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        """
        Initialize agent.

        Args:
            name: Agent name
            description: Agent purpose and capabilities
            model_name: LLM model to use (defaults to settings)
            temperature: LLM temperature (0-1)
            max_tokens: Maximum tokens for generation
        """
        self.name = name
        self.description = description
        self.model_name = model_name or settings.OPENAI_MODEL
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            openai_api_key=settings.OPENAI_API_KEY,
        )

        # Token tracking
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0

        logger.info(f"Initialized agent: {self.name}")

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.
        Must be implemented by subclasses.

        Returns:
            System prompt string
        """
        pass

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method for the agent.
        Must be implemented by subclasses.

        Args:
            input_data: Input data dictionary

        Returns:
            Processed output dictionary
        """
        pass

    def build_messages(self, user_prompt: str) -> List:
        """
        Build messages for LLM call.

        Args:
            user_prompt: User message content

        Returns:
            List of message objects
        """
        return [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=user_prompt),
        ]

    async def call_llm(
        self,
        user_prompt: str,
        response_format: Optional[str] = None
    ) -> str:
        """
        Call LLM with prompt and return response.

        Args:
            user_prompt: User message
            response_format: Expected response format (e.g., "json")

        Returns:
            LLM response content
        """
        try:
            messages = self.build_messages(user_prompt)

            # Add format instruction if needed
            if response_format == "json":
                messages.append(
                    HumanMessage(
                        content="Respond ONLY with valid JSON. No markdown, no explanations."
                    )
                )

            response = await self.llm.ainvoke(messages)

            # Track token usage
            if hasattr(response, "response_metadata"):
                usage = response.response_metadata.get("token_usage", {})
                self.prompt_tokens = usage.get("prompt_tokens", 0)
                self.completion_tokens = usage.get("completion_tokens", 0)
                self.total_tokens = usage.get("total_tokens", 0)

            return response.content

        except Exception as e:
            logger.error(f"LLM call failed in {self.name}: {e}")
            raise

    def calculate_cost(self) -> float:
        """
        Calculate cost based on token usage.
        GPT-4 Turbo pricing: $10/1M prompt tokens, $30/1M completion tokens

        Returns:
            Cost in USD
        """
        prompt_cost = (self.prompt_tokens / 1_000_000) * 10
        completion_cost = (self.completion_tokens / 1_000_000) * 30
        return round(prompt_cost + completion_cost, 6)

    async def execute(self, input_data: Dict[str, Any]) -> AgentOutput:
        """
        Execute agent with input data and return structured output.

        Args:
            input_data: Input data dictionary

        Returns:
            AgentOutput object
        """
        start_time = time.time()
        logger.info(f"Agent {self.name} starting execution")

        try:
            # Process input
            result = await self.process(input_data)

            # Calculate metrics
            execution_time_ms = int((time.time() - start_time) * 1000)
            cost = self.calculate_cost()

            output = AgentOutput(
                agent_name=self.name,
                success=True,
                data=result.get("data", {}),
                summary=result.get("summary", ""),
                reasoning_steps=result.get("reasoning_steps", []),
                confidence_score=result.get("confidence_score", 75.0),
                execution_time_ms=execution_time_ms,
                tokens_used=self.total_tokens,
                cost_usd=cost,
            )

            logger.info(
                f"Agent {self.name} completed successfully. "
                f"Time: {execution_time_ms}ms, Tokens: {self.total_tokens}, Cost: ${cost}"
            )

            return output

        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Agent {self.name} failed: {e}")

            return AgentOutput(
                agent_name=self.name,
                success=False,
                data={},
                summary=f"Agent execution failed: {str(e)}",
                reasoning_steps=[],
                confidence_score=0.0,
                execution_time_ms=execution_time_ms,
                tokens_used=self.total_tokens,
                cost_usd=self.calculate_cost(),
                error=str(e),
            )

    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON response from LLM.

        Args:
            response: LLM response string

        Returns:
            Parsed JSON dictionary
        """
        try:
            # Remove markdown code blocks if present
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]

            return json.loads(response.strip())

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}\nResponse: {response}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")

    def extract_reasoning_steps(self, text: str) -> List[str]:
        """
        Extract reasoning steps from LLM response.

        Args:
            text: LLM response text

        Returns:
            List of reasoning steps
        """
        steps = []
        lines = text.split("\n")

        for line in lines:
            line = line.strip()
            # Look for numbered steps or bullet points
            if line and (
                line[0].isdigit()
                or line.startswith("-")
                or line.startswith("•")
                or line.startswith("*")
            ):
                # Clean up formatting
                step = line.lstrip("0123456789.-•* ").strip()
                if step:
                    steps.append(step)

        return steps

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data before processing.

        Args:
            input_data: Input data to validate

        Returns:
            True if valid, raises ValueError if invalid
        """
        if not input_data:
            raise ValueError("Input data cannot be empty")

        return True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, model={self.model_name})"
