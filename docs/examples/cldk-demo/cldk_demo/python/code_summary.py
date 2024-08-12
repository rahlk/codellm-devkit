"""
Generate summary for all the methods in the project in a given directory.
"""

from pdb import set_trace
from cldk import CLDK
from pathlib import Path
from typing import Annotated, Dict

from loguru import logger
import typer

from cldk_demo.utils import (
    prompt,
    format_inst,
    print_to_console,
)

# Initialize Typer
app = typer.Typer(
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=False,
    add_completion=False,
)


@app.command()
def generate_summary(
    project_path: Annotated[
        str, typer.Option(..., "--project-path", "-p", help="Path to the Java project")
    ],
    use_watsonx: Annotated[
        bool, typer.Option(..., "--use-watsonx", "-w", help="Use WatsonX for prompting")
    ] = False,
):
    # Initialize cldk for python and build analysis object
    cldk = CLDK(language="python")
    analysis = cldk.analysis(project_path)

    # Iterate over all the modules in the project
    for module in analysis.get_modules():
        # Iterate over all the methods in the module
        for method in module.functions:
            logger.info(
                f"Generating test for method {method.name} in project at {project_path}"
            )
            # Generate the instruction for the LLM
            instruction = format_inst(
                code=method.body,
                focal_method=method.name,
                task="generate a brief summary",
                language="python",
            )
            # Prompt the LLM
            llm_output = prompt(
                message=instruction,
                model_id="granite-code:20b-instruct",
                extract_code=False,
                backend="watsonx" if use_watsonx else "ollama",
            )
            # Print the output to console and pause execution
            print_to_console(
                instruction, llm_output, title="Summary", syntax="markdown"
            )
            set_trace()


if __name__ == "__main__":
    app()
