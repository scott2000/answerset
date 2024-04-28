from dataclasses import dataclass
from typing import Optional, Union

from .config import Config
from .diff import Choice, ChoicePair

@dataclass(frozen=True)
class UnmatchedChoice:
    __slots__ = 'is_correct', 'choice'

    is_correct: bool
    choice: Choice

class Arranger:
    __slots__ = 'config', 'given', 'correct', 'cached_pairs', 'closest_to_given', 'assigned_to_given', 'used_correct'

    def __init__(self, config: Config, given: list[Choice], correct: list[Choice]) -> None:
        self.config = config
        self.given = given
        self.correct = correct

        # ChoicePairs are created when needed to avoid doing unnecessary work
        self.cached_pairs: dict[tuple[int, int], ChoicePair] = {}

        # The closest "correct" choice to each "given" choice is saved between
        # iterations to improve efficiency. After the first iteration, it is
        # only be necessary to find a new closest choice if two "given" choices
        # were closest to the same "correct" choice.
        self.closest_to_given: dict[int, int] = {}

        # Final assignments from "given" to "correct" choices
        self.assigned_to_given: dict[int, int] = {}

        # Set of already used "correct" choices
        self.used_correct: set[int] = set()

    def get_choice_pair(self, given_index: int, correct_index: int) -> ChoicePair:
        """Find the ChoicePair for a "given" part and a "correct" part."""

        if (given_index, correct_index) in self.cached_pairs:
            return self.cached_pairs[(given_index, correct_index)]

        pair = ChoicePair(self.config, self.given[given_index], self.correct[correct_index])
        self.cached_pairs[(given_index, correct_index)] = pair
        return pair

    def assign_to_closest(self, given_index: int) -> None:
        """Make the final assignment for a "given" part."""

        correct_index = self.closest_to_given[given_index]
        self.assigned_to_given[given_index] = correct_index
        self.used_correct.add(correct_index)

    def is_finished(self) -> bool:
        """Check whether all assignments have been made."""

        # If all "given" parts are assigned, we are done
        if len(self.assigned_to_given) == len(self.given):
            return True

        # If all "correct" parts are used, we are done
        if len(self.used_correct) == len(self.correct):
            return True

        return False

    def assign_exact_matches(self) -> None:
        """Assign all exact matches """

        for given_index in range(len(self.given)):
            if self.is_finished():
                break

            for correct_index in range(len(self.correct)):
                if correct_index in self.used_correct:
                    continue

                pair = self.get_choice_pair(given_index, correct_index)

                if pair.is_exact_match():
                    self.closest_to_given[given_index] = correct_index
                    self.assign_to_closest(given_index)
                    break

    def best_choice_pair_for(self, given_index: int) -> Optional[ChoicePair]:
        """Find the best ChoicePair for a specific "given" part."""

        # Check for already found best ChoicePair
        if given_index in self.closest_to_given and self.closest_to_given[given_index] not in self.used_correct:
            return self.get_choice_pair(given_index, self.closest_to_given[given_index])

        # Find the closest "correct" part
        closest = None
        closest_choice_pair: Optional[ChoicePair] = None
        for correct_index in range(len(self.correct)):
            # Skip "correct" parts which were already used
            if correct_index in self.used_correct:
                continue

            pair = self.get_choice_pair(given_index, correct_index)
            if pair.is_better_than(closest_choice_pair):
                closest = correct_index
                closest_choice_pair = pair

        # Remember the closest value and return the choice pair
        if closest is not None:
            self.closest_to_given[given_index] = closest
        return closest_choice_pair

    def step(self) -> bool:
        """
        Make an assignment for the most similar pair. Returns True if more
        steps are needed and False otherwise.
        """

        if self.is_finished():
            return False

        # Find closest pair of "given" and "correct"
        closest = None
        closest_choice_pair: Optional[ChoicePair] = None
        for given_index in range(len(self.given)):
            # Skip "given" parts which are already assigned
            if given_index in self.assigned_to_given:
                continue

            pair = self.best_choice_pair_for(given_index)
            if pair is not None and pair.is_better_than(closest_choice_pair):
                closest = given_index
                closest_choice_pair = pair

        if closest is None:
            return False

        self.assign_to_closest(closest)
        return True

    def finalize(self) -> list[Union[ChoicePair, UnmatchedChoice]]:
        """Create a list of parts which should be compared."""

        # Put "given" parts and their matching "correct" parts first
        parts: list[Union[ChoicePair, UnmatchedChoice]] = []
        for given_index in range(len(self.given)):
            if given_index in self.assigned_to_given:
                parts.append(self.get_choice_pair(given_index, self.assigned_to_given[given_index]))
            else:
                parts.append(UnmatchedChoice(False, self.given[given_index]))

        # Put all unused "correct" parts after
        for correct_index in range(len(self.correct)):
            if correct_index not in self.used_correct:
                parts.append(UnmatchedChoice(True, self.correct[correct_index]))

        return parts

def arrange(config: Config, given: list[Choice], correct: list[Choice]) -> list[Union[ChoicePair, UnmatchedChoice]]:
    """Rearrange parts so that similar ones line up."""

    arranger = Arranger(config, given, correct)
    arranger.assign_exact_matches()
    while arranger.step():
        pass

    return arranger.finalize()
