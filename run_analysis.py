# -*- coding: utf-8 -*-
"""
run_analysis.py
直接运行：python run_analysis.py
无需 Jupyter，结果自动保存到 outputs/ 文件夹
"""

import warnings; warnings.filterwarnings("ignore")
import pandas as pd, numpy as np
import matplotlib.pyplot as plt, matplotlib.ticker as mticker
import seaborn as sns, csv, io as sio, os, sys

# ── 字体设置 ──────────────────────────────────────────────────────
plt.rcParams["font.sans-serif"] = ["SimHei","Microsoft YaHei","Arial Unicode MS","DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
sns.set_theme(style="whitegrid", palette="Set2")

# ── 路径设置 ──────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH  = os.path.join(SCRIPT_DIR, "Online Retail.xlsx")
OUT_DIR    = os.path.join(SCRIPT_DIR, "outputs")
os.makedirs(OUT_DIR, exist_ok=True)
os.chdir(SCRIPT_DIR)

print("=" * 55)
print("   电商销售数据分析 — Online Retail Dataset")
print("=" * 55)

# ══════════════════════════════════════════════════════
# 1. 数据加载
# ══════════════════════════════════════════════════════
print("\n[1/6] 加载数据...")
assert os.path.exists(FILE_PATH), f"找不到文件: {FILE_PATH}"

with open(FILE_PATH, "rb") as f:
    magic = f.read(4)

if magic[:2] == b"PK":
    df = pd.read_excel(FILE_PATH, sheet_name=0, engine="openpyxl", dtype=str, header=0)
elif magic[:2] == b"\xd0\xcf":
    df = pd.read_excel(FILE_PATH, sheet_name=0, engine="xlrd", dtype=str, header=0)
else:
    with open(FILE_PATH, "r", encoding="latin-1") as f:
        first_line = f.readline()
    sep = "\t" if first_line.count("\t") > first_line.count(",") else ","
    df = pd.read_csv(FILE_PATH, encoding="latin-1", sep=sep, dtype=str)

# 单列格式自动拆分
if df.shape[1] == 1:
    col_header = df.columns[0]
    col_names  = [c.strip() for c in col_header.split(",")]
    parsed_rows = []
    for val in df[col_header]:
        if pd.isna(val) or str(val).strip() == "":
            continue
        try:
            row = next(csv.reader(sio.StringIO(str(val))))
            if len(row) == len(col_names):
                parsed_rows.append(row)
            elif len(row) > len(col_names):
                extra = len(row) - len(col_names)
                fixed = row[:2] + [",".join(row[2:2+extra+1])] + row[2+extra+1:]
                parsed_rows.append(fixed)
        except Exception:
            continue
    df = pd.DataFrame(parsed_rows, columns=col_names)

print(f"    加载成功: {df.shape[0]:,} 行 × {df.shape[1]} 列")

# ══════════════════════════════════════════════════════
# 2. 数据清洗
# ══════════════════════════════════════════════════════
print("\n[2/6] 清洗数据...")
df_clean = df.copy()
before = len(df_clean)
df_clean.drop_duplicates(inplace=True)
print(f"    去重: 删除 {before-len(df_clean):,} 行")

df_clean["CustomerID"] = (df_clean["CustomerID"].astype(str)
                          .replace("nan","Unknown").replace("","Unknown").fillna("Unknown"))
df_clean["Description"] = df_clean["Description"].fillna("Unknown Product")

df_clean["Quantity"]  = pd.to_numeric(df_clean["Quantity"],  errors="coerce")
df_clean["UnitPrice"] = pd.to_numeric(df_clean["UnitPrice"], errors="coerce")
before = len(df_clean)
df_clean = df_clean[(df_clean["Quantity"] > 0) & (df_clean["UnitPrice"] > 0)]
df_clean = df_clean[~df_clean["InvoiceNo"].astype(str).str.startswith("C")]
print(f"    过滤后保留: {len(df_clean):,} 行")

df_clean["AmountSpent"] = df_clean["Quantity"] * df_clean["UnitPrice"]
df_clean["InvoiceDate"] = pd.to_datetime(df_clean["InvoiceDate"])
df_clean["Year"]      = df_clean["InvoiceDate"].dt.year
df_clean["Month"]     = df_clean["InvoiceDate"].dt.month
df_clean["YearMonth"] = df_clean["InvoiceDate"].dt.to_period("M")
df_clean["DayOfWeek"] = df_clean["InvoiceDate"].dt.dayofweek
df_clean["Hour"]      = df_clean["InvoiceDate"].dt.hour

# ══════════════════════════════════════════════════════
# 3. KPI 计算
# ══════════════════════════════════════════════════════
print("\n[3/6] 计算核心指标...")
valid = df_clean[df_clean["CustomerID"] != "Unknown"]
total_gmv       = df_clean["AmountSpent"].sum()
total_orders    = df_clean["InvoiceNo"].nunique()
total_customers = valid["CustomerID"].nunique()
avg_order_value = df_clean.groupby("InvoiceNo")["AmountSpent"].sum().mean()
avg_unit_price  = df_clean["UnitPrice"].mean()
repeat_rate     = (valid.groupby("CustomerID")["InvoiceNo"].nunique() > 1).mean() * 100

print(f"    Total GMV        : GBP {total_gmv:>12,.2f}")
print(f"    Total Orders     :     {total_orders:>12,}")
print(f"    Total Customers  :     {total_customers:>12,}")
print(f"    Avg Order Value  : GBP {avg_order_value:>12,.2f}")
print(f"    Repeat Rate      :     {repeat_rate:>11.1f}%")

# ══════════════════════════════════════════════════════
# 4. 可视化
# ══════════════════════════════════════════════════════
print("\n[4/6] 生成图表...")

# 4a. 月度销售趋势
monthly_sales = df_clean.groupby("YearMonth")["AmountSpent"].sum().reset_index()
monthly_sales["YearMonth_str"] = monthly_sales["YearMonth"].astype(str)
monthly_sales["MoM_Growth"]    = monthly_sales["AmountSpent"].pct_change() * 100
peak = monthly_sales.loc[monthly_sales["AmountSpent"].idxmax()]
peak_idx = monthly_sales["AmountSpent"].idxmax()

fig, ax = plt.subplots(figsize=(14, 5))
ax.fill_between(monthly_sales["YearMonth_str"], monthly_sales["AmountSpent"], alpha=0.15, color="#2E86AB")
ax.plot(monthly_sales["YearMonth_str"], monthly_sales["AmountSpent"],
        marker="o", linewidth=2.5, markersize=5, color="#2E86AB")
ax.annotate(f"Peak\nGBP {peak['AmountSpent']:,.0f}",
            xy=(peak_idx, peak["AmountSpent"]),
            xytext=(max(peak_idx-2,0), peak["AmountSpent"]*1.08),
            arrowprops=dict(arrowstyle="->", color="#E63946", lw=1.5),
            fontsize=9, color="#E63946", ha="center")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"GBP {x/1e3:.0f}K"))
