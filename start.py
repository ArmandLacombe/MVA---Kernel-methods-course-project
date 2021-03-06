# -*- coding: utf-8 -*-
"""start.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ZOCoBX4lXlI_eSjuhQeuvN43kzZXz0ys
"""

import numpy as np
from google.colab import files
from google.colab import drive
import matplotlib.pyplot as plt
import scipy
import pandas as pd
import itertools
import time
from math import factorial
from tqdm import tqdm

drive.mount('/content/drive')

# %cd /content/drive/My Drive/taf/Kernel
# %ls

def reverse_complement(seq):
    seq_rev=seq[::-1]
    Dic_comp={"A":"T","C":"G","T":"A","G":"C"}
    mot=""
    for i in range(len(seq_rev)):
        mot=mot+Dic_comp[seq_rev[i]]
    return mot

def Data_embeddings(data,motif_len=5,non_gap_k=2, test = False):
    Alphabet=["A","T","C","G"]
    all_possible=(len(Alphabet))**(motif_len)

    letter_comb = itertools.product(Alphabet, repeat=motif_len)
    Dic={}
    count=0
    for i in letter_comb:
        mo=''
        for j in i:
            mo=mo+str(j)
        mot_reverse=reverse_complement(mo)
        for gap in itertools.combinations(range(motif_len),motif_len-non_gap_k):
            mot_gap=list(mo)
            mot_reverse_gap=list(mot_reverse)
            for ind in gap:
                mot_gap[ind]='_'
                mot_reverse_gap[len(mot_reverse_gap)-1-ind]='_'
            mot_gap="".join(mot_gap)
            mot_reverse_gap="".join(mot_reverse_gap)
            if not(mot_gap in Dic.keys()) or not(mot_reverse_gap in Dic.keys()):
                Dic[mot_gap]=count
                Dic[mot_reverse_gap]=count
                count=count+1
    compteur=0
    for i in Dic.keys():
        Dic[i]=compteur
        compteur=compteur+1
        
    taille_des_ligne=np.ones(data.shape[0])  
    data_new=np.zeros((data.shape[0],compteur))
    data_indic=np.zeros((data.shape[0],compteur))
    print('dic ok')       
    for i in range(data.shape[0]):
        ligne=data[i]
        taille_des_ligne[i]=factorial(len(ligne))/(factorial(len(ligne)-motif_len)*factorial(motif_len))
        for k in range(len(ligne)-motif_len+1):
            mot=ligne[k:int(k+motif_len)]
            mot_reverse=reverse_complement(mot)
            for gap in itertools.combinations(range(motif_len),motif_len-non_gap_k):
                mot_gap=list(mot)
                mot_reverse_gap=list(mot_reverse)
                for ind in gap:
                    mot_gap[ind]='_'
                    mot_reverse_gap[len(mot_reverse_gap)-1-ind]='_'
                mot_gap="".join(mot_gap)
                mot_reverse_gap="".join(mot_reverse_gap)
                data_new[i,Dic[mot_gap]]=data_new[i,Dic[mot_gap]]+1
                data_indic[i,Dic[mot_gap]]=1
                data_indic[i,Dic[mot_reverse_gap]]=1
                data_new[i,Dic[mot_reverse_gap]]=data_new[i,Dic[mot_reverse_gap]]+1
    for i in range(data_new.shape[0]):
        data_new[i]=data_new[i]/taille_des_ligne[i]
        
    if test == False:
      NB=np.sum(data_indic,axis=0)
      indice_a_pas_sup=np.where(NB!=0)[0]
      data_indic=data_indic[:,indice_a_pas_sup]
      data_new=data_new[:,indice_a_pas_sup]

    return data_new,data_indic

def reverse_complement(seq):
    seq_rev=seq[::-1]
    Dic_comp={"A":"T","C":"G","T":"A","G":"C"}
    mot=""
    for i in range(len(seq_rev)):
        mot=mot+Dic_comp[seq_rev[i]]
    return mot

