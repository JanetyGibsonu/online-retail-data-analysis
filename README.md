# 电商销售数据分析 — Online Retail Dataset

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![pandas](https://img.shields.io/badge/pandas-2.x-150458)](https://pandas.pydata.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

基于 UCI Online Retail Dataset，对英国某在线零售商 2010–2011 年共 **54 万条** 交易记录进行完整的数据清洗、探索分析与用户价值分层，最终产出可落地的业务改进建议。

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

## 项目结构

```
ecommerce_project/
├── run_analysis.py              # 一键运行脚本（推荐，无需 Jupyter）
├── online_retail_analysis.ipynb # Jupyter Notebook 版本
├── analysis_functions.py        # 可复用分析函数（RFM / KPI）
├── data_loading.py              # 数据加载工具
├── requirements.txt             # Python 依赖
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
git clone https://github.com/<your-username>/online-retail-analysis.git
cd online-retail-analysis
```

### 第二步：安装依赖

```bash
pip install -r requirements.txt
```

### 第三步：获取数据集

从 [Kaggle](https://www.kaggle.com/datasets/carrie1/ecommerce-data) 下载数据集，支持以下格式，放到项目根目录即可：

| 文件名 | 格式 | 说明 |
|--------|------|------|
| `Online Retail.xlsx` | Excel 或 CSV-in-xlsx | Kaggle 下载的原始文件（直接放入，无需转换）|
| `Online Retail.csv` | 标准 CSV | 将 xlsx 另存为 CSV 后重命名使用 |

> 脚本会自动检测文件真实格式（xlsx / csv / 单列csv-in-xlsx），无需手动处理。
> 若修改文件名，请同步修改 `run_analysis.py` 第 18 行的 `FILE_PATH`。

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
[4/6] 生成图表...       5 张图表 ✓
[5/6] 业务洞察...
[6/6] 导出CSV...        5 个文件 ✓
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
3. **尾部 SKU 清仓折扣** — 识别销量末尾 30% 商品，释放资金流

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

## 数据来源

UCI Machine Learning Repository — [Online Retail Data Set](https://archive.ics.uci.edu/ml/datasets/online+retail)

> Chen, D., Sain, S.L., and Guo, K. (2012). Data mining for the online retail industry: A case study of RFM model-based customer segmentation using data mining. *Journal of Database Marketing and Customer Strategy Management*, 19(3), 197–208.

---

## License

MIT
