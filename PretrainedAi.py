from tensorflow.keras import layers, models # type: ignore
from tensorflow.keras.constraints import max_norm # type: ignore
from tensorflow.keras.callbacks import Callback # type: ignore
import tensorflow as tf
import config
from config import path
import os
import DataManager
from AiFilter import filterEEG
import numpy as np

def build_eegnet(nb_classes):
    pretrained = models.load_model("EEGNetv4_pretrained.h5") 
    inputs = layers.Input(shape=(4, 128, 1)) #128 = 256Hz / 2
    x = layers.Conv2D(filters=8, kernel_size=(64, 1), padding='same', use_bias=False)(inputs)
    for layer in pretrained.layers[1:]:
        x = layer(x)

    outputs = layers.Dense(nb_classes, activation='softmax')(x)
    finetune_model = models.Model(inputs=inputs, outputs=outputs)
    for layer in finetune_model.layers[:-2]:
        layer.trainable = False
    return finetune_model


if os.path.exists(path("models", "EEGNet.h5")):
    model = models.load_model(path("models", "EEGNet.h5"))
else:
    nb_classes = len(DataManager.eegData)
    model = build_eegnet(nb_classes)
    model.compile(loss='sparse_categorical_crossentropy', optimizer=tf.keras.optimizers.Adam(1e-4), metrics=['accuracy'], run_eagerly=True)
    
Chans = 4
Samples = 256
stride = 128
batch_size = 16
epochs = 50

def train():
    global model, Chans, Samples, stride, batch_size, epochs
    
    X_list, y_list = [], []

    for class_id, file_name in enumerate(list(map(lambda x: x+".csv", DataManager.eegData))):
        data = np.loadtxt(path("data", file_name), delimiter=',')

        filtered_data = np.zeros_like(data)
        for ch in range(data.shape[1]):  # 각 채널 반복
            filtered_data[:, ch] = filterEEG(data[:, ch])
            
        for start in range(0, data.shape[0] - Samples + 1, stride):
            window = filtered_data[start:start+Samples].T[..., np.newaxis]  # (Chans, Samples, 1)
            X_list.append(window)
            y_list.append(class_id)
    X_train = np.stack(X_list)  # (총 trial 수, Chans, Samples, 1)
    y_train = np.array(y_list)  # (총 trial 수,
    model.fit(X_train, y_train, batch_size=batch_size, epochs=epochs, shuffle=True, callbacks=[CTkProgressBarCallback()])
    model.save(path("models", "EEGNet.h5"))

class CTkProgressBarCallback(Callback):
    def __init__(self):
        super().__init__()
        self.progressbar = config.app.progress
        self.progressbar.grid(row=2, column=0, padx=20, pady=10, sticky="nsew", columnspan=2)

    def on_epoch_begin(self, epoch, logs=None):
        self.current_epoch = epoch
        self.epochs = self.params['epochs']
        self.steps_per_epoch = self.params['steps']

    def on_batch_end(self, batch, logs=None):
        total_batches = self.epochs * self.steps_per_epoch
        current_batch = self.current_epoch * self.steps_per_epoch + batch + 1
        progress_value = current_batch / total_batches
        self.progressbar.set(progress_value)
        self.progressbar.master.update()  # UI 갱신