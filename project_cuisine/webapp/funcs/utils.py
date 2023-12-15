import numpy as np

def transform_label(label, vocab):
    return vocab.inverse_transform(np.array([label]))

def transform_probs_to_labels(probs, threshold: float = 0.5):
    return (probs > threshold).astype(int)