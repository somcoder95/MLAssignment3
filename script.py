import numpy as np
from scipy.io import loadmat
from scipy.optimize import minimize
from sklearn.datasets import fetch_mldata
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix


def preprocess():
    """ 
     Input:
     Although this function doesn't have any input, you are required to load
     the MNIST data set from file 'mnist_all.mat'.

     Output:
     train_data: matrix of training set. Each row of train_data contains 
       feature vector of a image
     train_label: vector of label corresponding to each image in the training
       set
     validation_data: matrix of training set. Each row of validation_data 
       contains feature vector of a image
     validation_label: vector of label corresponding to each image in the 
       training set
     test_data: matrix of training set. Each row of test_data contains 
       feature vector of a image
     test_label: vector of label corresponding to each image in the testing
       set
    """

    mat = loadmat('mnist_all.mat')  # loads the MAT object as a Dictionary

    n_feature = mat.get("train1").shape[1]
    n_sample = 0
    for i in range(10):
        n_sample = n_sample + mat.get("train" + str(i)).shape[0]
    n_validation = 1000
    n_train = n_sample - 10 * n_validation

    # Construct validation data
    validation_data = np.zeros((10 * n_validation, n_feature))
    for i in range(10):
        validation_data[i * n_validation:(i + 1) * n_validation, :] = mat.get("train" + str(i))[0:n_validation, :]

    # Construct validation label
    validation_label = np.ones((10 * n_validation, 1))
    for i in range(10):
        validation_label[i * n_validation:(i + 1) * n_validation, :] = i * np.ones((n_validation, 1))

    # Construct training data and label
    train_data = np.zeros((n_train, n_feature))
    train_label = np.zeros((n_train, 1))
    temp = 0
    for i in range(10):
        size_i = mat.get("train" + str(i)).shape[0]
        train_data[temp:temp + size_i - n_validation, :] = mat.get("train" + str(i))[n_validation:size_i, :]
        train_label[temp:temp + size_i - n_validation, :] = i * np.ones((size_i - n_validation, 1))
        temp = temp + size_i - n_validation

    # Construct test data and label
    n_test = 0
    for i in range(10):
        n_test = n_test + mat.get("test" + str(i)).shape[0]
    test_data = np.zeros((n_test, n_feature))
    test_label = np.zeros((n_test, 1))
    temp = 0
    for i in range(10):
        size_i = mat.get("test" + str(i)).shape[0]
        test_data[temp:temp + size_i, :] = mat.get("test" + str(i))
        test_label[temp:temp + size_i, :] = i * np.ones((size_i, 1))
        temp = temp + size_i

    # Delete features which don't provide any useful information for classifiers
    sigma = np.std(train_data, axis=0)
    index = np.array([])
    for i in range(n_feature):
        if (sigma[i] > 0.001):
            index = np.append(index, [i])
    train_data = train_data[:, index.astype(int)]
    validation_data = validation_data[:, index.astype(int)]
    test_data = test_data[:, index.astype(int)]

    # Scale data to 0 and 1
    train_data /= 255.0
    validation_data /= 255.0
    test_data /= 255.0

    return train_data, train_label, validation_data, validation_label, test_data, test_label


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def blrObjFunction(initialWeights, *args):
    """
    blrObjFunction computes 2-class Logistic Regression error function and
    its gradient.

    Input:
        initialWeights: the weight vector (w_k) of size (D + 1) x 1 
        train_data: the data matrix of size N x D
        labeli: the label vector (y_k) of size N x 1 where each entry can be either 0 or 1 representing the label of corresponding feature vector

    Output: 
        error: the scalar value of error function of 2-class logistic regression
        error_grad: the vector of size (D+1) x 1 representing the gradient of
                    error function
    """
    train_data, labeli = args
    N=len(train_data)
    b=1/N
    n_data = train_data.shape[0]
    n_features = train_data.shape[1]
    error = 0
    error_grad = np.zeros((n_features + 1, 1))
    initialWeights = initialWeights.reshape((n_feature+1,1)) 
    #Adding bias at beginning
    a=np.ones((train_data.shape[0],1))
    train_data=np.concatenate((a,train_data), axis = 1)
   
    error=labeli*np.log(sigmoid(np.dot(train_data,initialWeights)))+(1-labeli)*np.log(1-sigmoid(np.dot(train_data,initialWeights)))
    error=np.sum(error)
    error=b*error
    error=-(error)
    error_grad = (sigmoid(np.dot(train_data,initialWeights)) - labeli) * train_data
    error_grad = np.sum(error_grad, 0)
    error_grad=b*error_grad
    


    
    return error, error_grad


