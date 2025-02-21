# -*- coding: utf-8 -*-
"""Flowers_Recognition.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/13Cc0gdxLZULmI4OaSNlz2zta9kmnlOMO
"""

!ls

import tensorflow as tf
device_name = tf.test.gpu_device_name()
if device_name != '/device:GPU:0':
  raise SystemError('GPU device not found')
print('Found GPU at: {}'.format(device_name))

!wget -qq https://www.dropbox.com/s/vj61417lofjebju/utils.zip
!wget -qq https://www.dropbox.com/s/pcv5wpk0ybsohib/flowers.zip


!unzip -qq flowers.zip
!rm flowers.zip

!unzip -qq utils.zip
!rm utils.zip


!ls

!ls flowers

!ls flowers/rose

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
import matplotlib.pyplot as plt


from sutils import *
import os, json
from glob import glob
import numpy as np

import keras

from tensorflow.keras import optimizers

from tensorflow.keras.applications import InceptionV3
from tensorflow.keras.applications.vgg16 import VGG16


from tensorflow.python.keras.preprocessing import image
from tensorflow.python.keras.preprocessing.image import ImageDataGenerator

from tensorflow.python.keras.models import Model,load_model,Sequential

from tensorflow.python.keras.layers import Dense, GlobalAveragePooling2D, Dropout,Flatten, Input, Conv2D, MaxPooling2D, Dropout, Flatten
from tensorflow.python.keras import backend as K

from tensorflow.keras.callbacks import ModelCheckpoint, Callback

print(tf.__version__)
print(tf.keras.__version__)
print(keras.__version__)

!ls flowers

batch_size = 32
epochs = 10

lr = 0.001

import glob
import pandas as pd

filenames_n0 = glob.glob('./flowers/daisy/*.jpg')
filenames_n1 = glob.glob('./flowers/dandelion/*.jpg')
filenames_n2 = glob.glob('./flowers/rose/*.jpg')
filenames_n3 = glob.glob('./flowers/sunflower/*.jpg')
filenames_n4 = glob.glob('./flowers/tulip/*.jpg')

names = ['daisy', 'dandelion','rose','sunflower','tulip']


len(filenames_n1)

filenames_n3[:10]

df = pd.DataFrame(filenames_n0, columns = ["filename"])
df2 = pd.DataFrame(filenames_n1, columns = ["filename"])
df3 = pd.DataFrame(filenames_n2, columns = ["filename"])
df4 = pd.DataFrame(filenames_n3, columns = ["filename"])
df5 = pd.DataFrame(filenames_n4, columns = ["filename"])

df.head()

df['class'] = pd.Series([0 for x in range(len(df.index))], index=df.index)
df2['class'] = pd.Series([1 for x in range(len(df2.index))], index=df2.index)
df3['class'] = pd.Series([2 for x in range(len(df3.index))], index=df3.index)
df4['class'] = pd.Series([3 for x in range(len(df4.index))], index=df4.index)
df5['class'] = pd.Series([4 for x in range(len(df5.index))], index=df5.index)

df.head()

df3.head()

train_set_percentage = .9


train_df = df[:int(len(df)*train_set_percentage)]
val_df = df[int(len(df)*train_set_percentage):]

train_df2 = df2[:int(len(df2)*train_set_percentage)]
val_df2 = df2[int(len(df2)*train_set_percentage):]

train_df3 = df3[:int(len(df3)*train_set_percentage)]
val_df3 = df3[int(len(df3)*train_set_percentage):]

train_df4 = df4[:int(len(df4)*train_set_percentage)]
val_df4 = df4[int(len(df4)*train_set_percentage):]

train_df5 = df5[:int(len(df5)*train_set_percentage)]
val_df5 = df5[int(len(df5)*train_set_percentage):]



df_new_train = pd.concat([train_df, train_df2, train_df3, train_df4, train_df5])
df_new_val = pd.concat([val_df, val_df2, val_df3, val_df4, val_df5])

df_new_train.shape


df = df_new_train.sample(frac=1).reset_index(drop=True)
df_val = df_new_val.sample(frac=1).reset_index(drop=True)

df.head()

print(df.shape)
print(df_val.shape)

df['class'].unique()

print(df['class'].value_counts())


ax = df['class'].value_counts().plot.barh()
ax.set_xlabel("Number of Examples", fontsize=12)
ax.set_ylabel("Flowers - training set", fontsize=12)
ax.set_yticklabels(['Dandelions','Tulips','Roses','Daisies','Sunflower'], rotation=0, fontsize=12)
plt.show()

train_filenames_list = df["filename"].tolist()
train_labels_list = df["class"].astype('int32').tolist()

val_filenames_list = df_val["filename"].tolist()
val_labels_list = df_val["class"].astype('int32').tolist()

