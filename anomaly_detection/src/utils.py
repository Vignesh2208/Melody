import os
import warnings
import sys
from scipy.fftpack import fft
from scipy.signal import blackman
import matplotlib.pyplot as plt
import numpy as np
from operator import itemgetter 
from sklearn import mixture
from operator import truediv
from hmmlearn import hmm
from statistics import mean
from statistics import stdev
import math
from sklearn.decomposition import PCA
from autoperiod import *
import statsmodels
from statsmodels import tsa
from statsmodels.tsa import stattools
import statsmodels
from sklearn.metrics import mean_squared_error
warnings.simplefilter("ignore", DeprecationWarning)

def extractAverageSamplingPeriod(trainSamples):
	N = len(trainSamples)
	i = 1
	T = 0.0
	nFields = len(trainSamples[0])
	while i < N :
		T = T + float(trainSamples[i][nFields-1]) - float(trainSamples[i-1][nFields-1])
		i = i + 1

	T = T/float(N*1000)
	return T

def getFFT(signal,T):

	N = len(signal)
	xf = np.linspace(0.0, 1.0/(2.0*float(T)), N/2)
	w = blackman(N)
	ffts = []
	sfft = fft(np.array(signal)*w)

	return xf,sfft

def getRMSErrs(orig_values,arimaResultCls,windowSize,threshold=None) :
	rmsErrs = []
	j = 1
	nSamples = len(orig_values)
	detection_time = None
	while j + windowSize < nSamples :

		predicted_values = arimaResultCls.predict(start=j,end=j+windowSize-1)
		rms_err = math.sqrt(mean_squared_error(predicted_values,orig_values[j:j+windowSize]))
		rmsErrs.append(rms_err)

		if detection_time == None and threshold != None :
			if rms_err > threshold :
				detection_time = j + windowSize -1
		j = j + windowSize




	if j < nSamples - 1 :
		predicted_values = arimaResultCls.predict(start=j,end=nSamples-1)

		rms_err = math.sqrt(mean_squared_error(predicted_values,orig_values[j:]))
		rmsErrs.append(rms_err)


		if detection_time == None and threshold != None :
			if rms_err > threshold :
				detection_time = j + windowSize - 1




	return rmsErrs,detection_time
	

def plotSignal(signal,N=100):


	x = np.linspace(0,N,N)
	plt.plot(x,signal[0:N])
	plt.grid()
	plt.show()

def plotPCAFFTs(trainSamples) :

	nSamples = len(trainSamples)
	assert nSamples > 1
	nSignals = len(trainSamples[0])
	assert nSignals >= 1 

	if nSignals <= 2 :
		f,axarr = plt.subplots(2)
	else :		
		f,axarr = plt.subplots(int(nSignals/2) + nSignals % 2,2)

	N = nSamples
	for i in xrange(0,nSignals):

		subplotX = int(i/2)
		subplotY = i % 2
		signal = np.array(map(itemgetter(i),trainSamples))

		xf,fftVal = getFFT(signal,1)
		if nSignals <= 2 :
			axarr[subplotY].plot(xf[1:N/2], 2.0/N * np.abs(fftVal[1:N/2]), '-r')
			axarr[subplotY].set_title("FFT - Signal No : " + str(i + 1))
			axarr[subplotY].grid(True)
		else :
			axarr[subplotX,subplotY].plot(xf[1:N/2], 2.0/N * np.abs(fftVal[1:N/2]), '-r')
			axarr[subplotX,subplotY].set_title("FFT - Signal No : " + str(i + 1))
			axarr[subplotX,subplotY].grid(True)


	plt.tight_layout()
	plt.show()
		


	
	

def extractOptPCADimensionality(trainSamples) :
	assert len(trainSamples) >= 2 
	nFeatures = len(trainSamples[0])
	pca = PCA(n_components=nFeatures)
	pca.fit(trainSamples)

	percentageExplainedVariance = []
	nComponents = []
	pSum  = 0.0
	nComponents99 = -1

	print "nFeatures Here = ", nFeatures

	for i in xrange(0,len(pca.explained_variance_ratio_)) :
		pSum = pSum + pca.explained_variance_ratio_[i]
		if pSum >= 0.99 and nComponents99 == -1 :
			nComponents99 = i + 1
		nComponents.append(i+1)
		percentageExplainedVariance.append(pSum*100.0)
	
	assert nComponents99 != -1
	return nComponents99

def normalize(timeSeries,nfFactor) :

	if isinstance(timeSeries[0],(int,float)) == True :
		nFeatures = 1
	else :
		nFeatures = len(timeSeries[0])

	assert len(nfFactor) == nFeatures
	nSamples = len(timeSeries)
	normalizedTimeSeries = []

	for i in xrange(0,nFeatures) :
		if nfFactor[i] == 0.0 :
			nfFactor[i] = 1.0

	for i in xrange(0,nSamples):
		if isinstance(timeSeries[0],(int,float)) == True :
			normalizedTimeSeries.append(float(timeSeries[i])/float(nfFactor[0]))
		else :
			normalizedTimeSeries.append(map(truediv,timeSeries[i],nfFactor))


	return np.array(normalizedTimeSeries)