def Data_embeddings_fortest2(data,motif_len=5,with_reverse=False, test = False):
    Alphabet=["A","T","C","G"]
    all_possible=(len(Alphabet))**(motif_len)
    data_new=np.zeros((data.shape[0],all_possible))
    data_indic=np.zeros((data.shape[0],all_possible))
    letter_comb = itertools.product(Alphabet, repeat=motif_len)
    Dic={}
    count=0
    for i in letter_comb:
        mo=''
        for j in i:
            mo=mo+str(j)
        mot_reverse=reverse_complement(mo)
        Dic[mo]=count
        Dic[mot_reverse]=count
        count=count+1
                
    for i in range(data.shape[0]):
        ligne=data[i]
        for k in range(len(ligne)-motif_len+1):
            mot=ligne[k:int(k+motif_len)]
            data_new[i,Dic[mot]]=data_new[i,Dic[mot]]+1
            data_indic[i,Dic[mot]]=1
            if with_reverse:
                data_indic[i,Dic[reverse_complement(mot)]]=1
                data_new[i,Dic[reverse_complement(mot)]]=data_new[i,Dic[mot]]+1
    
    if test == False:
      NB=np.sum(data_indic,axis=0)
      indice_a_pas_sup=np.where(NB!=0)[0]
      data_indic=data_indic[:,indice_a_pas_sup]
      data_new=data_new[:,indice_a_pas_sup]
      NB=np.sum(data_indic,axis=0)
      IDF=np.log(data_indic.shape[0]*1.0/NB)
      data_indic_IDF=data_indic*IDF
    
    return data_new,data_indic

def get_X_feat(Xtrainvalues, taille_pca = 100, motif_len = 8, non_gap_k = 6, Xtestvalues = [0]):
  #Xvalues is typically X['seq'].values
  
  X_new,X_ind=Data_embeddings(Xtrainvalues,motif_len=motif_len,non_gap_k=non_gap_k, test = True)
  X_newS = scipy.sparse.coo_matrix(X_new)
  u,s,v = scipy.sparse.linalg.svds(X_newS, k = taille_pca)
  X_pca2 = u @ scipy.sparse.diags(s)

  X_feat=(X_pca2-np.mean(X_pca2,axis=0))/np.std(X_pca2,axis=0)
  
  if len(Xtestvalues) > 1:
    X_te_new,X_te_ind = Data_embeddings(Xtestvalues,motif_len=motif_len,non_gap_k=non_gap_k, test = True)
    X_te_newS = scipy.sparse.coo_matrix(X_te_new)
    tmp = X_te_newS @ v.T
    X_feat_test = (tmp-np.mean(tmp,axis=0))/np.std(tmp,axis=0)
    return [X_feat, X_feat_test]
  
  return X_feat

def get_X_feat_fortest2(Xtrainvalues, taille_pca = 100, motif_len = 8, non_gap_k = 6, Xtestvalues = [0]):
  #Xvalues is typically X['seq'].values
  
  X_new,X_ind = Data_embeddings_fortest2(Xtrainvalues,motif_len=motif_len,with_reverse = True, test = True)
  X_newS = scipy.sparse.coo_matrix(X_new)
  u,s,v = scipy.sparse.linalg.svds(X_newS, k = taille_pca)
  X_pca2 = u @ scipy.sparse.diags(s)

  X_feat=(X_pca2-np.mean(X_pca2,axis=0))/np.std(X_pca2,axis=0)
  
  if len(Xtestvalues) > 1:
    X_te_new,X_te_ind = Data_embeddings_fortest2(Xtestvalues,motif_len=motif_len,with_reverse = True, test = True)
    X_te_newS = scipy.sparse.coo_matrix(X_te_new)
    tmp = X_te_newS @ v.T
    X_feat_test = (tmp-np.mean(tmp,axis=0))/np.std(tmp,axis=0)
    return [X_feat, X_feat_test]
  
  return X_feat