def blrPredict(W, data):
    """
     blrObjFunction predicts the label of data given the data and parameter W 
     of Logistic Regression
     
     Input:
         W: the matrix of weight of size (D + 1) x 10. Each column is the weight 
         vector of a Logistic Regression classifier.
         X: the data matrix of size N x D
         
     Output: 
         label: vector of size N x 1 representing the predicted label of 
         corresponding feature vector given in data matrix

    """
    label = np.zeros((data.shape[0], 1))

   
    a=np.ones((data.shape[0],1))
    data=np.concatenate((a,data), axis = 1)
    label = sigmoid(np.dot(data, W)) 
    label = np.argmax(label, axis=1)    # get maximum for each class
    label = label.reshape((data.shape[0],1))

    return label
def mlrObjFunction(params, *args):
    """
    mlrObjFunction computes multi-class Logistic Regression error function and
    its gradient.

    Input:
        initialWeights_b: the weight vector of size (D + 1) x 10
        train_data: the data matrix of size N x D
        labeli: the label vector of size N x 1 where each entry can be either 0 or 1
                representing the label of corresponding feature vector

    Output:
        error: the scalar value of error function of multi-class logistic regression
        error_grad: the vector of size (D+1) x 10 representing the gradient of
                    error function
    """
    train_data, labeli = args
    n_data = train_data.shape[0]
    n_feature = train_data.shape[1]
    
    error = 0
    error_grad = np.zeros((n_feature + 1, n_class))
    W=params.reshape((n_feature+1,n_class)) 
    #Adding bias at beginning
    a=np.ones((train_data.shape[0],1))
    train_data=np.concatenate((a,train_data), axis = 1)
    O=sigmoid(np.dot(train_data,W))
    
   
    error=labeli*np.log(sigmoid(np.dot(train_data,W)))+(1-labeli)*np.log(1-sigmoid(np.dot(train_data,W)))
    error=np.sum(error)
    
    error=-(error)
    #print(error)
    
    error_grad=np.dot((O-labeli).T,train_data)
    error_grad=error_grad.T
    error_grad=error_grad.flatten()
    #print(error_grad.shape)
    
    
    

    return error, error_grad
def mlrPredict(W, data):
    """
     mlrObjFunction predicts the label of data given the data and parameter W
     of Logistic Regression

     Input:
         W: the matrix of weight of size (D + 1) x 10. Each column is the weight
         vector of a Logistic Regression classifier.
         X: the data matrix of size N x D

     Output:
         label: vector of size N x 1 representing the predicted label of
         corresponding feature vector given in data matrix

    """
    label = np.zeros((data.shape[0], 1))

   
    a=np.ones((data.shape[0],1))
    data=np.concatenate((a,data), axis = 1)
    label = sigmoid(np.dot(data, W)) 
    label = np.argmax(label, axis=1)    # get maximum for each class
    label = label.reshape((data.shape[0],1))
    return label


"""
Script for Logistic Regression
"""
train_data, train_label, validation_data, validation_label, test_data, test_label = preprocess()

# number of classes
n_class = 10

# number of training samples
n_train = train_data.shape[0]

# number of features
n_feature = train_data.shape[1]

Y = np.zeros((n_train, n_class))
for i in range(n_class):
    Y[:, i] = (train_label == i).astype(int).ravel()

# Logistic Regression with Gradient Descent
W = np.zeros((n_feature + 1, n_class))
initialWeights = np.zeros((n_feature + 1, 1))
opts = {'maxiter': 100}
for i in range(n_class):
    labeli = Y[:, i].reshape(n_train, 1)
    args = (train_data, labeli)
    nn_params = minimize(blrObjFunction, initialWeights, jac=True, args=args, method='CG', options=opts)
    W[:, i] = nn_params.x.reshape((n_feature + 1,))

# Find the accuracy on Training Dataset
predicted_label = blrPredict(W, train_data)
print('\n Training set Accuracy:' + str(100 * np.mean((predicted_label == train_label).astype(float))) + '%')
a=confusion_matrix(train_label,predicted_label)

# Find the accuracy on Validation Dataset
predicted_label = blrPredict(W, validation_data)
print('\n Validation set Accuracy:' + str(100 * np.mean((predicted_label == validation_label).astype(float))) + '%')

