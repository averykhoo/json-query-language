# json-query-language

a powerful query language to match json objects (and someday, maybe to extract data from json objects)

## query language

### basic matching of primitives

* str
  * exact match: provide a string, which can be empty
  * regex match: provide a `re.Pattern` object
  * glob match: use `fnmatch.translate()` to convert to regex
* int
  * exact match: provide an integer or float (with no fractional part, obviously)
  * range match: provide a `range` object
* float
  * exact match: provide an integer or float, which can be inf / -inf / NaN
  * fuzzy match: TODO maybe use a kwarg to define this? or create a `approx()` class?
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

### advanced matching

* to match at least one of a list of objects, provide a tuple of objects
* a tuple that includes an Ellipsis will match anything
* an empty tuple matches nothing
* nesting tuples has no additional effect
* tuples also work for complex matching with lists and dicts (see below)
* TODO: should there be a pattern for AND, not just OR? how about XOR or NOT?
  * maybe this can be done with multiple passes of matching, instead of more complex match logic?

### array matching

* exact match: provide a list of values, which can be empty
* pattern match: use Ellipsis to match zero or more of any elem
  * use Ellipsis in a tuple to match exactly one elem
* ~~index match: provide a dict with int keys, which can be negative~~

Example: match at least one True (but not at the start of the list), and end with False or None

```python
pattern = [(...,), ..., True, ..., (False, None)]
```

Example: match at least one True, and end with a False

```python
pattern = [..., True, ..., False]
# pattern_2 = {...: True, -1: False}
```

Example: match at least one True and at least one False

```python
pattern = ([..., True, ..., False, ...], [..., False, ..., True, ...])
```

### dict matching

* exact (subtree) match: provide a dict, which can be empty
* match just a value: use Ellipsis as a key
* match non-empty: use Ellipsis as key and value
* TODO: exact complete match? maybe an `exact()` class?

# todo

* `exact()`
* `all()` or `and()`
* `not()` or `none()`
* maybe `or()` or `xor()` or `one()` or `any()`
* maybe `fuzzy()` or `approx()` or `truthy()` or `falsy()`
