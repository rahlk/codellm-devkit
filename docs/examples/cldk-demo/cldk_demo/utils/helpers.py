from pdb import set_trace
import sys
import ollama
from genai import Credentials, Client
from genai.schema import (
    TextGenerationParameters,
    TextGenerationReturnOptions,
)

from yank_code import extract_code_blocks
from dotenv import load_dotenv


from loguru import logger

from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel

console = Console()


class ProjectNotFoundError(Exception):
    """
    Exception raised when a project is not found at the specified path.
    """

    def __init__(self, project_path: str):
        self.project_path = project_path
        super().__init__(f"Project not found at {project_path}")


def configure_logger(log_level: int):
    """
    Configure the logger with the given log level.

    Args:
        log_level (int): The log level to be set for the logger.
    """
    # Remove default logger
    logger.remove()

    # Add custom logger with dynamic log level
    if log_level == 0:
        level_str = "TRACE"
    elif log_level == 1:
        level_str = "DEBUG"
    elif log_level == 2:
        level_str = "INFO"
    elif log_level == 3:
        level_str = "WARNING"
    elif log_level == 4:
        level_str = "ERROR"
    elif log_level == 5:
        level_str = "CRITICAL"

    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <4}</level> | <level>{message}</level>",
        colorize=True,
        level=level_str.upper(),
    )


def format_inst(code, focal_method, focal_class=None, task="write a junit test", language="java"):
    """
    Format the instruction for the given focal method and class.

    Args:
        code (str): The code snippet to be formatted.
        focal_method (str): The focal method to be included in the instruction.
        focal_class (str): The focal class to be included in the instruction.
        task (str): The task to be performed. Defaults to "write a junit test".
        language (str): The language of the code snippet. Defaults to "java".
    Returns:
        str: The formatted instruction.
    """
    if focal_class is None:
        inst = f"Question: Can you {task.lower()} for the method `{focal_method}` below?\n"
    else:
        inst = f"Question: Can you {task.lower()} for the method `{focal_method}` in the class `{focal_class}` below?\n"

    inst += "\n"
    inst += f"```{language}\n"
    inst += code
    inst += "```" if code.endswith("\n") else "\n```"
    inst += "\n"
    return inst


def _prompt_watsonx(
    message: str,
    temp: float = 0.25,
    model_id: str = "ibm/granite-34b-code-instruct",
    extract_code: bool = True,
):
    """
    Prompt models on WatsonX

    Args:
        message (str): The message to prompt the LLM.
        temp (float): The temperature for sampling. Defaults to 0.25.
        model (str): The model to use for prompting. Defaults to "ibm/granite-34b-code-instruct".
        extract_code (bool): Whether to extract code blocks from the response. Defaults to True.

    Returns:
        str: An iterator over the responses from the model.
    """
    load_dotenv()
    credentials = Credentials.from_env()
    client = Client(credentials=credentials)
    codegen_params = TextGenerationParameters(
        max_new_tokens=1024,
        min_new_tokens=20,
        temperature=temp,
        decoding_method="sample",
        return_options=TextGenerationReturnOptions(
            input_text=True,
        ),
    )

    for response in client.text.generation.create(
        model_id=model_id,
        inputs=[f"Question: {message}\n\nAnswer:\n"],
        parameters=codegen_params,
    ):
        response_text = response.results
        if len(response_text):
            if extract_code:
                extracted_code = extract_code_blocks(response_text[0].generated_text)
                if extracted_code:
                    return extracted_code[0]["code"][:-4]
            else:
                return response_text[0].generated_text.replace("<|endoftext|>", "\n")


def _prompt_ollama(
    message: str, model_id: str = "granite-code:20b-instruct", extract_code: bool = True
) -> str:
    """Prompt locally using Ollama.

    Args:
        message (str): The message to prompt the LLM.
        model (str): The model to use for prompting. Choose from (https://ollama.com/library). Defaults to "granite-code:20b-instruct".
        extract_code (bool): Whether to extract code blocks from the response. Defaults to True.

    Returns:
        str: Model Response text.
    """

    try:
        response_object = ollama.generate(model=model_id, prompt=message)
        response_text = response_object["response"]
        if extract_code:
            extracted_code = extract_code_blocks(response_text)
            if extracted_code:
                return extracted_code[0]["code"].replace("```", "\n")
        else:
            return response_text.replace("<|endoftext|>", "\n")
    except ollama.ResponseError as e:
        logger.error(f"{e.error}")
        set_trace()


def prompt(
    message: str,
    model_id: str,
    temp: float = 0.25,
    extract_code: bool = True,
    backend: str = "ollama",
) -> str:
    """
    Prompt models on WatsonX or locally using Ollama.

    Args:
        message (str): The message to prompt the LLM.
        temp (float): The temperature for sampling. Defaults to 0.25.
        model (str): The model to use for prompting. Defaults to "ibm/granite-34b-code-instruct".
        extract_code (bool): Whether to extract code blocks from the response. Defaults to True.
        backend (str): The backend to use for prompting. Defaults to "ollama".

    Returns:
        str: An iterator over the responses from the model.
    """
    if backend == "ollama":
        logger.info(f"Prompting {model_id} running locally using Ollama.")
        return _prompt_ollama(message, model_id, extract_code)
    else:
        logger.info(f"Prompting {model_id} on watsonx")
        return _prompt_watsonx(message, model_id, extract_code)


def print_to_console(instruction: str, llm_output: str, title: str, syntax="java"):
    """
    Print the instruction and the generated test in a formatted way.

    Args:
        instruction (str): The instruction to be printed.
        llm_output (str): The output generated by the LLM.
        title (str): The title of the output.
        syntax (str): The syntax highlighting to be used. Defaults to "java".
    """
    _print_instruction(instruction)
    _print_llm_output(llm_output, title, syntax)


def _print_instruction(instruction: str):
    """
    Print the instruction in a formatted way.

    Args:
        instruction (str): The instruction to be printed.
    """
    console.print(
        Panel(
            Syntax(instruction, lexer="markdown"),
            title="Instruction",
            border_style="white",
        ),
        new_line_start=True,
    )


def _print_llm_output(llm_output: str, title: str, syntax="java"):
    """
    Print the generated test in a formatted way.

    Args:
        llm_output (str): The output generated by the LLM.
        title (str): The title of the output.
        syntax (str): The syntax highlighting to be used. Defaults to "java".
    """
    console.print(
        Panel(
            Syntax(llm_output, line_numbers=True, word_wrap=True, lexer=syntax),
            title=f"{title}",
            border_style="blue",
        ),
        new_line_start=True,
    )
