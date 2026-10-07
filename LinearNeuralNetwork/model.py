import torch.nn as nn

class HealthClassifier(nn.Module):
    """
    Model Bayi untuk klasifikasi gejala sederhana.
    Total parameter: ~310 (sangat ringan untuk CPU)
    """
    def __init__(self, input_size=19, hidden_size=10, output_size=10):
        super(HealthClassifier, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size)
        )
    
    def forward(self, x):
        return self.network(x)
    
    @staticmethod
    def count_parameters(model):
        return sum(p.numel() for p in model.parameters() if p.requires_grad)