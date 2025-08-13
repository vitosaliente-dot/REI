import json
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import value_bet


def mock_urlopen(*args, **kwargs):
    data = [
        {
            "home_team": "Team A",
            "away_team": "Team B",
            "bookmakers": [
                {
                    "key": "betmgm",
                    "markets": [
                        {
                            "key": "h2h",
                            "outcomes": [
                                {"name": "Team A", "price": 2.2},
                                {"name": "Team B", "price": 1.7},
                            ],
                        }
                    ],
                },
                {
                    "key": "bet365",
                    "markets": [
                        {
                            "key": "h2h",
                            "outcomes": [
                                {"name": "Team A", "price": 2.0},
                                {"name": "Team B", "price": 1.8},
                            ],
                        }
                    ],
                },
            ],
        }
    ]
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(data).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp
    return mock_resp


def test_get_best_value():
    with patch("value_bet.urlopen", mock_urlopen):
        with patch.dict("os.environ", {"ODDS_API_KEY": "test"}):
            result = value_bet.get_best_value()
            assert result["market"] == "Team A"
            assert result["betmgm"] == 2.2
            assert result["bet365"] == 2.0
            assert abs(result["value"] - 0.2) < 1e-9
