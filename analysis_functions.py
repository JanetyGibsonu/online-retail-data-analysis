# -*- coding: utf-8 -*-
"""
analysis_functions.py
核心分析函数库

包含数据清洗、RFM建模、用户分类等复用函数。
"""

import numpy as np
import pandas as pd


# ──────────────────────────────────────────────
# 1. 数据清洗
# ──────────────────────────────────────────────

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    对原始 Online Retail 数据执行标准清洗流程
    
    清洗步骤：
        1. 删除完全重复行
        2. 填充 CustomerID / Description 缺失值
        3. 过滤 Quantity <= 0 和 UnitPrice <= 0 的异常记录
        4. 移除退货订单（InvoiceNo 以 'C' 开头）
        5. 新增 AmountSpent 销售额列
        6. 解析 InvoiceDate 并派生时间维度字段

    Parameters
    ----------
    df : pd.DataFrame
        从 Excel / CSV 直接读取的原始数据

    Returns
    -------
    pd.DataFrame
        清洗后的数据
    """
    df_clean = df.copy()

    # 1. 去重
    before = len(df_clean)
    df_clean.drop_duplicates(inplace=True)
    print(f"  [去重] {before:,} → {len(df_clean):,}（删除 {before - len(df_clean):,} 行）")

    # 2. 填充缺失值（统一转为字符串，避免 float 类型 NaN 干扰）
    df_clean["CustomerID"] = df_clean["CustomerID"].astype(str).replace("nan", "Unknown").fillna("Unknown")
    df_clean["Description"] = df_clean["Description"].fillna("Unknown Product")

    # 3. 过滤异常数值
    before = len(df_clean)
    df_clean = df_clean[df_clean["Quantity"] > 0]
    df_clean = df_clean[df_clean["UnitPrice"] > 0]
    print(f"  [过滤异常值] 删除 {before - len(df_clean):,} 条（Quantity/UnitPrice ≤ 0）")

    # 4. 移除退货订单
    before = len(df_clean)
    df_clean = df_clean[~df_clean["InvoiceNo"].astype(str).str.startswith("C")]
    print(f"  [退货订单] 移除 {before - len(df_clean):,} 条")

    # 5. 销售额
    df_clean["AmountSpent"] = df_clean["Quantity"] * df_clean["UnitPrice"]

    # 6. 时间维度
    df_clean["InvoiceDate"] = pd.to_datetime(df_clean["InvoiceDate"])
    df_clean["Year"]       = df_clean["InvoiceDate"].dt.year
    df_clean["Month"]      = df_clean["InvoiceDate"].dt.month
    df_clean["YearMonth"]  = df_clean["InvoiceDate"].dt.to_period("M")
    df_clean["DayOfWeek"]  = df_clean["InvoiceDate"].dt.dayofweek  # 0=Mon
    df_clean["Hour"]       = df_clean["InvoiceDate"].dt.hour

    print(f"  ✅ 清洗完成：最终 {len(df_clean):,} 行 × {df_clean.shape[1]} 列")
    return df_clean


# ──────────────────────────────────────────────
# 2. RFM 建模
# ──────────────────────────────────────────────

def calculate_rfm(df: pd.DataFrame) -> pd.DataFrame:
    """
    基于交易数据计算每位客户的 RFM 指标

    Recency   ─ 最近一次购买距参考日期的天数（越小越好）
    Frequency ─ 历史购买订单数（越大越好）
    Monetary  ─ 历史消费总金额（越大越好）

    参考日期取数据集最大日期 + 1 天，确保 Recency ≥ 1。

    Parameters
    ----------
    df : pd.DataFrame
        清洗后的数据（必须包含 CustomerID / InvoiceDate / InvoiceNo / AmountSpent）

    Returns
    -------
    pd.DataFrame
        每位有效客户的 RFM 原始值及 1-4 分评分，含 RFM_Score 总分（3-12）
    """
    # 仅保留有效客户
    df_valid = df[df["CustomerID"] != "Unknown"].copy()

    reference_date = df_valid["InvoiceDate"].max() + pd.Timedelta(days=1)

    rfm = df_valid.groupby("CustomerID").agg(
        Recency   = ("InvoiceDate",  lambda x: (reference_date - x.max()).days),
        Frequency = ("InvoiceNo",    "nunique"),
        Monetary  = ("AmountSpent",  "sum"),
    ).reset_index()

    # 打分（1-4，4为最优）
    # Recency：天数越少越好 → 标签反序
    rfm["R_Score"] = pd.qcut(rfm["Recency"],   4, labels=[4, 3, 2, 1]).astype(int)

    # Frequency：使用 rank 打破同分值
    rfm["F_Score"] = pd.qcut(
        rfm["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]
    ).astype(int)

    # Monetary：金额越高越好
    rfm["M_Score"] = pd.qcut(rfm["Monetary"],  4, labels=[1, 2, 3, 4]).astype(int)

    rfm["RFM_Score"] = rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]

    return rfm


def classify_users(rfm: pd.DataFrame) -> pd.DataFrame:
    """
    根据 RFM_Score 将用户分为四个价值段

    分段规则（总分 3-12）：
        高价值用户  ── 10-12
        中价值用户  ──  7-9
        低价值用户  ──  4-6
        休眠用户    ──  3

    Parameters
    ----------
    rfm : pd.DataFrame
        calculate_rfm() 的输出

    Returns
    -------
    pd.DataFrame
        新增 UserSegment 列
    """
    conditions = [
        rfm["RFM_Score"] >= 10,
        rfm["RFM_Score"].between(7, 9),
        rfm["RFM_Score"].between(4, 6),
        rfm["RFM_Score"] <= 3,
    ]
    choices = ["高价值用户", "中价值用户", "低价值用户", "休眠用户"]
    rfm = rfm.copy()
    rfm["UserSegment"] = np.select(conditions, choices, default="未知")
    return rfm


# ──────────────────────────────────────────────
# 3. 辅助统计
# ──────────────────────────────────────────────

def get_overview(df: pd.DataFrame) -> dict:
    """
    快速计算核心业务指标

    Returns
    -------
    dict
        total_gmv / total_orders / total_customers /
        avg_order_value / avg_unit_price
    """
    valid = df[df["CustomerID"] != "Unknown"]
    return {
        "total_gmv":        df["AmountSpent"].sum(),
        "total_orders":     df["InvoiceNo"].nunique(),
        "total_customers":  valid["CustomerID"].nunique(),
        "avg_order_value":  df.groupby("InvoiceNo")["AmountSpent"].sum().mean(),
        "avg_unit_price":   df["UnitPrice"].mean(),
    }


def get_repeat_rate(df: pd.DataFrame) -> float:
    """
    计算客户复购率（购买次数 > 1 的客户占比）

    Returns
    -------
    float
        复购率，0-1 之间
    """
    valid = df[df["CustomerID"] != "Unknown"]
    purchase_counts = valid.groupby("CustomerID")["InvoiceNo"].nunique()
    return (purchase_counts > 1).mean()
