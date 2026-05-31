import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path
import json

if len(sys.argv) <= 1:
    print(f"Use:\npython {sys.argv[0]} [path to the log file]")
    exit(-1)

log_filename = Path(sys.argv[1])
with open(log_filename, "r") as f:
    log = json.load(f)

loss_train = {
    "total" : [],
    "regression" : [],
    "classification" : [],
}

loss_validation = {
    "total" : [],
    "regression" : [],
    "classification" : [],
}

accuracy_train = []
accuracy_validation = []

mae_train = []
mae_validation = []

epochs = []
lr = []

for epoch in log:
    epochs.append(epoch["epoch"])
    lr.append(epoch["lr"])
    loss = epoch["loss"]
    for loss_type in loss["train"]:
        loss_train[loss_type].append(loss["train"][loss_type])
    for loss_type in loss["validation"]:
        loss_validation[loss_type].append(loss["validation"][loss_type])
    
    accuracy_train.append(epoch["accuracy"]["train"])
    accuracy_validation.append(epoch["accuracy"]["validation"])

    mae_train.append(epoch["mae"]["train"])
    mae_validation.append(epoch["mae"]["validation"])

fig, axes = plt.subplots(1, 2, figsize=(12,10))
fig.suptitle("Loss")
for ax, loss, title in zip(axes, (loss_train, loss_validation), ("Train", "Validation")):
    ax.plot(epochs, loss["total"], label="Total")
    ax.plot(epochs, loss["regression"], label="Regression")
    ax.plot(epochs, loss["classification"], label="Classification")
    ax.set_title(title)
    ax.set_xlabel("Epoch")
    ax.legend()
plt.show()

fig, ax = plt.subplots(1, 1, figsize=(12,10))
fig.suptitle("Accuracy")
ax.plot(epochs, accuracy_train, label="Train")
ax.plot(epochs, accuracy_validation, label="Validation")
ax.set_xlabel("Epoch")
ax.legend()
plt.show()


fig, ax = plt.subplots(1, 1, figsize=(12,10))
fig.suptitle("MAE (normalized regression values)")
ax.plot(epochs, mae_train, label="Train")
ax.plot(epochs, mae_validation, label="Validation")
ax.set_xlabel("Epoch")
ax.legend()
plt.show()

fig, ax = plt.subplots(1, 1, figsize=(12,10))
fig.suptitle("Learning rate")
ax.plot(epochs, lr)
ax.set_xlabel("Epoch")
plt.show()
