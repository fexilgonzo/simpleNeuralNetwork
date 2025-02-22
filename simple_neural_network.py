import torch
import torch.nn.functional as F
import torchvision.datasets as datasets
import torchvision.transforms as transforms
from torch import optim
from torch import nn
from torch.utils.data import DataLoader
from tqdm import tqdm

# Define the Neural Network Architecture
# The input layer will have 784 neurons (28x28 pixels). The hidden layer will have 50 neurons, and the output layer will have 10 neurons.
class NN(nn.Module):
    def __init__(self, input_size, num_classes):
        """
        Here we define the layers of the neural networks.
        Parameters: 
            input_size: int
                The size of the input, in this case 784 (28x28)
            num_classes: int
                The number of classes we want to predict, in this case 10 (digits 0 through 9)
        """
        super(NN, self).__init__()
        self.fc1 = nn.Linear(input_size, 50)
        self.fc2 = nn.Linear(50, num_classes)

    def forward(self, x):
        """
        Here we define the forward pass of the neural network.
        Parameters:
            x: torch.Tensor
                The input tensor
                
        Returns:
            torch.Tensor
                The output tensor after passing through the network.
        """

        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x
    
# Set up device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Set up hyperparameters. These configuration settings are used to tune how the model is trained.
input_size = 784  # 28x28 pixels
num_classes = 10  # digits 0-9
learning_rate = 0.001
batch_size = 64
num_epochs = 100

# We use the torchvisions.datasets module to load the MNIST dataset, and use DataLoader to handle batching and shuffling
train_dataset = datasets.MNIST(root="dataset/", download=True, train=True, transform=transforms.ToTensor())
train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)

test_dataset = datasets.MNIST(root="dataset/", download=True, train=False, transform=transforms.ToTensor())
test_loader = DataLoader(dataset=test_dataset, batch_size=batch_size, shuffle=True)

# We initialize the neural network and move it to the device (CPU or GPU), in this case CPU :(
model = NN(input_size=input_size, num_classes=num_classes).to(device)

# Now we will define the loss and the optimizer. We will use cross-entropy loss for classification and the Adam optimizer to update the model's weights.
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

# The next step is to train the network. We will loop through the dataset multiple times (this is known as an epoch) and update the model's weights based on the loss. 
for epoch in range(num_epochs):
    print(f"Epoch [{epoch + 1}/{num_epochs}]")
    for batch_index, (data, targets) in enumerate(tqdm(train_loader)):
        data = data.to(device)
        targets = targets.to(device)
        
        # Reshape data to (batch_size, input_size)
        data = data.reshape(data.shape[0], -1)

        # Forward pass: compute the model output
        scores = model(data)
        loss = criterion(scores, targets)

        # Backward pass: compute the gradients
        optimizer.zero_grad()
        loss.backward()

        # Optimization step: update the model parameters
        optimizer.step()

# Now we need to check for accuracy. This function will test the accuracy of our model on both the train and test datasets.
def check_accuracy(loader, model):
    """
    Checks the accuracy of the model on the given dataset loader.

    Parameters:
        loader: DataLoader
            The DataLoader for the dataset to check accuracy on.
        model: nn.Module
            The neural network model.
    """
    if loader.dataset.train:
        print("Checking accuracy on training data")
    else:
        print("Checking accuracy on test data")

    num_correct = 0
    num_samples = 0
    model.eval()  # Set the model to evaluation mode

    with torch.no_grad():  # Disable gradient calculation
        for x, y in loader:
            x = x.to(device)
            y = y.to(device)
            x = x.reshape(x.shape[0], -1)

            # Forward pass: compute the model output
            scores = model(x)
            _, predictions = scores.max(1)  # Get the index of the max log-probability
            num_correct += (predictions == y).sum()  # Count correct predictions
            num_samples += predictions.size(0)  # Count total samples

        # Calculate accuracy
        accuracy = float(num_correct) / float(num_samples) * 100
        print(f"Got {num_correct}/{num_samples} with accuracy {accuracy:.2f}%")
    
    model.train()  # Set the model back to training mode

# Final accuracy check on training and test sets
check_accuracy(train_loader, model)
check_accuracy(test_loader, model)

# Simple Neural Network: Done!