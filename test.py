'''Testing script'''

def process_twitter_sent():
    from pathlib import Path
    import json
    from tqdm.auto import tqdm
    import pandas as pd

    Path('datasets/twitter_sent').mkdir()

    input_path = Path('datasets/twitter_sent.csv')
    output_paths = [Path('datasets/twitter_sent/train.jsonl'),
                    Path('datasets/twitter_sent/test.jsonl')]

    df = pd.read_csv(input_path, header=0).dropna()

    train = df.query('part == "train"')
    test = df.query('part == "test"')

    train = train.reset_index(drop=True)
    test = test.reset_index(drop=True)

    for split, output_path in zip([train, test], output_paths):
        for idx, row in tqdm(split.iterrows()):
            data_dict = dict(tweet_id=row.twitterid, label=row.polarity)
            json_line = json.dumps(data_dict)
            with output_path.open('a') as f:
                f.write(json_line)
                if idx < len(split) - 1:
                    f.write('\n')


def process_lcc2():
    from pathlib import Path
    import json
    from tqdm.auto import tqdm
    import pandas as pd
    from sklearn.model_selection import train_test_split

    Path('datasets/lcc2').mkdir()

    input_path = Path('datasets/lcc2.csv')
    output_paths = [Path('datasets/lcc2/train.jsonl'),
                    Path('datasets/lcc2/test.jsonl')]

    df = pd.read_csv(input_path, header=0).dropna(subset=['valence', 'text'])

    for idx, row in df.iterrows():
        try:
            int(row.valence)
        except:
            df = df.drop(idx)
            continue
        if row.text.strip() == '':
            df = df.drop(idx)
        else:
            if int(row.valence) > 0:
                sentiment = 'positiv'
            elif int(row.valence) < 0:
                sentiment = 'negativ'
            else:
                sentiment = 'neutral'
            df.loc[idx, 'valence'] = sentiment

    train, test = train_test_split(df, test_size=0.3, stratify=df.valence)
    train = train.reset_index(drop=True)
    test = test.reset_index(drop=True)

    for split, output_path in zip([train, test], output_paths):
        for idx, row in tqdm(split.iterrows()):
            data_dict = dict(text=row.text, label=row.valence)
            json_line = json.dumps(data_dict)
            with output_path.open('a') as f:
                f.write(json_line)
                if idx < len(split) - 1:
                    f.write('\n')


def process_lcc1():
    from pathlib import Path
    import json
    from tqdm.auto import tqdm
    import pandas as pd
    from sklearn.model_selection import train_test_split

    Path('datasets/lcc1').mkdir()

    input_path = Path('datasets/lcc1.csv')
    output_paths = [Path('datasets/lcc1/train.jsonl'),
                    Path('datasets/lcc1/test.jsonl')]

    df = pd.read_csv(input_path, header=0).dropna(subset=['valence', 'text'])

    for idx, row in df.iterrows():
        try:
            int(row.valence)
        except:
            df = df.drop(idx)
            continue
        if row.text.strip() == '':
            df = df.drop(idx)
        else:
            if int(row.valence) > 0:
                sentiment = 'positiv'
            elif int(row.valence) < 0:
                sentiment = 'negativ'
            else:
                sentiment = 'neutral'
            df.loc[idx, 'valence'] = sentiment

    train, test = train_test_split(df, test_size=0.3, stratify=df.valence)
    train = train.reset_index(drop=True)
    test = test.reset_index(drop=True)

    for split, output_path in zip([train, test], output_paths):
        for idx, row in tqdm(split.iterrows()):
            data_dict = dict(text=row.text, label=row.valence)
            json_line = json.dumps(data_dict)
            with output_path.open('a') as f:
                f.write(json_line)
                if idx < len(split) - 1:
                    f.write('\n')


def process_europarl2():
    from pathlib import Path
    import json
    from tqdm.auto import tqdm
    import pandas as pd
    from sklearn.model_selection import train_test_split

    Path('datasets/europarl2').mkdir()

    input_path = Path('datasets/europarl2.csv')
    output_paths = [Path('datasets/europarl2/train.jsonl'),
                    Path('datasets/europarl2/test.jsonl')]

    df = pd.read_csv(input_path, header=0).dropna()

    train, test = train_test_split(df, test_size=0.3, stratify=df.polarity)
    train = train.reset_index(drop=True)
    test = test.reset_index(drop=True)

    for split, output_path in zip([train, test], output_paths):
        for idx, row in tqdm(split.iterrows(), total=len(split)):
            data_dict = dict(text=row.text, label=row.polarity)
            json_line = json.dumps(data_dict)
            with output_path.open('a') as f:
                f.write(json_line)
                if idx < len(split) - 1:
                    f.write('\n')


