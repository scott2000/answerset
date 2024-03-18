# Answer Set Config

The config file is in [JSON format](https://en.wikipedia.org/wiki/JSON), with
all valid options listed below. After making any changes, please restart Anki.
For more information about these features, see the
[GitHub repository](https://github.com/scott2000/answerset#config).

## Enable Answer Choice Comments \[...]

Valid Options: `false` or `true`

If set to `true`, you can add comments at the end of answer choices in square
brackets like `[...]`. These comments will not be checked when comparing typed
answers to the expected answer, so they can be used to add notes.

Example: `mouse [animal], bat [baseball]`

## Enable Answer Comments (...)

Valid Options: `false` or `true`

If set to `true`, you can add comments at the end of answers in parentheses
like `(...)`. These comments will not be checked when comparing typed answers
to the expected answer, so they can be used to add notes. Unlike `[...]`,
these comments apply to the answer as a whole rather than to individual
answer choices.

Example: `mouse, bat (animals)`

## Enable Lenient Validation

Valid Options: `false` or `true`

If set to `true`, answer checking will be more lenient, and will not require
answers to match character-for-character. For instance, "Ignored Characters"
and text in brackets or parentheses may be left out in answers, and it will
not be marked as an error.

## Equivalent Strings

This option is an array of arrays of strings which should be considered to be
equivalent to each other when checking answers. These strings may contain
special characters such as spaces or apostrophes, but be careful to follow the
correct [JSON format](https://en.wikipedia.org/wiki/JSON) for arrays and
strings. To disable this option, leave it empty (like `[]`).

Example: `[["I am", "I'm", "Im"], ["'re", " are"]]`

## Ignore Case

Valid Options: `false` or `true`

If set to `true`, uppercase and lowercase letters may be used interchangably
when answering. For instance, you could type "anki" when the answer is "Anki".

## Ignore Separators in Brackets

Valid Options: `false` or `true`

If set to `true`, commas and semicolons may be used inside of brackets or
parentheses without causing the answer to be split into multiple choices.

## Ignored Characters

This option configures which characters may be left out in answers without it
being marked as an error if "Lenient Validation" is enabled. The default value
is `" .-"`, which specifies to ignore missing spaces, periods (`.`), and
hyphens (`-`), but you can put any characters between the quotes to ignore them
instead. If you don't want to ignore any characters, don't put anything between
the quotes (like `""`).

## Numeric Comparison Factor

This option sets how close to the correct answer numbers need to be for them to
be considered almost correct. For instance, if set to 1.0 (the default), then
the numbers must match exactly in numeric value to be accepted.

If set to 1.25, then if the correct answer is `x`, any number between `x/1.25`
and `x*1.25` will be accepted. Answers within this range will be shown in
yellow by default to indicate that they are not exactly correct. You may also
use the reciprocal of the factor, so a factor of 0.8 would be exactly
equivalent to a factor of 1.25.

If this option is set to 0, then numeric comparisons will be disabled entirely,
meaning that numbers will be compared as strings of digits only.

## Separators

This option configures which characters can be used to separate answer choices.
The default value is `";,"`, meaning that if there are any semicolons, then
semicolons will be used as the answer separator, otherwise if there are any
commas, then commas will be used, otherwise answers will not be split at all.

If you want to answer in full sentences, it may be a good idea to change this
to `";"` to prevent commas from being misinterpreted. If you only use this
add-on for other features, you could even set it to `""` to prevent any answers
from being split into choices.
