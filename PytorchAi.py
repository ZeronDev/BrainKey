import os
import numpy as np
from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from braindecode.models import EEGNet
from AiFilter import filterEEG
import DataManager
from config import LearningProgressBar, path
import threading
from copy import deepcopy

Chans = 4
Samples = 768    # sliding window
stride = 384
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
    train_loader, val_loader = preprocessing()
    threading.Thread(target=lambda model=model, loader=(train_loader, val_loader), optimizer=optimizer, criterion=criterion: train(model, loader, optimizer, criterion), daemon=True).start()

def preprocessing():
    X_list, y_list = [], []

    baseline_data = np.loadtxt(path("data", "base.csv"), delimiter=',')  # shape: (samples, chans)
    baseline_mean = np.mean(baseline_data, axis=0, keepdims=True)  # 채널별 평균
    eeg = deepcopy(DataManager.eegData)
    eeg.remove("base")
    for class_id, file_name in enumerate(list(map(lambda x: x+".csv", eeg))):
        counter = 0
        eegFile = f"{os.path.splitext(file_name)[0]}{'' if not counter else counter}.csv"
        while ((os.path.exists(path("data", eegFile)) or counter == 0)):
            data = np.loadtxt(path("data", eegFile), delimiter=',')
            
            filtered_data = np.zeros_like(data)
            for ch in range(data.shape[1]):
                filtered_data[:, ch] = filterEEG(data[:, ch])
            
            # sliding window
            for start in range(0, data.shape[0] - Samples + 1, stride):
                window = filtered_data[start:start+Samples].T  # (Chans, Samples)
                window -= baseline_mean.T
                window = (window - window.mean(axis=1, keepdims=True)) / (window.std(axis=1, keepdims=True) + 1e-6)
                X_list.append(window)
                y_list.append(class_id)
                augmented = augment_eeg(window, n_augment=3, noise_std=0.01, max_shift=10)
                X_list.extend(augmented)
                y_list.extend([class_id]*len(augmented))
            
            counter += 1
            eegFile = f"{os.path.splitext(file_name)[0]}{counter}.csv"

    X = np.stack(X_list)                  # (num_windows, Chans, Samples)
    # X = X[:, np.newaxis, :, :]            # add channel dim → (num_windows, 1, Chans, Samples)
    y = np.array(y_list)
    indices = np.arange(len(y))
    np.random.shuffle(indices)
    X = X[indices]
    y = y[indices]
    
    print(y)

    # X_tensor = torch.tensor(X, dtype=torch.float32)
    # y_tensor = torch.tensor(y, dtype=torch.long)

    # dataset = TensorDataset(X_tensor, y_tensor)
    # loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=0) Train
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.1, stratify=y)

    print(f"Train samples: {len(y_train)}, Validation samples: {len(y_val)}")

    # 텐서 변환
    X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
    y_train_tensor = torch.tensor(y_train, dtype=torch.long)
    X_val_tensor = torch.tensor(X_val, dtype=torch.float32)
    y_val_tensor = torch.tensor(y_val, dtype=torch.long)

    # DataLoader 생성
    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    val_dataset = TensorDataset(X_val_tensor, y_val_tensor)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)


    return train_loader, val_loader

def train(model, loader, optimizer, criterion):
    progress_bar = LearningProgressBar(epochs)
    train_loader, val_loader = loader


    for _ in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        progress_bar.update()
        
        for X_batch, y_batch in train_loader:
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

    evaluate(model, val_loader)

def augment_eeg(window, n_augment=3, noise_std=0.01, max_shift=10):
    """
    단일 EEG window를 증강
    window: (Chans, Samples)
    """
    augmented = []

    for _ in range(n_augment):
        w = window.copy()
        
        # 1. 랜덤 노이즈
        w += np.random.normal(0, noise_std, w.shape)
        
        # 2. 시간축 랜덤 이동
        shift = np.random.randint(-max_shift, max_shift+1)
        if shift > 0:
            w = np.concatenate([np.zeros((w.shape[0], shift)), w[:, :-shift]], axis=1)
        elif shift < 0:
            w = np.concatenate([w[:, -shift:], np.zeros((w.shape[0], -shift))], axis=1)
        
        augmented.append(w)
    
    return augmented

if __name__ == "__main__":
    pytorchLearn()

def evaluate(model, loader):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for X_batch, y_batch in loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            outputs = model(X_batch)
            _, predicted = torch.max(outputs, 1)
            correct += (predicted == y_batch).sum().item()
            total += y_batch.size(0)
    acc = correct / total
    print(f"Validation Accuracy: {acc*100:.2f}%")
    return acc