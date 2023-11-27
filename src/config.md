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

## Ignored Characters

This option configures which characters may be left out in answers without it
being marked as an error if "Lenient Validation" is enabled. The default value
is `" .-"`, which specifies to ignore missing spaces, periods (`.`), and
hyphens (`-`), but you can put any characters between the quotes to ignore them
instead. If you don't want to ignore any characters, don't put anything between
the quotes (like `""`).