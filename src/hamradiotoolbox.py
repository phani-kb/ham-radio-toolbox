import click
from webdriver_manager.chrome import ChromeDriverManager

from hrt.common import constants, utils
from hrt.common.config_reader import ConfigReader, HRTConfig, logger
from hrt.common.constants import DEFAULT_ANSWER_DISPLAY_PRACTICE_EXAM, DEFAULT_QUIZ_QUESTION_COUNT
from hrt.common.enums import (
    CallSignDownloadType,
    CountryCode,
    DownloadType,
    ExamType,
    GeneralQuestionListingType,
    HRTEnum,
    MarkedQuestionListingType,
    NumberOfLetters,
    QuestionAnswerDisplay,
    QuestionDisplayMode,
    QuestionListingType,
    QuestionRefType,
    QuizAnswerDisplay,
    QuizSource,
    RankBy,
    SortBy,
    TopQuestionsListingType,
)
from hrt.downloaders.base_downloader import DownloaderFactory
from hrt.processors.callsign_processor import CallSignsProcessor
from hrt.processors.question_processor import QuestionProcessor
from hrt.processors.quiz_processor import QuizProcessor


@click.group(
    context_settings={
        "auto_envvar_prefix": "HMT",
        "help_option_names": ["-h", "--help"],
        "show_default": True,
    }
)
@click.option(
    "--config",
    default="config/config.yml",
    type=click.Path(),
    help="Path to the configuration file.",
)
@click.pass_context
def hamradiotoolbox(ctx, config):
    """Ham Radio Toolbox CLI for managing questions, quizzes, practice exams and
    querying callsigns."""
    config_reader = ConfigReader(config)
    config: HRTConfig | None = config_reader.config
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
        countries = CountryCode.supported_ids()
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
        utils.write_output([str(option) for option in answer_display_options])
    if exam_types:
        logger.info("Showing exam types.")
        exam_types = ExamType.list()
        utils.write_output([str(option) for option in exam_types])
    if question_ref_types:
        logger.info("Showing question reference types.")
        question_ref_types = QuestionRefType.list()
        utils.write_output([str(option) for option in question_ref_types])
    if quiz_source:
        logger.info("Showing quiz source options.")
        quiz_source_options = QuizSource.list()
        utils.write_output([str(option) for option in quiz_source_options])
    if enum:
        logger.info(f"Showing details for enum: {enum}")
        all_subclasses = get_all_subclasses(HRTEnum)
        enum_class = next((cls for cls in all_subclasses if cls.__name__ == enum), None)
        if enum_class:
            logger.info(enum_class.__doc__)
            options = enum_class.list()
            descriptions = [str(enum_class.from_value(opt)) for opt in options]
            utils.write_output(descriptions)
        else:
            logger.error(f"Enum {enum} not found.")


def get_common_question_params(ctx):
    """Extract common parameters for question commands."""
    config = ctx.obj["config"]
    country_code = ctx.obj["country_code"]
    answer_display = ctx.obj["answer_display"]
    save_to_file = ctx.obj["save_to_file"]
    exam_type = utils.select_option_from_list(
        ExamType.supported_country_options(CountryCode.from_id(country_code)), "Exam type"
    )
    country_code = CountryCode.from_id(country_code)
    answer_display = QuestionAnswerDisplay.from_id(answer_display)
    exam_type = ExamType.from_id(exam_type)
    logger.info(
        f"Listing questions for country: {country_code}, exam type: {exam_type} "
        f"with answer display: {answer_display} "
        f"and save to file: {save_to_file}",
    )

    return config, country_code, answer_display, save_to_file, exam_type


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
@click.option(
    "--no-save-to-file",
    is_flag=True,
    default=False,
    help="Display the output without saving to file.",
)
@click.pass_context
def question(ctx, country, answer_display, no_save_to_file):
    """Commands related to question management."""
    ctx.obj["country_code"] = country
    ctx.obj["answer_display"] = answer_display
    ctx.obj["save_to_file"] = not no_save_to_file


