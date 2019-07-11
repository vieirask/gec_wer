#!/usr/bin/zsh
## This script is to run the complete GEC system on any given test set

# set -e
# set -x

#source ../paths.sh
BASE_DIR=/clwork/kengo/model/WER/mlconvgec2018
DATA_DIR=$BASE_DIR/data
MODEL_DIR=$BASE_DIR/GEC_tra_sam_token_src
SCRIPTS_DIR=$BASE_DIR/scripts
SOFTWARE_DIR=$BASE_DIR/software



if [ $# -ge 3 ]; then
    input_file=$1
    output_path=$2
    model_path=$3
else
    echo "Please specify the paths to the input_file and output directory"
    echo "Usage: `basename $0` <input_file> <output_dir> <gpu-device-num(e.g: 0)> <path to model_file/dir> [optional args: <path-to-reranker-weights> <featuers,e.g:eo,eolm]"   >&2
fi
if [[ -d "$model_path" ]]; then
    models=`ls ${model_path}/*pt | tr '\n' ' ' | sed "s| \([^$]\)| --path \1|g"`
    echo ${models}
elif [[ -f "$model_path" ]]; then
    models=${model_path}
elif [[ ! -e "$model_path" ]]; then
    echo "Model path not found: $model_path"
fi


FAIRSEQPY=${SOFTWARE_DIR}/fairseq-py

token_num=$4
output_dir=${output_path}_${token_num}
mkdir -p ${output_dir}

beam=12
nbest=${beam}
threads=12

current_dir=$(cd $(dirname $0) && pwd)

DATA_DIR=$5

device=$6

# path to scripts directories
M2_SCRIPTS=${DATA_DIR}/scripts/m2_scripts/
MOSES_SCRIPTS=${DATA_DIR}/scripts/moses_scripts/
LANG8_SCRIPTS=${DATA_DIR}/scripts/lang-8_scripts/
NLTK_SCRIPTS=${DATA_DIR}/scripts/nltk_scripts/

REPLACE_UNICODE=${MOSES_SCRIPTS}/replace-unicode-punctuation.perl
REMOVE_NON_PRINT=${MOSES_SCRIPTS}/remove-non-printing-char.perl
NORMALIZE_PUNCT=${MOSES_SCRIPTS}/normalize-punctuation.perl

TOKENIZER="$NLTK_SCRIPTS/word-tokenize.py"

cat ${input_file} | ${REPLACE_UNICODE} | ${REMOVE_NON_PRINT} | sed  's/\\"/\"/g' | sed 's/\\t/ /g' | ${NORMALIZE_PUNCT} |  ${TOKENIZER}  > ${output_dir}/input.tok.txt

$SCRIPTS_DIR/apply_bpe.py -c ${MODEL_DIR}/models/bpe_model/train.bpe.model < ${output_dir}/input.tok.txt > ${output_dir}/input.bpe.txt

# add token
python path to add_token.py ${output_dir}/input.bpe.txt ${token_num} ${output_dir}

# running fairseq on the input text
if [ -n "$device" ]; then
  CUDA_VISIBLE_DEVICES=$device python ${FAIRSEQPY}/generate.py --no-progress-bar --path ${models} --beam ${beam} --nbest ${beam} --interactive --workers ${threads} ${MODEL_DIR}/processed/bin < ${output_dir}/input.bpe.token.txt > ${output_dir}/output.bpe.nbest.txt
else
  python ${FAIRSEQPY}/generate.py --cpu --no-progress-bar --path ${models} --beam ${beam} --nbest ${beam} --interactive --workers ${threads} ${MODEL_DIR}/processed/bin < ${output_dir}/input.bpe.token.txt > ${output_dir}/output.bpe.nbest.txt
fi

# getting best hypotheses
cat ${output_dir}/output.bpe.nbest.txt | grep "^H"  | python -c "import sys; x = sys.stdin.readlines(); x = ' '.join([ x[i] for i in range(len(x)) if(i%$nbest == 0) ]); print(x)" | cut -f3 > ${output_dir}/output.bpe.txt

# debpe
cat ${output_dir}/output.bpe.txt | sed 's|@@ ||g' | sed '$ d' > ${output_dir}/output.tok.txt