# Find the accuracy on Testing Dataset
predicted_label = blrPredict(W, test_data)
print('\n Testing set Accuracy:' + str(100 * np.mean((predicted_label == test_label).astype(float))) + '%')
b=confusion_matrix(test_label,predicted_label)

print('\n Confusion Matrix for blr Training Set\n')
print(a)
print('\n Confusion Matrix for blr Testing Set\n')
print(b)


"""
Script for Support Vector Machine
"""

print('\n\n--------------SVM-------------------\n\n')

#SVM with Linear Kernel
clf = SVC(kernel='linear')
train_label=train_label.ravel()
clf.fit(train_data,train_label)
ypred=clf.predict(train_data)
print("Training set accuracy for linear kernel:",(accuracy_score(train_label,ypred)))
ypred=clf.predict(validation_data)
print("Validation set accuracy for linear kernel:",(accuracy_score(validation_label,ypred)))
ypred=clf.predict(test_data)
print("Test set accuracy for linear kernel:",(accuracy_score(test_label,ypred)))
#SVM with RBF kernel and gamma=1
clf = SVC(kernel='rbf',gamma=1)
train_label=train_label.ravel()
clf.fit(train_data,train_label)
ypred=clf.predict(train_data)
print("Training set accuracy for SVM with RBF kernel and gamma=1:",(accuracy_score(train_label,ypred)))
ypred=clf.predict(validation_data)
print("Validation set accuracy for SVM with RBF kernel and gamma=1:",(accuracy_score(validation_label,ypred)))
ypred=clf.predict(test_data)
print("Test set accuracy for SVM with RBF kernel and gamma=1:",(accuracy_score(test_label,ypred)))
#SVM with RBF and default parameters
clf = SVC(kernel='rbf')
train_label=train_label.ravel()
clf.fit(train_data,train_label)
ypred=clf.predict(train_data)
print("Training set accuracy for SVM with RBF kernel :",(accuracy_score(train_label,ypred)))
ypred=clf.predict(validation_data)
print("Validation set accuracy for SVM with RBF kernel:",(accuracy_score(validation_label,ypred)))
ypred=clf.predict(test_data)
print("Test set accuracy for SVM with RBF kernel:",(accuracy_score(test_label,ypred)))

#SVM with RBF and different values of C
clf = SVC(kernel='rbf',C=1.0)
train_label=train_label.ravel()
clf.fit(train_data,train_label)
ypred=clf.predict(train_data)
print("Training set accuracy for SVM with RBF kernel and C=1 :",(accuracy_score(train_label,ypred)))
ypred=clf.predict(validation_data)
print("Validation set accuracy for SVM with RBF kernel and C=1:",(accuracy_score(validation_label,ypred)))
ypred=clf.predict(test_data)
print("Test set accuracy for SVM with RBF kernel and C=1:",(accuracy_score(test_label,ypred)))
#The accuracies for different values of C upto 100 have been reported in the report
"""
Script for Extra Credit Part
"""
# FOR EXTRA CREDIT ONLY
W_b = np.zeros((n_feature + 1, n_class))
initialWeights_b = np.zeros((n_feature + 1, n_class))
opts_b = {'maxiter': 100}

args_b = (train_data, Y)
nn_params = minimize(mlrObjFunction, initialWeights_b, jac=True, args=args_b, method='CG', options=opts_b)
W_b = nn_params.x.reshape((n_feature + 1, n_class))


# Find the accuracy on Training Dataset
predicted_label_b = mlrPredict(W_b, train_data)
print('\n Training set Accuracy:' + str(100 * np.mean((predicted_label_b == train_label.reshape(train_label.shape[0],1)).astype(float))) + '%')
a=confusion_matrix(train_label,predicted_label_b)
# Find the accuracy on Validation Dataset
predicted_label_b = mlrPredict(W_b, validation_data)
print('\n Validation set Accuracy:' + str(100 * np.mean((predicted_label_b == validation_label).astype(float))) + '%')

# Find the accuracy on Testing Dataset
predicted_label_b = mlrPredict(W_b, test_data)
print('\n Testing set Accuracy:' + str(100 * np.mean((predicted_label_b == test_label).astype(float))) + '%')
b=confusion_matrix(test_label,predicted_label_b)

print('\n Confusion Matrix for blr Training Set\n')
print(a)
print('\n Confusion Matrix for blr Testing Set\n')
print(b)







