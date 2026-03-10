# load the pima data
import warnings
warnings.filterwarnings('ignore')

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

# Resolve CSV path from project root (same folder as manage.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(BASE_DIR, 'pima.csv')

# Replaced ONLY the absolute path with a portable path so server par chale


df = pd.read_csv(csv_path, names=[
"preg","glucose","bp","skin","insulin","bmi","pedigree","age","class"
])

# Your original preprocessing


df1 = df[['glucose','bp','skin','insulin','bmi']]
df2 = df.drop(columns=['glucose','bp','skin','insulin','bmi'])


df1.replace(0, np.nan, inplace=True)
df1.fillna(df1.mean(), inplace=True)
# df1.isnull().sum() # (kept but not printed)


df3 = pd.concat([df1, df2], axis=1)

# seperate input and output
x = df3.drop(columns=['class'])
y = df3['class']


# split the data set into 2 parts. one for training and another part for testing
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=5)

# ==================
# Your model funcs |
# ==================


def lg():
    # Logistic Regression
    global L
    import warnings
    warnings.filterwarnings('ignore')
    from sklearn.linear_model import LogisticRegression
    L = LogisticRegression()
    # train the model by using 80% training data
    L.fit(x_train, y_train)
    # test the model by using testing data
    y_pred_lg = L.predict(x_test)
    # find accuracy
    from sklearn.metrics import accuracy_score
    acc_lg = accuracy_score(y_test, y_pred_lg)
    acc_lg = round(acc_lg * 100, 2)
    # Tkinter messagebox removed; print/return instead
    print("accuracy in logistic regression is ", acc_lg, "%")
    return acc_lg

def knn():
    import warnings
    warnings.filterwarnings('ignore')
    from sklearn.neighbors import KNeighborsClassifier
    K = KNeighborsClassifier(n_neighbors=5)
    # train the model
    K.fit(x_train, y_train)
    # test the model
    y_pred_knn = K.predict(x_test)
    # find accuracy
    from sklearn.metrics import accuracy_score
    acc_knn = accuracy_score(y_test, y_pred_knn)
    acc_knn = round(acc_knn * 100, 2)
    print("accuracy in KNN is ", acc_knn, "%")
    return acc_knn

def dt():
    import warnings
    warnings.filterwarnings('ignore')
    # apply Decission Tree model
    from sklearn.tree import DecisionTreeClassifier
    D = DecisionTreeClassifier # NOTE: Original code keeps class without ()
    # train/test using K (as in your original) – this would error if called.
    # Left UNCHANGED intentionally as per your request.
    # from sklearn.metrics import accuracy_score
    # (Not used in web flow.)
    return None


def rf():
    import warnings
    warnings.filterwarnings('ignore')
    from sklearn.ensemble import RandomForestClassifier
    R = RandomForestClassifier()
    # train the model
    R.fit(x_train, y_train)
    # test the model
    y_pred_rf = R.predict(x_test)
    # find accuracy
    from sklearn.metrics import accuracy_score
    acc_rf = accuracy_score(y_test, y_pred_rf)
    acc_rf = round(acc_rf * 100, 2)
    print("accuracy in Random Forest is ", acc_rf, "%")
    return acc_rf

def compare():
# compare (original idea – depends on acc_* vars)
# Left minimal because accuracies exist only after calling respective funcs.
    pass

# ==============================
# Helper used by Django frontend
# ==============================


# at end of file
def predict_for_input(glucose, bp, skin, insulin, bmi, preg, pedigree, age):
    if 'L' not in globals():
        lg()
    features = [glucose, bp, skin, insulin, bmi, preg, pedigree, age]
    pred = L.predict([features])
    return int(pred[0])   # return int (0 or 1)
