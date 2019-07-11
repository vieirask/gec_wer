import sys

if __name__ == '__main__':
    input_path = str(sys.argv[1])
    token_num = int(sys.argv[2])
    out_put_dir = str(sys.argv[3])

    token_list = ['first', 'second', 'third', 'fourth', 'fifth']

    with open(f'{out_put_dir}/input.bpe.token.txt', 'w') as out_file:
        for line in open(input_path, 'r'):
            out_file.write(f'<{token_list[token_num]}> {line}')
