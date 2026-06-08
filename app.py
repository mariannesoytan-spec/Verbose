from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(name)

@app.route("/")
def home():
return jsonify({
"status": "online",
"endpoints": [
"/chart/<month>/<year>"
]
})

@app.route("/chart/<month>/<year>")
def chart(month, year):

try:
    url = f"https://satta-king-fast.com/new-faridabad/satta-result-chart/nf/?month={month}&year={year}"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    rows = []

    for row in soup.find_all("tr"):
        cols = [
            c.get_text(" ", strip=True)
            for c in row.find_all(["td", "th"])
        ]

        if len(cols) >= 6:
            rows.append(cols[:6])

    if len(rows) < 2:
        return jsonify({
            "success": False,
            "error": "No chart data found"
        }), 404

    data_rows = rows[1:]

    shift_ds = (
        len(data_rows) > 1 and
        data_rows[0][1] == ""
    )

    ds_values = []

    if shift_ds:
        ds_values = [
            row[1]
            for row in data_rows
            if row[1]
        ]

    result = []

    for i, row in enumerate(data_rows):

        if not any(row[2:]):
            continue

        if shift_ds:
            ds = ds_values[i] if i < len(ds_values) else None
        else:
            ds = row[1] if row[1] else None

        result.append({
            "day": row[0],
            "ds": ds,
            "fr": row[2] or None,
            "nf": row[3] or None,
            "gz": row[4] or None,
            "ga": row[5] or None
        })

    return jsonify({
        "success": True,
        "month": month,
        "year": year,
        "count": len(result),
        "data": result
    })

except Exception as e:
    return jsonify({
        "success": False,
        "error": str(e)
    }), 500

if name == "main":
app.run(host="0.0.0.0", port=5000)