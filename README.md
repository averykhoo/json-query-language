# json-query-language

a ~~powerful~~ non-existent query language to match json objects
(and maybe someday it can help to extract data from json objects)

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

### (maybe) `not()` matching

* limit a dict to the keys {1, 2, 3}:
  * `{1: ..., 2: ..., 3: ..., not(...): ...}`
  * this should work because matching attempts will probably be done in dictionary order, and the `not(...)` is done
    after the match fails for the whitelisted options
* limit a dict to the values {1, 2, 3}:
  * `not(...: not((1, 2, 3)))`
* limit a list to the elems {1, 2, 3} (in any order):
  * `not([..., not((1, 2, 3)), ...])`

# todo

* do i want special handlers for these?
  * `exact()`
  * `all()` or `and()`
  * `not()` or `none()` (or allow negation of other classes?)
  * maybe `or()` or `xor()` or `one()` or `any()` (or `odd()` or `even()`)
  * maybe `fuzzy()` or `approx()` or `truthy()` or `falsy()`
  * maybe allow lambdas or functions for complex matching? already allowing regex after all
