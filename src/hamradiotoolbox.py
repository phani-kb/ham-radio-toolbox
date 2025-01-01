import click


@click.group(
    context_settings={
        "auto_envvar_prefix": "HMT",
        "help_option_names": ["-h", "--help"],
        "show_default": True,
    }
)
@click.option(
    "--config",
    default="./config.yml",
    type=click.Path(),
    help="Path to the configuration file.",
)
@click.pass_context
def hamradiotoolbox():
    """Ham Radio Toolbox CLI for managing questions, quizzes, practice exams and
    querying callsigns."""
    pass


if __name__ == "__main__":
    hamradiotoolbox()
