import torch
import torch.optim as optim
import numpy as np
import json
import argparse
import datetime

from pathlib import Path
from tqdm import tqdm

from dataset.point_cloud_dataset import PointCloudDataset
from model.pointnet2 import PointNet2, PointNet2Loss

def parse_args():
    parser = argparse.ArgumentParser('training')
    parser.add_argument('--use_cpu', action='store_true', default=False, help='use cpu mode')
    parser.add_argument('--dataset_path', type=str, required=True, help="Path to the dataset")
    parser.add_argument('--batch_size', type=int, default=8, help='batch size in training')
    parser.add_argument('--checkpoint', default=None, help='Load pretrained model weights')
    parser.add_argument('--epoch', default=100, type=int, help='number of epoch in training')
    parser.add_argument('--learning_rate', default=0.001, type=float, help='learning rate in training')
    parser.add_argument('--decay_rate', type=float, default=1e-4, help='decay rate')
    parser.add_argument('--gamma', type=float, default=0.95, help='gamma')
    parser.add_argument('--num_points', type=int, default=1024, help='Point Number')
    return parser.parse_args()

def test(model, valloader, criterion, device):
    model.eval()

    val_losses = {
        "total" : 0.0,
        "regression" : 0.0,
        "classification" : 0.0,
    }
    
    correct = 0
    total = 0
    mae = 0
    with torch.no_grad():

        for point_clouds, labels in tqdm(valloader, total=len(valloader)):
            point_clouds = point_clouds.to(device)

            labels["regression"] = labels["regression"].to(device)
            labels["classification"] = labels["classification"].to(device)

            outputs = model(point_clouds)
            loss = criterion(outputs, labels)

            for key in val_losses.keys():
                val_losses[key] += loss[key].item()

            pred_class = outputs["classification"].argmax(dim=1)
            correct += (pred_class == labels["classification"]).sum().item()
            total += point_clouds.shape[0]

            pred_values = outputs["regression"]
            mae += torch.abs(pred_values - labels["regression"]).mean().item()

        for key in val_losses.keys():
            val_losses[key] /= len(valloader)

        accuracy = correct / total
        mae /= len(valloader)

        return val_losses, accuracy, mae

def train(args):
    if args.use_cpu:
        device = torch.device("cpu")
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    checkpoint_path = Path(__file__).parent.joinpath("checkpoints")
    if not checkpoint_path.exists():
        checkpoint_path.mkdir()
    log_path = Path(__file__).parent.joinpath("logs")
    if not log_path.exists():
        log_path.mkdir()
    
    timestr = str(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M'))
    current_checkpoint_path = checkpoint_path.joinpath(f"checkpoint_{timestr}")
    current_checkpoint_path.mkdir()

    dataset_path = Path(args.dataset_path)
    point_cloud_path = dataset_path.joinpath("point_clouds_data")
    parameters_path = dataset_path.joinpath("parameters")
    
    train_dataset = PointCloudDataset(point_cloud_path, parameters_path, split = "train", num_points=args.num_points)
    val_dataset = PointCloudDataset(point_cloud_path, parameters_path, split = "val", num_points=args.num_points)
    trainloader = torch.utils.data.DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=4, drop_last=False)
    valloader = torch.utils.data.DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=4, drop_last=False)

    model = PointNet2()

    if args.checkpoint is not None:
        checkpoint = torch.load(args.checkpoint)

        model.load_state_dict(checkpoint["model_state_dict"])
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])

    model.to(device)

    criterion = PointNet2Loss(regression_weight=0.25, classification_weight=1.0)

    optimizer = optim.Adam(model.parameters(), lr=args.learning_rate, weight_decay=args.decay_rate)
    scheduler = optim.lr_scheduler.ExponentialLR(optimizer, gamma=args.gamma)

    log = []
    best_val_loss = float("inf")
    for epoch in range(args.epoch):
        model.train()
        train_losses = {
            "total" : 0.0,
            "regression" : 0.0,
            "classification" : 0.0,
        }
        correct = 0
        total = 0
        train_mae = 0.0
        for point_clouds, labels in tqdm(trainloader, total=len(trainloader)):
            point_clouds = point_clouds.to(device)

            labels["regression"] = labels["regression"].to(device)
            labels["classification"] = labels["classification"].to(device)

            optimizer.zero_grad()

            outputs = model(point_clouds)
            
            loss = criterion(outputs, labels)
            for key in train_losses.keys():
                train_losses[key] += loss[key].item()

            pred_class = outputs["classification"].argmax(dim=1)

            correct += (pred_class == labels["classification"]).sum().item()
            total += point_clouds.shape[0]

            pred_values = outputs["regression"]
            train_mae += torch.abs(pred_values - labels["regression"]).mean().item()

            loss["total"].backward()

            optimizer.step()
        
        for key in train_losses.keys():
            train_losses[key] /= len(trainloader)

        train_accuracy = correct / total
        train_mae /= len(trainloader)

        val_losses, val_accuracy, val_mae = test(model, valloader, criterion, device)
        
        log_current = {
            "epoch" : epoch,
            "lr" : optimizer.param_groups[0]["lr"],
            "loss" : {
                "train" : train_losses,
                "validation": val_losses
            },
            "accuracy" : {
                "train" : train_accuracy,
                "validation" : val_accuracy,
            },
            "mae" : {
                "train" : train_mae,
                "validation" : val_mae
            }
        }
        print(json.dumps(log_current, indent = 4))
        log.append(log_current)
        with open(log_path.joinpath(f"log_{timestr}.json"), "w") as f:
            json.dump(log, f, indent = 4)

        torch.save({
            "epoch" : epoch,
            "model_state_dict" : model.state_dict(),
            "optimizer_state_dict" : optimizer.state_dict(),
        }, current_checkpoint_path.joinpath("latest.pth"))

        if val_losses["total"] < best_val_loss:
            best_val_loss = val_losses["total"]
            torch.save({
                "epoch" : epoch,
                "model_state_dict" : model.state_dict(),
                "optimizer_state_dict" : optimizer.state_dict(),
            }, current_checkpoint_path.joinpath("best.pth"))
        
        scheduler.step()

if __name__ == "__main__":
    args = parse_args()
    train(args)