@question.command("list")
@click.option(
    "--criteria",
    type=click.Choice(GeneralQuestionListingType.ids()),
    help="List questions with specific criteria.",
)
@click.option(
    "--top-criteria",
    type=click.Choice(TopQuestionsListingType.ids()),
    help="List top N questions.",
)
@click.pass_context
def list_questions(
    ctx,
    criteria,
    top_criteria,
):
    """List questions based on the criteria."""
    config, country_code, answer_display, save_to_file, exam_type = get_common_question_params(ctx)
    criteria_type: QuestionListingType | None = GeneralQuestionListingType.ALL
    max_questions = 0
    if criteria:
        criteria_type = QuestionListingType.from_id(criteria)
        logger.info(f"Listing questions based on criteria: {criteria_type}")
    elif top_criteria:
        logger.info(f"Listing top {top_criteria} questions.")
        criteria_type = QuestionListingType.from_id(top_criteria)
        max_questions = utils.read_number_from_input(
            "Enter the number of questions to list",
            constants.MIN_TOP_QUESTIONS_COUNT,
            constants.MAX_TOP_QUESTIONS_COUNT,
        )

    logger.info(f"Exam type: {exam_type}")
    qp = QuestionProcessor(
        config,
        country_code,
        exam_type,
    )
    qp.list(criteria_type, answer_display, max_questions, save_to_file)


@question.command("marked")
@click.option(
    "--criteria",
    type=click.Choice(MarkedQuestionListingType.ids()),
    default=MarkedQuestionListingType.WRONG_ATTEMPT.id,
    help="List marked questions with specific criteria.",
)
@click.pass_context
def list_marked_questions(ctx, criteria):
    """List marked questions based on the criteria."""
    config, country_code, answer_display, save_to_file, exam_type = get_common_question_params(ctx)
    questions_count = utils.read_number_from_input(
        "Enter the number of attempts/count to consider",
        constants.MIN_MARKED_QUESTIONS_COUNT,
        constants.MAX_MARKED_QUESTIONS_COUNT,
    )

    qp = QuestionProcessor(
        config,
        country_code,
        exam_type,
    )
    criteria_type: QuestionListingType = QuestionListingType.from_id(criteria)
    qp.list_marked(criteria_type, answer_display, questions_count, save_to_file)


# QUIZ COMMANDS
@hamradiotoolbox.group("quiz")
@click.option(
    "--country",
    type=click.Choice(CountryCode.supported_ids(), case_sensitive=False),
    required=True,
    help="Country for which to start the quiz.",
)
@click.option(
    "--number-of-questions",
    type=int,
    help="Number of questions in the quiz.",
)
@click.option(
    "--answer-display",
    type=click.Choice(QuizAnswerDisplay.ids()),
    default=QuizAnswerDisplay.AFTER_QUESTION.id,
    help="Display the question w/o answer.",
)
@click.option(
    "--qs",
    type=click.Choice(QuizSource.ids()),
    default=QuizSource.ALL.id,
    help="Source of questions for the quiz.",
)
@click.pass_context
def quiz(ctx, country, number_of_questions, answer_display, qs):
    """Commands for managing quizzes."""
    ctx.obj["country_code"] = country
    ctx.obj["answer_display"] = answer_display
    config = ctx.obj["config"]
    quiz_config: dict = config.get("quiz")
    if not number_of_questions and quiz_config:
        number_of_questions = quiz_config.get("number_of_questions", DEFAULT_QUIZ_QUESTION_COUNT)
    if number_of_questions and number_of_questions < 1:
        logger.error("Number of questions should be greater than 0.")
        return
    ctx.obj["number_of_questions"] = number_of_questions
    ctx.obj["quiz_config"] = quiz_config

    print_config: dict = config.get("print_question")
    if not answer_display:
        answer_display = print_config.get(
            "answer_display",
        )
    ctx.obj["answer_display"] = answer_display
    ctx.obj["print_config"] = print_config

    metrics_config: dict = config.get("metrics")
    if not metrics_config:
        logger.error("Metrics configuration not found.")
        return
    ctx.obj["metrics_config"] = metrics_config

    ctx.obj["qs"] = qs

    logger.info(
        f"Quiz for country: {country}, number of questions: {number_of_questions}, "
        f"answers display: {answer_display}, quiz source: {qs}"
    )


@quiz.command("start")
@click.pass_context
def start_quiz(ctx):
    """Start a quiz based on the exam type."""
    country_code = ctx.obj["country_code"]
    if not country_code:
        logger.error("Country code not found.")
        return

    country: CountryCode = CountryCode.from_id(country_code)  # type: ignore
    exam_type: str | None = utils.select_option_from_list(
        ExamType.supported_country_ids(country), "Exam type"
    )
    if not exam_type:
        logger.error("Exam type not found.")
        return
    number_of_questions = ctx.obj["number_of_questions"]
    config = ctx.obj["config"]
    answer_display = ctx.obj["answer_display"]
    quiz_source = ctx.obj["qs"]
    quiz_config = ctx.obj["quiz_config"]
    print_config = ctx.obj["print_config"]
    metrics_config = ctx.obj["metrics_config"]
    if not number_of_questions:
        number_of_questions = quiz_config.get("number_of_questions", DEFAULT_QUIZ_QUESTION_COUNT)
    logger.info(f"Starting quiz for {exam_type} with {number_of_questions} questions.")
    qp = QuestionProcessor(
        config,
        country,
        ExamType.from_id(exam_type),
        QuestionDisplayMode.QUIZ,
    )
    question_bank = qp.get_question_bank()
    quiz_processor = QuizProcessor(
        question_bank,
        number_of_questions,
        QuestionDisplayMode.QUIZ,
        QuizAnswerDisplay.from_id(answer_display),
        QuizSource.from_id(quiz_source),
        quiz_config,
        print_config,
        metrics_config,
    )
    quiz_processor.process()


