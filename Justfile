# default recipe - lists all available recipes
default:
  just --list

# run type checking (mypy)
mypy:
  uv run mypy --package gutensearch --strict

# run linting (ruff check)
check:
  uv run ruff check gutensearch/ --fix

# format Python code (ruff format)
fmt:
  uv run ruff format gutensearch/

# remove all build artifacts
clean:
  rm -rf dist
  rm -rf build
  rm -rf htmlcov