ax.set_title("Monthly Sales Trend (GMV)", fontsize=14, fontweight="bold")
ax.set_xlabel("Year-Month"); ax.set_ylabel("Sales Amount")
plt.xticks(rotation=45, ha="right", fontsize=9); ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "monthly_sales_trend.png"), dpi=150, bbox_inches="tight")
plt.close()
print("    monthly_sales_trend.png ✓")

# 4b. 国家分布
country_sales = df_clean.groupby("Country")["AmountSpent"].sum().sort_values(ascending=False)
uk_pct = country_sales.get("United Kingdom", 0) / total_gmv * 100
pie_data = pd.concat([country_sales.head(9), pd.Series({"Others": country_sales.iloc[9:].sum()})])
fig, ax = plt.subplots(figsize=(11, 7))
wedges, texts, autotexts = ax.pie(pie_data.values, labels=pie_data.index, autopct="%1.1f%%",
    colors=sns.color_palette("Set2", len(pie_data)), startangle=140,
    wedgeprops={"linewidth":0.8,"edgecolor":"white"}, textprops={"fontsize":10})
for at in autotexts: at.set_color("white"); at.set_fontweight("bold"); at.set_fontsize(9)
ax.set_title("Sales Distribution by Country", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "country_sales_pie.png"), dpi=150, bbox_inches="tight")
plt.close()
print("    country_sales_pie.png ✓")

# 4c. 用户复购
valid_cust   = df_clean[df_clean["CustomerID"] != "Unknown"]
purchase_cnt = valid_cust.groupby("CustomerID")["InvoiceNo"].nunique().reset_index(name="PurchaseCount")
spending     = valid_cust.groupby("CustomerID")["AmountSpent"].sum().reset_index(name="TotalSpent")
single = (purchase_cnt["PurchaseCount"] == 1).sum()
repeat_b = (purchase_cnt["PurchaseCount"] > 1).sum()
spending_sorted = spending.sort_values("TotalSpent", ascending=False)
top20 = spending_sorted.iloc[:int(len(spending_sorted)*0.2)]
top20_pct = top20["TotalSpent"].sum() / spending_sorted["TotalSpent"].sum() * 100

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
freq_dist = purchase_cnt["PurchaseCount"].value_counts().sort_index().head(15)
axes[0].bar(freq_dist.index.astype(str), freq_dist.values, color="#5BC0BE", edgecolor="white")
axes[0].set_title("Customer Purchase Frequency (Top 15)", fontsize=12, fontweight="bold")
axes[0].set_xlabel("Number of Purchases"); axes[0].set_ylabel("Customer Count")
axes[0].tick_params(axis="x", rotation=45)
axes[1].pie([single, repeat_b], labels=["One-time","Repeat"], autopct="%1.1f%%",
    colors=["#FC9E4F","#2E86AB"], startangle=90,
    wedgeprops={"linewidth":0.8,"edgecolor":"white"}, textprops={"fontsize":11})