def standardize(timeSeries,musigmaEstimates=None) :

	if musigmaEstimates == None :
		toEstimate = True
	else :
		toEstimate = False



	nSamples = len(timeSeries)
	assert nSamples >= 2
	
	if isinstance(timeSeries[0],(int,float)) == True :
		nFeatures = 1
		if toEstimate == True :
			mu = mean(timeSeries)
			sigma = stdev(timeSeries)
		else :
			mu = musigmaEstimates[0]
			sigma = musigmaEstimates[1]
	else :
		nFeatures = len(timeSeries[0])
		if toEstimate == True :
			mu = []
			sigma = []
			for i in xrange(0,nFeatures) :
				signal = np.array(map(itemgetter(i),timeSeries))
				mu.append(mean(signal))
				sigma.append(stdev(signal))
		else :
			mu = musigmaEstimates[0]
			sigma = musigmaEstimates[1]


	assert mu != None
	assert sigma != None

	standardizedTimeSeries = []

	for i in xrange(0,nSamples):
		if isinstance(timeSeries[0],(int,float)) == True :
			if sigma == 0.0 :
				print "The only signal available is a constant. Any variation can be detected as anomaly. Exiting."
				sys.exit(0)
			else :
				standardizedTimeSeries.append(float(timeSeries[i] - float(mu))/float(sigma))

		else :
			standardizedInput = []
			nNonConstants = 0

			for j in xrange(0,nFeatures):
				if sigma[j] != 0.0 :
					standardizedInput.append(float(timeSeries[i][j] - float(mu[j]))/float(sigma[j]))
					nNonConstants = nNonConstants + 1
				else :
					standardizedInput.append(float(timeSeries[i][j] - 0.0)/float(1.0))
		
			if nNonConstants == 0 :
				print "All available signals available are constant. Any variation can be detected as anomaly. Exiting."
				sys.exit(0)
			else :
				standardizedTimeSeries.append(standardizedInput)


	return np.array(standardizedTimeSeries),(mu,sigma)


# Only for MSU SCADA Dataset
def plotInterestingFFTs(trainCharacteristics) :
	plt.close('all')
	plt.subplots_adjust(hspace=0.7)
	N= len(trainCharacteristics['FunctionCode'][3])

	xf,fCode3 = getFFT(normalize(trainCharacteristics['FunctionCode'][3], [max(trainCharacteristics['FunctionCode'][3])]),1)
	xf,fCode16 = getFFT(normalize(trainCharacteristics['FunctionCode'][16],[max(trainCharacteristics['FunctionCode'][16])]),1)
	xf,networkBytes = getFFT(normalize(trainCharacteristics['Network']['Bytes'],[max(trainCharacteristics['Network']['Bytes'])]),1)
	xf,setpoint = getFFT(normalize(trainCharacteristics['Registers'][16]['w'],[max(trainCharacteristics['Registers'][16]['w'])]),1)	
	xf,pipelinePSI = getFFT(normalize(trainCharacteristics['Registers'][14]['r'],[max(trainCharacteristics['Registers'][14]['r'])]),1)	

	
	f,axarr = plt.subplots(3,2)
	axarr[0,0].set_ylim(0,max(2.0/N * np.abs(fCode3[1:N/2])))
	axarr[0,0].set_xlim([-0.05,0.5])
	axarr[0,0].plot(xf[1:N/2], 2.0/N * np.abs(fCode3[1:N/2]), '-r')
	axarr[0,0].set_title("FFT - Function Code 3 Access")
	axarr[0,0].grid(True)

	
	axarr[0,1].set_ylim(0,max(2.0/N * np.abs(fCode16[1:N/2])))
	axarr[0,1].set_xlim([-0.05,0.5])
	axarr[0,1].plot(xf[1:N/2], 2.0/N * np.abs(fCode16[1:N/2]), '-r')
	axarr[0,1].set_title("FFT - Function Code 16 Access")
	axarr[0,1].grid(True)

	
	axarr[1,0].set_ylim(0,max(2.0/N * np.abs(setpoint[1:N/2])))
	axarr[1,0].set_xlim([-0.05,0.5])
	axarr[1,0].plot(xf[1:N/2], 2.0/N * np.abs(setpoint[1:N/2]), '-r')
	axarr[1,0].set_title("FFT - Setpoint Reg Write")
	axarr[1,0].grid(True)


	axarr[1,1].set_ylim(0,max(2.0/N * np.abs(pipelinePSI[1:N/2])))
	axarr[1,1].set_xlim([-0.05,0.5])
	axarr[1,1].plot(xf[1:N/2], 2.0/N * np.abs(pipelinePSI[1:N/2]), '-r')
	axarr[1,1].set_title("FFT - Pressure Reg Read")
	axarr[1,1].grid(True)


	axarr[2,0].set_ylim(0,max(2.0/N * np.abs(networkBytes[1:N/2])))
	axarr[2,0].set_xlim([-0.05,0.5])
	axarr[2,0].plot(xf[1:N/2], 2.0/N * np.abs(networkBytes[1:N/2]), '-r')
	axarr[2,0].set_title("FFT - Network Bytes")
	axarr[2,0].grid(True)

	axarr[2,1].axis('off')


	plt.tight_layout()
	plt.show()
