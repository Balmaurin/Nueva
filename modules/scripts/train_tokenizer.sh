#!/usr/bin/env bash
set -euo pipefail

# Directorios
CORPUS=datasets/corpus_clean.txt
OUT=core/model/tokenizer/shaili_sp

# Verificar existencia del corpus
if [ ! -f "$CORPUS" ]; then
    echo "Error: Corpus no encontrado en $CORPUS"
    exit 1
fi

# Entrenar tokenizador SentencePiece
spm_train --input="$CORPUS" \
  --model_prefix="$OUT" \
  --vocab_size=32000 \
  --model_type=unigram \
  --character_coverage=0.9995 \
  --input_sentence_size=20000000 \
  --shuffle_input_sentence=true \
  --normalization_rule_name=nmt_nfkc \
  --user_defined_symbols=<pad>,<eos>,<sep>,<inst>,<resp>,<sys>,<med>,<math>,<prog>,<soc>,<sport>

# Verificar resultado
if [ -f "${OUT}.model" ] && [ -f "${OUT}.vocab" ]; then
    echo "Tokenizador entrenado exitosamente en $OUT"
else
    echo "Error: Entrenamiento de tokenizador fallido"
    exit 1
fi
