#!/usr/bin/zsh
## This script is to run the complete GEC system on any given test set

set -e
set -x

source ../paths.sh

if [ $# -ge 4 ]; then
    input_file=$1
    output_dir=$2
    device=$3
    model_path=$4
else
    echo "Please specify the paths to the input_file and output directory"
    echo "Usage: `basename $0` <input_file> <output_dir> <gpu-device-num(e.g: 0)> <path to model_file/dir> [optional args: <path-to-reranker-weights> <featuers,e.g:eo,eolm]"   >&2
fi
if [[ -d "$model_path" ]]; then
    models=`ls $model_path/*pt | tr '\n' ' ' | sed "s| \([^$]\)| --path \1|g"`
    echo $models
elif [[ -f "$model_path" ]]; then
    models=$model_path
elif [[ ! -e "$model_path" ]]; then
    echo "Model path not found: $model_path"
fi


FAIRSEQPY=$SOFTWARE_DIR/fairseq-py

token_num=$5


beam=12
nbest=$beam
threads=12

current_dir=$(cd $(dirname $0) && pwd)

mkdir -p $output_dir
$SCRIPTS_DIR/apply_bpe.py -c models/bpe_model/train.bpe.model < $input_file > $output_dir/input.bpe.txt

# add token
python path to add_token.py $output_dir/input.bpe.txt $token_num $output_dir

# running fairseq on the test data
CUDA_VISIBLE_DEVICES=$device python $FAIRSEQPY/generate.py --no-progress-bar --path $models --beam $beam --nbest $beam --interactive --workers $threads processed/bin < $output_dir/input.bpe.token.txt > $output_dir/output.bpe.nbest.txt

# getting best hypotheses
cat $output_dir/output.bpe.nbest.txt | grep "^H"  | python -c "import sys; x = sys.stdin.readlines(); x = ' '.join([ x[i] for i in range(len(x)) if(i%$nbest == 0) ]); print(x)" | cut -f3 > $output_dir/output.bpe.txt

# debpe
cat $output_dir/output.bpe.txt | sed 's|@@ ||g' | sed '$ d' > $output_dir/output.tok.txt
