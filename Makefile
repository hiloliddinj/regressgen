# Entry points for reproducing this project. See REPRODUCTION.md for detail.
.PHONY: help setup check validate baseline final headline sweep report trajectories clean

help:
	@echo "make setup        install the pinned environment (uv, python 3.12.13)"
	@echo "make check        lint + unit tests + link check      (no cost)"
	@echo "make validate     re-prove the corpus invariants      (no cost, ~15 min)"
	@echo "make baseline     run the baseline x3 over the corpus"
	@echo "make final        run the shipped agent x3 over the corpus"
	@echo "make headline     baseline + final + report  (the main result)"
	@echo "make sweep        every rung of the changelog"
	@echo "make report       print the scoreboard and significance tests"
	@echo "make trajectories regenerate trajectories/ from results/"
	@echo ""
	@echo "Start with:  make setup && make validate"

setup:
	uv sync

check:
	uv run --with ruff ruff check regressgen/ tools/ tests/
	uv run pytest tests/ -q
	uv run python tools/check_links.py

validate:
	uv run regressgen validate

baseline:
	uv run regressgen run --system baseline --repeat 3 --workers 4

final:
	uv run regressgen run --system v4-discipline --repeat 3 --workers 4

headline:      ## the comparison that carries the result, with repeats
	$(MAKE) baseline
	$(MAKE) final
	uv run regressgen report

sweep:         ## every rung; the headline pair repeated, the rest once
	uv run regressgen run --system baseline --system v4-discipline \
	  --repeat 3 --workers 4
	uv run regressgen run \
	  --system v2-tools --system v3-exec \
	  --system v5-fixprobe --system v6-critic --workers 4
	uv run python tools/update_readme.py

report:
	uv run regressgen report
	uv run python tools/analyze.py

trajectories:
	uv run python tools/export_trajectories.py --label confirmatory
	uv run python tools/export_trajectories.py \
	  --results-dir results/_exploratory-17case --label exploratory

clean:
	rm -rf .pytest_cache .ruff_cache
	find . -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
