"""Analyze an F1 session: fastest lap, lap counts, and a team-colored top-10 chart."""

from pathlib import Path

import fastf1
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


PROJECT_DIR = Path(__file__).resolve().parent
CACHE_DIR = PROJECT_DIR / ".cache" / "fastf1"
OUTPUT_DIR = PROJECT_DIR / "output"


def main():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(CACHE_DIR))

    year = int(input("Year: ").strip())
    race_venue = input("Race venue: ").strip()
    session_type = input("Session type (Q=Qualifying, R=Race): ").strip().upper()
    while session_type not in {"Q", "R"}:
        print("Enter Q for qualifying or R for the race.")
        session_type = input("Session type (Q/R): ").strip().upper()
    try:
        session = fastf1.get_session(year, race_venue, session_type)
        session.load()
    except Exception as error:
        print(
            f"Could not load {race_venue} {year} ({session_type}). "
            "Check that the year has data, the venue matches FastF1's naming, "
            f"and you're online. Details: {error}"
        )
        return

    print(f"Loaded: {session.event['EventName']} - {session.name}")
    print(f"Date: {session.date}")

    laps = session.laps
    fastest_lap = laps.pick_fastest()
    print(
        f"Fastest lap: {fastest_lap['Driver']} - "
        f"{fastest_lap['LapTime']} (lap {fastest_lap['LapNumber']})"
    )

    lap_counts = (
        laps.groupby("Driver")["LapNumber"]
        .count()
        .sort_values(ascending=False)
    )
    print("\nLaps recorded by driver:")
    print(lap_counts.to_string())

    most_laps = lap_counts.max()
    leaders = lap_counts[lap_counts == most_laps].index.tolist()
    print(f"\nMost laps: {', '.join(leaders)} ({most_laps})")

    top_five_drivers = lap_counts.head(5).index
    top_five_laps = laps[
        laps["Driver"].isin(top_five_drivers)
    ].dropna(subset=["LapTime"])
    average_lap_seconds = (
        top_five_laps.groupby("Driver")["LapTime"].mean().mean().total_seconds()
    )
    print(f"Average lap time for the top five drivers: {average_lap_seconds:.3f}s")
    print(f"Fastest lap time: {fastest_lap['LapTime']}")

    top_ten = (
        laps.dropna(subset=["LapTime", "LapNumber", "Team"])
        .nsmallest(10, "LapTime")
        .copy()
    )
    top_ten["LapTimeSeconds"] = top_ten["LapTime"].dt.total_seconds()
    top_ten["Label"] = top_ten.apply(
        lambda lap: f"{lap['Driver']} (lap {int(lap['LapNumber'])})", axis=1
    )
    teams = top_ten["Team"].drop_duplicates().tolist()
    palette = plt.get_cmap("tab10")
    team_colors = {
        team: palette(index % palette.N) for index, team in enumerate(teams)
    }

    chart_laps = top_ten.iloc[::-1]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(
        chart_laps["Label"],
        chart_laps["LapTimeSeconds"],
        color=[team_colors[team] for team in chart_laps["Team"]],
    )
    ax.set_xlabel("Lap time (seconds)")
    ax.set_title(f"Top 10 Fastest Laps - {session.event['EventName']} {session.name}")
    ax.legend(
        handles=[Patch(color=team_colors[team], label=team) for team in teams],
        title="Team",
    )
    fig.tight_layout()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    chart_path = OUTPUT_DIR / f"top_10_fastest_laps_{year}_{session_type}.png"
    fig.savefig(chart_path, dpi=150, bbox_inches="tight")
    print(f"Chart saved to: {chart_path}")
    plt.show()

    try:
        race_session = session
        if session_type != "R":
            race_session = fastf1.get_session(year, race_venue, "R")
            race_session.load()

        race_results = race_session.results
        if race_results.empty:
            print(f"Race winner for {race_venue} GP could not be determined: no results available.")
        else:
            race_winner = race_results.iloc[0]["FullName"]
            print(f"Race winner for {race_venue} GP is {race_winner}")
    except Exception as error:
        print(f"Could not determine the race winner for {race_venue} GP. Details: {error}")


if __name__ == "__main__":
    main()