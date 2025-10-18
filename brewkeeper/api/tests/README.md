# Tests

## How to Run from Root

```sh
PYTHONPATH="brewkeeper/:$PYTHONPATH" pytest $HOME/dev/brew-keeper-api/brewkeeper/api/tests/
```

## Nice Aliases

```sh
# alias for running a single test
# (follow this alias with the path to the test file)
alias pytestf='PYTHONPATH="brewkeeper/:$PYTHONPATH" pytest'

# alias for running all tests
alias pytests='PYTHONPATH="brewkeeper/:$PYTHONPATH" pytest $HOME/dev/brew-keeper-api/brewkeeper/api/tests/'
```
