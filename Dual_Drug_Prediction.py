#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 15:41:58 2020

@author: sid vijay
"""


# Importing the libraries
import numpy as np
import pandas as pd
import keras
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.metrics import mean_squared_error

response_data2 = pd.read_csv('T1tumor_response.csv') # USE FOR 4T1 TUMOR DATA
#response_data2 = pd.read_csv('T1cell_response.csv') # USE FOR 4T1 CELL DATA
drug_list2 = response_data2.iloc[:, 0].values
alldrugs2 = pd.read_csv('kir_allDrugs_namesDoses.csv', encoding='latin1')

alldrugs2 = alldrugs2.set_index('compound')
dataset2 = alldrugs2.loc[drug_list2]
response2 = response_data2['Response'].values
dataset2["response"] = response2

# populate recursive_elimination_kinases_T1tumor.csv or recursive_elimination_kinases_T1cell.csv file with top kinases
kinase_list = pd.read_csv('recursive_elimination_kinases_T1tumor.csv')
kinase_list = kinase_list.values.tolist()

kinases = []
for kinase in kinase_list:
    kinases.append(kinase[0])
    
# Importing the dataset
X = dataset2[kinases].values
y = dataset2.iloc[:, 298].values

#Initialize hyperparameters in model to optimized hyperparameter values
classifier = Sequential()
classifier.add(Dense(units = 100, kernel_initializer = 'TruncatedNormal', activation = 'relu', input_dim = len(kinases)))
classifier.add(Dense(units = 100, kernel_initializer = 'TruncatedNormal', activation = 'relu'))
classifier.add(Dense(units = 1, kernel_initializer = 'TruncatedNormal' )) 
classifier.compile(loss = 'mean_squared_error', optimizer='adam')
classifier.fit(X,y, epochs=80, batch_size=44)


## GENERATING COMBO DATASET

X_predict = alldrugs2.loc[drug_list2]
X_predict = X_predict[kinases]
prediction_index = X_predict.index.tolist()
X_predict = X_predict.iloc[:, 0:len(kinases)+2].values

results = []
def row_combiner(row1, row2):
    combined_row = []
    for num in range(len(row1)):
        value1 = row1[num]/100
        value2 = row2[num]/100
        final_value = (value1 * value2)/(value1 + value2 - (value1 * value2))
        final_value = final_value * 100
        combined_row.append(final_value)
    return(combined_row)

def DrugComboDataCombiner():
    for drug_number in range(len(prediction_index)):
        for drug_number2 in range(drug_number + 1, len(prediction_index)):
            combined_list = row_combiner(X_predict[drug_number], X_predict[drug_number2])
            combined_list = [combined_list]
            y_pred = classifier.predict(np.array(combined_list))
            results.append([str(prediction_index[drug_number]), str(prediction_index[drug_number2]), y_pred[0][0]])
        print(drug_number)

    
DrugComboDataCombiner()

results_df = pd.DataFrame(results)
results_df.to_csv("Dual_Drug_Combo_Predictions_4T1_train_set.csv", header = ["Drug 1", "Drug 2", "Prediction"])
X_predict = alldrugs2
X_predict = X_predict[kinases]
prediction_index = X_predict.index.tolist()
X_predict = X_predict.iloc[:, 0:len(kinases)+2].values

# Predicting the Test set results
y_pred = classifier.predict(X_predict)
untested_inhibitor_prediction = pd.DataFrame(y_pred.tolist(), index = prediction_index)




