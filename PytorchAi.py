import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from braindecode.models import EEGNet
from AiFilter import filterEEG
import DataManager
from config import LearningProgressBar, path
import threading

Chans = 4
Samples = 256     # sliding window
stride = 128
batch_size = 16        
epochs = 150
learning_rate = 1e-4
n_classes = len(DataManager.eegData)
freeze_until_layer = 4  # 앞쪽 레이어 freeze
device = torch.device('cpu')
MODEL_PATH = path("models", "EEGNetv4.pth")

def build_eegnet():
    model = EEGNet(
        n_chans=Chans,
        n_outputs=n_classes,
        n_times=Samples,
        final_conv_length='auto'
    ).to(device)

    params_path = path("pretrained_models", "params.pt")
    pretrained_state = torch.load(params_path, map_location=device)
    for name, param in pretrained_state.items():
        print(name, param.shape)
    model_state = model.state_dict()
    for k in model_state.keys():
        if k in pretrained_state and "final_layer.conv_classifier" not in k:  # fc: classifier layer
            model_state[k] = pretrained_state[k]
    model.load_state_dict(model_state)

    for idx, param in enumerate(model.parameters()):
        if idx < freeze_until_layer:
            param.requires_grad = False

    return model

model = build_eegnet()

if os.path.exists(MODEL_PATH):
    model.load_state_dict(torch.load(MODEL_PATH, map_location=device))

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=learning_rate)

def pytorchLearn():
    global model, optimizer, criterion
    model = build_eegnet()
    loader = preprocessing()
    threading.Thread(target=lambda model=model, loader=loader, optimizer=optimizer, criterion=criterion: train(model, loader, optimizer, criterion), daemon=True).start()

def preprocessing():
    X_list, y_list = [], []

    for class_id, file_name in enumerate(list(map(lambda x: x+".csv", DataManager.eegData))):
        data = np.loadtxt(os.path.join("data", file_name), delimiter=',')
        
        filtered_data = np.zeros_like(data)
        for ch in range(data.shape[1]):
            filtered_data[:, ch] = filterEEG(data[:, ch])
        
        # sliding window
        for start in range(0, data.shape[0] - Samples + 1, stride):
            window = filtered_data[start:start+Samples].T  # (Chans, Samples)
            window = (window - window.mean(axis=1, keepdims=True)) / (window.std(axis=1, keepdims=True) + 1e-6)
            X_list.append(window)
            y_list.append(class_id)

    X = np.stack(X_list)                  # (num_windows, Chans, Samples)
    # X = X[:, np.newaxis, :, :]            # add channel dim → (num_windows, 1, Chans, Samples)
    y = np.array(y_list)
    indices = np.arange(len(y))
    np.random.shuffle(indices)
    X = X[indices]
    y = y[indices]
    
    print(y)

    X_tensor = torch.tensor(X, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.long)

    dataset = TensorDataset(X_tensor, y_tensor)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=0)

    return loader

def train(model, loader, optimizer, criterion):
    progress_bar = LearningProgressBar(epochs)

    for _ in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        progress_bar.update()
        
        for X_batch, y_batch in loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            
            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * X_batch.size(0)
            _, predicted = torch.max(outputs, 1)
            correct += (predicted == y_batch).sum().item()
            total += y_batch.size(0)
    progress_bar.end()
        
    os.makedirs("models", exist_ok=True)
    torch.save(model.state_dict(), "models/EEGNetv4.pth")

if __name__ == "__main__":
    pytorchLearn()