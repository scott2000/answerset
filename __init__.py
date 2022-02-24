import difflib
import html
import unicodedata as ucd
import re

from aqt.reviewer import Reviewer

junk_re = re.compile(r"[-\s]")
prefix_limit = 3
max_dist = 0x7fffffff

def dist(a, b):
    """Returns the Levenshtein distance between two strings suffixes."""

    # Make string "b" be smaller than "a"
    if len(a) < len(b):
        a, b = b, a

    # If "b" is empty, the distance is the length of "a"
    if not len(b):
        return len(a)

    # Iteratively compute using an array and two variables
    arr = list(range(1, len(b) + 1))
    for i in range(len(a)):
        prev_prev = i
        curr_prev = i + 1

        for j in range(len(b)):
            prev_curr = arr[j]

            if a[i] == b[j]:
                arr[j] = prev_prev
            else:
                arr[j] = min(prev_curr, curr_prev, prev_prev) + 1

            prev_prev = prev_curr
            curr_prev = arr[j]

    return arr[-1]

def adj_dist(a, b):
    """
    Returns the Levenshtein distance between two strings adjusted to prefer
    matching prefixes and ignore whitespace and hyphens.
    """

    # Remove whitespace and hyphens
    a = re.sub(junk_re, '', a)
    b = re.sub(junk_re, '', b)

    # If equal, then return 0 immediately
    if a == b:
        return 0

    # Find the length of the shared prefix
    overlap = min(len(a), len(b))
    prefix = 0
    while prefix < overlap and a[prefix] == b[prefix]:
        prefix += 1

    # Drop shared prefix for distance calculation
    a = a[prefix:]
    b = b[prefix:]

    # Return distance adjusted for prefix length
    return dist(a, b) + prefix_limit - min(prefix, prefix_limit)

