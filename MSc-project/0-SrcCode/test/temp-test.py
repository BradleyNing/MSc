import pandas as pd

df_train = pd.read_csv('../upload/banking.csv')
label_col = 0

y_column = df_train.columns[label_col]
X_columns = df_train.columns[label_col+1:]

print y_column
print X_columns, len(X_columns)
print df_train.columns, len(df_train.columns)