# PRACTICE EXAM COMMANDS
@hamradiotoolbox.group("practice")
@click.option(
    "--country",
    type=click.Choice(CountryCode.supported_ids(), case_sensitive=False),
    required=True,
    help="Country for which to start the quiz.",
)
@click.pass_context
def practice(ctx, country):
    """Commands for managing practice exams."""
    ctx.obj["country_code"] = country
    config = ctx.obj["config"]

    practice_config: dict = config.get_practice_exam_settings()
    if not practice_config:
        logger.error("Practice exam configuration not found.")
        return
    ctx.obj["practice_config"] = practice_config

    country_config = config.get_country_settings(country)
    if not country_config:
        logger.error(f"Country {country} not found in the configuration.")
        return
    ctx.obj["country_config"] = country_config

    ctx.obj["print_config"] = config.get("print_question")

    metrics_config: dict = config.get("metrics")
    if not metrics_config:
        logger.error("Metrics configuration not found.")
        return
    ctx.obj["metrics_config"] = metrics_config

    logger.info(f"Practice exam for country: {country}")


@practice.command("start")
@click.pass_context
def start_practice_exam(ctx):
    """Start a practice exam."""
    country_code = ctx.obj["country_code"]
    if not country_code:
        logger.error("Country code not found.")
        return
    country = CountryCode.from_id(country_code)
    exam_type = utils.select_option_from_list(ExamType.supported_country_ids(country), "Exam type")
    if not exam_type:
        logger.error("Exam type not found.")
        return

    country_config = ctx.obj["country_config"]
    exam_type_config = country_config.get("question_bank").get(exam_type)
    if not exam_type_config:
        logger.error(
            f"Exam type {exam_type} not found in the country {country_code} configuration."
        )
        return
    number_of_questions = exam_type_config.get("number_of_questions")
    if not number_of_questions:
        logger.error("Number of questions not found.")
        return

    config = ctx.obj["config"]
    metrics_config = ctx.obj["metrics_config"]
    practice_config = ctx.obj["practice_config"]
    print_config = ctx.obj["print_config"]
    logger.info(f"Starting practice exam for {exam_type} with {number_of_questions} questions.")
    qp = QuestionProcessor(
        config,
        country,
        ExamType.from_id(exam_type),
        QuestionDisplayMode.PRACTICE_EXAM,
    )

    question_bank = qp.get_question_bank()
    quiz_processor = QuizProcessor(
        question_bank,
        number_of_questions,
        QuestionDisplayMode.PRACTICE_EXAM,
        QuizAnswerDisplay.from_id(DEFAULT_ANSWER_DISPLAY_PRACTICE_EXAM.id),
        QuizSource.ALL,
        practice_config.get(DEFAULT_ANSWER_DISPLAY_PRACTICE_EXAM.id),
        print_config,
        metrics_config,
    )
    quiz_processor.process()


# DOWNLOAD COMMANDS
@hamradiotoolbox.group("download")
@click.option(
    "--country",
    type=click.Choice(CountryCode.supported_ids(), case_sensitive=False),
    required=True,
    help="Country for which to download the question bank.",
)
@click.option(
    "--output",
    default="data/output",
    type=click.Path(),
    help="Output folder to save the downloaded files.",
)
@click.pass_context
def download(ctx, country, output):
    """Commands for downloading data."""
    ctx.obj["country_code"] = country
    ctx.obj["output"] = output
    logger.info(f"Downloading data for country: {country}")


