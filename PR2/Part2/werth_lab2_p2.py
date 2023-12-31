# -*- coding: utf-8 -*-
"""Werth_Lab2_P2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ubhzIFQAgLn8veOGydsv1GhPH2dj_E-6
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
from torchvision import transforms, datasets

# load the CIFAR100 dataset
data_transforms = transforms.Compose([
  transforms.ToTensor(),
  transforms.Normalize(
      mean = [0.485, 0.456, 0.406],   # Usimg mean and std dev of ImageNet
      std = [0.229, 0.224, 0.225])
])

trainset = torchvision.datasets.CIFAR100(root='./data', train=True, download=True, transform=data_transforms)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=64, shuffle=True)

# Create our own CNN

class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()

        # 3 convolutional layers
        self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, 3, padding=1)

        # 1 max pooling layer
        self.pool = nn.MaxPool2d(2, 2)

        # fully connected layers
        self.fc1 = nn.Linear(128 * 4 * 4, 512)
        self.fc2 = nn.Linear(512, 100)  # 100 classes in CIFAR-100

    def forward(self, x):
        x = self.pool(nn.functional.relu(self.conv1(x)))
        x = self.pool(nn.functional.relu(self.conv2(x)))
        x = self.pool(nn.functional.relu(self.conv3(x)))
        x = x.view(-1, 128 * 4 * 4)
        x = nn.functional.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# call what we just defined to create a model
model = CNN()

# Create our loss and optimizer similar to part 1
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)

# Training the CNN
for epoch in range(30):  # use 30 epochs
    print("Epoch", epoch+1, "/30")
    total_loss = 0.0    # track our loss as we train to make sure we are training effectively
    for i, data in enumerate(trainloader, 0):
        inputs, labels = data
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    # tracking loss for testing purposes
    print(f"Epoch {epoch + 1}, Loss: {total_loss / len(trainloader)}")

torch.save(model.state_dict(), 'trained_CNN.pth')

# load model to predict labels for test set and print accuracy
testset = datasets.CIFAR100('.', train=False, transform = data_transforms, download=True)
test_loader = torch.utils.data.DataLoader(testset, batch_size=64, shuffle=True)

# Move the model to GPU (if available):
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
model = model.to(device)

# Set model to evaluation / testing mode
model.eval()

# define vars for accuracy evaluation later
correct = 0
total = 0

with torch.no_grad():
  for i, data in enumerate(test_loader, 0):
    images, labels = data
    images, labels = images.to(device), labels.to(device)

    outputs = model(images)
    _, preds = torch.max(outputs, 1)
    correct += (preds == labels).sum().item()
    total += labels.size(0)

accuracy = (correct / total) * 100
print(accuracy)