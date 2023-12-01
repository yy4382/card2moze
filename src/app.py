import exp_csv as csv_gen
from exp_csv import trans_date
from flask import Flask, jsonify, request, Response, send_from_directory, redirect
from urllib.parse import quote
import request_expense as rq
from flask_cors import CORS
from datetime import datetime
import os
import os

# os.chdir("..")


app = Flask(__name__)
cors = CORS(
    app,
    resources={r"/*": {"origins": "*", "expose_headers": ["Content-Disposition", "Content-Type"]}},
)


@app.route("/")
def main_page():
    return send_from_directory(os.getcwd() + "/dist", "index.html")


@app.route("/<path:path>")
def route_dist(path):
    return send_from_directory(os.getcwd() + "/dist", path)


@app.route("/get_csv", methods=["GET"])
def get_csv_by_time():
    start_time = (
        datetime.fromtimestamp(int(request.args.get("start_time")) / 1000)
        if "start_time" in request.args
        else None
    )
    end_time = (
        datetime.fromtimestamp(int(request.args.get("end_time")) / 1000)
        if "end_time" in request.args
        else None
    )
    try:
        csv: str = csv_gen.run_by_time(start_time, end_time)
    except csv_gen.NoEntryException:
        return jsonify({"success": False, "error": "No entry found"})
    except csv_gen.RequestTypeException as e:
        return jsonify({"success": False, "error": "Request for types", "stores": e.no_type_stores})
    return jsonify(
        {
            "success": True,
            "csv": csv,
            "start_time": start_time.timestamp() * 1000,
            "end_time": end_time.timestamp() * 1000,
        }
    )


@app.route("/get_csv", methods=["POST"])
def get_csv_by_entry():
    entries = request.json
    for entry in entries:
        entry["time"] = trans_date(entry["time"])
    try:
        csv, start_time, end_time = csv_gen.run_by_entry(entries)
    except csv_gen.NoEntryException:
        return jsonify({"success": False, "error": "No entry found"})
    except csv_gen.RequestTypeException as e:
        return jsonify({"success": False, "error": "Request for types", "stores": e.no_type_stores})

    return jsonify(
        {
            "success": True,
            "csv": csv,
            "start_time": start_time.timestamp() * 1000,
            "end_time": end_time.timestamp() * 1000,
        }
    )


@app.route("/update_types", methods=["POST"])
def update_types():
    types = request.json
    success = csv_gen.update_types(types)
    return jsonify({"success": success})


@app.route("/update_entries", methods=["GET"])
def update_entries():
    start_time = (
        datetime.fromtimestamp(int(request.args.get("start_time")) / 1000)
        if "start_time" in request.args
        else None
    )
    try:
        rq.run(start_time)
    except ConnectionError:
        return jsonify({"success": False, "error": "Connection error"})

    return jsonify({"success": True})


@app.route("/update_cookie", methods=["POST"])
def update_cookie():
    cookie = request.json["cookie"]
    rq.update_cookie(cookie)
    return jsonify({"success": True})


@app.route("/get_entries", methods=["GET"])
def get_entries():
    start_time = (
        datetime.fromtimestamp(int(request.args.get("start_time")) / 1000)
        if "start_time" in request.args
        else None
    )
    end_time = (
        datetime.fromtimestamp(int(request.args.get("end_time")) / 1000)
        if "end_time" in request.args
        else None
    )
    return jsonify(csv_gen.get_entries_by_time(start_time, end_time))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5500)
