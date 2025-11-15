from datasets import load_dataset

# Login using e.g. `huggingface-cli login` to access this dataset
ds = load_dataset("shzyk/DiagnosisArena")
ds["test"].to_csv("diagnosis_arena_dataset.csv", index=False)