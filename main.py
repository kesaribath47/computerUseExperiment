import asyncio
import base64
import json
import logging
import os
from pathlib import Path
from typing import Callable, Optional

import openlit
from anthropic import APIResponse
from anthropic import Anthropic
from anthropic.types.beta import BetaMessage, BetaMessageParam, BetaTextBlock

from computer_use_demo.loop import sampling_loop, APIProvider
from computer_use_demo.tools import ToolResult

# Constants
DEFAULT_INSTRUCTION = "Save an image of a cat to the desktop."
MODEL_NAME = "claude-3-5-sonnet-20241022"
SCREENSHOTS_DIR = Path("screenshots")
MAX_TOKENS = 4096
MAX_RECENT_IMAGES = 10

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize OpenLIT with default collector endpoint
openlit.init(otlp_endpoint="http://127.0.0.1:4318")

def get_api_key() -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "Please set your API key in the ANTHROPIC_API_KEY environment variable"
        )
    return api_key

# client = Anthropic(
#     api_key=get_api_key(),
# )

# message = client.messages.create(
#     max_tokens=1024,
#     messages=[
#         {
#             "role": "user",
#             "content": "Hello, What is LLM Observability?",
#         }
#     ],
#     model="claude-3-opus-20240229",
# )


def setup_callbacks() -> tuple[
    Callable[[dict], None],
    Callable[[ToolResult, str], None],
    Callable[[APIResponse[BetaMessage]], None]
]:
    """Configure and return the callback functions for the sampling loop."""
    
    def output_callback(content_block: BetaTextBlock) -> None:
        if content_block.type == "text":
            logger.info(f"Assistant: {content_block.text}")

    def tool_output_callback(result: ToolResult, tool_use_id: str) -> None:
        if result.output:
            logger.info(f"Tool Output [{tool_use_id}]: {result.output}")
        if result.error:
            logger.error(f"Tool Error [{tool_use_id}]: {result.error}")
        if result.base64_image:
            save_screenshot(result.base64_image, tool_use_id)

    def api_response_callback(response: APIResponse[BetaMessage]) -> None:
        response_content = json.loads(response.text)["content"]
        logger.debug(
            "API Response:\n%s",
            json.dumps(response_content, indent=4)
        )

    return output_callback, tool_output_callback, api_response_callback


def save_screenshot(base64_image: str, tool_use_id: str) -> None:
    """Save a base64 encoded screenshot to the screenshots directory."""
    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    screenshot_path = SCREENSHOTS_DIR / f"screenshot_{tool_use_id}.png"
    
    with open(screenshot_path, "wb") as f:
        f.write(base64.b64decode(base64_image))
    logger.info(f"Saved screenshot: {screenshot_path}")


async def main(instruction: Optional[str] = None) -> None:
    """
    Main execution function for the Computer Use Demo.
    """
    try:
        client = Anthropic(
            api_key = get_api_key(),
        )
        
        user_instruction = instruction or DEFAULT_INSTRUCTION
        
        logger.info(
            "Starting Claude 'Computer Use'.\n"
            f"Instructions provided: '{user_instruction}'"
        )

        # Create messages list directly
        messages: list[BetaMessageParam] = [{
            "role": "user",
            "content": user_instruction,
        }]

        client.messages.create(
            max_tokens=MAX_TOKENS,
            messages = messages,
            model = MODEL_NAME,
        )

        output_cb, tool_cb, api_cb = setup_callbacks()
        
        await sampling_loop(
            model = MODEL_NAME,
            provider = APIProvider.ANTHROPIC,
            system_prompt_suffix = "",
            messages = messages,  # Pass the messages list directly
            output_callback = output_cb,
            tool_output_callback = tool_cb,
            api_response_callback = api_cb,
            api_key = get_api_key(),
            only_n_most_recent_images = MAX_RECENT_IMAGES,
            max_tokens = MAX_TOKENS,
        )

    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    import sys
    
    user_instruction = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    
    try:
        asyncio.run(main(user_instruction))
    except KeyboardInterrupt:
        logger.info("SIGINT: Application stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
