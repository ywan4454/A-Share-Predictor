# 基于跨市场时间差（Lead-Lag Effect）的A股半导体走势预测系统设计文档

## 1. 项目架构

项目将采用模块化设计，目录结构如下：
```text
us:korea_trend/
├── data/                   # 存放下载或处理后的 CSV 数据缓存
├── src/
│   ├── data_fetcher.py     # 负责使用 yfinance 和 akshare 下载数据（包含代理设置）
│   ├── processor.py        # 负责处理数据对齐、缺失值过滤、特征计算
│   └── model.py            # 负责模型构建、训练及预测（基于 RandomForest）
├── main.py                 # 主程序入口，串联数据获取、处理和预测流程
├── requirements.txt        # Python 依赖包列表
└── design.md               # 项目设计文档
```

## 2. 数据获取逻辑 (`src/data_fetcher.py`)

- **代理设置**：为解决 `yfinance` 在大陆的网络问题，代码开头将注入环境变量：
  ```python
  import os
  os.environ["HTTP_PROXY"] = "http://127.0.0.1:1087"
  os.environ["HTTPS_PROXY"] = "http://127.0.0.1:1087"
  ```
- **美股特征数据 (T-1日)**：
  - 标的：费城半导体指数 ETF (`SOXX`)。
  - 来源：`yfinance`。
  - 提取字段：获取日线数据中的 `Close`，并计算单日涨跌幅 `(Close_{T-1} - Close_{T-2}) / Close_{T-2}`。
- **韩股特征数据 (T日早盘)**：
  - 标的：三星电子 (`005930.KS`) 或 SK海力士 (`000660.KS`)。
  - 来源：`yfinance`。
  - 提取字段：鉴于分钟级数据获取不稳定，采用 T 日开盘跳空涨跌幅作为早盘表现代理指标。计算公式为 `(Open_{T} - Close_{T-1}) / Close_{T-1}`。
- **A股标签数据 (T日)**：
  - 标的：半导体 ETF (`512480`)。
  - 来源：`akshare` (`ak.fund_etf_hist_em`)。
  - 提取字段：计算日内表现 `(Close_{T} - Open_{T}) / Open_{T}`。若大于0，则标签 `Label=1` (涨)，否则 `Label=0` (跌)。

## 3. 时区对齐与数据处理逻辑 (`src/processor.py`)

跨市场数据对齐是本项目核心。我们需要确保美股、韩股、A股的交易日严丝合缝地对齐，避免引入未来数据或时间错位。

1. **基准时间线构建**：以 A股 (`512480`) 的交易日作为基准时间轴 T。
2. **特征前置对齐**：
   - 对于 T 日，我们需要找到 T-1 日的美股特征。由于节假日不同，美股的最近一个交易日不一定是 T-1 的日历日。我们将使用 `T` 日之前的美股最后一个有效交易日作为 T-1 表现。
   - 韩股特征则直接取日期等于 T 日的数据（如果韩股 T 日休市，则当天 A 股预测缺乏韩股特征输入，整行抛弃处理）。
3. **缺失值与休市过滤**：使用 `pandas.merge` 将所有特征通过日期 Index 合并。合并后若出现 NaN（代表当日某一市场休市或无数据），则直接 `dropna()` 剔除该样本，保证训练数据的纯净性。
4. **特征工程合并**：最终输出一个对齐后的 DataFrame，包含列：`Date`, `SOXX_return_T-1`, `Samsung_gap_T`, `A_ETF_Label_T`。

## 4. 模型训练与预测 (`src/model.py`)

- **模型选择**：`sklearn.ensemble.RandomForestClassifier`。
- **训练流程**：
  - 划分训练集和测试集（按照时间顺序，如最近 N 天作为测试集，之前的数据作为训练集）。
  - 使用对齐后的特征 `[SOXX_return_T-1, Samsung_gap_T]` 预测 `A_ETF_Label_T`。
- **在线预测 (推断阶段)**：
  - 在 T 日早盘（如上午9:30前），获取最新的美股昨收盘涨幅，以及韩股最新的开盘价。
  - 将最新特征送入训练好的模型，输出今日 A股半导体 ETF 上涨的概率（`predict_proba`）。

## 5. 项目依赖 (`requirements.txt`)

```text
pandas
numpy
yfinance
akshare
scikit-learn
```
