#------------------------------------------------------------------#
#   Credit: https://github.com/yanx27/Pointnet_Pointnet2_pytorch   #
#------------------------------------------------------------------#
import bpy
import torch.nn as nn
import torch.nn.functional as F
pointnet2_utils = bpy.data.texts["pointnet2_utils.py"].as_module()

class PointNet2(nn.Module):
    def __init__(self):
        super(PointNet2, self).__init__()
        self.sa1 = pointnet2_utils.PointNetSetAbstractionMsg(512, [0.1, 0.2, 0.4], [16, 32, 128], 0,[[32, 32, 64], [64, 64, 128], [64, 96, 128]])
        self.sa2 = pointnet2_utils.PointNetSetAbstractionMsg(128, [0.2, 0.4, 0.8], [32, 64, 128], 320,[[64, 64, 128], [128, 128, 256], [128, 128, 256]])
        self.sa3 = pointnet2_utils.PointNetSetAbstraction(None, None, None, 640 + 3, [256, 512, 1024], True)
        self.fc1 = nn.Linear(1024, 512)
        self.bn1 = nn.BatchNorm1d(512)
        self.drop1 = nn.Dropout(0.4)
        self.fc2 = nn.Linear(512, 256)
        self.bn2 = nn.BatchNorm1d(256)
        self.drop2 = nn.Dropout(0.5)

        self.regression_head = nn.Linear(256, 5)
        self.classification_head = nn.Linear(256, 7)

    def forward(self, xyz):
        B, _, _ = xyz.shape
        l1_xyz, l1_points = self.sa1(xyz, None)
        l2_xyz, l2_points = self.sa2(l1_xyz, l1_points)
        _, l3_points = self.sa3(l2_xyz, l2_points)
        x = l3_points.view(B, 1024)
        x = self.drop1(F.relu(self.bn1(self.fc1(x))))
        x = self.drop2(F.relu(self.bn2(self.fc2(x))))

        regression_output = self.regression_head(x)
        classification_output = self.classification_head(x)

        return {
            "regression": regression_output,
            "classification": classification_output,
        }


class PointNet2Loss(nn.Module):
    def __init__(self, regression_weight, classification_weight):
        super(PointNet2Loss, self).__init__()

        self.regression_loss_f = nn.MSELoss()
        self.classification_loss_f = nn.CrossEntropyLoss()

        self.regression_weight = regression_weight
        self.classification_weight = classification_weight

    def forward(self, pred, target):

        regression_loss = self.regression_loss_f(pred["regression"], target["regression"])
        classification_loss = self.classification_loss_f(pred["classification"], target["classification"])

        total_loss = regression_loss * self.regression_weight + classification_loss * self.classification_weight
        
        return {
            "total" : total_loss,
            "regression" : regression_loss,
            "classification" : classification_loss,
        }