class Arranger:
    def __init__(self, given, correct):
        self.given = given
        self.correct = correct
        self.memo = {}
        self.closest = {}
        self.assigned = {}
        self.used = set()

    def get_dist(self, i, j):
        """Find the distance between a "given" part and a "correct" part."""

        if (i, j) in self.memo:
            return self.memo[(i, j)]

        d = adj_dist(self.given[i][0], self.correct[j][0])
        self.memo[(i, j)] = d
        return d

    def min_for(self, i):
        """
        Compute the minimum distance for a specific "given" part to the nearest
        matching "correct" part.
        """

        # Check for already computed minimum distance
        if i in self.closest and self.closest[i] not in self.used:
            return self.get_dist(i, self.closest[i])

        # Find the closest "correct" part
        closest = None
        closestDist = max_dist
        for j in range(len(self.correct)):
            # Skip "correct" parts which were already used
            if j in self.used:
                continue

            # Update minimum distance
            d = self.get_dist(i, j)
            if d < closestDist:
                closest = j
                closestDist = d

                # A distance of 0 is an exact match
                if d == 0:
                    break

        # Remember the closest value and return the distance
        self.closest[i] = closest
        return closestDist

    def step(self):
        """
        Make an assignment for the shortest distance pair. Returns True if more
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
        closestDist = max_dist
        for i in range(len(self.given)):
            # Skip "given" parts which are already assigned
            if i in self.assigned:
                continue

            # Update minimum distance
            d = self.min_for(i)
            if d < closestDist:
                closest = i
                closestDist = d

                # A distance of 0 is an exact match
                if d == 0:
                    break

        # Record the assignment
        target = self.closest[closest]
        self.assigned[closest] = target
        self.used.add(target)

        return True

    def finalize(self):
        """Create a list of parts which should be compared."""

        # Put "given" parts and their matching "correct" parts first
        parts = []
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

    def arrange(given, correct):
        """Rearrange parts so that similar ones line up."""

        arranger = Arranger(given, correct)
        while arranger.step():
            pass
        return arranger.finalize()

def split_comment(string, start, end):
    """
    Find a comment delimited by "start" and "end" and remove it from the end of
    the string. The comment cannot be the whole string, and it must come at the
    end. Nesting is allowed, but not multiple independent comments in a string.
    """

    # If the string is too small or doesn't end with the delimiter, don't split
    if len(string) < 3 or string[-1] != end:
        return string, ''

    # Iterate backwards through string checking for delimiters
    depth = 1
    for i in range(2, len(string)):
        ch = string[-i]
        if ch == start:
            depth -= 1

            # If start of comment is found, make sure it is valid
            if depth == 0:
                # If there are delimiters in the remaining string, it's invalid
                stripped = string[:-i].strip()
                if start in stripped or end in stripped:
                    break

                # It is valid so return the comment separately
                return string[:-i].strip(), ' ' + string[-i:]

        elif ch == end:
            depth += 1

    return string, ''

def split_options(string, sep):
    """
    Split a string on a separator, trim whitespace, and remove a comment
    delimited by square brackets.
    """

    parts = string.split(sep)
    stripped = []
    for i in range(len(parts)):
        s = parts[i].strip()
        if s:
            stripped.append(split_comment(s, '[', ']'))

    return stripped

def is_combining(ch):
    """Check if a character is a Unicode combining mark."""

    return ucd.category(ch).startswith('M')

def group_combining(string):
    """Group combining characters with the previous character."""

    parts = []
    current = ''
    for ch in string:
        if is_combining(ch):
            if not current:
                current = '\xa0'

            current += ch
        else:
            if current:
                parts.append(current)

            current = ch

    if current:
        parts.append(current)

    return parts

def is_junk(ch):
    return len(ch) == 1 and re.match(junk_re, ch)

def good(s: str) -> str:
    return f"<span class=typeGood>{html.escape(s)}</span>"

def bad(s: str) -> str:
    return f"<span class=typeBad>{html.escape(s)}</span>"

def missed(s: str) -> str:
    return f"<span class=typeMissed>{html.escape(s)}</span>"

def renderDiffs(given, correct, givenElems, correctElems):
    """Create the diff comparison strings for each part."""

    # Separate comments from parts
    given, givenComment = given
    correct, correctComment = correct

    # Only diff comments if they were given
    if givenComment:
        given += givenComment
        correct += correctComment

    # Group combining characters to give cleaner diffs
    given = group_combining(given)
    correct = group_combining(correct)

    givenElem = ''
    correctElem = ''

    givenIndex = 0
    correctIndex = 0

    # Iterate through matching blocks to render the diff
    s = difflib.SequenceMatcher(is_junk, given, correct, autojunk=False)
    for i, j, cnt in s.get_matching_blocks():
        # Check for bad text in "given"
        if givenIndex < i:
            givenElem += bad(''.join(given[givenIndex:i]))

        # Check for missing text in "correct"
        if correctIndex < j:
            correctElem += missed(''.join(correct[correctIndex:j]))

            # If completely missing in "given", add hyphen
            if givenIndex == i:
                givenElem += bad('-')

        if not cnt:
            continue

        givenIndex = i + cnt
        correctIndex = j + cnt

        # Add good text for both
        givenElem += good(''.join(given[i:givenIndex]))
        correctElem += good(''.join(correct[j:correctIndex]))

    # If a comment wasn't diffed, add it back
    if correctComment and not givenComment:
        correctElem += html.escape(correctComment)

    # Append the diffs to the arrays
    givenElems.append(givenElem)
    correctElems.append(correctElem)

def correct(self, given: str, correct: str, **kwargs) -> str:
    """Display the corrections for a type-in answer."""

    # Normalize using NFC to make comparison consistent
    given = ucd.normalize('NFC', given)
    correct = ucd.normalize('NFC', correct)

    # Remove comments in parentheses
    given, givenComment = split_comment(given, '(', ')')
    correct, correctComment = split_comment(correct, '(', ')')

    # Pick separator as ';' if one is used, otherwise ','
    sep = ';' if ';' in correct else ','

    # Split on the separator
    given = split_options(given, sep)
    correct = split_options(correct, sep)

    # Arrange the parts so that similar ones line up and render the diffs
    givenElems = []
    correctElems = []
    for given, correct in Arranger.arrange(given, correct):
        if not given:
            correctElems.append(missed(correct[0]) + correct[1])
        elif not correct:
            givenElems.append(bad(''.join(given)))
        else:
            renderDiffs(given, correct, givenElems, correctElems)

    # Diff comments if they were given
    if givenComment:
        given = givenComment.strip()
        correct = correctComment.strip()
        if not correct:
            givenElems.append(bad(''.join(given)))
        else:
            renderDiffs((given, ''), (correct, ''), givenElems, correctElems)

    sep = html.escape(sep) + ' '
    res = ''

    # Combine the diffs for all "given" parts
    start = True
    for elem in givenElems:
        if start:
            start = False
        else:
            res += sep
        res += elem

    res += '<br><span id=typearrow>&darr;</span><br>'

    # Combine the diffs for all "correct" parts
    start = True
    for elem in correctElems:
        if start:
            start = False
        else:
            res += sep
        res += elem

    # If a comment wasn't diffed, add it back
    if correctComment and not givenComment:
        res += html.escape(correctComment)

    res = f'<div><code id=typeans>{res}</code></div>'

    return res

Reviewer.correct = correct
