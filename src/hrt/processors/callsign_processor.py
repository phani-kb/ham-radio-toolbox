"""Processor for generating callsign questions."""

from hrt.common import utils
from hrt.common.config_reader import HRTConfig, logger
from hrt.common.constants import CW_DOT_DASH_WEIGHT
from hrt.common.enums import NumberOfLetters, RankBy
from hrt.common.utils import get_word_combinations, write_output


class CallSignsProcessor:
    """Processor for generating callsign questions."""

    def __init__(
        self,
        config,
        country_code,
        phonetic_clarity_option,
        confusing_pair_option,
        rank_by,
        match_options,
        include_options,
        exclude_options,
        sort_by,
    ):
        self.config: HRTConfig = config
        self.country_code = country_code
        self.phonetic_clarity_option = phonetic_clarity_option
        self.confusing_pair_option = confusing_pair_option
        self.rank_by = rank_by
        self.match_options = match_options
        self.include_options = include_options
        self.exclude_options = exclude_options
        self.sort_by = sort_by
        self.scores = {}

    def get_country_code(self):
        """Get the country code."""
        return self.country_code

    def get_phonetic_clarity_option(self):
        """Get the phonetic clarity option."""
        return self.phonetic_clarity_option

    def get_confusing_pair(self):
        """Get the confusing pair option."""
        return self.confusing_pair_option

    def get_includes(self):
        """Get the include options."""
        return self.include_options

    def get_excludes(self):
        """Get the exclude options."""
        return self.exclude_options

    def load_callsigns(self):
        """Load the callsigns."""
        callsign_config = self.config.get_country_settings(self.country_code).get("callsign")
        folder_path = self.config.get_input().get("folder")
        folder_path = f"{folder_path}/{self.country_code}/callsign"
        file_path = callsign_config.get("available").get("file")
        file_path = f"{folder_path}/{file_path}"
        return utils.load_callsigns_from_file(file_path)

    @staticmethod
    def match_callsigns_with_words(callsigns, words):
        """Match callsigns with words, ignoring case."""
        matched_callsigns = set()
        matches_with_words = set()
        for callsign in callsigns:
            for word in words:
                if word.lower() in callsign.lower():
                    matched_callsigns.add(callsign)
                    matches_with_words.add(f"{callsign} - {word}")
                    break
        return matched_callsigns, matches_with_words

    def get_words_by_length(self, length):
        """Get words by length."""
        file_key = {2: "two_letter_words", 3: "three_letter_words"}.get(length)
        if not file_key:
            return []

        input_folder = self.config.get_input().get("folder")
        file_path = self.config.get_input().get("files").get(file_key)
        file_path = f"{input_folder}/{file_path}"
        return utils.read_words_from_file(file_path) if file_path else []

    def _process_end_option(self, callsigns: set, option_set: set) -> set:
        """Process END option for callsigns."""
        matched_callsigns = {cs for cs in callsigns if cs[-1] in option_set}
        logger.info(
            "Included callsigns based on END value(s): %s: %d",
            option_set,
            len(matched_callsigns),
        )
        return matched_callsigns

    def _process_multiple_option(self, callsigns: set, option_set: set) -> set:
        """Process MULTIPLE option for callsigns."""
        matched_callsigns = set()
        for callsign in callsigns:
            if any(char * 2 in callsign or char * 3 in callsign for char in option_set):
                matched_callsigns.add(callsign)
        logger.info(
            "Included callsigns based on MULTIPLE value(s): %s: %d",
            option_set,
            len(matched_callsigns),
        )
        return matched_callsigns

    def process_options(self, callsigns, options, include=True):
        """Process callsigns by specific options."""
        country_code = self.get_country_code()
        key = "includes" if include else "excludes"
        final_callsigns = set()

        # Handle ALL option
        if NumberOfLetters.ALL.name in options:
            options = (
                NumberOfLetters.get_supported_number_of_letters("include")
                if include
                else NumberOfLetters.get_supported_number_of_letters("exclude")
            )
            options.remove(NumberOfLetters.ALL.name)

        # Filter valid options
        options = [opt for opt in options if self.config.get_callsign().get(key).get(opt)]
        if not options:
            return callsigns

        # Process each option
        for option in options:
            option_value = self.config.get_callsign().get(key).get(option)
            if not option_value:
                continue

            option_set = set(option_value)
            if option == NumberOfLetters.END.name:
                matched = self._process_end_option(callsigns, option_set)
            elif option == NumberOfLetters.MULTIPLE.name:
                matched = self._process_multiple_option(callsigns, option_set)
            else:
                matched = self.match_callsigns_with_combinations(callsigns, option_set)
                logger.info(
                    "Included callsigns based on %s value(s): %s: %d",
                    option,
                    option_set,
                    len(matched),
                )
            final_callsigns.update(matched)

        # Save results
        logger.info("Callsigns based on criteria: %d", len(final_callsigns))
        output_folder = f"{self.config.get_output().get('folder')}/{country_code}"
        output_file_path = f"{output_folder}/{key}.txt"
        write_output(final_callsigns, output_file_path)
        logger.info("Matched callsigns saved to %s", output_file_path)

        return final_callsigns

    def _process_must_include_exclude(self, callsigns: set) -> set:
        """Process must include and exclude callsigns."""
        must_include = set(self.config.get_callsign().get("must_include") or set())
        must_exclude = set(self.config.get_callsign().get("must_exclude") or set())

        if must_include:
            logger.info("Must include callsigns: %d", len(must_include))
        if must_exclude:
            logger.info("Must exclude callsigns: %d", len(must_exclude))

        # Filter callsigns based on must include and exclude
        if not must_include and not must_exclude:
            return callsigns
        if must_include and must_exclude:
            # remove callsigns that must be excluded
            final_exclude = must_exclude - must_include
            callsigns = callsigns - final_exclude
        logger.info("Final callsigns after must include/exclude: %d", len(callsigns))
        return callsigns

    def process_match_option(self, callsigns, length, country_code):
        """Process callsigns by matching with words of specific length."""
        words = self.get_words_by_length(length)
        logger.info("Loaded %d %d-letter words.", len(words), length)

        matched_callsigns, matches_with_words = self.match_callsigns_with_words(callsigns, words)
        logger.info("Matched %d callsigns with %d-letter words.", len(matched_callsigns), length)

        output_folder = self.config.get_output().get("folder")
        output_folder = f"{output_folder}/{country_code}"
        output_filename = f"matched-{length}-letter_words.txt"
        output_file_path = f"{output_folder}/{output_filename}"
        write_output(matches_with_words, output_file_path)
        logger.info("Matched callsigns saved to %s", output_file_path)
        return matched_callsigns

    @staticmethod
    def match_callsigns_with_combinations(callsigns, option_set):
        """Match callsigns with combinations of options."""
        matched_callsigns = set()
        for callsign in callsigns:
            for option in option_set:
                combinations = get_word_combinations(option)
                if any(combination.lower() in callsign.lower() for combination in combinations):
                    matched_callsigns.add(callsign)
                    break
        return matched_callsigns

    def rank_callsigns_by_cw_weight(self, callsigns):
        """Rank callsigns by CW weight."""
        sorted_callsigns = []
        morse_code = self.config.get_callsign().get("morse_code")
        for callsign in callsigns:
            weight = 0
            number_of_dot_dash = 0
            for letter in callsign:
                morse = morse_code.get(letter.upper())
                if morse:
                    number_of_dot_dash += len(morse)
                    for char in morse:
                        weight += CW_DOT_DASH_WEIGHT.get(char, 0)
                    weight += len(morse) - 1  # 1 unit gap between each dash or dot in a character
                else:
                    logger.warning("No morse code found for letter: %s", letter)
            weight += (len(callsign) - 1) * 3  # 3 unit gap between each character
            weight += 3  # extra 3 units for the last character
            sorted_callsigns.append((callsign, weight, number_of_dot_dash))

        sorted_callsigns = sorted(sorted_callsigns, key=lambda x: (x[1], x[2]), reverse=False)
        output_folder = self.config.get_output().get("folder")
        output_folder = f"{output_folder}/{self.country_code}"
        output_file_path = f"{output_folder}/rank-by-{RankBy.CW_WEIGHT.value}.txt"
        write_output(sorted_callsigns, output_file_path)
        logger.info("Ranked callsigns by CW weight saved to %s", output_file_path)
        return sorted_callsigns

    def process_callsigns(self):
        """Process callsigns."""
        country_code = self.get_country_code()
        logger.info("Processing callsigns for country code: %s", country_code)
        logger.info("Phonetic clarity options: %s", self.get_phonetic_clarity_option())
        logger.info("Confusing pairs: %s", self.get_confusing_pair())

        # Load and process callsigns
        callsigns = self.load_callsigns()
        logger.info("Available callsigns: %d", len(callsigns))

        # Handle match options
        if self.match_options:
            length = 2 if "2l" in self.match_options else 3 if "3l" in self.match_options else None
            if length is None:
                raise ValueError("Invalid match option.")
            callsigns = self.process_match_option(callsigns, length, country_code)

        # Process include/exclude options
        included_callsigns = (
            self.process_options(callsigns, self.include_options)
            if self.include_options
            else set()
        )
        excluded_callsigns = (
            self.process_options(callsigns, self.exclude_options, False)
            if self.exclude_options
            else set()
        )

        # Determine final set based on include/exclude options
        if self.include_options and self.exclude_options:
            callsigns = included_callsigns - excluded_callsigns
        elif self.include_options:
            callsigns = included_callsigns
        elif self.exclude_options:
            callsigns = callsigns - excluded_callsigns

        # Sort and finalize callsigns
        final_callsigns = set(utils.sort_callsigns(list(callsigns), self.sort_by))
        logger.info("Final callsigns: %d", len(final_callsigns))

        # Save final callsigns
        final_file_path = f"{self.config.get_output().get('folder')}/{country_code}/final.txt"
        write_output(list(final_callsigns), final_file_path)
        logger.info("Final callsigns saved to %s", final_file_path)

        # Process must include/exclude callsigns
        final_callsigns = self._process_must_include_exclude(final_callsigns)

        # Rank callsigns if requested
        if self.rank_by and RankBy.CW_WEIGHT.id == self.rank_by[0][0]:
            final_callsigns = self.rank_callsigns_by_cw_weight(final_callsigns)

        logger.info("Final callsigns: %d", len(final_callsigns))
        return final_callsigns