def get_K(X_feat, gamma = .005):

  mat_no = (X_feat ** 2).sum(axis=1)
  mat_sp = -2 * np.dot(X_feat, X_feat.T)
  mat_sp += mat_no.reshape(-1, 1)
  mat_sp += mat_no
  K = np.exp(- gamma * mat_sp)

  nu = np.linalg.norm(K, ord=2)
  
  return [K, nu]

def get_K_rbf(X_feat, gamma = .005):

  mat_no = (X_feat ** 2).sum(axis=1)
  mat_sp = -2 * np.dot(X_feat, X_feat.T)
  mat_sp += mat_no.reshape(-1, 1)
  mat_sp += mat_no
  K = np.exp(- gamma * mat_sp)

  nu = np.linalg.norm(K, ord=2)
  
  return K

def get_K_lap(X_feat, gamma = .005):
  
  n = X_feat.shape[0]
  K2 = np.zeros((n, n))
  
  for i in range(n-1):
    for j in range(i,n):
      K2[i][j] = scipy.spatial.distance.cityblock(X_feat[i],X_feat[j])
  
  K2 = K2 + K2.T
  K2 = np.exp(- gamma * K2)
  
  nu = np.linalg.norm(K2, ord=2)
  
  return K2

def get_cv_folders(X_feat, Yvalues, K, k_fold = 5, seed = 1):
  #Yvalues is typically Y['Bound'].values

  n = X_feat.shape[0]
  np.random.seed(seed)
  perm = np.random.permutation(n)
  nsplit = int(n/k_fold)

  x_train_set, x_val_set, y_train_set, y_val_set, K_set, K_decoder_set = [], [], [], [], [], []

  for split in range(k_fold):
    x_train_set.append(np.concatenate((X_feat[perm][:split*nsplit],X_feat[perm][(split+1)*nsplit:]), axis=0))
    x_val_set.append(X_feat[perm][split*nsplit:(split+1)*nsplit])
    y_train_set.append(np.concatenate((Yvalues[perm][:split*nsplit],Y['Bound'].values[perm][(split+1)*nsplit:]), axis=0))
    y_val_set.append(Yvalues[perm][split*nsplit:(split+1)*nsplit])
    indices = np.concatenate((np.arange(0,split*nsplit).reshape(1,-1),np.arange((split+1)*nsplit,n).reshape(1,-1)), axis = 1).reshape(-1)
    K_set.append((((K[perm].T)[perm]).T)[np.ix_(indices,indices)])
    K_decoder_set.append((((K[perm].T)[perm]).T)[np.ix_(np.arange(split*nsplit, (split+1)*nsplit),indices)])
    
  return [x_train_set, x_val_set, y_train_set, y_val_set, K_set, K_decoder_set]

def proj(alpha,y,C):
  for i in range(len(alpha)):
    if alpha[i] * y[i] < 0 :
      alpha[i] = 0
    elif alpha[i] * y[i] > C :
      alpha[i] = C/y[i]
  return alpha

def proj_2(alpha,y):
  for i in range(len(alpha)):
    if alpha[i] * y[i] < 0 :
      alpha[i] = 0
  return alpha

def svm_accuracy(xt, y_val, K_decoder):
  y = 2*(y_val - .5)
  preds = K_decoder @ xt
  goods = np.sum((preds * y > 0).astype(int))
  return goods / len(y_val), preds