def process_europarl1():
    from pathlib import Path
    import json
    from tqdm.auto import tqdm
    import pandas as pd
    from sklearn.model_selection import train_test_split

    input_path = Path('datasets/europarl1.csv')
    output_paths = [Path('datasets/europarl1/train.jsonl'),
                    Path('datasets/europarl1/test.jsonl')]

    df = pd.read_csv(input_path, header=0).dropna(subset=['valence', 'text'])

    for idx, row in df.iterrows():
        try:
            int(row.valence)
        except:
            df = df.drop(idx)
            continue
        if row.text.strip() == '':
            df = df.drop(idx)
        else:
            if int(row.valence) > 0:
                sentiment = 'positiv'
            elif int(row.valence) < 0:
                sentiment = 'negativ'
            else:
                sentiment = 'neutral'
            df.loc[idx, 'valence'] = sentiment

    train, test = train_test_split(df, test_size=0.3, stratify=df.valence)
    train = train.reset_index(drop=True)
    test = test.reset_index(drop=True)

    for split, output_path in zip([train, test], output_paths):
        for idx, row in tqdm(split.iterrows()):
            data_dict = dict(text=row.text, label=row.valence)
            json_line = json.dumps(data_dict)
            with output_path.open('a') as f:
                f.write(json_line)
                if idx < len(split) - 1:
                    f.write('\n')


def process_angrytweets():
    from pathlib import Path
    import json
    from tqdm.auto import tqdm
    import pandas as pd
    from sklearn.model_selection import train_test_split

    input_path = Path('datasets/angry_tweets.csv')
    output_paths = [Path('datasets/angry_tweets/train.jsonl'),
                    Path('datasets/angry_tweets/test.jsonl')]

    df = pd.read_csv(input_path, header=0)

    for idx, row in df.iterrows():
        labels = json.loads(row.annotation.replace('\'', '\"'))
        if len(set(labels)) > 1 or 'skip' in labels:
            df = df.drop(idx)
        else:
            df.loc[idx, 'annotation'] = labels[0]

    train, test = train_test_split(df, test_size=0.3, stratify=df.annotation)
    train = train.reset_index(drop=True)
    test = test.reset_index(drop=True)

    for split, output_path in zip([train, test], output_paths):
        for idx, row in tqdm(split.iterrows()):
            data_dict = dict(tweet_id=row.twitterid, label=row.annotation)
            json_line = json.dumps(data_dict)
            with output_path.open('a') as f:
                f.write(json_line)
                if idx < len(split) - 1:
                    f.write('\n')


def process_dkhate():
    from pathlib import Path
    import json
    from tqdm.auto import tqdm
    import pandas as pd

    input_paths = [Path('datasets/dkhate/dkhate.train.tsv'),
                   Path('datasets/dkhate/dkhate.test.tsv')]
    output_paths = [Path('datasets/dkhate/dkhate_train.jsonl'),
                    Path('datasets/dkhate/dkhate_test.jsonl')]

    for input_path, output_path in zip(input_paths, output_paths):
        df = pd.read_csv(input_path, sep='\t')
        for idx, row in tqdm(df.iterrows()):
            data_dict = dict(tweet=row.tweet, label=row.subtask_a)
            json_line = json.dumps(data_dict)
            with output_path.open('a') as f:
                f.write(json_line)
                if idx < len(df) - 1:
                    f.write('\n')

def process_dane():
    from pathlib import Path
    import json
    from tqdm.auto import tqdm
    import re

    input_paths = [Path('datasets/dane/ddt.train.conllu'),
                   Path('datasets/dane/ddt.dev.conllu'),
                   Path('datasets/dane/ddt.test.conllu')]
    output_paths = [Path('datasets/dane/dane_train.jsonl'),
                    Path('datasets/dane/dane_val.jsonl'),
                    Path('datasets/dane/dane_test.jsonl')]

    for input_path, output_path in zip(input_paths, output_paths):
        tokens = list()
        pos_tags = list()
        heads = list()
        deps  = list()
        ner_tags = list()
        ids = list()
        doc = ''
        lines = input_path.read_text().split('\n')
        for idx, line in enumerate(tqdm(lines)):
            if line.startswith('# text = '):
                doc = re.sub('# text = ', '', line)
            elif line.startswith('#'):
                continue
            elif line == '':
                if tokens != []:
                    data_dict = dict(ids=ids,
                                     doc=doc,
                                     tokens=tokens,
                                     pos_tags=pos_tags,
                                     heads=heads,
                                     deps=deps,
                                     ner_tags=ner_tags)
                    json_line = json.dumps(data_dict)
                    with output_path.open('a') as f:
                        f.write(json_line)
                        if idx < len(lines) - 1:
                            f.write('\n')
                ids = list()
                tokens = list()
                pos_tags = list()
                heads = list()
                deps = list()
                ner_tags = list()
                doc = ''
            else:
                data = line.split('\t')
                ids.append(data[0])
                tokens.append(data[1])
                pos_tags.append(data[3])
                heads.append(data[6])
                deps.append(data[7])
                ner_tags.append(data[9].replace('name=', '').split('|')[0])

if __name__ == '__main__':
    process_dane()
