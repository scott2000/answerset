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
    __slots__ = 'config', 'given', 'correct', 'cached_pairs', 'closest', 'assigned', 'used'

    def __init__(self, config: Config, given: list[Choice], correct: list[Choice]) -> None:
        self.config = config
        self.given = given
        self.correct = correct
        self.cached_pairs: dict[tuple[int, int], ChoicePair] = {}
        self.closest: dict[int, int] = {}
        self.assigned: dict[int, int] = {}
        self.used: set[int] = set()

    def get_choice_pair(self, i: int, j: int) -> ChoicePair:
        """Find the ChoicePair for a "given" part and a "correct" part."""

        if (i, j) in self.cached_pairs:
            return self.cached_pairs[(i, j)]

        pair = ChoicePair(self.config, self.given[i], self.correct[j])
        self.cached_pairs[(i, j)] = pair
        return pair

    def best_choice_pair_for(self, i: int) -> Optional[ChoicePair]:
        """Find the best ChoicePair for a specific "given" part."""

        # Check for already found best ChoicePair
        if i in self.closest and self.closest[i] not in self.used:
            return self.get_choice_pair(i, self.closest[i])

        # Check for exact matches
        for j in range(len(self.correct)):
            # Skip "correct" parts which were already used
            if j in self.used:
                continue

            pair = self.get_choice_pair(i, j)
            if pair.is_exact_match():
                self.closest[i] = j
                return pair

        # Find the closest "correct" part
        closest = None
        closest_choice_pair: Optional[ChoicePair] = None
        for j in range(len(self.correct)):
            # Skip "correct" parts which were already used
            if j in self.used:
                continue

            pair = self.get_choice_pair(i, j)
            if pair.is_better_than(closest_choice_pair):
                closest = j
                closest_choice_pair = pair

        # Remember the closest value and return the choice pair
        if closest is not None:
            self.closest[i] = closest
        return closest_choice_pair

    def step(self) -> bool:
        """
        Make an assignment for the most similar pair. Returns True if more
        steps are needed and False otherwise.
        """

        # If all "given" parts are assigned, we are done
        if len(self.assigned) == len(self.given):
            return False

        # If all "correct" parts are used, we are done
        if len(self.used) == len(self.correct):
            return False

        # Find closest pair of "given" and "correct"
        closest = None
        closest_choice_pair: Optional[ChoicePair] = None
        for i in range(len(self.given)):
            # Skip "given" parts which are already assigned
            if i in self.assigned:
                continue

            pair = self.best_choice_pair_for(i)
            if pair is not None and pair.is_better_than(closest_choice_pair):
                closest = i
                closest_choice_pair = pair

                if pair.is_exact_match():
                    break

        if closest is None:
            return False

        # Record the assignment
        target = self.closest[closest]
        self.assigned[closest] = target
        self.used.add(target)

        return True

    def finalize(self) -> list[Union[ChoicePair, UnmatchedChoice]]:
        """Create a list of parts which should be compared."""

        # Put "given" parts and their matching "correct" parts first
        parts: list[Union[ChoicePair, UnmatchedChoice]] = []
        for i in range(len(self.given)):
            if i in self.assigned:
                parts.append(self.get_choice_pair(i, self.assigned[i]))
            else:
                parts.append(UnmatchedChoice(False, self.given[i]))

        # Put all unused "correct" parts after
        for j in range(len(self.correct)):
            if j not in self.used:
                parts.append(UnmatchedChoice(True, self.correct[j]))

        return parts

def arrange(config: Config, given: list[Choice], correct: list[Choice]) -> list[Union[ChoicePair, UnmatchedChoice]]:
    """Rearrange parts so that similar ones line up."""

    arranger = Arranger(config, given, correct)
    while arranger.step():
        pass

    return arranger.finalize()
