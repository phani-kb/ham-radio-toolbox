import click

from hrt.common import utils
from hrt.common.config_reader import ConfigReader, HRTConfig, logger
from hrt.common.enums import (
    CountryCode,
    ExamType,
    HRTEnum,
    QuestionAnswerDisplay,
    QuestionRefType,
    QuizSource,
)


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
def hamradiotoolbox(ctx, config):
    """Ham Radio Toolbox CLI for managing questions, quizzes, practice exams and
    querying callsigns."""
    config_reader = ConfigReader(config)
    config: HRTConfig = config_reader.config
    ctx.obj = {"config": config}
    logger.info("Ham Radio Toolbox initialized with config: %s", config_reader.file_path)


def get_all_subclasses(cls):
    """Recursively get all subclasses of a given class."""
    subclasses = set(cls.__subclasses__())
    for subclass in subclasses.copy():
        subclasses.update(get_all_subclasses(subclass))
    return sorted(subclasses, key=lambda x: x.__name__)


# SHOW COMMANDS
@hamradiotoolbox.command("show")
@click.option("--countries-supported", is_flag=True, help="Show supported countries.")
@click.option("--phonetics", is_flag=True, help="Show phonetics.")
@click.option("--answer-display", is_flag=True, help="Show answer display options.")
@click.option("--exam-types", is_flag=True, help="Show exam types.")
@click.option("--question-ref-types", is_flag=True, help="Show question reference types.")
@click.option("--quiz-source", is_flag=True, help="Show quiz source options.")
@click.option(
    "--enum",
    type=click.Choice([cls.__name__ for cls in get_all_subclasses(HRTEnum)]),
    help="Show details of the specified enum.",
)
@click.pass_context
def show(
    ctx,
    countries_supported,
    phonetics,
    answer_display,
    exam_types,
    question_ref_types,
    quiz_source,
    enum,
):
    """Commands for showing information."""
    if countries_supported:
        logger.info("Showing supported countries.")
        countries = CountryCode.list()
        utils.write_output(countries)
    if phonetics:
        logger.info("Showing phonetics.")
        callsign_settings = ctx.obj["config"].get_callsign()
        phonetics = callsign_settings.get("phonetics") if callsign_settings else None
        if phonetics:
            phonetics = [f"{key}: {value}" for key, value in phonetics.items()]
        utils.write_output(phonetics)
    if answer_display:
        logger.info("Showing answer display options.")
        answer_display_options = QuestionAnswerDisplay.list()
        utils.write_output(answer_display_options)
    if exam_types:
        logger.info("Showing exam types.")
        exam_types = ExamType.list()
        utils.write_output(exam_types)
    if question_ref_types:
        logger.info("Showing question reference types.")
        question_ref_types = QuestionRefType.list()
        utils.write_output(question_ref_types)
    if quiz_source:
        logger.info("Showing quiz source options.")
        quiz_source_options = QuizSource.list()
        utils.write_output(quiz_source_options)
    if enum:
        logger.info(f"Showing details for enum: {enum}")
        all_subclasses = get_all_subclasses(HRTEnum)
        enum_class = next((cls for cls in all_subclasses if cls.__name__ == enum), None)
        if enum_class:
            options = enum_class.list()
            descriptions = [str(enum_class.from_id(opt)) for opt in options]
            utils.write_output(descriptions)
        else:
            logger.error(f"Enum {enum} not found.")


# QUESTION COMMANDS
@hamradiotoolbox.group("question")
@click.option(
    "--country",
    type=click.Choice(CountryCode.supported_ids(), case_sensitive=False),
    required=True,
    help="Country for which to manage questions.",
)
@click.option(
    "--answer-display",
    type=click.Choice(QuestionAnswerDisplay.ids()),
    default=QuestionAnswerDisplay.WITH_QUESTION.id,
    help="Display the question w/o answer.",
)
@click.option("--save-to-file", is_flag=True, default=True, help="Save the output to a file.")
@click.pass_context
def question(ctx, country, answer_display, save_to_file):
    """Commands related to question management."""
    ctx.obj["country_code"] = country
    ctx.obj["answer_display"] = answer_display
    ctx.obj["save_to_file"] = save_to_file


if __name__ == "__main__":
    hamradiotoolbox()
    logger.info("Ham Radio Toolbox completed.")
    logger.shutdown()
