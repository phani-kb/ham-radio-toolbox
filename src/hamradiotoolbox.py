import click

from hrt.common import utils
from hrt.common.config_reader import ConfigReader, HRTConfig, logger
from hrt.common.enums import (
    CountryCode,
    ExamType,
    HRTEnum,
    NumberOfLetters,
    QuestionAnswerDisplay,
    QuestionRefType,
    QuizSource,
    RankBy,
    SortBy,
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


# CALLSIGN COMMANDS
@hamradiotoolbox.command("callsign")
@click.option(
    "--country",
    type=click.Choice(CountryCode.supported_ids(), case_sensitive=False),
    required=True,
    help="Country for which to query the callsign.",
)
@click.option(
    "--match",
    type=click.Choice(NumberOfLetters.get_supported_number_of_letters("word_match")),
    help="Match words with 2 or 3 letters of available callsign.",
)
@click.option(
    "--include",
    type=click.Choice(NumberOfLetters.get_supported_number_of_letters("include")),
    multiple=True,
    default=["all"],
    help="Include callsigns by specific criteria: 1l (1-letter), 1n (1-number), 2l (2-letter), "
    "3l (3-letter), el (end letter), all (all criteria).",
)
@click.option(
    "--exclude",
    type=click.Choice(NumberOfLetters.get_supported_number_of_letters("exclude")),
    multiple=True,
    default=["all"],
    help="Exclude callsigns by a specific criteria: 1l (1-letter), 1n (1-number), 2l (2-letter), "
    "3l (3-letter), el (end letter), ml (multiple letters), all (all criteria).",
)
@click.option(
    "--sort-by",
    type=click.Choice(SortBy.ids()),
    default=SortBy.CALLSIGN.id,
    help="Sort the callsigns by a specific criteria: callsign (alphabetical order), "
    "rank (ranking order).",
)
@click.option(
    "--rank-by",
    type=click.Choice(RankBy.ids()),
    help="Rank the callsigns by a specific criteria: ease-of-use (how easy it is to use), "
    "phonetic-clarity (how clear it sounds), "
    "confusing-pair (how similar it is to another callsign) "
    "and cw-weight (how easy it is to send in Morse code).",
)
@click.pass_context
def callsign(ctx, country, match, include, exclude, sort_by, rank_by):
    """Query and analyze callsigns for a specific country."""

    def get_phonetic_clarity_options(hrt_config: HRTConfig):
        return hrt_config.get("callsign").get("phonetic_clarity")

    def get_confusing_pairs(hrt_config: HRTConfig):
        return hrt_config.get("callsign").get("confusing_pairs")

    config = ctx.obj["config"]

    if rank_by and RankBy(rank_by) == RankBy.PHONETIC_CLARITY:
        phonetic_clarity_options = get_phonetic_clarity_options(config)
        utils.select_from_options(
            phonetic_clarity_options, "Phonetic clarity option"
        )

    if rank_by and RankBy(rank_by) == RankBy.CONFUSING_PAIR:
        confusing_pairs = get_confusing_pairs(config)
        utils.select_from_options(confusing_pairs, "Confusing pair")

    include_options = include if include else []
    exclude_options = exclude if exclude else []
    logger.info(f"Include options: {include_options}, Exclude options: {exclude_options}")


if __name__ == "__main__":
    hamradiotoolbox()
    logger.info("Ham Radio Toolbox completed.")
    logger.shutdown()
