import pandas as pd
import numpy as np
import re
import pickle
import urllib.request as urllib
import zipfile
import os
import argparse
import pickle


# ICD 9 Clinical Classification System Dictionaries
def get_icd9_ccs(save_path='./data'):
    save_name_icd9 = 'name_icd9_map.pkl'
    save_tok_icd9 = 'diag.vocab'
    _fname_singledx = 'AppendixASingleDX.txt'
    path_ccs = os.path.join(save_path, _fname_singledx)

    if (os.path.isfile(os.path.join(save_path, save_tok_icd9)) and
            os.path.isfile(os.path.join(save_path, save_name_icd9))):
        name_icd9 = pickle.load(open(os.path.join(save_path, save_name_icd9), 'rb'))
        tok_icd9 = pickle.load(open(os.path.join(save_path, save_tok_icd9), 'rb'))
        return name_icd9, tok_icd9

    if (not os.path.isfile(path_ccs)):
        urllib.urlretrieve('https://hcup-us.ahrq.gov/toolssoftware/ccs/AppendixASingleDX.txt', os.path.join(save_path, 'AppendixASingleDX.txt'))

    text = str(open(path_ccs, 'rb').read())
    text = text.split('\\n')
    text = text[4:] # ignore headling lines
    text = [t.strip(' ') for t in text if t != '']
    text = [re.sub(' +', ' ', t) for t in text]

    reg = r'^[1-9]+\s+[a-zA-Z]'
    name_icd9 = {}
    tok_icd9 = {}
    prev = -1

    for t in text:
        if len(re.findall(reg, t)) > 0:
            tt = t.split(' ')
            name_icd9[int(tt[0])] = ' '.join(tt[1:])
            prev = tt[0]
            tok_icd9[prev] = []
            first = True
        if (not first):
            tt = t.split(' ')
            tok_icd9[prev].extend(tt)
        else:
            first = False
    t = {}
    for k, v in tok_icd9.items():
        for vv in v:
            t[vv] = int(k)
    tok_icd9 = t
    # incremental tokens 1, 2, 3..
    t = {}
    for k, v in name_icd9.items():
        if (k not in t.keys()):
            t[k] = len(t)

    # retokenize
    for k, v in tok_icd9.items():
        tok_icd9[k] = t[v]

    with open(os.path.join(save_path, save_name_icd9), 'wb') as handle:
        pickle.dump(name_icd9, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open(os.path.join(save_path, save_tok_icd9), 'wb') as handle:
        pickle.dump(tok_icd9, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return name_icd9, tok_icd9

def get_cptevents_ccs(save_path='./data'):

    def process_cr(cr):
        t = cr.split('-')
        mi, ma = t[0].strip(), t[1].strip()
        mi = mi.strip("'")
        ma = ma.strip("'")
        reg = r'[a-zA-Z]+'
        c = ''.join(re.findall(reg, mi))
        c2 = ''.join(re.findall(reg, ma))
        reg = r'[1-9]+'
        mi = ''.join(re.findall(reg, mi))
        ma = ''.join(re.findall(reg, ma))
        mi = int(mi)
        ma = int(ma)
        if (ma < mi):
            t = ma
            ma = mi
            mi = ma
        return [mi, ma, c, c2]

    save_name_cptccs = 'cpt_ccs_df.pkl'
    _fname_cptproc = '2019_ccs_services_procedures.zip'
    path_to_file = os.path.join(save_path, _fname_cptproc)

    if (os.path.isfile(os.path.join(save_path, save_name_cptccs))):
        df = pickle.load(open(path_to_file, 'rb'))
        return df

    if (not os.path.isfile(path_to_file[:-4])):
        urllib.urlretrieve('https://hcup-us.ahrq.gov/toolssoftware/ccs_svcsproc/2019_ccs_services_procedures.zip', _fname_cptproc)
        zip_ref = zipfile.ZipFile(path_to_file, 'r')
        zip_ref.extractall('./')
        zip_ref.close()
        os.remove(path_to_file)

    #outputs a dataframe with min and max code ranges
    df = pd.read_csv(path_to_file[:-3] + 'csv', header=1)
    df.loc[:, 'Code Range'] = df['Code Range'].apply(process_cr)
    t = pd.DataFrame(df['Code Range'].tolist(), columns=['min', 'max', 'minc', 'maxc'])
    df = df.join(t)
    df = df.drop('Code Range', axis=1)

    with open('./cpt_ccs_df.pkl', 'wb') as handle:
        pickle.dump(df, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return df
if __name__ == '__main__':
    parser = argparse.ArgumentParser('HCUP-US CCS Tools ICD9/CPT')
    parser.add_argument('-t', '--tool', type=str, default='', help='tools available are ICD9 or CPT')
    parser.add_argument('-sp', '--save_path', type=str, default='.', help='path to save output files')


    args = parser.parse_args()

    assert args.tool == 'ICD9' or args.tool == 'CPT', "tool: choose between [ICD9, CPT]"

    if not os.path.exists(args.save_path):
        os.makedirs(args.save_path)

    if args.tool == 'ICD9':
        get_icd9_ccs(args.save_path)
    elif args.tool == 'CPT':
        get_cptevents_ccs(args.save_path)

