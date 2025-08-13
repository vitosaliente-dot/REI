import os
import json
from urllib.request import urlopen
from urllib.error import URLError, HTTPError


def get_best_value(sport_key="soccer", region="us"):
    """Fetch odds from BetMGM and Bet365 and return the best value bet.

    Args:
        sport_key (str): Key of the sport to query (e.g. "soccer").
        region (str): Region to query, per The Odds API regions.

    Returns:
        dict | None: Dictionary containing event, market, odds and value if found.
    """
    api_key = os.environ.get("ODDS_API_KEY")
    if not api_key:
        raise RuntimeError("ODDS_API_KEY environment variable not set")

    url = (
        f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
        f"?regions={region}&oddsFormat=decimal"
        f"&bookmakers=betmgm,bet365&apiKey={api_key}"
    )

    with urlopen(url) as response:
        data = json.load(response)

    best = None
    for event in data:
        bm = {b["key"]: b for b in event.get("bookmakers", [])}
        if "betmgm" not in bm or "bet365" not in bm:
            continue
        mgm_outcomes = bm["betmgm"]["markets"][0]["outcomes"]
        b365_outcomes = bm["bet365"]["markets"][0]["outcomes"]
        for outcome in mgm_outcomes:
            name = outcome["name"]
            price_mgm = float(outcome["price"])
            match = next((o for o in b365_outcomes if o["name"] == name), None)
            if match:
                price_b365 = float(match["price"])
                value = price_mgm - price_b365
                if not best or value > best["value"]:
                    best = {
                        "event": f"{event['home_team']} vs {event['away_team']}",
                        "market": name,
                        "betmgm": price_mgm,
                        "bet365": price_b365,
                        "value": value,
                    }
    return best


if __name__ == "__main__":
    try:
        result = get_best_value()
        if result:
            print("Melhor odd de valor encontrada:")
            print(result)
        else:
            print("Nenhuma odd de valor encontrada.")
    except (URLError, HTTPError) as e:
        print(f"Erro de rede: {e}")
    except Exception as e:
        print(f"Erro: {e}")
