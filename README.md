# Card to MOZE

## API 一览



## 运行指南

项目正常运行还需要在根目录下有 `data/` 和 `dist/` 目录。他们会在 docker 运行时被挂载到容器中。

```
.
├── ...
├── docker-compose.yml
├── data
│   ├── cookie.txt
│   ├── expenses-extended.csv
│   ├── expenses-type.json
│   └── expenses.json
└── dist
    ├── ...
    └── index.html
```

`dist/` 是前端文件。可以通过 `git clone -b gh-pages https://github.com/yy4382/card2moze_frontend.git dist` 下载。

`data/` 文件夹下是数据文件：

  - `cookie.txt`：以文本形式存储 cookie
  - `expenses-type.json`：存储每个店名对应的 MOZE 中的额外属性，如类别等
  - `expenses.json`：保存消费记录
  - `expenses-extended.csv`（可选）：一份 MOZE 格式的 CSV，可以通过它生成 `expenses-type.json`

示例：

`expenses.json`:

```json
{
  "expenses": [
    {
      "name": "时光水吧",
      "amount": -4,
      "time": "2023-11-30 19:12:19",
      "balance": 0.4,
      "id": "[order_no=************************]"
    },
    {
      "name": "西式快餐",
      "amount": -5,
      "time": "2023-11-30 18:52:58",
      "balance": 4.4,
      "id": "[order_no=************************]"
    }
  ]
}
```

`expenses-type.json`:

```json
{
  "stores":{"店名":{}},
	"templates":[{},{}]
}
```

```json
{
  "stores": {
    "彼得家·铁板厨房": {
      "主类别＊": "饮食",
      "子类别＊": "食堂",
      "名称": "",
      "商家": "校内食堂",
      "项目": "生活"
    },
    "库迪咖啡": {
      "主类别＊": "饮食",
      "子类别＊": "现做饮品",
      "名称": "库迪咖啡",
      "商家": "库迪",
      "项目": "生活"
    },
    "快餐": {
      "主类别＊": "饮食",
      "子类别＊": "食堂",
      "名称": "",
      "商家": "校内食堂",
      "项目": "生活"
    }
  },
  "templates": [
    {
      "主类别＊": "饮食",
      "子类别＊": "食堂",
      "名称": "",
      "商家": "校内食堂",
      "项目": "生活"
    },
    {
      "主类别＊": "饮食",
      "子类别＊": "现做饮品",
      "名称": "库迪咖啡",
      "商家": "库迪",
      "项目": "生活"
    },
  ]
}
```

