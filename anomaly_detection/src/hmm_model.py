import warnings
from utils import *
warnings.simplefilter("ignore", DeprecationWarning)



def getStateSimilarityMatrix(observations,nStages,nMixtures) :

	Sim = []
	j = 0
	while j < 2*nStages :
		currStateSim = []
		i = 0
		while i < 2*nStages :
			if j < nStages:
				srcStateGMM = observations[j]['gmms'][nMixtures - 1]
				if i < nStages :
					dstStateSamples = observations[i]['samples']
				elif len(observations[i % nStages]['anomalousSamples']) > 0 :
					dstStateSamples = observations[i % nStages]['anomalousSamples']
				if dstStateSamples != None :
					currStateSim.append(srcStateGMM.bic(np.array(dstStateSamples)))
					dstStateSamples = None
			elif len(observations[j % nStages]['anomalousSamples']) > 0 :
				srcStateGMM = observations[j % nStages]['agmms'][nMixtures - 1]
				if i < nStages :
					dstStateSamples = observations[i]['samples']
				elif len(observations[i % nStages]['anomalousSamples']) > 0 :
					dstStateSamples = observations[i % nStages]['anomalousSamples']
				if dstStateSamples != None :
					currStateSim.append(srcStateGMM.bic(np.array(dstStateSamples)))
					dstStateSamples = None
			i = i + 1

		Sim.append(currStateSim)
		j = j + 1
		
	print "BIC State Similarity Matrix (Lower values => more Similar) = "
	print np.array(Sim)
	return Sim
				
				



def scoreSamples(samples,hmm,windowSize,debug=False) :
	scores = []
	assert windowSize > 0
	N = windowSize
	nWindows = int(len(samples)/windowSize)
	nSamples = len(samples)
	i = 0
	while i + N < nSamples :
		scores.append(hmm.score(np.array(samples[i:i+N])))
		#i = i  + 1
		i = i + N
		
	scores.append(hmm.score(np.array(samples[i:])))
	if debug == True :
		print "scores = ", scores
	if len(scores) > 1 :
		return mean(scores)/float(windowSize),(1.96*stdev(scores))/float(math.sqrt(len(scores))),scores
	else :
		return mean(scores)/float(windowSize),0.0,scores
	

def trainHMM(observations,trainSamples,nMixtures=1,nStages=1,cvType='diag') :

	nStates = nStages
	assert nStates > 0
	transmat = []
	startProb = [float(1.0/nStates)]*nStates
	startProb = [0.0]*nStates
	startProb[0] = 1.0
	
	for j in xrange(0,nStates) :
		transmat.append([0.0]*nStates)
		transmat[j][j] = 1


	
	
	transmat = np.array(transmat)
	means = []
	covars = []
	weights = []
	gmms = []

	for j in xrange(0,nStages) :
		if j < nStages :
			gmm = observations[j]['gmms'][nMixtures - 1]
		
		if gmm != None :	
			means.append(gmm.means_)
			covars.append(gmm.covars_)
			weights.append(gmm.weights_)
			gmms.append(gmm)
			gmm = None


		

	means = np.array(means)
	covars = np.array(covars)
	weights = np.array(weights)
	
	
	

	if nStates >= nStages :
		gmmHMM = hmm.GMMHMM(n_components=nStates,n_mix=nMixtures,covariance_type=cvType,params='', init_params='',n_iter=1000,tol=0.0001)
		gmmHMM.means_ = means
		gmmHMM.covars_ = covars
		gmmHMM.weights_ = weights

		"""
		gmmHMM = hmm.GaussianHMM(n_components=nStates,n_iter=10000,tol=0.0001,params='',covariance_type=cvType,init_params='')
		gmmHMM.means_ = means[0]
		gmmHMM.covars_ = covars[0]
		gmmHMM.weights_ = weights[0]
		"""

		gmmHMM.startprob_ = np.array(startProb)
		gmmHMM.transmat_  = np.array(transmat)
		gmmHMM.gmms_ = gmms
		#gmmHMM.fit(np.array(trainSamples))
		
		print "GMMHMM Score = ", gmmHMM.score(np.array(trainSamples))
		
		
		

	return gmmHMM
	


def trainGMMs(trainSamples,sysPeriod=1,nMaxMixtures=10,cvType='full') :
	assert len(trainSamples) > 0
	nFeatures = len(trainSamples[0])
	nSamples = len(trainSamples)
	nStages = sysPeriod
	observations = {}
	featureMax = []

	for i in xrange(0,nStages):
		observations[i] = {}
		observations[i]['samples'] = []
		observations[i]['gmms'] = []
		observations[i]['bic'] = []


	for i in xrange(0,nSamples):
		currStage = i % nStages
		observations[currStage]['samples'].append(trainSamples[i])


	max_BIC_List = []
	for i in xrange(1,nMaxMixtures+1):
		max_BIC = -np.infty
		for j in xrange(0,nStages) :
			g = mixture.GMM(n_components=i,covariance_type=cvType,n_iter=100000,tol=0.0001)
			g.fit(np.array(observations[j]['samples']))
			bic = float(g.bic(np.array(observations[j]['samples'])))
			observations[j]['bic'].append(bic)
			observations[j]['gmms'].append(g)
			
			if bic > max_BIC :
				max_BIC = bic
		max_BIC_List.append(max_BIC)

	
	
	nOptMixtures = max_BIC_List.index(min(max_BIC_List)) + 1
	
	#print "Max BICs For Samples w.r.t nMixtures = ", max_BIC_List
	print "Optimum number of Mixtures = ", nOptMixtures

	assert nOptMixtures <= nMaxMixtures
	return observations, nOptMixtures