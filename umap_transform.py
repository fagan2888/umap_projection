#! /usr/bin/python
import sys
import numpy as np
import umap

from scipy.stats.stats import spearmanr
from scrna_utils import load_marker_matrix


refrun_NAME = sys.argv[1]
marker_INFILE = sys.argv[2]
proj_PREFIX = sys.argv[3]
k_PARAM = int(sys.argv[4])
used_genes = sys.argv[5]
projrun_NAMES = sys.argv[6::]


print('Loading data...')
rmatrix_INFILE = refrun_NAME+'/'+refrun_NAME+'.matrix.txt'
rgids,rgenes,rmatrix = load_marker_matrix(rmatrix_INFILE,marker_INFILE,1)

pdata = []
for run in projrun_NAMES:
	pmatrix_INFILE = run+'/'+run+'.matrix.txt'
	pdata.append(load_marker_matrix(pmatrix_INFILE,marker_INFILE,1))

print(len(pdata),len(pdata[0]),len(pdata[0][0]),len(pdata[0][1]),len(pdata[0][2]))

print('Filtering data...')
rmatrix_filt = []
pdata_filt = [[] for run in projrun_NAMES]
with open(used_genes,'w') as g:
	for i in range(len(rgenes)):
		if sum(rmatrix[i]) > 0:
			ct=0
			for pdat in pdata:
				if sum(pdat[2][i]) > 0:
					ct+=1
			if ct == len(pdata):
				for j in range(len(projrun_NAMES)):
					pdata_filt[j].append(pdata[j][2][i])
				rmatrix_filt.append(rmatrix[i])
				gene = rgids[i]
				g.write('%(gene)s\n' % vars())

rmatrix_filt = np.array(rmatrix_filt)
pdata_filt = np.array(pdata_filt)
print(len(pdata_filt[0]))
del pdata
del rmatrix

print('Computing model...')
umap_model = umap.UMAP(n_neighbors=k_PARAM,random_state=42,metric='spearman').fit(rmatrix_filt.T)
model_OUTFILE = proj_PREFIX+'.umap_proj_model.txt'
np.savetxt(model_OUTFILE,umap_model.embedding_,delimiter='\t')

print('Computing projections...')
for i in range(len(pdata_filt)):
	umap_proj = umap_model.transform(np.float32(pdata_filt[i].T))
	proj_OUTFILE = proj_PREFIX+'.'+projrun_NAMES[i]+'.umap_proj.txt'
	np.savetxt(proj_OUTFILE,umap_proj,delimiter='\t')
	
