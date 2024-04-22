import syft as sy                                   # works with federated learning, allow local training
import tensorflow as tf                             # either TORCH
import torch                                        # or TF
from transformers import AutoModel, AutoTokenizer
import numpy as np
import pandas as pd
import matplotlib as plt
print('input the separation of data like 80-20, 70-15-15 :\n\n')
from sklearn.model_selection import train_test_split # metrics
from sklearn.metrics import accuracy_score

print('libs are working correctly')

