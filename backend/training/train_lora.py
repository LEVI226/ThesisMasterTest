"""
ÉTAPE 2 — Fine-tuning LoRA de whisper-small sur le train split MInDS-14.
PEFT LoRA r=16, cibles q_proj/v_proj, fp16 GPU, 3 epochs, lr=1e-4, seed=42.
Sauvegarde l'adaptateur dans models/lora_small_minds14/.
Log de perte dans results/lora_training_log.csv.

OOM fallback : réduire per_device_train_batch_size à 1, puis r=8,
puis changer MODEL_NAME pour "openai/whisper-base".
"""
import sys
import csv
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Any

_root = str(Path(__file__).resolve().parents[2])
sys.path = [p for p in sys.path if p not in ("", ".", _root)]
sys.path.insert(0, _root)   # réinsère pour que backend.* soit importable

import torch
import numpy as np
import librosa
from datasets import Dataset
from transformers import (
    WhisperForConditionalGeneration,
    WhisperProcessor,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    TrainerCallback,
)
from peft import LoraConfig, get_peft_model, TaskType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MANIFEST_CSV  = Path("datasets/lora_train/manifest.csv")
ADAPTER_DIR   = Path("models/lora_small_minds14")
TRAINING_LOG  = Path("results/lora_training_log.csv")
MODEL_NAME    = "openai/whisper-small"
TARGET_SR     = 16_000
LANG_TO_ID    = {"en": "english", "fr": "french", "de": "german"}


def load_audio(path: str) -> np.ndarray:
    audio, _ = librosa.load(path, sr=TARGET_SR, mono=True)
    return audio[:TARGET_SR * 30]   # tronquer à 30 s max


@dataclass
class WhisperCollator:
    processor: Any
    decoder_start_token_id: int

    def __call__(self, features):
        inp = [{"input_features": f["input_features"]} for f in features]
        batch = self.processor.feature_extractor.pad(inp, return_tensors="pt")
        lbl = [{"input_ids": f["labels"]} for f in features]
        lbl_batch = self.processor.tokenizer.pad(lbl, return_tensors="pt")
        labels = lbl_batch["input_ids"].masked_fill(
            lbl_batch.attention_mask.ne(1), -100
        )
        # Supprimer le token de début si le trainer le réinjecte automatiquement.
        if (labels[:, 0] == self.decoder_start_token_id).all():
            labels = labels[:, 1:]
        batch["labels"] = labels
        return batch


class LossLogger(TrainerCallback):
    def __init__(self):
        self.rows = []

    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs and "loss" in logs:
            self.rows.append({
                "step":  state.global_step,
                "epoch": round(state.epoch, 3),
                "loss":  round(logs["loss"], 4),
            })


def main():
    rows = list(csv.DictReader(open(MANIFEST_CSV, encoding="utf-8")))
    logger.info("Train split : %d échantillons", len(rows))

    processor = WhisperProcessor.from_pretrained(MODEL_NAME)

    def process(row):
        audio = load_audio(row["audio_path"])
        feats = processor.feature_extractor(
            audio, sampling_rate=TARGET_SR
        ).input_features[0]
        processor.tokenizer.set_prefix_tokens(
            language=LANG_TO_ID.get(row["language"], "english"),
            task="transcribe",
        )
        labels = processor.tokenizer(row["transcription"]).input_ids
        return {"input_features": feats, "labels": labels}

    logger.info("Prétraitement des %d clips audio…", len(rows))
    processed = [process(r) for r in rows]
    hf_ds = Dataset.from_list(processed)
    hf_ds.set_format("torch")

    model = WhisperForConditionalGeneration.from_pretrained(MODEL_NAME)
    model.config.use_cache = False
    model.config.forced_decoder_ids = None

    lora_cfg = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.SEQ_2_SEQ_LM,
    )
    model = get_peft_model(model, lora_cfg)
    model.print_trainable_parameters()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    fp16   = device == "cuda"
    ADAPTER_DIR.mkdir(parents=True, exist_ok=True)

    training_args = Seq2SeqTrainingArguments(
        output_dir=str(ADAPTER_DIR),
        num_train_epochs=3,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,   # batch effectif = 8
        learning_rate=1e-4,
        warmup_steps=50,
        fp16=fp16,
        logging_steps=10,
        save_strategy="epoch",
        seed=42,
        predict_with_generate=False,
        report_to="none",
    )

    loss_logger = LossLogger()
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=hf_ds,
        data_collator=WhisperCollator(
            processor=processor,
            decoder_start_token_id=model.config.decoder_start_token_id,
        ),
        callbacks=[loss_logger],
    )

    logger.info("Entraînement sur %s (fp16=%s)…", device.upper(), fp16)
    trainer.train()

    model.save_pretrained(str(ADAPTER_DIR))
    processor.save_pretrained(str(ADAPTER_DIR))
    logger.info("Adaptateur LoRA sauvegardé → %s", ADAPTER_DIR)

    TRAINING_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(TRAINING_LOG, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["step", "epoch", "loss"])
        w.writeheader()
        w.writerows(loss_logger.rows)
    logger.info("Log d'entraînement → %s", TRAINING_LOG)

    if loss_logger.rows:
        last = loss_logger.rows[-1]
        logger.info(
            "Loss finale step %d (epoch %.1f) : %.4f",
            last["step"], last["epoch"], last["loss"],
        )


if __name__ == "__main__":
    main()
