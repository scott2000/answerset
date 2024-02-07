from typing import Optional

from .config import Config

prefix_limit = 3
max_similarity = 0x7fffffff

def similarity(a: str, b: str) -> int:
    """
    Returns the length of the longest common subsequence between two strings suffixes.
    """

    # Make string "b" be smaller than "a"
    if len(a) < len(b):
        a, b = b, a

    # If "b" is empty, the similarity is zero
    if not len(b):
        return 0

    # Iteratively compute using an array and two variables
    arr = [0] * len(b)
    for i in range(len(a)):
        prev_prev = 0
        curr_prev = 0

        for j in range(len(b)):
            prev_curr = arr[j]

            if a[i] == b[j]:
                arr[j] = prev_prev + 1
            else:
                arr[j] = max(prev_curr, curr_prev)

            prev_prev = prev_curr
            curr_prev = arr[j]

    return arr[-1]

def adj_similarity(config: Config, a_full: str, b_full: str) -> int:
    """
    Returns the similarity between two strings adjusted to prefer matching
    prefixes and ignore junk characters.
    """

    # Remove characters that aren't useful for matching
    a = a_full.translate(config.junk_trans)
    b = b_full.translate(config.junk_trans)

    # If a string has all junk characters, then leave them
    if not a or not b:
        a, b = a_full, b_full

    # If equal, then return max_similarity immediately
    if a == b:
        return max_similarity

    # Find the length of the shared prefix, up to prefix_limit
    overlap = min(len(a), len(b), prefix_limit)
    prefix = 0
    while prefix < overlap and a[prefix] == b[prefix]:
        prefix += 1

    # Return similarity adjusted for prefix length
    return prefix_limit * similarity(a, b) + prefix

# Answer choice and comment tuple
Choice = tuple[str, str]

# Pairing of given and correct answer choices
ChoicePair = tuple[Optional[Choice], Optional[Choice]]

class Arranger:
    __slots__ = 'config', 'given', 'correct', 'memo', 'closest', 'assigned', 'used'

    def __init__(self, config: Config, given: list[Choice], correct: list[Choice]):
        self.config = config
        self.given = given
        self.correct = correct
        self.memo: dict[tuple[int, int], int] = {}
        self.closest: dict[int, int] = {}
        self.assigned: dict[int, int] = {}
        self.used: set[int] = set()

    def get_similarity(self, i: int, j: int) -> int:
        """Find the similarity between a "given" part and a "correct" part."""

        if (i, j) in self.memo:
            return self.memo[(i, j)]

        s = adj_similarity(self.config, self.given[i][0], self.correct[j][0])
        self.memo[(i, j)] = s
        return s

    def max_for(self, i: int) -> int:
        """
        Compute the maximum similarity for a specific "given" part to the nearest
        matching "correct" part.
        """

        # Check for already computed maximum similarity
        if i in self.closest and self.closest[i] not in self.used:
            return self.get_similarity(i, self.closest[i])

        # Find the closest "correct" part
        closest = None
        closest_similarity = -1
        for j in range(len(self.correct)):
            # Skip "correct" parts which were already used
            if j in self.used:
                continue

            # Update maximum similarity
            s = self.get_similarity(i, j)
            if s > closest_similarity:
                closest = j
                closest_similarity = s

                # A similarity of max_similarity is an exact match
                if s == max_similarity:
                    break

        # Remember the closest value and return the similarity
        if closest is not None:
            self.closest[i] = closest
        return closest_similarity

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
        closest_similarity = -1
        for i in range(len(self.given)):
            # Skip "given" parts which are already assigned
            if i in self.assigned:
                continue

            # Update maximum similarity
            s = self.max_for(i)
            if s > closest_similarity:
                closest = i
                closest_similarity = s

                # A similarity of max_similarity is an exact match
                if s == max_similarity:
                    break

        # Record the assignment
        if closest is None:
            return False

        target = self.closest[closest]
        self.assigned[closest] = target
        self.used.add(target)

        return True

    def finalize(self) -> list[ChoicePair]:
        """Create a list of parts which should be compared."""

        # Put "given" parts and their matching "correct" parts first
        parts: list[ChoicePair] = []
        for i in range(len(self.given)):
            if i in self.assigned:
                parts.append((self.given[i], self.correct[self.assigned[i]]))
            else:
                parts.append((self.given[i], None))

        # Put all unused "correct" parts after
        for j in range(len(self.correct)):
            if j not in self.used:
                parts.append((None, self.correct[j]))

        return parts

def arrange(config: Config, given: list[Choice], correct: list[Choice]) -> list[ChoicePair]:
    """Rearrange parts so that similar ones line up."""

    arranger = Arranger(config, given, correct)
    while arranger.step():
        pass

    return arranger.finalize()
