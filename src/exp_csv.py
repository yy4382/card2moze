import csv
import json
from datetime import datetime


class NoTypeException(Exception):
    def __init__(self, message, desc: str):
        # self.templates = templates.copy()
        self.desc = desc
        self.message = message
        super().__init__(self.message)


class NoEntryException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class RequestTypeException(Exception):
    def __init__(self, message, no_type_stores: list):
        self.no_type_stores = no_type_stores
        self.message = message
        super().__init__(self.message)


def run_by_time(start_time=None, end_time=None):
    """返回一个从start_time到end_time的csv字符串"""
    entries = get_entries_by_time(start_time, end_time)
    return entries2csv_str(entries)


def get_entries_by_time(start_time=None, end_time=None):
    expenses_raw: list = json.load(open("data/expenses.json", "r"))["expenses"]
    if end_time == start_time is None:
        return expenses_raw
    end_time = datetime.now() if end_time is None else end_time
    start_time = datetime.fromtimestamp(0) if start_time is None else start_time
    # 从文件中筛选 entries
    entries = []
    for exp_raw in expenses_raw:
        exp_raw["time"] = trans_date(exp_raw["time"])
        if exp_raw["time"] >= end_time:
            continue
        if exp_raw["time"] <= start_time:
            break
        entries.append(exp_raw)
    return entries


def run_by_entry(entries):
    """将entry转换为csv字符串"""
    start_time = entries[-1]["time"]
    end_time = entries[0]["time"]
    return entries2csv_str(entries), start_time, end_time


def entries2csv_str(entries):
    csv_dict = []
    no_type_stores = []
    for entry in entries:
        entry["time"] = trans_date(entry["time"]) if type(entry["time"]) is str else entry["time"]
        try:
            csv_dict.append(_entry_to_csv(entry))
        except NoTypeException:
            no_type_stores.append(entry["name"])
    if len(csv_dict) == 0:
        raise NoEntryException("No entry found")
    if len(no_type_stores) > 0:
        raise RequestTypeException("request for types", no_type_stores)
    from io import StringIO

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=empty_csv.keys())
    writer.writeheader()
    writer.writerows(csv_dict)
    csv_string = output.getvalue()
    output.close()
    return csv_string


extended_attr = ["主类别＊", "子类别＊", "名称", "商家", "项目"]
type_file: str = "data/expenses-type.json"
extended_file: str = "data/expenses-extended.csv"


def gen_type_from_file(
    *,
    force_edit: bool = False,
):
    """generate extended expense type from expenses-extended.csv"""
    if force_edit:
        exp_types = {}
        templates = []
    else:
        try:
            exp_types: dict = json.load(open(type_file, "r"))["stores"]
            templates: list = json.load(open(type_file, "r"))["templates"]
            if set(exp_types[next(iter(exp_types))].keys()) != set(extended_attr):
                exp_types = {}
                templates = []
        except json.decoder.JSONDecodeError:
            exp_types = {}
            templates = []
    with open(extended_file, "r") as f:
        for expense_csv in list(csv.DictReader(f)):
            store_name = expense_csv["描述"]
            if store_name in exp_types:
                continue
            exp_types[store_name] = {}
            for attr in extended_attr:
                exp_types[store_name][attr] = expense_csv[attr]
            already_exist = False
            for template in templates:
                if template == exp_types[store_name]:
                    already_exist = True
                    break
            if not already_exist:
                templates.append(exp_types[store_name])
    json.dump(
        {"stores": exp_types, "templates": templates},
        open(type_file, "w"),
        ensure_ascii=False,
        indent=2,
    )


empty_csv = {
    "帐户": "",
    "币种": "",
    "记录类型＊": "",
    "主类别＊": "",
    "子类别＊": "",
    "金额＊": "",
    "手续费": "",
    "折扣": "",
    "名称": "",
    "商家": "",
    "日期＊": "",
    "时间": "",
    "项目": "",
    "描述": "",
    "标签": "",
    "对象": "",
}


def trans_date(d, *, to_str=None, to_datetime=None):
    """将字符串转换为`datetime.datetime`对象，如果d为`None`则返回`None`，如果d为`datetime.datetime`对象则返回字符串"""
    if d is None:
        return None
    if to_str is True:
        return d if type(d) is str else d.strftime("%Y-%m-%d %H:%M:%S")
    if to_datetime is True:
        try:
            return d if type(d) is datetime else datetime.strptime(d, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return d if type(d) is datetime else datetime.strptime(d, "%Y-%m-%d")
    if type(d) is str:
        try:
            return datetime.strptime(d, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return datetime.strptime(d, "%Y-%m-%d")
    else:
        return d.strftime("%Y-%m-%d %H:%M:%S")


# def _get_type_from_input(desc: str, templates) -> dict:
#     new_type = {}
#     print(f"-----\n为{desc}创建额外类型：")
#     for attr in extended_attr:
#         new_type[attr] = input(f"{attr}:")
#     is_new = False
#     if is_new:
#         templates.append(new_type)
#     return new_type


def _get_extended_attr(desc: str) -> dict:
    types = json.load(open("data/expenses-type.json", "r"))
    exp_types = types["stores"]
    if desc in exp_types:
        same_attr: bool = set(exp_types[desc].keys()) == set(extended_attr)
        if same_attr:
            return exp_types[desc]
    raise NoTypeException("No type found", desc)
    # new_type = _get_type_from_input(desc, types["templates"])
    # exp_types[desc] = new_type
    #
    # json.dump(types, open("data/expenses-type.json", "w"), ensure_ascii=False, indent=2)
    # return new_type


def _entry_to_csv(exp_raw) -> dict:
    exp_csv = empty_csv.copy()
    exp_csv.update(
        {
            "帐户": "校园卡",
            "记录类型＊": "支出",
            "金额＊": exp_raw["amount"],
            "日期＊": exp_raw["time"].strftime("%Y/%m/%d"),
            "时间": exp_raw["time"].strftime("%H:%M"),
            "描述": exp_raw["name"],
        }
    )

    # 特殊处理
    if exp_csv["描述"] == "库迪咖啡" and float(exp_csv["金额＊"]) >= -8.8:
        exp_csv["描述"] = "库迪咖啡旁饮料铺"

    # 更新extended属性
    exp_csv.update(_get_extended_attr(exp_csv["描述"]))

    return exp_csv


def update_types(types: dict) -> bool:
    try:
        exp_types: dict = json.load(open(type_file, "r"))["stores"]
        templates: list = json.load(open(type_file, "r"))["templates"]
    except json.decoder.JSONDecodeError:
        return False
    exp_types.update(types)
    for store in types.values():
        if store not in templates:
            templates.append(store)
    json.dump(
        {"stores": exp_types, "templates": list(templates)},
        open(type_file, "w"),
        ensure_ascii=False,
        indent=2,
    )
    return True


if __name__ == "__main__":
    import os

    os.chdir("..")
    gen_type_from_file(force_edit=True)