def cvSVM(x_train_set, x_val_set, y_train_set, y_val_set, K_set, K_decoder_set, gammaFW, C = 1, eta = 1, verbose = 0, k_fold  = 5, iterations = 1000):
  #gammaFW should be 1/nu, nu = get_K(...)[1]
  
  tic = time.clock()
  
  accuracies = [[] for _ in range(k_fold)]
  objectives = [[] for _ in range(k_fold)]
  preds = []

  for split in range(k_fold):

    x_train = x_train_set[split][:]
    x_val   = x_val_set[split][:]
    y_train = y_train_set[split][:]
    y_val   = y_val_set[split][:]
    K_train = K_set[split][:]
    K_decoder = K_decoder_set[split][:]

    xt = np.zeros(x_train.shape[0])
    y = 2*(y_train-.5)

    for iteration in range(iterations):
      yt = xt - 2 * gammaFW * (K_train @ xt - y)
      xt = xt + eta * (proj(yt, y,C) - xt)
      objectives[split].append(xt.T @ K_train @ xt - 2 * xt.T @ y)

      if iteration % 10 == 0:
        accuracies[split].append(svm_accuracy(xt, y_val, K_decoder)[0])

    preds.append(svm_accuracy(xt, y_val, K_decoder)[1])

  toc = time.clock()
  
  if verbose > 0:
    print('time :', toc-tic)
    print(np.array(accuracies)[:,-1], np.mean(np.array(accuracies)[:,-1]))
  if verbose > 1:
    plt.figure(figsize=(20,5))
    plt.subplot(1, 2, 1)
    for i in range(len(objectives)):
      plt.plot(np.array(objectives[i]))
    plt.title('objective evolution')
    plt.xlabel('iteration')
    plt.ylabel('objective')
    plt.subplot(1, 2, 2)
    for i in range(len(accuracies)):
      plt.plot(np.arange(0,iterations,10),np.array(accuracies[i]))
    plt.plot(np.arange(0,iterations,10),np.mean(np.array(accuracies),axis=0), color = 'k')
    plt.title('accuracies evolution')
    plt.xlabel('iteration')
    plt.ylabel('accuracy')
    plt.show()
    

  return [accuracies, preds, objectives]

def predictSVM(x_train, x_test, y_train, K_train, K_decoder, gammaFW, C = 1, eta = 1, iterations = 1000, verbose = False):
  #gammaFW should be 1/nu, nu = get_K(...)[1]
    
  xt = np.zeros(x_train.shape[0])
  y = 2*(y_train-.5)
  objective = []

  for iteration in range(iterations):
    yt = xt - 2 * gammaFW * (K_train @ xt - y)
    xt = xt + eta * (proj(yt, y, C) - xt)
    objective.append(xt.T @ K_train @ xt - 2 * xt.T @ y)
    
  predictions = K_decoder @ xt
  
  if verbose == True:
    plt.plot(objective)
    plt.show()
    
  return predictions

def cvSVM2(x_train_set, x_val_set, y_train_set, y_val_set, K_set, K_decoder_set, gammaFW, eta = 1, verbose = 0, k_fold  = 5, iterations = 1000):
  #gammaFW should be 1/nu, nu = get_K(...)[1]
  
  tic = time.clock()
  accuracies = [[] for _ in range(k_fold)]
  objectives = [[] for _ in range(k_fold)]
  preds2 = []

  for split in range(k_fold):

    x_train = x_train_set[split][:]
    x_val   = x_val_set[split][:]
    y_train = y_train_set[split][:]
    y_val   = y_val_set[split][:]
    K_train = K_set[split][:]
    K_decoder = K_decoder_set[split][:]

    xt = np.zeros(x_train.shape[0])
    y = 2*(y_train-.5)

    for iteration in range(iterations):
      yt = xt - 2 * gammaFW * (K_train @ xt - y)
      xt = xt + eta * (proj_2(yt, y) - xt)
      objectives[split].append(xt.T @ K_train @ xt - 2 * xt.T @ y)

      if iteration % 10 == 0:
        accuracies[split].append(svm_accuracy(xt, y_val, K_decoder)[0])

    preds2.append(svm_accuracy(xt, y_val, K_decoder)[1])

  toc = time.clock()
  
  if verbose > 0:
    print('time :', toc-tic)
    print(np.array(accuracies)[:,-1], np.mean(np.array(accuracies)[:,-1]))
  if verbose > 1:
    plt.figure(figsize=(20,5))
    plt.subplot(1, 2, 1)
    for i in range(len(objectives)):
      plt.plot(np.array(objectives[i]))
    plt.title('objective evolution')
    plt.xlabel('iteration')
    plt.ylabel('objective')
    plt.subplot(1, 2, 2)
    for i in range(len(accuracies)):
      plt.plot(np.arange(0,iterations,10),np.array(accuracies[i]))
    plt.plot(np.arange(0,iterations,10),np.mean(np.array(accuracies),axis=0), color = 'k')
    plt.title('accuracies evolution')
    plt.xlabel('iteration')
    plt.ylabel('accuracy')
    plt.show()
    

  return [accuracies, preds2, objectives]

