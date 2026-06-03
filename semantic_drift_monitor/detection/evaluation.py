import numpy as np


def compute_annotator_agreement(labels_a: list[int], labels_b: list[int]) -> float:
    if len(labels_a) != len(labels_b):
        raise ValueError("Annotation lists must have the same length.")
    if not labels_a:
        return 0.0
    observed = sum(a == b for a, b in zip(labels_a, labels_b)) / len(labels_a)
    labels = sorted(set(labels_a) | set(labels_b))
    expected = 0.0
    for label in labels:
        p_a = labels_a.count(label) / len(labels_a)
        p_b = labels_b.count(label) / len(labels_b)
        expected += p_a * p_b
    if expected == 1:
        return 1.0
    return float((observed - expected) / (1 - expected))


def evaluate_binary_classifier(predicted_labels: list[int], true_labels: list[int]) -> dict[str, float]:
    if len(predicted_labels) != len(true_labels):
        raise ValueError("Prediction and truth lists must have the same length.")
    tp = sum(pred == 1 and true == 1 for pred, true in zip(predicted_labels, true_labels))
    fp = sum(pred == 1 and true == 0 for pred, true in zip(predicted_labels, true_labels))
    fn = sum(pred == 0 and true == 1 for pred, true in zip(predicted_labels, true_labels))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": float(precision), "recall": float(recall), "f1": float(f1)}


def permutation_test(group_a: np.ndarray, group_b: np.ndarray, n_permutations: int = 1000) -> tuple[float, float]:
    observed = float(np.mean(group_a) - np.mean(group_b))
    combined = np.concatenate([group_a, group_b])
    n_a = len(group_a)
    diffs = []
    for _ in range(n_permutations):
        shuffled = np.random.permutation(combined)
        diffs.append(float(np.mean(shuffled[:n_a]) - np.mean(shuffled[n_a:])))
    p_value = (np.sum(np.abs(diffs) >= abs(observed)) + 1) / (n_permutations + 1)
    return observed, float(p_value)
