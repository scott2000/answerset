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
new_css = '<style>.typePass { background-color: #ffe49b; }</style>'

# Up to Anki 2.1.54
try:
    from aqt.reviewer import Reviewer

    def correct(self: Reviewer, given: str, correct: str, **kwargs: Any) -> str:
        return new_css + compare_answer_no_html(user_config, correct, given)

    Reviewer.correct = correct # type: ignore
except:
    pass

# Anki 2.1.56+ (correction was moved to Rust backend)
try:
    import aqt
    from anki.collection import Collection
    from anki.utils import html_to_text_line

    def compare_answer(self: Collection, expected: str, provided: str) -> str:
        # Strip AV tags if possible
        try:
            if aqt.mw:
                expected = aqt.mw.col.media.strip_av_tags(expected)
        except:
            pass

        # Strip HTML tags
        expected = html_to_text_line(expected)

        return new_css + compare_answer_no_html(user_config, expected, provided)

    Collection.compare_answer = compare_answer # type: ignore
except:
    pass