def predictSVM2(x_train, x_test, y_train, K_train, K_decoder, gammaFW, eta = 1, iterations = 1000, verbose = False):
  #gammaFW should be 1/nu, nu = get_K(...)[1]
    
  xt = np.zeros(x_train.shape[0])
  y = 2*(y_train-.5)
  objective = []

  for iteration in range(iterations):
    yt = xt - 2 * gammaFW * (K_train @ xt - y)
    xt = xt + eta * (proj_2(yt, y) - xt)
    objective.append(xt.T @ K_train @ xt - 2 * xt.T @ y)
    
  predictions = K_decoder @ xt
  
  if verbose == True:
    plt.plot(objective)
    plt.show()
    
  return predictions

def cvLogisticRegression(x_train_set, x_val_set, y_train_set, y_val_set, K_set, K_decoder_set, eta = .001, verbose = 2, k_fold  = 10, iterations = 100):

  tic = time.clock()
  accuracies = [[] for _ in range(k_fold)]
  objectives = [[] for _ in range(k_fold)]
  predicts = []

  for split in range(k_fold):

    x_train = np.concatenate((x_train_set[split][:] ,np.ones(len(x_train_set[split])).reshape(-1,1)),axis=1)
    x_val   = np.concatenate((x_val_set[split][:]   ,np.ones(len(x_val_set[split])).reshape(-1,1)),axis=1)
    y_train = y_train_set[split][:]
    y_val   = y_val_set[split][:]
    
    theta = np.zeros(x_train.shape[1])

    for _ in range(iterations):
      preds = 1/(1 + np.exp(- x_train @ theta))
      theta = theta - eta * x_train.T @ (preds - y_train)
      preds_val = 1/(1 + np.exp(- x_val @ theta))
      accuracies[split].append(np.sum(((preds_val-.5)*(y_val-.5) > 0).astype(int))/len(y_val))
      objectives[split].append(y_train @ np.log(preds) - (1-y_train) @ np.log(1-preds))
      
    predicts.append(preds_val - .5)

  toc = time.clock()
  
  if verbose > 0:
    print('time :', toc-tic)
    print(np.array(accuracies)[:,-1], np.mean(np.array(accuracies)[:,-1]))
  if verbose > 1:  
    plt.figure(figsize=(20,5))
    plt.subplot(1, 2, 1)
    for i in range(len(objectives)):
      plt.plot(np.array(objectives[i]))
    plt.title('objective evolution')
    plt.xlabel('iteration')
    plt.ylabel('objective')
    plt.subplot(1, 2, 2)
    for i in range(len(accuracies)):
      plt.plot(np.array(accuracies[i]))
    plt.plot(np.mean(np.array(accuracies),axis=0), color = 'k')
    plt.title('accuracies evolution')
    plt.xlabel('iteration')
    plt.ylabel('accuracy')
    plt.show()
    
    return [accuracies, predicts, objectives]

def predictLogisticRegression(x_train, x_test, y_train, eta = .001, iterations = 100, verbose = False):
  
  objective = []
  
  x_train = np.concatenate((x_train ,np.ones(len(x_train)).reshape(-1,1)),axis=1)
  x_test = np.concatenate((x_test ,np.ones(len(x_test)).reshape(-1,1)),axis=1)
  
  theta = np.zeros(x_train.shape[1])

  for _ in range(iterations):
    preds = 1/(1 + np.exp(- x_train @ theta))
    theta = theta - eta * x_train.T @ (preds - y_train)
    objective.append(y_train @ np.log(preds) - (1-y_train) @ np.log(1-preds))
    
  predictions = 1/(1 + np.exp(- x_test @ theta))
  
  if verbose == True:
    plt.plot(objective)
    plt.show()

  return predictions - .5

