# -*- coding: utf-8 -*-
"""
data_loading.py
数据加载工具函数

支持从本地文件或Kaggle自动下载Online Retail数据集
"""

import os
import pandas as pd

# 本文件所在目录（无论从哪里运行，路径都正确）
_HERE = os.path.dirname(os.path.abspath(__file__))


def _detect_format(file_path: str) -> str:
    """
    通过读取文件头魔术字节判断真实格式，不依赖后缀名。

    xlsx 本质是 ZIP 包，头字节为 PK (50 4B)。
    xls 旧格式头字节为 D0 CF。
    CSV/文本文件头字节直接是可读字符。

    Returns: 'xlsx' | 'xls' | 'csv'
    """
    with open(file_path, "rb") as f:
        magic = f.read(4)

    if magic[:2] == b"PK":
        return "xlsx"          # ZIP 压缩包 → 真正的 xlsx
    elif magic[:2] == b"\xd0\xcf":
        return "xls"           # OLE2 复合文档 → 旧版 xls
    else:
        return "csv"           # 其余当 CSV 处理（包含"后缀是xlsx但内容是CSV"的情况）


def load_local_data(file_path="./Online Retail.xlsx", sheet_name="Online Retail"):
    """
    从本地文件加载数据。

    自动检测文件真实格式（不依赖后缀名），兼容以下情况：
    - 标准 .xlsx / .xls Excel 文件
    - 后缀为 .xlsx 但实际是 CSV 的文件（Kaggle 部分版本如此）
    - 标准 .csv 文件

    Parameters
    ----------
    file_path : str
        文件路径
    sheet_name : str
        Sheet名称（仅真正的 Excel 文件有效）

    Returns
    -------
    pd.DataFrame or None
    """
    try:
        fmt = _detect_format(file_path)
        print(f"   检测到文件格式: {fmt.upper()}  ({file_path})")

        if fmt == "xlsx":
            df = pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl")
        elif fmt == "xls":
            df = pd.read_excel(file_path, sheet_name=sheet_name, engine="xlrd")
        else:
            # CSV：依次尝试常见编码 + 分隔符组合
            df = None
            for enc in ("utf-8", "latin-1", "gbk", "utf-8-sig"):
                for sep in (",", "\t", ";"):
                    try:
                        tmp = pd.read_csv(file_path, encoding=enc, sep=sep, nrows=5)
                        # 有效：列数 > 1 且包含关键列
                        if tmp.shape[1] > 1 and any("InvoiceNo" in c for c in tmp.columns):
                            df = pd.read_csv(file_path, encoding=enc, sep=sep,
                                             dtype={"CustomerID": str})
                            print(f"   编码={enc}, 分隔符={repr(sep)}")
                            break
                    except Exception:
                        continue
                if df is not None:
                    break

            # 最后兜底：强制用 python engine 自动嗅探分隔符
            if df is None:
                for enc in ("utf-8", "latin-1"):
                    try:
                        df = pd.read_csv(file_path, encoding=enc, sep=None,
                                         engine="python", dtype={"CustomerID": str})
                        if df.shape[1] > 1:
                            print(f"   编码={enc}, 分隔符=自动检测")
                            break
                    except Exception:
                        continue

            if df is None:
                raise ValueError("无法解析 CSV 文件，请检查文件格式")

        print(f"✅ 成功加载: {df.shape[0]:,} 行 × {df.shape[1]} 列")
        return df

    except FileNotFoundError:
        print(f"❌ 文件未找到: {file_path}")
        return None
    except Exception as e:
        print(f"❌ 加载失败: {e}")
        return None


def download_kaggle_dataset(dest_dir="."):
    """
    使用 kagglehub 自动下载 Online Retail 数据集
    
    前提条件：
        1. pip install kagglehub
        2. 已配置 Kaggle API credentials（~/.kaggle/kaggle.json）
    
    Parameters
    ----------
    dest_dir : str
        数据集下载后存放目录（默认当前目录）
    
    Returns
    -------
    pd.DataFrame or None
    """
    try:
        import kagglehub  # noqa: F401
    except ImportError:
        print("❌ 未安装 kagglehub，请先运行: pip install kagglehub")
        return None

    try:
        import kagglehub

        dataset_path = kagglehub.dataset_download("carrie1/ecommerce-data")
        print(f"📥 数据集已下载到: {dataset_path}")

        # 遍历查找数据文件
        for root, _, files in os.walk(dataset_path):
            for file in files:
                if file.endswith(".csv") or file.endswith(".xlsx"):
                    full_path = os.path.join(root, file)
                    print(f"📄 找到数据文件: {full_path}")
                    if file.endswith(".csv"):
                        df = pd.read_csv(full_path, encoding="latin-1")
                    else:
                        df = pd.read_excel(full_path)
                    print(f"✅ 加载成功: {df.shape[0]:,} 行 × {df.shape[1]} 列")
                    return df

        print("❌ 下载目录中未找到数据文件")
        return None

    except Exception as e:
        print(f"❌ Kaggle下载失败: {e}")
        print("\n请手动从以下地址下载数据集：")
        print("  https://www.kaggle.com/datasets/carrie1/ecommerce-data")
        return None


def load_data(file_path="./Online Retail.xlsx", sheet_name="Online Retail"):
    """
    智能加载入口：按优先级依次尝试多个路径，全部失败时才尝试Kaggle下载

    查找顺序：
        1. 传入的 file_path（相对于当前工作目录）
        2. 与 data_loading.py 同目录下的同名文件
        3. 上述两者对应的 .csv 版本（data.csv / Online Retail.csv）

    Parameters
    ----------
    file_path : str
        首选文件路径，默认 './Online Retail.xlsx'
    sheet_name : str
        Sheet名称（仅Excel有效）

    Returns
    -------
    pd.DataFrame

    Raises
    ------
    RuntimeError
        所有方式均失败时抛出
    """
    filename = os.path.basename(file_path)

    # 候选路径列表（按优先级）
    candidates = [
        file_path,                                   # 1. 原始传入路径（相对cwd）
        os.path.join(_HERE, filename),               # 2. 脚本同目录
        os.path.join(_HERE, "Online Retail.xlsx"),   # 3. 固定文件名（兜底）
        os.path.join(_HERE, "data.csv"),             # 4. CSV 备用
    ]
    # 去重保持顺序
    seen = set()
    candidates = [p for p in candidates if not (p in seen or seen.add(p))]

    for path in candidates:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            print(f"📂 找到数据文件: {abs_path}")
            df = load_local_data(abs_path, sheet_name)
            if df is not None:
                return df

    # 全部本地路径失败，尝试Kaggle
    print("⚠️  未在以下路径找到数据文件：")
    for p in candidates:
        print(f"   {os.path.abspath(p)}")
    print("\n尝试从 Kaggle 自动下载...")
    df = download_kaggle_dataset()

    if df is None:
        raise RuntimeError(
            "数据加载失败！\n"
            f"请将 'Online Retail.xlsx' 放到以下任意位置：\n"
            f"  {os.path.abspath('.')}\n"
            f"  {_HERE}\n"
            "或从 Kaggle 下载：https://www.kaggle.com/datasets/carrie1/ecommerce-data"
        )
    return df
