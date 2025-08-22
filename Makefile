run:
	langgraph dev --allow-blocking

lint:
	ruff check src/

lint-fix:
	ruff check src/ --fix

format:
	ruff format src/

check-format:
	ruff format src/ --check

check-all: check-format lint
	@echo "All checks passed! ✅"

fix-all: lint-fix format
	@echo "All fixes applied! 🚀"