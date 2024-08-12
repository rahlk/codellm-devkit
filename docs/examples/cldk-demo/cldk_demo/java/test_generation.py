"""
Generate unit tests for all the methods in the project in a given directory.
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
def generate_test(
    project_path: Annotated[
        str, typer.Option(..., "--project-path", "-p", help="Path to the Java project")
    ],
    use_watsonx: Annotated[
        bool, typer.Option(..., "--use-watsonx", "-w", help="Use WatsonX for prompting")
    ] = False,
):
    logger.info(f"Generating unit tests for project at {project_path}")
    # Initialize cldk for java and build analysis object
    cldk = CLDK(language="java")
    analysis = cldk.analysis(project_path)
    # Iterate over all the files in the project
    for file_path, class_file in analysis.get_symbol_table().items():
        class_file_path = Path(file_path).absolute().resolve()
        # Iterate over all the classes in the file
        for type_name, type_declaration in class_file.type_declarations.items():
            # Iterate over all the methods in the class
            for method in type_declaration.callable_declarations.values():
                # Skip constructors (or any other method easily)
                if method.is_constructor:
                    continue

                logger.info(
                    f"Generating test for method {method.declaration} in class {type_name}"
                )

                # Initialize the treesitter utils for the class file content
                tree_sitter_utils = cldk.tree_sitter_utils(
                    source_code=class_file_path.read_text()
                )

                # Sanitize the class for analysis
                sanitized_class = tree_sitter_utils.sanitize_focal_class(
                    focal_method=method.declaration
                )
                # Create a simple instruction
                instruction = format_inst(
                    code=sanitized_class,
                    focal_method=method.declaration,
                    focal_class=type_name,
                    task="write a junit test",
                )
                # Prompt the LLM
                llm_output = prompt(
                    message=instruction,
                    model_id=(
                        "granite-code:20b-instruct"
                        if not use_watsonx
                        else "ibm/granite-34b-code-java-testgen-v1"
                    ),
                    backend="watsonx" if use_watsonx else "ollama",
                )
                print_to_console(instruction, llm_output, title="Generated Test")
                set_trace()


if __name__ == "__main__":
    app()