axes[1].set_title("One-time vs Repeat Customers", fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "customer_purchase_analysis.png"), dpi=150, bbox_inches="tight")
plt.close()
print("    customer_purchase_analysis.png ✓")

# 4d. 热销商品
product_revenue = (df_clean.groupby(["StockCode","Description"])["AmountSpent"]
                   .sum().reset_index().sort_values("AmountSpent", ascending=False))
top10 = product_revenue.head(10).copy()
top10["ShortDesc"] = top10["Description"].str[:40]
fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(top10["ShortDesc"], top10["AmountSpent"], color="#2E86AB", edgecolor="white")
ax.invert_yaxis()
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"GBP {x/1e3:.0f}K"))
ax.set_xlabel("Sales Amount")
ax.set_title("Top 10 Products by Revenue", fontsize=14, fontweight="bold")
for bar, val in zip(bars, top10["AmountSpent"]):
    ax.text(bar.get_width()+total_gmv*0.001, bar.get_y()+bar.get_height()/2,
            f"GBP {val:,.0f}", va="center", fontsize=8.5)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "top10_products.png"), dpi=150, bbox_inches="tight")
plt.close()
print("    top10_products.png ✓")

# 4e. RFM
sys.path.insert(0, SCRIPT_DIR)
from analysis_functions import calculate_rfm, classify_users
rfm = calculate_rfm(df_clean); rfm = classify_users(rfm)
order = ["高价值用户","中价值用户","低价值用户","休眠用户"]
colors_rfm = ["#2E86AB","#5BC0BE","#FC9E4F","#C9CBA3"]
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
seg_counts = rfm["UserSegment"].value_counts().reindex([s for s in order if s in rfm["UserSegment"].unique()])
seg_mon    = rfm.groupby("UserSegment")["Monetary"].mean().reindex([s for s in order if s in rfm["UserSegment"].unique()])
axes[0].bar(seg_counts.index, seg_counts.values, color=colors_rfm[:len(seg_counts)], edgecolor="white")
axes[0].set_title("Customers per RFM Segment", fontsize=12, fontweight="bold")
axes[0].tick_params(axis="x", rotation=15)
axes[1].bar(seg_mon.index, seg_mon.values, color=colors_rfm[:len(seg_mon)], edgecolor="white")
axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"GBP {x:,.0f}"))
axes[1].set_title("Avg Spend per RFM Segment", fontsize=12, fontweight="bold")
axes[1].tick_params(axis="x", rotation=15)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "rfm_segments.png"), dpi=150, bbox_inches="tight")
plt.close()
print("    rfm_segments.png ✓")

# ══════════════════════════════════════════════════════
# 5. 业务洞察
# ══════════════════════════════════════════════════════
print("\n[5/6] 业务洞察...")
top5_pct      = country_sales.head(5).sum() / total_gmv * 100
top10_rev_pct = product_revenue.head(10)["AmountSpent"].sum() / total_gmv * 100
top20_rev_pct = top20["TotalSpent"].sum() / spending_sorted["TotalSpent"].sum() * 100

print(f"    UK market share  : {uk_pct:.1f}%")
print(f"    Top-5 countries  : {top5_pct:.1f}%")
print(f"    Top-10 SKU share : {top10_rev_pct:.1f}%")
print(f"    Top-20% cust rev : {top20_rev_pct:.1f}%")

# ══════════════════════════════════════════════════════
# 6. 导出 CSV
# ══════════════════════════════════════════════════════
print("\n[6/6] 导出CSV...")

monthly_sales.drop(columns=["YearMonth"]).rename(columns={"YearMonth_str":"YearMonth"}) \
    .to_csv(os.path.join(OUT_DIR,"monthly_sales.csv"), index=False, encoding="utf-8-sig")
print("    monthly_sales.csv ✓")

cs = country_sales.reset_index(); cs.columns=["Country","TotalSales"]
cs["Pct%"] = (cs["TotalSales"]/total_gmv*100).round(2)
cs.to_csv(os.path.join(OUT_DIR,"country_sales.csv"), index=False, encoding="utf-8-sig")
print("    country_sales.csv ✓")

product_revenue.to_csv(os.path.join(OUT_DIR,"product_sales_ranking.csv"), index=False, encoding="utf-8-sig")
print("    product_sales_ranking.csv ✓")

purchase_cnt.merge(spending, on="CustomerID", how="left") \
    .to_csv(os.path.join(OUT_DIR,"customer_summary.csv"), index=False, encoding="utf-8-sig")
print("    customer_summary.csv ✓")

rfm.to_csv(os.path.join(OUT_DIR,"rfm_results.csv"), index=False, encoding="utf-8-sig")
print("    rfm_results.csv ✓")

print("\n" + "=" * 55)
print("  分析完成！所有文件已保存到 outputs/ 文件夹")
print("=" * 55)
