import os
import torch
from transformers import TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
import wandb


class LoRATrainer:
    def __init__(self, base_model, domain, config_path="utils/config.yaml"):
        """
        Inicializar entrenador LoRA para una rama específica

        Args:
            base_model: Modelo base Sheily
            domain: Dominio de especialización
            config_path: Ruta al archivo de configuración
        """
        self.base_model = base_model
        self.domain = domain

        # Configuración de LoRA
        self.lora_config = LoraConfig(
            r=16,  # Rango de adaptación
            lora_alpha=32,  # Escala de adaptación
            lora_dropout=0.05,  # Dropout para regularización
            target_modules=["q_proj", "v_proj", "o_proj"],
            bias="none",
            task_type="CAUSAL_LM",
        )

        # Preparar modelo para entrenamiento
        self.model = prepare_model_for_kbit_training(base_model.model)
        self.model = get_peft_model(self.model, self.lora_config)

        # Configuración de entrenamiento
        self.training_args = TrainingArguments(
            output_dir=f"branches/{domain}/adapter",
            num_train_epochs=2,
            per_device_train_batch_size=4,
            gradient_accumulation_steps=8,
            learning_rate=2e-4,
            warmup_steps=100,
            logging_dir=f"branches/{domain}/logs",
            logging_steps=10,
            evaluation_strategy="steps",
            eval_steps=100,
            save_total_limit=3,
            push_to_hub=False,
            report_to="wandb",
        )

    def prepare_dataset(self, dataset_path):
        """
        Preparar dataset para entrenamiento de rama

        Args:
            dataset_path: Ruta al dataset del dominio

        Returns:
            Dataset procesado
        """
        dataset = load_dataset("json", data_files=dataset_path)

        # Preprocesar dataset
        def preprocess_function(examples):
            # Formatear ejemplos para entrenamiento
            model_inputs = self.base_model.tokenizer(
                examples["instruction"] + " " + examples["input"],
                truncation=True,
                max_length=512,
            )
            model_inputs["labels"] = self.base_model.tokenizer(
                examples["output"], truncation=True, max_length=512
            )["input_ids"]
            return model_inputs

        processed_dataset = dataset.map(
            preprocess_function,
            batched=True,
            remove_columns=dataset["train"].column_names,
        )

        return processed_dataset

    def train(self, dataset_path):
        """
        Entrenar adapter LoRA para dominio específico

        Args:
            dataset_path: Ruta al dataset del dominio
        """
        # Inicializar wandb para seguimiento
        wandb.init(
            project=f"sheily-lora-{self.domain}",
            config={
                "domain": self.domain,
                "lora_r": self.lora_config.r,
                "lora_alpha": self.lora_config.lora_alpha,
                "learning_rate": self.training_args.learning_rate,
            },
        )

        # Preparar dataset
        processed_dataset = self.prepare_dataset(dataset_path)

        # Dividir dataset
        train_dataset = processed_dataset["train"]
        eval_dataset = processed_dataset["validation"]

        # Inicializar Trainer
        trainer = Trainer(
            model=self.model,
            args=self.training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
        )

        # Entrenar
        trainer.train()

        # Guardar adapter
        self.model.save_pretrained(f"branches/{self.domain}/adapter")

        # Finalizar wandb
        wandb.finish()

    def evaluate(self):
        """
        Evaluar rendimiento del adapter entrenado
        """
        # Implementar evaluación de calidad del adapter
        pass


def main():
    # Ejemplo de uso
    from modules.core.model.sheily_model import SheilyBaseModel

    base_model = SheilyBaseModel()
    trainer = LoRATrainer(base_model, domain="medicina")
    trainer.train("datasets/medicina.jsonl")


if __name__ == "__main__":
    main()
