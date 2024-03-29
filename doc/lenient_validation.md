# Lenient Validation

Sometimes you may not want to type out the full answer as it is written on the
card, so if lenient validation is enabled, these cases will not be marked as
errors when checking the answer. Instead, they will just be shown in gray.
Lenient validation is enabled by default, but it can be disabled or customized
in the Anki add-on config page.

## Missing Spaces, Periods, and Hyphens

Since spaces, periods, and hyphens usually aren't important when checking
answers, lenient validation will not show the answer as incorrect when they
are missing. In the Anki add-on config page, you can customize which
characters are allowed to be missing like this.

For example, if you type "We cooperated" for `We co-operated.`, it shows:

![Missing hyphen and period](../img/missing_hyphen_period.png)

## Missing Bracketed Text

Often, there are some words which are not required in an answer, such as text
in square brackets `[...]` or parentheses `(...)`. When lenient validation is
enabled, this text is optional and will not be shown as incorrect if it is
missing. If it is included, the brackets or parentheses are optional as well.

For example, if you type "start" for `start(ing)`, it shows:

![Missing parenthesized text](../img/missing_paren_text.png)

And if you type "starting" for `start(ing)`, it shows:

![Missing parentheses](../img/missing_parens.png)

## Missing Alternatives

Sometimes there may be multiple similar words in an answer which are all
correct. If you separate these words with slashes (`/`), lenient validation
will accept any one of them, and will not mark the missing alternatives as
incorrect.

For example, if you type "set in my ways" for `set in one's/my ways`, it shows:

![Missing alternative](../img/missing_alternative.png)

Spaces are only allowed in alternatives if the entire set of alternatives is
surrounded by square brackets `[...]` or parentheses `(...)`, but note that
this also makes it optional. For example, if have a card with
`we've got [a lot of/plenty of] time`, you can type "we've got a lot of time":

![Missing alternative with spaces](../img/missing_alternative_with_spaces.png)

But you could also type just "we've got time":

![Missing all alternatives in bracket](../img/missing_alternative_bracket.png)
