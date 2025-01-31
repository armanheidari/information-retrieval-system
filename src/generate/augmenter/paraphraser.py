import sys

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from path_handler import PathManager

path_manager = PathManager()
sys.path.append(str(path_manager.get_base_directory()))

from src.generate.config.config import ParaphraserConfig


class Paraphraser:
    def __init__(self, config: ParaphraserConfig):
        self.config = config
        self.tokenizer = AutoTokenizer.from_pretrained(config.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(config.model_name).to(config.device)

    def _tokenize(self, inputs: str) -> torch.Tensor:
        tokenized_inputs = self.tokenizer(
            f'paraphrase: {inputs}',
            truncation=True,
            padding="longest",
            return_tensors="pt", 
            max_length=self.config.max_length,
        )
        
        tokenized_inputs = tokenized_inputs.input_ids.to(self.config.device)  
        return tokenized_inputs
        
    def paraphrase(self, inputs: str) -> str:
        tokenized_inputs = self._tokenize(inputs)
        
        encoded_outputs = self.model.generate(
            tokenized_inputs, 
            temperature=self.config.temperature, 
            repetition_penalty=self.config.repetition_penalty,
            num_return_sequences=self.config.num_return_sequences, 
            no_repeat_ngram_size=self.config.no_repeat_ngram_size,
            num_beams=self.config.num_beams, 
            num_beam_groups=self.config.num_beam_groups,
            max_length=self.config.max_length, 
            diversity_penalty=self.config.diversity_penalty
        )

        decoded_outputs = self.tokenizer.batch_decode(
            sequences=encoded_outputs, 
            skip_special_tokens=True
        )

        return decoded_outputs


if __name__ == "__main__":
    from src.generate.config.default import PARAPHRASER_DEFAULT_CONFIG
    
    paraphraser = Paraphraser(PARAPHRASER_DEFAULT_CONFIG)
    print(paraphraser.paraphrase("Hello, how are you?"))