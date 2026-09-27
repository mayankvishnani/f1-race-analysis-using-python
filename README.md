# F1 Data Exploration

A small FastF1 project for exploring race and qualifying lap data. It prints the session's fastest lap, counts laps by driver, reports the driver(s) with the most laps, summarizes average lap time for the five drivers with the most recorded laps, and plots the ten fastest laps colored by team.

## Run with Docker

Install Docker Desktop and make sure it is running. From this folder, build the image once:

```powershell
docker build -t f1-race-analysis .
```

Run the analysis without creating a Python virtual environment. The FastF1 cache and chart are saved on your computer under `.cache/fastf1/` and `output/`:

```powershell
New-Item -ItemType Directory -Force .cache/fastf1, output | Out-Null
docker run --rm -it `
	--mount "type=bind,source=$($PWD.Path)\.cache\fastf1,target=/app/.cache/fastf1" `
	--mount "type=bind,source=$($PWD.Path)\output,target=/app/output" `
	f1-race-analysis
```

## Local Setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

```powershell
python f1_race_analysis.py
```

When you run `f1_race_analysis.py`, enter the year, venue, and session type at the prompts. Use a FastF1-recognized circuit or location name for the venue (for example, `Silverstone`, rather than `British GP`). Use `Q` for qualifying or `R` for the race. FastF1 downloads session data as needed and caches it under `.cache/fastf1/`, which is excluded from Git.
