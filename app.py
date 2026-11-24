from flask import Flask, jsonify, send_from_directory
import urllib.request
import urllib.error
import json
import os

app = Flask(__name__)

API_KEY = os.environ.get("FOOTBALL_API_KEY", "")
BASE_URL = "https://api.football-data.org/v4"


def api_get(path):
    if not API_KEY:
        raise Exception("API token belum dipasang.")

    req = urllib.request.Request(
        BASE_URL + path,
        headers={"X-Auth-Token": API_KEY}
    )

    with urllib.request.urlopen(req, timeout=20) as response:
        return json.loads(response.read())


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/api/matches")
def matches():
    try:
        data = api_get("/matches")
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analysis/<int:match_id>")
def analysis(match_id):
    try:
        # Informasi pertandingan
        match_data = api_get(f"/matches/{match_id}")
        match = match_data.get("match", match_data)

        home = match.get("homeTeam", {})
        away = match.get("awayTeam", {})

        home_id = home.get("id")
        away_id = away.get("id")

        result = {
            "match": match,
            "home_last5": [],
            "away_last5": [],
            "h2h": [],
            "errors": []
        }

        # 5 pertandingan terakhir tim kandang
        if home_id:
            try:
                data = api_get(
                    f"/teams/{home_id}/matches?status=FINISHED&limit=5"
                )
                result["home_last5"] = data.get("matches", [])
            except Exception as e:
                result["errors"].append(
                    "Home last 5: " + str(e)
                )

        # 5 pertandingan terakhir tim tandang
        if away_id:
            try:
                data = api_get(
                    f"/teams/{away_id}/matches?status=FINISHED&limit=5"
                )
                result["away_last5"] = data.get("matches", [])
            except Exception as e:
                result["errors"].append(
                    "Away last 5: " + str(e)
                )

        # Head to head
        try:
            data = api_get(
                f"/matches/{match_id}/head2head?limit=10"
            )
            result["h2h"] = data.get("matches", [])
        except Exception as e:
            result["errors"].append(
                "H2H: " + str(e)
            )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/standings/<competition>")
def standings(competition):
    try:
        data = api_get(
            f"/competitions/{competition}/standings"
        )
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8082
    )