def quickcheck(preds, target):
  return np.sum((preds*(target-.5) > 0).astype(int))/len(preds)

tic = time.clock()
print('loading data...')
X=pd.read_csv("data/Xtr0.csv")
Y=pd.read_csv("data/Ytr0.csv")

print('designing features...')
X_feat = get_X_feat(X['seq'].values, taille_pca = 100, motif_len = 8, non_gap_k = 6)

print('computing the kernel matrix...')
[K, nu] = get_K(X_feat, gamma = .005)
print('done. time elapsed : ',time.clock()-tic)

print('generating cv folders...')
[x_train_set, x_val_set, y_train_set, y_val_set, K_set, K_decoder_set] = get_cv_folders(X_feat, Y['Bound'].values, K, k_fold = 10, seed = 10)

out = cvSVM(x_train_set, x_val_set, y_train_set, y_val_set, K_set, K_decoder_set, 1/nu, C=1, eta = 1, verbose = 2, k_fold  = 10, iterations = 400)
out2 = cvSVM2(x_train_set, x_val_set, y_train_set, y_val_set, K_set, K_decoder_set, 1/nu, eta = 1, verbose = 2, k_fold  = 10, iterations = 400)
out3 = cvLogisticRegression(x_train_set, x_val_set, y_train_set, y_val_set, K_set, K_decoder_set, eta = .001, verbose = 2, k_fold  = 10, iterations = 100)

maxi = 0
wgh_maxi = 0
for i in range(1,30):
  for j in range(30):
    for k in range(30):
      wgh = np.array([i,j,k])
      tmp = np.mean(np.array([quickcheck((out[1][i]*wgh[0] + out2[1][i]*wgh[1] + out3[1][i]*wgh[2])/np.sum(wgh), y_val_set[i]) for i in range(len(out[1]))]))
      if tmp > maxi:
        maxi = tmp
        wgh_maxi = wgh
        print(wgh, maxi)

tic = time.clock()
print('loading data...')
Xtr=pd.read_csv("data/Xtr0.csv")
Ytr=pd.read_csv("data/Ytr0.csv")
Xte=pd.read_csv("data/Xte0.csv")

print('designing features...')
[X_train_feat, X_test_feat] = get_X_feat_fortest2(Xtr['seq'].values, taille_pca = 200, motif_len = 8, non_gap_k = 7, Xtestvalues = Xte['seq'].values)

print('computing the kernel matrix...')
K1 = get_K_rbf(np.concatenate((X_train_feat, X_test_feat), axis = 0), gamma = .005)
K2 = get_K_lap(np.concatenate((X_train_feat, X_test_feat), axis = 0), gamma = .005)
K = (K1 + K2)/2
nu = np.linalg.norm(K, ord=2)

K_train = K[:2000,:2000]
K_decoder = K[2000:,:2000]

print('predicting...')
predictions = predictSVM(X_train_feat, X_test_feat, Ytr['Bound'].values, K_train, K_decoder, 1/nu, eta = 1, C = 1)
predictions2=predictSVM2(X_train_feat, X_test_feat, Ytr['Bound'].values, K_train, K_decoder, 1/nu, eta = 1)
predictions3=predictLogisticRegression(X_train_feat, X_test_feat, Ytr['Bound'].values, eta = .001, iterations = 100)
print('done. time elapsed : ',time.clock()-tic)

prediction_globale = (wgh_maxi[0] * predictions + wgh_maxi[1] * predictions2 + wgh_maxi[2] * predictions3 > 0).astype(int)

