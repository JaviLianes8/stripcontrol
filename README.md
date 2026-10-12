# stripcontrol

Remove or detect C0/C1 control characters from text while keeping standard whitespace

## Install

```
pip install stripcontrol
```

## Usage

```python
from stripcontrol import strip_control, has_control, find_control

dirty = "log line\x00 end\x7f\twith tab\n"

strip_control(dirty)
# 'log line end\twith tab\n'

has_control(dirty)
# True

find_control(dirty)
# [(8, 0), (13, 127)]
```

Tab, newline and carriage return survive by default. Pass your own allow-list to
keep other characters, or an empty string to strip every control character:

```python
strip_control("a\x1b[31m", keep="\x1b")
# 'a\x1b[31m'

strip_control("a\tb\nc", keep="")
# 'abc'
```

`strip_control` targets the C0 range (U+0000 to U+001F), DEL (U+007F) and the C1
range (U+0080 to U+009F). `has_control` and `find_control` report any control
character other than the three standard whitespace ones.

## Why

Log lines, filenames and terminal output often carry stray control characters that
corrupt displays or files. The naive filters people reach for either strip too much
(eating the tab, newline and carriage return that text needs) or lean on
`unicodedata` category checks that are easy to get wrong. Heavier tools such as
`ftfy` do this as part of a much larger mending pipeline. This library is the small,
typed, zero-dependency primitive: a correct allow-list, three clear functions and
nothing else to install.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
