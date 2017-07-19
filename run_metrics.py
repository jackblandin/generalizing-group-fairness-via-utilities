import os, sys
import numpy as np
from misc.two_naive_bayes import *
from misc.zafar_classifier import *
from misc.prejudice_regularizer import *
from misc.black_box_auditing import *
from sklearn import svm
from data.propublica.load_numerical_compas import *
from data.german.load_german_data import *
from data.adult.load_adult import *
import algorithms.zafar.fair_classification.utils as ut
import algorithms.zafar.fair_classification.loss_funcs as lf
from metrics.metrics import *
from sklearn.svm import SVC

def prepare_compas():
  sensitive_attrs = ["race"]
  sensitive_attr = sensitive_attrs[0]
  train_fold_size = 0.7

  run_compas_repair()

  X, y, x_control = load_compas_data("all_numeric.csv")
  X_repaired_1, y_repaired_1, x_control_repaired_1 = load_compas_data("repaired-compas-scores-two-years-violent_1.csv")

  perm = range(0,len(y)) # shuffle data before creating each fold
  shuffle(perm)
  X = X[perm]
  X_repaired_1 = X_repaired_1[perm]

  y = y[perm]

  for k in x_control.keys():
    x_control[k] = x_control[k][perm]

  # Split into train and test
  x_train, y_train, x_control_train, x_test, y_test, x_control_test = ut.split_into_train_test(X, y, x_control, train_fold_size)

  x_train_1, y_train_1, x_control_train_1, x_test_1, y_test_1, x_control_test_1 = ut.split_into_train_test(X_repaired_1, y_repaired_1, x_control_repaired_1, train_fold_size)

  return x_train, y_train, x_control_train, x_test, y_test, x_control_test, x_train_1, y_train_1, x_control_train_1, x_test_1, y_test_1, x_control_test_1, sensitive_attr 

def prepare_adult():
  sensitive_attrs = ["sex"]
  sensitive_attr = sensitive_attrs[0]
  train_fold_size = 0.7

  run_adult_repair()

  X, y, x_control = load_adult_data("data/adult/adult-all-numerical-converted.csv")
  X_repaired_1, y_repaired_1, x_control_repaired_1 = load_adult_data("data/adult/Repaired_Data_Files/Fixed_Adult_1.csv")
  
  ut.compute_p_rule(x_control["sex"], y)
  X = ut.add_intercept(X)
  X_repaired_1 = ut.add_intercept(X_repaired_1)

  perm = range(0,len(y))
  shuffle(perm)
  X = X[perm]
  X_repaired_1 = X_repaired_1[perm]
  y = y[perm]

  for k in x_control.keys():
    x_control[k] = x_control[k][perm]

  x_train, y_train, x_control_train, x_test, y_test, x_control_test = ut.split_into_train_test(X, y, x_control, train_fold_size)

  x_train_repaired_1, y_train_repaired_1, x_control_train_repaired_1, x_test_repaired_1, y_test_repaired_1, x_control_test_repaired_1 = ut.split_into_train_test(X_repaired_1, y_repaired_1, x_control_repaired_1, train_fold_size)

  return x_train, y_train, x_control_train, x_test, y_test, x_control_test, x_train_repaired_1, y_train_repaired_1, x_control_train_repaired_1, x_test_repaired_1, y_test_repaired_1, x_control_test_repaired_1, sensitive_attr