outfile_test0 = np.concatenate((Xte['Id'].values.reshape(-1,1), prediction_globale.reshape(-1,1)), axis = 1)
np.savetxt("preds_test0_start.csv", outfile_test0, delimiter=",")

tic = time.clock()
print('loading data...')
X=pd.read_csv("data/Xtr1.csv")
Y=pd.read_csv("data/Ytr1.csv")

print('designing features...')
X_feat = get_X_feat(X['seq'].values, taille_pca = 200, motif_len = 8, non_gap_k = 7)

print('computing the kernel matrix...')
[K, nu] = get_K(X_feat, gamma = .005)
print('done. time elapsed : ',time.clock()-tic)

print('generating cv folders...')
[x_train_set, x_val_set, y_train_set, y_val_set, K_set, K_decoder_set] = get_cv_folders(X_feat, Y['Bound'].values, K, k_fold = 10, seed = 10)

out = cvSVM(x_train_set, x_val_set, y_train_set, y_val_set, K_set, K_decoder_set, 1/nu, C=1, eta = 1, verbose = 2, k_fold  = 10, iterations = 400)
out2 = cvSVM2(x_train_set, x_val_set, y_train_set, y_val_set, K_set, K_decoder_set, 1/nu, eta = 1, verbose = 2, k_fold  = 10, iterations = 400)
out3 = cvLogisticRegression(x_train_set, x_val_set, y_train_set, y_val_set, K_set, K_decoder_set, eta = .001, verbose = 2, k_fold  = 10, iterations = 100)

maxi = 0
wgh_maxi = 0
for i in range(1,30):
  for j in range(30):
    for k in range(30):
      wgh = np.array([i,j,k])
      tmp = np.mean(np.array([quickcheck((out[1][i]*wgh[0] + out2[1][i]*wgh[1] + out3[1][i]*wgh[2])/np.sum(wgh), y_val_set[i]) for i in range(len(out[1]))]))
      if tmp > maxi:
        maxi = tmp
        wgh_maxi = wgh
        print(wgh, maxi)

tic = time.clock()
print('loading data...')
Xtr=pd.read_csv("data/Xtr1.csv")
Ytr=pd.read_csv("data/Ytr1.csv")
Xte=pd.read_csv("data/Xte1.csv")

print('designing features...')
[X_train_feat, X_test_feat] = get_X_feat_fortest2(Xtr['seq'].values, taille_pca = 200, motif_len = 8, non_gap_k = 7, Xtestvalues = Xte['seq'].values)

print('computing the kernel matrix...')
K1 = get_K_rbf(np.concatenate((X_train_feat, X_test_feat), axis = 0), gamma = .005)
K2 = get_K_lap(np.concatenate((X_train_feat, X_test_feat), axis = 0), gamma = .005)
K = (K1 + K2)/2
nu = np.linalg.norm(K, ord=2)

K_train = K[:2000,:2000]
K_decoder = K[2000:,:2000]

print('predicting...')
predictions = predictSVM(X_train_feat, X_test_feat, Ytr['Bound'].values, K_train, K_decoder, 1/nu, eta = 1, C = 1)
predictions2=predictSVM2(X_train_feat, X_test_feat, Ytr['Bound'].values, K_train, K_decoder, 1/nu, eta = 1)
predictions3=predictLogisticRegression(X_train_feat, X_test_feat, Ytr['Bound'].values, eta = .001, iterations = 100)
print('done. time elapsed : ',time.clock()-tic)

prediction_globale = (wgh_maxi[0] * predictions + wgh_maxi[1] * predictions2 + wgh_maxi[2] * predictions3 > 0).astype(int)

outfile_test1 = np.concatenate((Xte['Id'].values.reshape(-1,1), prediction_globale.reshape(-1,1)), axis = 1)
np.savetxt("preds_test1_start.csv", outfile_test1, delimiter=",")

tic = time.clock()
print('loading data...')
X=pd.read_csv("data/Xtr2.csv")
Y=pd.read_csv("data/Ytr2.csv")