def get_downloader(ctx, download_type_value: str, country_download_type_config_key: str):
    country_code = ctx.obj["country_code"]
    country = CountryCode.from_id(country_code)
    output = ctx.obj["output"]
    config = ctx.obj["config"]

    chrome_driver_path: str = config.get("web_driver")
    if not chrome_driver_path:
        chrome_driver_path = ChromeDriverManager().install()
        logger.info(f"Chrome driver path not found. Installing driver at: {chrome_driver_path}")

    country_config = config.get_country_settings(country_code)
    if not country_config:
        logger.error(f"Country {country_code} not found in the configuration")
        return None

    output_config = config.get_output()
    if not output_config:
        logger.error("Output configuration not found")
        return None

    output_folder = output or (output_config.get("folder") if output_config else None)
    if not output_folder:
        logger.error("Output folder not found")
        return None

    download_type = DownloadType.from_id_and_country(download_type_value, country)
    if not download_type:
        logger.error(f"Download type {download_type_value} not found in the configuration")
        return None

    dt_config = config.get_country_settings(country_code).get(country_download_type_config_key)
    app_config = config.get("application")

    return DownloaderFactory.get_downloader(
        chrome_driver_path,
        country,
        download_type,
        output_folder,
        dt_config,
        app_config,
    )


@download.command("question-bank")
@click.pass_context
def download_question_bank(ctx):
    """Download a question bank for a specific country."""
    downloader = get_downloader(ctx, "question-bank", "question_bank")
    if not downloader:
        logger.error("Downloader not found.")
        return

    country_code = ctx.obj["country_code"]
    country = CountryCode.from_id(country_code)
    exam_type = utils.select_option_from_list(
        ExamType.supported_country_ids(country),
        "Exam type",
    )
    et = ExamType.from_id_and_country(exam_type, country)
    if not et:
        logger.error(f"Exam type {exam_type} not found in the configuration")
        return

    downloader.download_question_bank(et)


@download.command("callsign")
@click.pass_context
def download_callsign(ctx):
    """Download callsigns for a specific country."""
    downloader = get_downloader(ctx, "callsign", "callsign")
    if not downloader:
        logger.error("Downloader not found.")
        return

    country_code = ctx.obj["country_code"]
    country = CountryCode.from_id(country_code)
    cs_type = utils.select_option_from_list(
        CallSignDownloadType.supported_country_options(country),
        "Callsign type",
    )
    if not cs_type:
        logger.error(f"Callsign type {cs_type} not found in the configuration")
        return

    callsign_dt = CallSignDownloadType.from_value_and_country(cs_type, country)
    if not callsign_dt:
        logger.error(f"Callsign download type {cs_type} not found in the configuration")
        return

    downloader.download_callsigns(callsign_dt)


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
    help="Sort the callsigns by a specific criteria: callsign (alphabetical order).",
)
@click.option(
    "--rank-by",
    type=click.Choice(RankBy.ids()),
    help="Rank the callsigns by a specific criteria: phonetic-clarity (how clear it sounds), "
    "confusing-pair (how similar it is to another callsign) "
    "and cw-weight (how easy it is to send in Morse code).",
)
@click.pass_context
def callsign(ctx, country, match, include, exclude, sort_by, rank_by):
    """Query and analyze callsigns for a specific country."""

    def get_phonetic_clarity_options(hrt_config: HRTConfig):
        callsign_config = hrt_config.get("callsign")
        return (
            callsign_config.get("phonetic_clarities")
            if isinstance(callsign_config, dict)
            else None
        )

    def get_confusing_pairs(hrt_config: HRTConfig):
        callsign_config = hrt_config.get("callsign")
        return (
            callsign_config.get("confusing_pairs") if isinstance(callsign_config, dict) else None
        )

    config = ctx.obj["config"]

    phonetic_clarity = None
    if rank_by and rank_by == RankBy.PHONETIC_CLARITY.id:
        phonetic_clarity_options = get_phonetic_clarity_options(config)
        if isinstance(phonetic_clarity_options, dict):
            phonetic_clarity = utils.select_from_options(
                phonetic_clarity_options, "Phonetic clarity option"
            )
        else:
            logger.error("Phonetic clarity options not found or not a dictionary")

    confusing_pair = None
    if rank_by and rank_by == RankBy.CONFUSING_PAIR.id:
        confusing_pairs = get_confusing_pairs(config)
        if isinstance(confusing_pairs, dict):
            confusing_pair = utils.select_from_options(confusing_pairs, "Confusing pair")
        else:
            logger.error("Confusing pairs not found or not a dictionary")

    match_options = match if match else []
    include_options = include if include else []
    exclude_options = exclude if exclude else []
    logger.info(f"Include options: {include_options}, Exclude options: {exclude_options}")

    processor = CallSignsProcessor(
        config,
        country,
        phonetic_clarity,
        confusing_pair,
        rank_by,
        match_options,
        include_options,
        exclude_options,
        sort_by,
    )
    processor.process_callsigns()


if __name__ == "__main__":
    hamradiotoolbox()
    logger.info("Ham Radio Toolbox completed.")
    logger.shutdown()
