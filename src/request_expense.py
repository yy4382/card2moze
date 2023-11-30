import json
from datetime import datetime, timedelta
from exp_csv import trans_date

import requests


def run(start_time: datetime = None):
    ExpenseGetSave(start_time)


cookie = open("data/cookie.txt", "r").read()



def update_cookie(new_cookie):
    global cookie
    cookie = new_cookie


class ExpenseGetSave:
    def __init__(self, start_time=None, file="data/expenses.json") -> None:
        self.file = file
        if start_time is not None:
            self.expenses_json = {"expenses": []}
            self.__start_time = start_time
            self.__get_expenses()
            return
        try:
            self.expenses_json: dict = json.load(open(self.file, "r"))
            _ = self.expenses_json["expenses"][0]["time"]
        except (json.decoder.JSONDecodeError, FileNotFoundError, KeyError, IndexError):
            self.expenses_json = {"expenses": []}
            self.__start_time = datetime.now() - timedelta(days=3)
            self.__get_expenses()
            return

        for exp in self.expenses_json["expenses"]:
            exp["time"] = trans_date(exp["time"])

        self.__update_expenses()

        # for exp in self.expenses_json["expenses"]:
        #     exp["time"] = trans_date(exp["time"])
        # self.expenses_json["start_time"] = trans_date(self.expenses_json["start_time"])
        # self.expenses_json["newest_date"] = trans_date(self.expenses_json["newest_date"])
        #
        # newest_date = self.expenses_json["newest_date"]
        # if start_time is None:
        #     self.__start_time = newest_date
        # elif start_time <= newest_date:
        #     self.__start_time = newest_date
        # else:
        #     self.expenses_json["gaps"].append(
        #         f"{trans_date(newest_date)} -- {trans_date(start_time)}"
        #     )
        #     self.__start_time = start_time

    @staticmethod
    def request_card(page):
        url = "http://card.xjtu.edu.cn/Report/GetPersonTrjn"
        # noinspection SpellCheckingInspection
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            # "X_REQUESTED_WITH": "d79b05a6ca557534b4a9d567d15b7b3df53dee36ef26eedff811a8d8a90b51de",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, "
            "like Gecko) Mobile/15E148 toon/6.4.1 toonType/150 msgsealType/1150 toongine/1.0.11 "
            "toongineBuild/11 platform/iOS language/zh-Hans skin/white fontIndex/0",
            "Referer": "http://card.xjtu.edu.cn/PPage/ComePage?flowID=15",
            "Connection": "keep-alive",
            "Cookie": cookie,
        }

        data = f"account=253079&page={page}&json=true"
        import time

        response_json = None
        retry_count = 0
        while retry_count < 3:
            try:
                response = requests.post(url, headers=headers, data=data)
                response.encoding = "utf-8"
                response_json = json.loads(response.text)
                break
            except Exception as e:
                print(e)
                retry_count += 1
                time.sleep(1)  # Wait for 1 second before retrying

        if retry_count == 3:
            raise ConnectionError("Failed to make the request after 3 attempts")

        expenses = []
        for expense in response_json["rows"]:
            # noinspection SpellCheckingInspection
            if float(expense["TRANAMT"]) >= 0:
                continue
            # noinspection SpellCheckingInspection
            expenses.append(
                {
                    "name": expense["MERCNAME"].strip(),
                    "amount": expense["TRANAMT"],
                    "time": trans_date(expense["OCCTIME"]),
                    "balance": expense["CARDBAL"],
                    "id": expense["JDESC"],
                }
            )
        return expenses

    def __update_expenses(self):
        """按照 `self.__start_time` 的要求获取并更新 `self.expenses_json`"""
        expenses = []
        newest_time = self.expenses_json["expenses"][0]["time"]
        for page in range(1, 20):
            expenses_ = self.request_card(page)
            expenses += expenses_
            if expenses[0]["time"] == newest_time:
                return
            if expenses[-1]["time"] <= newest_time:
                while expenses[-1]["time"] <= newest_time:
                    expenses.pop()
                break
        self.expenses_json["expenses"] = expenses + self.expenses_json["expenses"]

        for exp in self.expenses_json["expenses"]:
            exp["time"] = trans_date(exp["time"], to_str=True)
        json.dump(self.expenses_json, open(self.file, "w"), ensure_ascii=False, indent=2)

    def __get_expenses(self):
        expenses = []
        for page in range(1, 20):
            expenses_ = self.request_card(page)
            expenses += expenses_
            if expenses[-1]["time"] <= self.__start_time:
                while expenses[-1]["time"] <= self.__start_time:
                    expenses.pop()
                break
        self.expenses_json["expenses"] = expenses

        for exp in self.expenses_json["expenses"]:
            exp["time"] = trans_date(exp["time"], to_str=True)
        json.dump(self.expenses_json, open(self.file, "w"), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import os

    os.chdir("..")
    # print(type(datetime.now()))
    # run(datetime(2023, 11, 7))
    # update()