def prepare_german():
  sensitive_attrs = ["sex"]
  sensitive_attr = sensitive_attrs[0]
  train_fold_size = 0.3

  run_german_repair()

  X, y, x_control = load_german_data("german_numeric_sex_encoded_fixed.csv")
  X_repaired_1, y_repaired_1, x_control_repaired_1 = load_german_data("repaired_german_credit_data_1.csv")

  perm = range(0, len(y))
  shuffle(perm)
  X = X[perm]
  X_repaired_1 = X_repaired_1[perm]

  y = y[perm]

  x_control["sex"] = np.array(x_control["sex"])

  for k in x_control.keys():
    x_control[k] = x_control[k][perm]

  x_train, y_train, x_control_train, x_test, y_test, x_control_test = ut.split_into_train_test(X, y, x_control, train_fold_size)

  x_control_train["sex"] = np.array(x_control_train["sex"])
  x_control_test["sex"] = np.array(x_control_test["sex"])

  x_train_repaired_1, y_train_repaired_1, x_control_train_repaired_1, x_test_repaired_1, y_test_repaired_1, x_control_test_repaired_1 = ut.split_into_train_test(X_repaired_1, y_repaired_1, x_control_repaired_1, train_fold_size)

  x_control_train_repaired_1["sex"] = np.array(x_control_train_repaired_1["sex"])
  x_control_test_repaired_1["sex"] = np.array(x_control_test_repaired_1["sex"]) 

  return x_train, y_train, x_control_train, x_test, y_test, x_control_test, x_train_repaired_1, y_train_repaired_1, x_control_train_repaired_1, x_test_repaired_1, y_test_repaired_1, x_control_test_repaired_1, sensitive_attr

def print_res(metric):
  print("Accuracy: ", metric.accuracy())
  print("DI Score: ", metric.DI_score())
  print("BER: ", metric.BER())
  print("Utility: ", metric.utility())
  print("CV Score: ", metric.CV_score())
  

