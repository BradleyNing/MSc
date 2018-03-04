from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

import pandas as pd

def DropAndCode(df):
    for column in df.columns:
        if str(df[column].dtype) =='object':
            y = df[column].values
            le = LabelEncoder()
            y = le.fit_transform(y)
            df[column] = y  
    return df

print 'Hello...'
df_raw = pd.read_csv('../upload/banking.csv', header=0)
df_raw = DropAndCode(df_raw)
print df_raw.shape
df_raw.to_csv('../output/df_raw.csv', index=False)

df_X = pd.read_csv('../output/df_X.csv', header=0)
X_train = df_X.values
print X_train.shape

df_y = pd.read_csv('../output/df_y.csv', header=0)
y_train = df_y.values
y_train = y_train.ravel()
print y_train.shape

estimator = LogisticRegression(penalty='l2', C=0.1, random_state=0)
estimator.fit(X_train, y_train)

df2 = pd.read_csv('../output/df_test.csv', header=0)
X2_test = df2.values
print X2_test.shape
y2_pred = estimator.predict(X2_test)
df2['Prediction'] = y2_pred
df2.to_csv('../output/prediction.csv',index=False)