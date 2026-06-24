import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def train_and_predict(df):
    """
    训练模型并进行评估，预测最后一日的上涨概率
    """
    print("Training RandomForest model...")
    # 特征与标签
    features = ['SOXX_Return', 'Samsung_Gap']
    X = df[features]
    y = df['A_ETF_Label']
    
    # 划分训练集和测试集（按时间顺序划分，使用前面80%训练，后面20%测试）
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
    model.fit(X_train, y_train)
    
    # 测试集准确率
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Model test accuracy (on last 20% data): {acc:.2%}")
    
    # 预测最近一天的 A 股表现（模拟推断阶段）
    latest_features = X.iloc[[-1]]
    latest_date = X.index[-1].strftime('%Y-%m-%d')
    prob = model.predict_proba(latest_features)[0]
    
    print(f"\n--- Prediction for the latest date in data: {latest_date} ---")
    print(f"US SOXX Return (T-1): {latest_features['SOXX_Return'].values[0]*100:.2f}%")
    print(f"Samsung Gap (T): {latest_features['Samsung_Gap'].values[0]*100:.2f}%")
    print(f"Probability of A-share Semiconductor ETF UP: {prob[1]*100:.2f}%")
    
    return model
