import torch
import torch.nn as nn

class Encoder(nn.Module):

    def __init__(self, rep_dim, moco_dim):
        super(Encoder, self).__init__()
        self.rep_dim = rep_dim
        self.moco_dim = moco_dim
        self.conv1 = nn.Conv3d(1, 8, kernel_size=3, stride=1, padding=1)
        self.bn1 = nn.BatchNorm3d(8)
        self.act = nn.ELU()
        self.conv2 = nn.Conv3d(8, 8, kernel_size=3, stride=2, padding=1)
        self.bn2 = nn.BatchNorm3d(8)
        self.downsample1 = self._make_layer(8, 16)
        self.downsample2 = self._make_layer(16, 32)
        self.downsample3 = self._make_layer(32, 64) #[N,64,2,2,2]
        self.conv3 = nn.Conv3d(64, 128, kernel_size=3, stride=1, padding=1)
        self.bn3 = nn.BatchNorm3d(128)
        self.conv4 = nn.Conv3d(128, rep_dim, kernel_size=3, stride=2, padding=1)
        self.bn4 = nn.BatchNorm3d(rep_dim)
        self.cfc = nn.Sequential(nn.Linear(rep_dim+3, rep_dim), nn.ELU())
        self.fc = nn.Linear(rep_dim, moco_dim)

    def _make_layer(self, in_channels, out_channels):
        return nn.Sequential(nn.Conv3d(in_channels, out_channels, kernel_size=3, padding=1),
                             nn.BatchNorm3d(out_channels),
                             nn.ELU(inplace=True),
                             nn.Conv3d(out_channels, out_channels, kernel_size=3, padding=1),
                             nn.BatchNorm3d(out_channels),
                             nn.ELU(inplace=True),
                             nn.Conv3d(out_channels, out_channels, kernel_size=3, stride=2, padding=1),
                             nn.BatchNorm3d(out_channels),
                             nn.ELU(inplace=True))

    def forward(self, x, loc):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.act(x)
        x = self.conv2(x)
        x = self.bn2(x)
        x = self.act(x)
        x = self.downsample1(x)
        x = self.downsample2(x)
        x = self.downsample3(x)
        x = self.conv3(x)
        x = self.bn3(x)
        x = self.act(x)
        x = self.conv4(x)
        x = self.bn4(x)
        x = self.act(x) # x: 64 * 512 * 1 * 1 * 1
        x = torch.cat([x.view(-1, self.rep_dim), loc], 1)
        x = self.cfc(x)
        x = self.fc(x)
        return x