num_classes = 5

df.shape

img_rows, img_cols = 299,299

def _parse_function(filename, label):
  image_string = tf.read_file(filename)
  image_decoded = tf.image.decode_jpeg(image_string)
  image_resized = tf.image.resize_images(image_decoded, [img_rows, img_cols])
  label = tf.one_hot(label, num_classes)
  return image_resized, label

filenames = tf.constant(train_filenames_list)

labels = tf.constant(train_labels_list)

val_filenames = tf.constant(val_filenames_list)
val_labels = tf.constant(val_labels_list)

train_dataset = tf.data.Dataset.from_tensor_slices((filenames, labels))
train_dataset = train_dataset.map(_parse_function)
train_dataset = train_dataset.repeat(100)
train_dataset = train_dataset.batch(32)

valid_dataset = tf.data.Dataset.from_tensor_slices((val_filenames, val_labels))
valid_dataset = valid_dataset.map(_parse_function)
valid_dataset = valid_dataset.repeat(100)
valid_dataset = valid_dataset.batch(32)

test_dataset = tf.data.Dataset.from_tensor_slices((val_filenames, val_labels))
test_dataset = test_dataset.map(_parse_function)
test_dataset = test_dataset.repeat(100)
test_dataset = test_dataset.batch(32)

base_model = InceptionV3(weights='imagenet', include_top=False)

base_model.summary()

x = base_model.output
x = GlobalAveragePooling2D()(x)

x = Dense(1024, activation='relu')(x)

predictions = Dense(num_classes, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=predictions)

for layer in base_model.layers:
    if 'batch' in layer.name:
      print(layer.name)
      layer.trainable = True
    else:
      layer.trainable = False

for layer in model.layers:
    print(layer.name)
    print(layer.trainable)

opt = optimizers.Adam(lr)

model.compile(optimizer= opt, loss='categorical_crossentropy',metrics=['accuracy'])

!mkdir checkpoints


checkpoint = ModelCheckpoint('./checkpoints/weights_{epoch:02d}_{val_acc:.2f}.hdf5', verbose=1, save_best_only=True, mode='auto')

train_steps = 100
val_steps = 50
epochs = 5

history = model.fit( train_dataset, steps_per_epoch = train_steps,
                   epochs = epochs,
                   validation_data = valid_dataset,
                   validation_steps = val_steps,
                   callbacks=[checkpoint])

history = model.fit( train_dataset, steps_per_epoch = train_steps,
                   epochs = epochs,
                   validation_data = valid_dataset,
                   validation_steps = val_steps,
                   callbacks=[checkpoint])

!ls checkpoints

model.load_weights('./checkpoints/weights_02_0.91.hdf5')

metrics = model.evaluate(valid_dataset,steps=50)
print("model accuracy:",metrics[1])

metrics = model.evaluate(valid_dataset,steps=50)
print("model accuracy:",metrics[1])

preds = model.predict(test_dataset,steps=10)
preds = preds.argmax(axis=-1)

preds.shape

test_labels = val_labels_list[0:320]

len(test_labels)

from sklearn.metrics import confusion_matrix
import itertools

cm = confusion_matrix(test_labels,preds)

def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

cm_plot_labels = names

# # Plot normalized confusion matrix
plt.figure(figsize=(16,8))
plot_confusion_matrix(cm, cm_plot_labels, normalize=True,
                      title='Flowers Normalized')

plt.show()

model.save('flowers.h5')

model.save_weights('flowers_weights.h5', save_format='h5')

!ls

model.save_weights('./flowers_tf')

!ls

!wget -qq https://www.dropbox.com/s/iupwkbumwldk9es/testing_flowers.zip


!unzip -qq testing_flowers.zip
!rm testing_flowers.zip



!ls

!ls testing_flowers

image_path = './testing_flowers/'

from IPython.display import Image

image_name = 'sunflower02.jpg'
Image(image_path+image_name)

from keras.preprocessing import image
from keras.applications.imagenet_utils import preprocess_input, decode_predictions
import numpy as np

img_path = os.path.join(image_path, image_name)
img = image.load_img(img_path, target_size=(299, 299))
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0)
# x = preprocess_input(x)
print('Input image shape:', x.shape)

pred = model.predict(x)
print('Predicted:', pred)

print(np.argmax(pred))

result= np.argmax(pred)
if result==0:
    print("Its a Daisy")
elif result==1:
    print("Its a Dandelion")
elif result==2:
    print("Its a Rose")
elif result==3:
    print("Its a Sunflower")
elif result==4:
    print("Its a Tulip")

names

from google.colab import files

files.download('flowers.h5')

files.download('flowers_weights.h5')

estimator = tf.keras.estimator.model_to_estimator(model)

!kill -9 -1