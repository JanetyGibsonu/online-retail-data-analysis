# 电商销售数据分析 — Online Retail Dataset

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-1.5%2B-150458.svg)](https://pandas.pydata.org)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.6%2B-orange.svg)](https://matplotlib.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

基于 UCI Online Retail Dataset，对英国某在线零售商 2010–2011 年共 **54 万条**交易记录进行完整的数据清洗、探索分析与用户价值分层，最终产出可落地的业务改进建议。

---

## 数据来源

本分析使用的数据集来自 [UCI Machine Learning Repository — Online Retail Dataset](https://archive.ics.uci.edu/ml/datasets/online+retail)，由 Kaggle 平台提供下载。数据集包含 541,909 条交易记录，涵盖 2010 年 12 月至 2011 年 12 月期间某英国在线零售商的真实订单数据。

**数据字段说明：**

| 字段 | 说明 |
|------|------|
| InvoiceNo | 发票号码（6 位整数，C 开头表示退货）|
| StockCode | 商品代码（5 位整数 / 字母）|
| Description | 商品描述 |
| Quantity | 购买数量（负数表示退货）|
| InvoiceDate | 交易日期和时间 |
| UnitPrice | 单价（英镑）|
| CustomerID | 客户编号（5 位整数）|
| Country | 客户所在国家 |

---

## 分析模块

| 模块 | 内容 |
|------|------|
| 数据清洗 | 去重、缺失值填充、异常值过滤、退货订单剔除 |
| 销售趋势 | 月度 GMV、环比增长率、峰值自动标注 |
| 地区分布 | 国家销售额排名 + 市场占比饼图 |
| 用户行为 | 复购率、购买频次分布、Top 20% 高价值客户分析 |
| 热销商品 | 销售额 / 销量双榜 TOP 10 |
| RFM 分层 | Recency · Frequency · Monetary 打分 + 四类用户群可视化 |
| 业务建议 | 三大数据驱动改进方向 |

---

## 分析结果预览

### 月度销售趋势
![月度销售趋势](outputs/monthly_sales_trend.png)

### 国家销售分布
![国家销售分布](outputs/country_sales_pie.png)

### 用户购买行为
![用户购买行为](outputs/customer_purchase_analysis.png)

### 热销商品 TOP 10
![热销商品](outputs/top10_products.png)

### RFM 用户价值分层
![RFM分层](outputs/rfm_segments.png)

> 所有图表和 CSV 文件均可通过运行脚本在本地生成。

---

## 项目结构

```
ecommerce_project/
├── run_analysis.py              # 一键运行脚本（推荐，无需 Jupyter）
├── online_retail_analysis.ipynb # Jupyter Notebook 版本
├── analysis_functions.py        # 可复用分析函数（RFM / KPI）
├── data_loading.py              # 数据加载工具（兼容多种格式）
├── requirements.txt             # Python 依赖
├── LICENSE                      # MIT 开源许可证
├── README.md
└── outputs/                     # 运行后自动生成
    ├── monthly_sales_trend.png
    ├── country_sales_pie.png
    ├── customer_purchase_analysis.png
    ├── top10_products.png
    ├── rfm_segments.png
    ├── monthly_sales.csv
    ├── country_sales.csv
    ├── product_sales_ranking.csv
    ├── customer_summary.csv
    └── rfm_results.csv
```

---

## 快速开始

### 第一步：克隆仓库

```bash
git clone https://github.com/<your-username>/online-retail-data-analysis.git
cd online-retail-data-analysis
```

### 第二步：安装依赖

```bash
pip install -r requirements.txt
```

### 第三步：获取数据集

从 [Kaggle](https://www.kaggle.com/datasets/carrie1/ecommerce-data) 下载数据集，将文件放到项目根目录：

| 文件名 | 格式 | 说明 |
|--------|------|------|
| `Online Retail.xlsx` | Excel 或 CSV-in-xlsx | Kaggle 下载的原始文件，直接放入即可 |
| `Online Retail.csv` | 标准 CSV | 将 xlsx 另存为 CSV 后使用 |

> 脚本会**自动检测**文件真实格式（xlsx / csv / 单列 csv-in-xlsx），无需手动转换。  
> 如需修改文件名，请同步修改 `run_analysis.py` 第 18 行的 `FILE_PATH`。

### 第四步：运行分析

**方式 A — 命令行一键运行（推荐）**

```bash
python run_analysis.py
```

运行完成后，5 张图表 + 5 个 CSV 自动保存到 `outputs/` 文件夹：

```
=======================================================
   电商销售数据分析 — Online Retail Dataset
=======================================================
[1/6] 加载数据...       加载成功: 541,909 行 × 8 列
[2/6] 清洗数据...       过滤后保留: 397,924 行
[3/6] 计算核心指标...
    Total GMV        : GBP    8,187,806.36
    Total Orders     :            18,536
    Total Customers  :             4,338
    Repeat Rate      :            35.7%
[4/6] 生成图表...       monthly_sales_trend.png ✓ ...
[5/6] 业务洞察...
[6/6] 导出CSV...        rfm_results.csv ✓
=======================================================
  分析完成！所有文件已保存到 outputs/ 文件夹
=======================================================
```

**方式 B — Jupyter Notebook**

```bash
jupyter notebook online_retail_analysis.ipynb
```

打开后重启 Kernel，点击"全部运行"。

---

## 主要发现

> 以下数值基于完整 UCI Online Retail 数据集，实际运行结果以终端输出为准。

- **总销售额 GMV**：约 £8.2M
- **英国市场占比**：约 85%，前 5 大市场合计约 92%
- **客户复购率**：约 35%，Top 20% 客户贡献约 80% 销售额
- **销售峰值**：2011 年 11 月，节日季明显拉升

## 业务建议

1. **建立会员积分体系** — 针对复购率偏低，预计提升 5–10%
2. **拓展德法等海外市场** — 小范围包邮测试，预计非英国市场增量 +15%
3. **尾部 SKU 清仓折扣** — 识别销量末尾 30% 商品，释放资金流降低仓储成本

---

## 环境依赖

```
pandas >= 1.5.0
numpy >= 1.23.0
matplotlib >= 3.6.0
seaborn >= 0.12.0
openpyxl >= 3.0.0
```

Python 版本：3.8 及以上（已在 3.12 验证通过）

---

## 常见问题

**Q：运行时报错 `FileNotFoundError: Online Retail.xlsx`**  
A：请先从 [Kaggle](https://www.kaggle.com/datasets/carrie1/ecommerce-data) 下载数据集，将文件放到项目根目录后重新运行。

**Q：图表中中文显示为方框**  
A：不影响分析结果和数值。如需显示中文，请安装 SimHei 字体，或在系统字体目录中添加支持中文的字体后重启 Python 环境。

**Q：CSV 文件可以直接运行吗？**  
A：可以。脚本支持 `.xlsx`、`.csv` 以及"xlsx 外壳但内容为 CSV"三种格式，自动识别，无需手动转换。

**Q：`KeyError: 'CustomerID'` 报错**  
A：通常是数据文件读取后列名未正确拆分。请确认文件放置路径正确，且文件名为 `Online Retail.xlsx`，然后重启 Python 后重新运行。

---

## 数据引用

> Chen, D., Sain, S.L., and Guo, K. (2012). Data mining for the online retail industry: A case study of RFM model-based customer segmentation using data mining. *Journal of Database Marketing and Customer Strategy Management*, 19(3), 197–208.

---

## License

本项目基于 [MIT License](LICENSE) 开源，欢迎 fork 和引用。
