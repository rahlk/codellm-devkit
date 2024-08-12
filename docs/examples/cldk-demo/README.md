# Evaluation of Zircon

This repository contains the code for evaluating the Zircon tool. The evaluation is done on a set of open-source Java 
projects. 

## Pre-requisites

- Python 3.11+
- Poetry (https://python-poetry.org/docs/)
- Sample projects (https://github.ibm.com/zircon/zircon-evaluation-datasets)
  
## Preparing the dataset

The dataset is available in a separate repository. Clone the repository as follows:

```bash
git clone git@github.ibm.com:zircon/zircon-evaluation-datasets.git
```

## Installation

First, clone the repository:

```bash
git clone git@github.ibm.com:zircon/zircon-evaluation.git
```

Then, install the zircon-eval package using poetry. 

```bash
poetry install
```

Test the installation by running the following command:

```bash
poetry run zircon-eval --help
```

You should see the help message for the zircon-eval command.

```help
❯ poetry run zircon-eval --help

 Usage: zircon-eval [OPTIONS]

 Create an instructions for test generation for all the methods in a given project using Codellm-Devkit.

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --project-path  -p      TEXT     Path to the Java project [default: None] [required]                                                           │
│    --verbosity     -v      INTEGER  Set verbosity level. 0=TRACE, 1=DEBUG, 2=INFO, 3=WARN, 4=ERROR, and 5=CRITICAL [default: 3]                   │
│    --temperature   -t      FLOAT    Set the temperature for the LLM. Setting to 0 would imply `greedy` execution. Default is 0.2 [default: 0.2]   │
│    --model-name    -n      TEXT     Name of the model to be used for generation [default: zircon-34b]                                             │
│    --model-path    -m      TEXT     Path to the model checkpoint to be used for generation                                                        │
│                                     [default: /modeling/models/zircon_g34b_v2/hf_step20000]                                                       │
│    --use-bam       -b               Use BAM for generation                                                                                        │
│    --help                           Show this message and exit.                                                                                   │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Usage

For example, to test the Zircon-34b on the commons-cli project, hosted on vella, you can run the following command:

```shell
poetry run zircon-eval --project-path /path/to/zircon-evaluation-datasets/commons-cli-rel-commons-cli-1.7.0/ \ 
--verbosity=2 --model-name=zircon-34b --model-path=/modeling/models/zircon_g34b_v2/hf_step20000 --temperature=0.2
```