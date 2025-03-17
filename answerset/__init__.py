# MIT License
#
# Copyright (c) 2024 Scott Taylor
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import Any

from .compare import compare_answer_no_html
from .config import Config


def get_config() -> Config:
    try:
        import aqt

        return Config(aqt.mw.addonManager.getConfig(__name__) if aqt.mw else None)
    except:
        return Config()


# Load user config
user_config = get_config()

# Custom CSS for numeric comparisons
new_css = "<style>.typePass { background-color: #ffe49b; }</style>"

# Up to Anki 2.1.54
try:
    from aqt.reviewer import Reviewer

    def correct(
        self: Reviewer,
        given: str,
        correct: str,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        return new_css + compare_answer_no_html(user_config, correct, given)

    Reviewer.correct = correct  # type: ignore
except:
    pass


def compare_answer_html(config: Config, correct: str, given: str) -> str:
    """Remove HTML tags and AV tags before comparing"""
    # Strip AV tags if possible
    try:
        import aqt

        correct = aqt.mw.col.media.strip_av_tags(correct)
    except:
        pass

    try:
        from anki.utils import html_to_text_line

        correct = html_to_text_line(correct)
    except:
        pass

    return compare_answer_no_html(config, correct, given)


# Anki 25.03+ (hooks were created in Anki to avoid monkey patching)
try:
    from aqt.gui_hooks import (  # type: ignore
        reviewer_will_compare_answer,
        reviewer_will_render_compared_answer,
    )

    def deactivate_default_rendering(
        expected_provided_tuple: tuple[str, str], type_pattern: str,
    ) -> tuple[str, str]:
        return "", ""

    reviewer_will_compare_answer.append(deactivate_default_rendering)

    def render_compare_answer(
        output: str, initial_expected: str, initial_provided: str, type_pattern: str,
    ) -> str:
        return new_css + compare_answer_html(
            user_config, initial_expected, initial_provided,
        )

    reviewer_will_render_compared_answer.append(render_compare_answer)

# Anki 2.1.56+ (correction was moved to Rust backend)
except ImportError:
    from anki.collection import Collection

    # TODO: handle "combining" argument
    def compare_answer(
        self: Collection,
        expected: str,
        provided: str,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        return new_css + compare_answer_html(user_config, expected, provided)

    Collection.compare_answer = compare_answer  # type: ignore

except:
    pass
