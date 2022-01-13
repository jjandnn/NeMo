import json
import re
from argparse import ArgumentParser
from pathlib import Path

from sklearn.metrics import accuracy_score, f1_score


CAPIT_LABELS_TO_NUMBERS = {"O": 0, "U": 1}
PUNCT_LABELS_TO_NUMBERS = {"O": 0, ",": 1, ".": 2, "?": 3}
NUMBERS_TO_CAPIT_LABELS = {v: k for k, v in CAPIT_LABELS_TO_NUMBERS.items()}
NUMBERS_TO_PUNCT_LABELS = {v: k for k, v in PUNCT_LABELS_TO_NUMBERS.items()}


SEPARATORS = re.compile(r"\s+")


def get_args():
    parser = ArgumentParser()
    parser.add_argument("--predictions", "-p", type=Path, required=True)
    parser.add_argument("--labels", "-l", type=Path, required=True)
    args = parser.parse_args()
    args.predictions = args.predictions.expanduser()
    args.labels = args.labels.expanduser()
    return args


def load_punctuation_capitalization_labels(text):
    text = SEPARATORS.sub(' ', text)
    pairs = text.split()
    return [PUNCT_LABELS_TO_NUMBERS[p[0]] for p in pairs], [CAPIT_LABELS_TO_NUMBERS[p[1]] for p in pairs]


def compute_scores(preds_text, labels_text):
    punct_preds, capit_preds = load_punctuation_capitalization_labels(preds_text)
    punct_labels, capit_labels = load_punctuation_capitalization_labels(labels_text)
    metrics = {
        "punctuation": {
            "accuracy": accuracy_score(punct_labels, punct_preds),
            "f1_macro": f1_score(punct_labels, punct_preds, average="macro"),
        },
        "capitalization": {
            "accuracy": accuracy_score(capit_labels, capit_preds),
            "f1": f1_score(capit_labels, capit_preds),
        },
    }
    unique_punct = set(punct_labels)
    unique_capit = set(capit_labels)
    for labels, preds, unique, key, number_to_label in [
        (punct_labels, punct_preds, unique_punct, 'punctuation', NUMBERS_TO_PUNCT_LABELS),
        (capit_labels, capit_preds, unique_capit, 'capitalization', NUMBERS_TO_CAPIT_LABELS),
    ]:
        for lbl_id in unique:
            metrics[key][f"f1_'{number_to_label[lbl_id]}'"] = f1_score(
                labels, preds, labels=[lbl_id], average="micro", zero_division=0,
            )
    return metrics


def main():
    args = get_args()
    with args.predictions.open() as fp, args.labels.open() as fl:
        preds_text = fp.read()
        labels_text = fl.read()
    scores = compute_scores(preds_text, labels_text)
    print(json.dumps(scores, indent=2))


if __name__ == "__main__":
    main()