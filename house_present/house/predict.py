from .clean import clean, convert
import pandas as pd
from sklearn.externals import joblib

def predict(data):
    data = clean(data)
    # print(data)
    columns = ['pay_way', 'tag', 'rent_way', 'house_type', 'size', 'orientation', 'floor', 'decorate_type', 'facility', 'traffic', 'address', 'coordinate']
    data = pd.DataFrame(data, columns=columns)
    data = convert(data)
    data.to_csv("./test.csv")
    print(data.info)
    return get_predicted_price(data)


def get_predicted_price(data):
    models_str=['LinearRegression','KNNRegressor','SVR','Ridge','Lasso','MLPRegressor','DecisionTree','ExtraTree','XGBoost','RandomForest','AdaBoost','GradientBoost','Bagging']
    # for name in models_str:
    #     save_path_name= '../house_predict/model/' + name +"_train_model.m"
    #     print('开始加载模型：'+ name)
    #     model = joblib.load(save_path_name)  #加载模型
    #     # 预测价格
    #     print('开始预测 price：'+ name)
    #     pred_y=model.predict(data)
    #     print(name + '预测结果为：', pred_y)

    name = models_str[9]
    save_path_name= '../house_predict/model/' + name +"_train_model.m"
    print('开始加载模型：'+ name)
    model = joblib.load(save_path_name)  #加载模型
    # 预测价格
    print('开始预测 price：'+ name)
    pred_y=model.predict(data)
    print(name + '预测结果为：', pred_y)
    return pred_y[0]
