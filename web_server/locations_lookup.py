# step - 1

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy_operator import DummyOperator

from random import randint
from datetime import datetime

import os
os.environ["HDF5_USE_FILE_LOCKING"]='FALSE'
import sys
sys.path.append('/content/src/')
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import matplotlib.patches as patches
import pandas as pd
from readers.nowcast_reader import read_data
import random

from google.colab import drive
drive.mount('/content/drive')

import sys
module_path = '/content/drive/MyDrive/Big-Data-Systems/neurips-2020-sevir/src'
sys.path.insert(0,module_path)

from display.display import get_cmap

"""## Load pretrained models"""

gan_file = '/content/drive/MyDrive/Big-Data-Systems/neurips-2020-sevir/models/nowcast/gan_generator.h5'
gan_model = tf.keras.models.load_model(gan_file,compile=False,custom_objects={"tf": tf})

"""## Load sample test data

To download sample test data, go to https://www.dropbox.com/s/27pqogywg75as5f/nowcast_testing.h5?dl=0
 and save file to `data/sample/nowcast_testing.h5`

"""
location = 'Boston'

# Load catalog data for looking up location in the random locations
df_locs = pd.read_csv('/content/drive/MyDrive/Big-Data-Systems/catalog_50_locs.csv')

#searching the city name in city column of the file
df_locs['city'].apply(lambda row: row.astype(str).str.contains(location).any(), axis=1)

# Load a part of the test dataset
x_test,y_test = read_data('/content/drive/MyDrive/Big-Data-Systems/neurips-2020-sevir/data/interim/nowcast_testing1.h5',end=50)

"""## Plot samples for test set"""

## 
# Functions for plotting results
##

def loading_model():
    return randint(1, 10)

def save_image():
    return randint(1, 50)

norm = {'scale':47.54,'shift':33.44}
hmf_colors = np.array( [
    [82,82,82], 
    [252,141,89],
    [255,255,191],
    [145,191,219]
])/255

# Model that implements persistence forecast that just repeasts last frame of input
class persistence:
    def predict(self,x_test):
        return np.tile(x_test[:,:,:,-1:],[1,1,1,12])

def plot_hit_miss_fa(ax,y_true,y_pred,thres):
    mask = np.zeros_like(y_true)
    mask[np.logical_and(y_true>=thres,y_pred>=thres)]=4
    mask[np.logical_and(y_true>=thres,y_pred<thres)]=3
    mask[np.logical_and(y_true<thres,y_pred>=thres)]=2
    mask[np.logical_and(y_true<thres,y_pred<thres)]=1
    cmap=ListedColormap(hmf_colors)
    ax.imshow(mask,cmap=cmap)


def visualize_result(models,x_test,y_test,idx,ax,labels):
    #print(x_test[0])
    fs=12
    cmap_dict = lambda s: {'cmap':get_cmap(s,encoded=True)[0],
                           'norm':get_cmap(s,encoded=True)[1],
                           'vmin':get_cmap(s,encoded=True)[2],
                           'vmax':get_cmap(s,encoded=True)[3]}

    
    pers = persistence().predict(x_test[idx:idx+1])
    pers = pers*norm['scale']+norm['shift']
    x_test = x_test[idx:idx+1]
    y_test = y_test[idx:idx+1]*norm['scale']+norm['shift']
    y_preds=[]
    for i,m in enumerate(models):
        yp = m.predict(x_test)
        if isinstance(yp,(list,)):
            yp=yp[0]
        y_preds.append(yp*norm['scale']+norm['shift'])
    
    k = 0
    for i in range(0,3):
      for j in range(0,4):
        
        ax[i][j].imshow(y_test[0,:,:,k],**cmap_dict('vil'))
        k = k + 1


#function to run every hour

def run_model_hourly():
    idx= random.randrange(10,50)
    fig,ax = plt.subplots(3,4,figsize=(10,7))
    visualize_result([gan_model],x_test,y_test,idx,ax,labels=['cGAN+MAE'])


# step - 2
default_arg_values = {
    'owner' : 'airflow',
    'depends_on_past' : False,
    'start_date' : datetime(2022, 3, 30),
    'retries' : 0
}

# step - 3

with DAG("DAG-3", default_args=default_arg_values, schedule_interval="@hourly", catchup=False) as dag:

# step - 4
   
    visualize_model = PythonOperator(
        task_id = "visualize_model",
        python_callable = run_model_hourly
    )

    load_model = PythonOperator(
        task_id = "loading_model",
        python_callable = loading_model
    )

    save_images = BashOperator(
        task_id = "save_image",
        bash_command = "echo 'save_image'"
    )

    start = DummyOperator(
        task_id='start',
        dag=dag
    )

    end = DummyOperator(
        task_id='end',
        dag=dag
    )


# step - 5

start >> load_model >> visualize_model >> save_images >> end