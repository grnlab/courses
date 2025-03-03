#!/usr/bin/env python3

import argparse
import numpy as np
import pandas as pd
# P value cutoff for DE of KO gene
pcut=0.05

# Parse command line arguments
parser = argparse.ArgumentParser(description='Process raw input file for workshop.')
parser.add_argument('path_in', type=str, help='Input raw file path')
parser.add_argument('path_out', type=str, help='Output processed file path')
args = parser.parse_args()
path_in = args.path_in
path_out = args.path_out

# Read input file
df=pd.read_excel(path_in,sheet_name='DESeq2 DEG S4',header=0,index_col=None)
# Rename columns
df.rename(columns={'log2FoldChange':'lfc','padj':'p','KO':'target','gene_name':'gene'},inplace=True)
# Filter KO conditions that have the KO gene measured
t1=df['target']==df['gene']
t2=set(df['gene'][t1])
df=df[df['target'].isin(t2)].copy()
t1=df['target']==df['gene']
assert t1.sum()==len(np.unique(df['target'].values)), f'{t1.sum()} != {len(np.unique(df["target"].values))}'
# Filter KO conditions that have lower expression for the KO gene
# t2=(df.loc[t1,'p']<pcut)&(df.loc[t1,'lfc']<0)
# if not t2.all():
# 	t2=set(df.index[t1][t2])
# 	df=df[df['ko'].isin(t2)].copy()
# 	t1=df['ko']==df.index
# 	assert t1.sum()==len(np.unique(df['ko'].values)), f'{t1.sum()} != {len(np.unique(df["ko"].values))}'
# Use raw p-values for the KO gene
df.loc[t1,'p']=df.loc[t1,'pvalue']
assert (df.loc[t1,'p']==df.loc[t1,'pvalue']).all()
# Drop columns that are not needed
df=df[['gene','target','p','lfc']].copy()
# Drop rows with missing values, indicating failed QC for DE
df.dropna(inplace=True)

# Write output file
df.to_csv(path_out,sep="\t",index=False,header=True)