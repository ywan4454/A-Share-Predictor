import pandas as pd

def align_data(soxx_df, samsung_df, ashare_df):
    """
    将美股、韩股数据对齐到A股的交易日。
    A股的T日：
      - 韩股：取T日
      - 美股：取T日之前最近的一个交易日 (T-1或更早)
    """
    print("Aligning cross-market data...")
    # 以A股交易日为基准
    df = pd.DataFrame(index=ashare_df.index)
    df['A_ETF_Label'] = ashare_df['A_ETF_Label']
    
    # 1. 对齐韩股 T日特征：直接按日期 merge。如果韩股休市，会是 NaN
    df = df.join(samsung_df[['Samsung_Gap']], how='left')
    
    # 2. 对齐美股 T-1 特征：向后寻找最近的美股交易日
    soxx_returns = soxx_df[['SOXX_Return']].dropna()
    
    df_reset = df.reset_index()
    soxx_reset = soxx_returns.reset_index()
    
    # merge_asof 需要先按时间排序
    df_reset = df_reset.sort_values('Date')
    soxx_reset = soxx_reset.sort_values('Date')
    
    # allow_exact_matches=False 代表严格取 T 日之前最近的一个交易日作为 T-1
    aligned = pd.merge_asof(
        df_reset,
        soxx_reset,
        left_on='Date',
        right_on='Date',
        direction='backward',
        allow_exact_matches=False 
    )
    
    aligned.set_index('Date', inplace=True)
    
    # 3. 剔除含有 NaN 的行（代表某方休市或数据缺失）
    original_len = len(aligned)
    aligned.dropna(inplace=True)
    print(f"Data aligned. Original A-share days: {original_len}, After dropping NaNs: {len(aligned)}")
    
    return aligned
