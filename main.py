import os
import sys

# 将当前目录加入系统路径，确保 src 包能被找到
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_fetcher import fetch_us_soxx, fetch_korea_samsung, fetch_ashare_etf
from src.processor import align_data
from src.model import train_and_predict

def main():
    # 确保 data 目录存在
    os.makedirs('data', exist_ok=True)
    
    # 1. 获取数据 (取最近两年的数据进行回测训练)
    soxx_df = fetch_us_soxx("2022-01-01")
    samsung_df = fetch_korea_samsung("2022-01-01")
    ashare_df = fetch_ashare_etf("20220101")
    
    # 2. 对齐数据
    aligned_df = align_data(soxx_df, samsung_df, ashare_df)
    
    # 保存对齐后的数据以供检查
    aligned_df.to_csv('data/aligned_data.csv')
    print("Saved aligned data to data/aligned_data.csv")
    
    # 3. 训练与预测
    train_and_predict(aligned_df)

if __name__ == "__main__":
    main()
