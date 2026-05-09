# CITS3403-Group-Project
Group project for UWA CITS3403 sem1 2026

## Running the tests

```bash
cd studyquest
python -m venv .venv
.venv/Scripts/activate          # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r ../requirements.txt
pytest tests/test_xp_helpers.py tests/test_routes.py -v
```

That runs 21 unit tests (11 helper-function tests + 10 Flask test-client integration tests).

### Selenium browser tests

The selenium suite spins up a real Flask server on port 5050 with two seeded users (`alice`, `bob`, password `password1!` for both) and drives headless Chrome against it.

Requires Chrome (or Chromium) installed locally. Selenium Manager auto-fetches chromedriver, no separate install needed.

```bash
cd studyquest
pytest tests/test_selenium.py -v
```
