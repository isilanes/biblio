# Test that required local config file exists:
if [[ ! -f ~/.biblio.json ]]; then
  echo Missing required local config file \'~/.biblio.json\'
  exit
fi

# Run Django tests and go on only if no errors:
python -Wa -m coverage run --source="." manage.py test -v 2 --failfast || exit

# Check PEP8 compliance:
flake8  # must fix flake install

# Run complexity tests:
COMPLEXITY=$(find . -name '*.py' -exec radon cc -nc {} +)
if [[ "x$COMPLEXITY" != "x" ]]; then
    echo -e "\033[33m[WARNING]\033[\0m Some files include cyclomatic complexity of C or worse:"
    find . -name '*.py' -exec radon cc -nc {} +  # have to execute again, as echo $COMPLEXITY would lack colorization
else
    echo -e "\033[32m[OK]\033[\0m Cyclomatic complexity tests pass."
fi

# Run maintainability tests:
MAINTAINABILITY=$(find . -name '*.py' -exec radon mi -nb {} +)
if [[ "x$MAINTAINABILITY" != "x" ]]; then
    echo -e "\033[33m[WARNING]\033[\0m Some files include maintainability index of B or worse:"
    find . -name '*.py' -exec radon mi -nb {} +  # have to execute again, as simply echo would lack colorization
else
    echo -e "\033[32m[OK]\033[\0m Maintainability index tests pass."
fi

# Show coverage report:
echo -e "\nCoverage:"
python -m coverage report -m --skip-covered
