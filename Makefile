
.PHONY: all test proxies impact tables deck real clean
all: test tables impact deck

test:
	python -m pytest tests -q

proxies:
	python scripts/build_proxies.py

impact:
	python scripts/run_price_impact_check.py --stocks 120 --months 48 --impact-scale 0.3 --tag baseline
	python scripts/run_price_impact_race.py

tables:
	python scripts/run_all.py

deck:
	python scripts/build_deck.py

clean:
	rm -rf results/cache

real:
	python scripts/run_real.py $(ARGS)
