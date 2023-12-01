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
    """通过起止两个URL参数获取csv文件

    Arguments:

        - start_time {str} -- 起始时间，时间戳，单位毫秒
        - end_time {str} -- 结束时间，时间戳，单位毫秒

    Returns:

        - success {bool} -- 是否成功
        - csv {str} -- （若成功）csv文件的字符串
        - start_time {str} -- （若成功）起始时间，时间戳，单位毫秒
        - end_time {str} -- （若成功）结束时间，时间戳，单位毫秒
        - error {str} -- （若失败）错误信息
        - stores {list} -- （若失败）缺少类型的商店列表
    """
    if "start_time" not in request.args or "end_time" not in request.args:
        return jsonify({"success": False, "error": "No time provided"})
    try:
        start_time = datetime.fromtimestamp(int(request.args.get("start_time")) / 1000)  # type: ignore
        end_time = datetime.fromtimestamp(int(request.args.get("end_time")) / 1000)  # type: ignore
    except Exception:
        return jsonify({"success": False, "error": "Time provided may be wrong"})

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
    """根据提供的条目检索CSV数据。

    Args:
        entries (list): 条目列表，每个条目都是一个字典，包含以下键：
            - name (str): 商店名称
            - amount (str): 金额
            - time (str): 时间
            - balance (str): 余额
            - id (str): 交易ID

    Returns:
        包含成功状态、CSV数据、开始时间和结束时间的JSON响应。
        如果未找到条目，则响应将指示失败，并附带错误消息。
        如果存在请求类型异常，则响应将指示失败，并附带错误消息和受影响的商店。
    """
    try:
        entries: list = request.json if request.json is not None else []
        if len(entries) == 0:
            raise Exception
    except Exception:
        return jsonify({"success": False, "error": "entry provided may be wrong"})
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
    """
    Update the types of stores.

    This function receives a JSON object containing the updated types of stores.
    It then calls the `update_types` function from the `csv_gen` module to update the types in the CSV file.
    Finally, it returns a JSON response indicating the success of the update.

    Returns:
        A JSON response indicating the success of the update.
    """
    types = request.json
    if types is None:
        return jsonify({"success": False, "error": "No types provided"})
    success = csv_gen.update_types(types)
    return jsonify({"success": success})


@app.route("/update_entries", methods=["GET"])
def update_entries():
    """
    更新条目。

    根据请求参数中的 start_time 更新条目。如果请求参数中没有 start_time，则从已有数据的最后开始更新。

    Raises:
        ConnectionError: 如果发生连接错误。

    Returns:
        json: 包含更新成功与否的信息的字典。
    """
    start_time = (
        datetime.fromtimestamp(int(request.args.get("start_time")) / 1000)  # type: ignore
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
    try:
        if request.json is None:
            raise KeyError
        cookie = request.json["cookie"]
    except KeyError:
        return jsonify({"success": False, "error": "No cookie provided"})
    try:
        rq.update_cookie(cookie)
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)})
    return jsonify({"success": True})


@app.route("/get_entries", methods=["GET"])
def get_entries():
    start_time = (
        datetime.fromtimestamp(int(request.args.get("start_time")) / 1000) # type: ignore
        if "start_time" in request.args
        else None
    )
    end_time = (
        datetime.fromtimestamp(int(request.args.get("end_time")) / 1000) # type: ignore
        if "end_time" in request.args
        else None
    )
    return jsonify(csv_gen.get_entries_by_time(start_time, end_time))


@app.route("/get_no_types", methods=["GET"])
def get_no_types():
    no_type, templates = csv_gen.get_no_types()
    if len(no_type) == 0:
        return jsonify({"success": False, "error": "no no_type items"})
    return jsonify({"success": True, "no_type": no_type, "templates": templates})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5500)