print('designing features...')
X_feat = get_X_feat_fortest2(X['seq'].values, taille_pca = 200, motif_len = 8)

print('computing the kernel matrix...')
[K, nu] = get_K(X_feat, gamma = .005)
print('done. time elapsed : ',time.clock()-tic)

print('generating cv folders...')
[x_train_set, x_val_set, y_train_set, y_val_set, K_set, K_decoder_set] = get_cv_folders(X_feat, Y['Bound'].values, K, k_fold = 10, seed = 10)

out = cvSVM(x_train_set, x_val_set, y_train_set, y_val_set, K_set, K_decoder_set, 1/nu, C=.5, eta = 1, verbose = 2, k_fold  = 10, iterations = 400)
out2 = cvSVM2(x_train_set, x_val_set, y_train_set, y_val_set, K_set, K_decoder_set, 1/nu, eta = 1, verbose = 2, k_fold  = 10, iterations = 400)
out3 = cvLogisticRegression(x_train_set, x_val_set, y_train_set, y_val_set, K_set, K_decoder_set, eta = .001, verbose = 2, k_fold  = 10, iterations = 100)

maxi = 0
wgh_maxi = 0
for i in range(1,30):
  for j in range(30):
    for k in range(30):
      wgh = np.array([i,j,k])
      tmp = np.mean(np.array([quickcheck((out[1][i]*wgh[0] + out2[1][i]*wgh[1] + out3[1][i]*wgh[2])/np.sum(wgh), y_val_set[i]) for i in range(len(out[1]))]))
      if tmp > maxi:
        maxi = tmp
        wgh_maxi = wgh
        print(wgh, maxi)

tic = time.clock()
print('loading data...')
Xtr=pd.read_csv("data/Xtr2.csv")
Ytr=pd.read_csv("data/Ytr2.csv")
Xte=pd.read_csv("data/Xte2.csv")

print('designing features...')
[X_train_feat, X_test_feat] = get_X_feat_fortest2(Xtr['seq'].values, taille_pca = 200, motif_len = 8, Xtestvalues = Xte['seq'].values)

print('computing the kernel matrix...')
K1 = get_K_rbf(np.concatenate((X_train_feat, X_test_feat), axis = 0), gamma = .005)
K2 = get_K_lap(np.concatenate((X_train_feat, X_test_feat), axis = 0), gamma = .005)
K = (K1 + K2)/2
nu = np.linalg.norm(K, ord=2)

K_train = K[:2000,:2000]
K_decoder = K[2000:,:2000]

print('predicting...')
predictions = predictSVM(X_train_feat, X_test_feat, Ytr['Bound'].values, K_train, K_decoder, 1/nu, eta = 1, C = .5)
predictions2=predictSVM2(X_train_feat, X_test_feat, Ytr['Bound'].values, K_train, K_decoder, 1/nu, eta = 1)
predictions3=predictLogisticRegression(X_train_feat, X_test_feat, Ytr['Bound'].values, eta = .001, iterations = 100)
print('done. time elapsed : ',time.clock()-tic)

prediction_globale = (wgh_maxi[0] * predictions + wgh_maxi[1] * predictions2 + wgh_maxi[2] * predictions3 > 0).astype(int)

outfile_test2 = np.concatenate((Xte['Id'].values.reshape(-1,1), prediction_globale.reshape(-1,1)), axis = 1)
np.savetxt("preds_test2_start.csv", outfile_test2, delimiter=",")

file0 = np.loadtxt("preds_test0_start.csv", delimiter=",")
file1 = np.loadtxt("preds_test1_start.csv", delimiter=",")
file2 = np.loadtxt("preds_test2_start.csv", delimiter=",")

fileout = np.concatenate((file0,file1,file2), axis = 0).astype(int)

import pandas as pd

a = fileout[:,0]
b = fileout[:,1]

df = pd.DataFrame({"Id" : a, "Bound" : b})
df.to_csv("Yte.csv", index=False)