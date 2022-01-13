# json-query-language

a powerful query language to match json objects (and someday, maybe to extract data from json objects)

## query language

### basic object matching

* str
  * exact match: provide a string, which can be empty
  * regex match: provide a `re.Pattern` object
  * glob match: use `fnmatch.translate()` to convert to regex
* int
  * exact match: provide an integer or float (with no fractional part, obviously)
  * range match: provide a `range` object
* float
  * exact match: provide an integer or float, which can be inf / -inf / NaN
  * fuzzy match: TODO maybe use a kwarg to define this?
* bool
  * exact match: provide a bool
  * fuzzy (truthy) match: will not be supported
* complex
  * will not be supported
* null / None
  * provide None
  * TODO: should None match NaN?
  * TODO: should NaN match None?
* `*`
  * use Ellipsis `...` as a catch-all to match anything
  * note that Ellipsis behaves differently in a list!

### advanced object matching

* to match at least one of a list of objects, provide a tuple of objects
* a tuple that includes an Ellipsis will match anything
* an empty tuple matches nothing
* nesting tuples has no additional effect
* tuples also work for complex matching with lists and dicts (see below)

### array matching

* exact match: provide a list of values, which can be empty
* index match: provide a dict with int keys, which can be negative
* pattern match: use Ellipsis to match zero or more of any elem
  * use Ellipsis in a tuple to match exactly one elem

Example: match at least one True (but not at the start of the list), and end with False or None

```python
pattern = [(...,), ..., True, ..., (False, None)]
```