def run_metrics(data):
  if data == 'compas':
    x_train, y_train, x_control_train, x_test, y_test, x_control_test, x_train_feldman, y_train_feldman, x_control_train_feldman, x_test_feldman, y_test_feldman, x_control_test_feldman, sensitive_attr = prepare_compas()
    name = "propublica"
    feldman_filename = "compas_repaired"
    filename = "propublica_race_nb_0"
    classify = classify_compas
  elif data == 'german':
    x_train, y_train, x_control_train, x_test, y_test, x_control_test, x_train_feldman, y_train_feldman, x_control_train_feldman, x_test_feldman, y_test_feldman, x_control_test_feldman, sensitive_attr = prepare_german()
    name = "German"
    feldman_filename = "german_repaired"
    filename = "german_sex_nb_0"
    classify = classify_german
  elif data == 'adult':
    x_train, y_train, x_control_train, x_test, y_test, x_control_test, x_train_feldman, y_train_feldman, x_control_train_feldman, x_test_feldman, y_test_feldman, x_control_test_feldman, sensitive_attr = prepare_adult()
    name = "sex_adult"
    feldman_filename = "adult_repaired"
    filename = "feldmen_cleaned_sex_adult_nb_0"
    classify = classify_adult
    
  # SVM 
  print("Running SVM...")
  clf = SVC()
  clf.fit(x_train, y_train)
  predictions = clf.predict(x_test)
  fixed_predictions = []
  fixed_y_test = []

  for j in range(0, len(predictions)):
    print predictions[j]
    if predictions[j] == '0':
      fixed_predictions.append(0)
    elif predictions[j] == '1':
      fixed_predictions.append(1)

  for j in range(0, len(y_test)):
    print y_test[j]
    if y_test[j] == '0':
      fixed_y_test.append(0)
    elif y_test[j] == '1':
      fixed_y_test.append(1)

  svm_actual, svm_predicted, svm_protected = fixed_y_test, fixed_predictions, x_control_test[sensitive_attr].astype(int)

  x_train_float = x_train.astype(np.float)
  y_train_float = y_train.astype(np.float)
  x_test_float = x_test.astype(np.float)
  y_test_float = y_test.astype(np.float)

  # NB
  print("Running Naive Bayes...")
  nb = GaussianNB()
  nb.fit(x_train_float, y_train_float)
  predictions = nb.predict(x_test_float)
  fixed_predictions = []
  fixed_y_test = []

  for j in range(0, len(predictions)):
    if predictions[j] == 0.:
      fixed_predictions.append(0)
    elif predictions[j] == 1.:
      fixed_predictions.append(1)

  for j in range(0, len(y_test)):
    if y_test[j] == '0':
      fixed_y_test.append(0)
    elif y_test[j] == '1':
      fixed_y_test.append(1)  

  nb_actual, nb_predicted, nb_protected = fixed_y_test, fixed_predictions, x_control_test[sensitive_attr].astype(int)

  # LR
  print("Running Logistic Regression...")
  lr = LogisticRegression()
  lr.fit(x_train_float, y_train_float)
  predictions = lr.predict(x_test_float)
  fixed_predictions = []
  fixed_y_test = []

  for j in range(0, len(predictions)):
    if predictions[j] == 0.:
      fixed_predictions.append(0)
    elif predictions[j] == 1.:
      fixed_predictions.append(1)

  for j in range(0, len(y_test)):
    if y_test[j] == '0':
      fixed_y_test.append(0)
    elif y_test[j] == '1':
      fixed_y_test.append(1)

  lr_actual, lr_predicted, lr_protected = fixed_y_test, fixed_predictions, x_control_test[sensitive_attr].astype(int)

  # Kamishima
  print("Running Kamishima...")
  x_train_with_sensitive_feature = []
  for i in range(0, len(x_train_float)):
    val = x_control_train[sensitive_attr][i]
    feature_array = np.append(x_train_float[i], val)
    x_train_with_sensitive_feature.append(feature_array)
  
  x_train_with_sensitive_feature = np.array(x_train_with_sensitive_feature)

  x_test_with_sensitive_feature = []
  for i in range(0, len(x_test_float)):
    val = x_control_test[sensitive_attr][i]
    feature_array = np.append(x_test_float[i], val)
    x_test_with_sensitive_feature.append(feature_array)

  x_test_with_sensitive_feature = np.array(x_test_with_sensitive_feature)

  y_classified_results = train_classify(sensitive_attr, name, x_train_with_sensitive_feature.astype('float64'), y_train.astype('float64'), x_test_with_sensitive_feature.astype('float64'), y_test.astype('float64'), 1, 30, x_control_test)
  fixed_y_test = []
  for j in y_test_float:
      if j == 1.0:
          fixed_y_test.append(1)
      elif j == -1.0 or j == 0.0:
          fixed_y_test.append(0)
      else:
          print "Invalid class value in y_control_test"
  
  kam30_actual, kam30_predicted, kam30_protected = fixed_y_test, y_classified_results, x_control_test[sensitive_attr].astype(int)

  y_classified_results = train_classify(sensitive_attr, name, x_train_with_sensitive_feature.astype('float64'), y_train.astype('float64'), x_test_with_sensitive_feature.astype('float64'), y_test.astype('float64'), 1, 1, x_control_test)
  fixed_y_test = []
  for j in y_test_float:
      if j == 1.0:
          fixed_y_test.append(1)
      elif j == -1.0 or j == 0.0:
          fixed_y_test.append(0)
      else:
          print "Invalid class value in y_control_test" 

  kam1_actual, kam1_predicted, kam1_protected = fixed_y_test, y_classified_results, x_control_test[sensitive_attr].astype(int)

  # Calder's Two Naive Bayes
  print("Running Calders' Two Naive Bayes...")
  c2nb_protected_predicted, c2nb_protected_actual, c2nb_favored_predicted, c2nb_favored_actual = run_two_naive_bayes(0.0, filename, x_train, y_train, x_control_train, x_test, y_test, x_control_test, sensitive_attr)
  c2nb_protected_protected = [0] * len(c2nb_protected_predicted) 
  c2nb_favored_protected = [1] * len(c2nb_favored_predicted)


  # Feldman
  print("Running Feldman...")
  classify(feldman_filename, sensitive_attr, x_train_feldman, y_train_feldman, x_control_train_feldman, x_test_feldman, y_test_feldman, x_control_test_feldman) 

  # Zafar
  print("Running Zafar...")
  
  y_train = np.array(y_train)
  y_train = y_train.astype(float)
  x_control_train[sensitive_attr] = x_control_train[sensitive_attr].astype(float)
  x_control_test[sensitive_attr] = x_control_test[sensitive_attr].astype(float)

  # Params
  sensitive_attrs = [str(sensitive_attr)]
  apply_fairness_constraints = 0
  apply_accuracy_constraint = 0
  sep_constraint = 0
  loss_function = lf._logistic_loss
  sensitive_attrs_to_cov_thresh = {}
  gamma = None

  w = ut.train_model(x_train.astype(float), y_train, x_control_train, loss_function, apply_fairness_constraints, apply_accuracy_constraint, sep_constraint, sensitive_attrs, sensitive_attrs_to_cov_thresh, gamma)
  distances_boundary_test = (np.dot(x_test.astype(float), w)).tolist()
  predictions = np.sign(distances_boundary_test)
  fixed_y_test = []
  fixed_predictions = []

  for x in y_test.astype(float):
    if x == -1:
      fixed_y_test.append(0)
    elif x == 1:
      fixed_y_test.append(1)
    elif x == 0:
      fixed_y_test.append(0)
    else:
      print "Incorrect value in class values"

  for x in predictions:
    if x == -1:
      fixed_predictions.append(0)
    elif x == 1:
      fixed_predictions.append(1)
    elif x == 0:
      fixed_predictions.append(0)
    else:
      print "Incorrect value in class values"

  zafar_unconstrained_actual, zafar_unconstrained_predicted, zafar_unconstrained_protected = fixed_y_test, fixed_predictions, x_control_test[sensitive_attr].astype(int)

  # Params
  apply_fairness_constraints = 1
  apply_accuracy_constraint = 0
  sep_constraint = 0
  sensitive_attrs_to_cov_thresh = {"sex":0}

  w = ut.train_model(x_train.astype(float), y_train, x_control_train, loss_function, apply_fairness_constraints, apply_accuracy_constraint, sep_constraint, sensitive_attrs, sensitive_attrs_to_cov_thresh, gamma)
  distances_boundary_test = (np.dot(x_test.astype(float), w)).tolist()
  predictions = np.sign(distances_boundary_test)
  fixed_y_test = []
  fixed_predictions = []

  for x in y_test.astype(float):
    if x == -1:
      fixed_y_test.append(0)
    elif x == 1:
      fixed_y_test.append(1)
    elif x == 0:
      fixed_y_test.append(0)
    else:
      print "Incorrect value in class values"

  for x in predictions:
    if x == -1:
      fixed_predictions.append(0)
    elif x == 1:
      fixed_predictions.append(1)
    elif x == 0:
      fixed_predictions.append(0)
    else:
      print "Incorrect value in class values"

  zafar_opt_accuracy_actual, zafar_opt_accuracy_predicted, zafar_opt_accuracy_protected = fixed_y_test, fixed_predictions, x_control_test[sensitive_attr].astype(int)

  # Params
  apply_fairness_constraints = 0
  apply_accuracy_constraint = 1
  sep_constraint = 0
  gamma = 0.5

  w = ut.train_model(x_train.astype(float), y_train, x_control_train, loss_function, apply_fairness_constraints, apply_accuracy_constraint, sep_constraint, sensitive_attrs, sensitive_attrs_to_cov_thresh, gamma)
  distances_boundary_test = (np.dot(x_test.astype(float), w)).tolist()
  predictions = np.sign(distances_boundary_test)
  fixed_y_test = []
  fixed_predictions = []

  for x in y_test.astype(float):
    if x == -1:
      fixed_y_test.append(0)
    elif x == 1:
      fixed_y_test.append(1)
    elif x == 0:
      fixed_y_test.append(0)
    else:
      print "Incorrect value in class values"

  for x in predictions:
    if x == -1:
      fixed_predictions.append(0)
    elif x == 1:
      fixed_predictions.append(1)
    elif x == 0:
      fixed_predictions.append(0)
    else:
      print "Incorrect value in class values"

  zafar_opt_fairness_actual, zafar_opt_fairness_predicted, zafar_opt_fairness_protected = fixed_y_test, fixed_predictions, x_control_test[sensitive_attr].astype(int)

  # Params
  apply_fairness_constraints = 0
  apply_accuracy_constraint = 1
  sep_constraint = 1
  gamma = 1000.0

  w = ut.train_model(x_train.astype(float), y_train, x_control_train, loss_function, apply_fairness_constraints, apply_accuracy_constraint, sep_constraint, sensitive_attrs, sensitive_attrs_to_cov_thresh, gamma)
  distances_boundary_test = (np.dot(x_test.astype(float), w)).tolist()
  predictions = np.sign(distances_boundary_test)
  fixed_y_test = []
  fixed_predictions = []

  for x in y_test.astype(float):
    if x == -1:
      fixed_y_test.append(0)
    elif x == 1:
      fixed_y_test.append(1)
    elif x == 0:
      fixed_y_test.append(0)
    else:
      print "Incorrect value in class values"

  for x in predictions:
    if x == -1:
      fixed_predictions.append(0)
    elif x == 1:
      fixed_predictions.append(1)
    elif x == 0:
      fixed_predictions.append(0)
    else:
      print "Incorrect value in class values"

  zafar_nopos_classification_actual, zafar_nopos_classification_predicted, zafar_nopos_classification_protected = fixed_y_test, fixed_predictions, x_control_test[sensitive_attr].astype(int)
     
  #RUN METRICS
  svm_metrics = Metrics(svm_actual, svm_predicted, svm_protected)
  nb_metrics = Metrics(nb_actual, nb_predicted, nb_protected)
  lr_metrics = Metrics(lr_actual, lr_predicted, lr_protected)
  kam1_metrics = Metrics(kam1_actual, kam1_predicted, kam1_protected)
  kam30_metrics = Metrics(kam30_actual, kam30_predicted, kam30_protected)
  c2nb_protected_metrics = Metrics(c2nb_protected_actual, c2nb_protected_predicted, c2nb_protected_protected)
  c2nb_favored_metrics = Metrics(c2nb_favored_actual, c2nb_favored_predicted, c2nb_favored_protected)
  zafar_unconstrained_metrics = Metrics(zafar_unconstrained_actual, zafar_unconstrained_predicted, zafar_unconstrained_protected)   
  zafar_opt_accuracy_metrics = Metrics(zafar_opt_accuracy_actual, zafar_opt_accuracy_predicted, zafar_opt_accuracy_protected)
  zafar_opt_fairness_metrics = Metrics(zafar_opt_fairness_actual, zafar_opt_fairness_predicted, zafar_opt_fairness_protected)
  zafar_nopos_classification_metrics = Metrics(zafar_nopos_classification_actual, zafar_nopos_classification_predicted, zafar_nopos_classification_protected)
   
  print("================================= SVM =================================")
  print_res(svm_metrics)

  print("================================= NB =================================")
  print_res(nb_metrics)

  print("================================= LR =================================")
  print_res(lr_metrics)
  
  print("================================= Kamishima =================================")   
  print("  ETA = 1: ")
  print_res(kam1_metrics)
  print("  ETA = 30: ")
  print_res(kam30_metrics)

  print("================================= Calders Protected =================================")
  print_res(c2nb_protected_metrics)

  print("================================= Calders Favored =================================")
  print_res(c2nb_favored_metrics)
  
  print("================================= Zafar =================================")
  print("  Unconstrained: ")
  print_res(zafar_unconstrained_metrics)
  print("  Optimized for accuracy: ")
  print_res(zafar_opt_accuracy_metrics)
  print("  Optimized for fairness: ")
  print_res(zafar_opt_fairness_metrics)
  print("  No positive classification error: ")
  print_res(zafar_nopos_classification_metrics)
 
if __name__ == '__main__':
  print("###################################### German Data ######################################")
  #run_metrics('german')

  print("###################################### Adult Data #######################################")
  run_metrics('adult')

  print("###################################### Compas Data ######################################")
  #run_metrics('compas')