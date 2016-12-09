import os
import sys
import numpy as np
import scipy as sp
from scipy.fftpack import fft, ifft
from scipy.signal import blackman
import matplotlib.pyplot as plt
from operator import itemgetter 
from sklearn import mixture
from operator import truediv
from statistics import mean
from statistics import stdev
from scipy import signal
import math
from numpy import random
from scipy.signal import hamming 
from frequency_estimator import * 


def getFFT(signal,T):

	N = len(signal)
	xf = np.linspace(0.0, 1.0/(2.0*float(T)), N/2)
	w = blackman(N)
	ffts = []
	sfft = fft(np.array(signal)*w)

	return xf,sfft


def permute(X) :
	N = len(X)
	permutation = [0]*N

	for i in xrange(0,N) :
		permutation[i] = X[i]

	for i in xrange(0,N-1) :
		swapIdx = np.random.randint(i,N)
		assert swapIdx <= N-1
		tmp = permutation[i]
		permutation[i] = permutation[swapIdx]
		permutation[swapIdx] = tmp

	return permutation


def getPowerSpectralDensity(X,fs=1.0):
	assert fs > 0
	f, Pxx_den = signal.periodogram(X, fs,scaling='density',window=None,detrend=False)
	return (f,Pxx_den)

def getPowerSpectralThreshold(X,nPermutations=100,fs=1.0,percentile=99) :
	maxPower = []
	for i in xrange(0,nPermutations) :
		permutation = permute(X)
		f,PWSD = getPowerSpectralDensity(permutation,fs)
		maxPwr = max(PWSD)
		maxPower.append(maxPwr)

	maxPower  = sorted(maxPower)
	percentileIdx = int(nPermutations*percentile/100)
	assert percentileIdx <= nPermutations - 1


	return maxPower[percentileIdx]

def find_nearest(array,value):
    idx = (np.abs(array-value)).argmin()
    return array[idx]

def fourierExtrapolation(x, n_predict,n_harm,candidatePeriods):
	n = x.size
	t = np.arange(0, n)
	x_freqdom = sp.fftpack.fft(x)  		# detrended x in frequency domain
	f = sp.fftpack.fftfreq(n)
	flist = f.tolist()
	dominantPeriods = []
	indexes = list(range(n))
	# sort indexes by frequency, higher -> lower
	indexes.sort(key = lambda i: np.absolute(x_freqdom[i]),reverse=True)
	j = 0

	for i in candidatePeriods.keys():
		fi = 1.0/float(i)
		nearestFreq = find_nearest(f,fi)
		if np.abs(nearestFreq - fi) <= 0.01: 
			idx = flist.index(nearestFreq)
			negidx = flist.index(-1*nearestFreq)
			dominantPeriods.append(1.0/nearestFreq)
			indexes[j] = idx
			indexes[j+1] = negidx
			j = j + 2

	#print "dominant Periods = ", dominantPeriods, " n_harmonics = ", n_harm, " n_domperiods = ", len(dominantPeriods)
	t = np.arange(0, n + n_predict)
	restored_sig = np.zeros(t.size)
	for i in indexes[:1 + 2*n_harm]:
	    ampli = np.absolute(x_freqdom[i]) / n   # amplitude
	    phase = np.angle(x_freqdom[i])          # phase
	    restored_sig += ampli * np.cos(2 * np.pi * f[i] * t + phase)
	return restored_sig

def getPeriodHints(X,fs=1.0) :
	pThreshold = getPowerSpectralThreshold(X=X,nPermutations=100,fs=fs,percentile=99)
	assert pThreshold >= 0.0

	candidatePeriods = []
	candidateIntPeriods = {}
	f,PWSD = getPowerSpectralDensity(X,fs)
	PWSD = np.array(PWSD)
	N = len(X)
	NCoeffs = len(PWSD)
	for i in xrange(0,NCoeffs) :
		if PWSD[i] >= pThreshold :
			if i > 0 and PWSD[i] > PWSD[i-1] and PWSD[i] > PWSD[i+1]:
				candidatePeriods.append(float(1.0/f[i]))


	newCandidatePeriods = []
	for i in xrange(0,len(candidatePeriods)) :
		if candidatePeriods[i] < float(N/2) and candidatePeriods[i] > 2.0 :
			newCandidatePeriods.append(candidatePeriods[i])

			
	candidatePeriods = newCandidatePeriods
	if len(candidatePeriods) == 0 :

		print "Periodicity Test failed. Threshold = " , pThreshold
		return f,PWSD,candidatePeriods,pThreshold,0
		#sys.exit(0)

	# converting to closest integer periods 
	nCandidatePeriods = len(candidatePeriods)
	for i in xrange(0, nCandidatePeriods) :
		closestIntPeriod = (round(candidatePeriods[i],2))
		if closestIntPeriod in candidateIntPeriods.keys() :
			candidateIntPeriods[closestIntPeriod] = candidateIntPeriods[closestIntPeriod] + 1
		else :
			candidateIntPeriods[closestIntPeriod] =  1



	index1=10000;
	frameSize=256;
	index2=index1+frameSize-1;
	frames=X[index1:int(index2)+1]

	zeroPaddedFrameSize=16*frameSize;

	frames2=frames*hamming(len(frames));   
	frameSize=len(frames);

	if (zeroPaddedFrameSize>frameSize):
		zrs= np.zeros(zeroPaddedFrameSize-frameSize);
		frames2=np.concatenate((frames2, zrs), axis=0)

	#estSignal = np.array(fourierExtrapolation(x=X,n_predict=len(X),n_harm=len(candidateIntPeriods.keys()),candidatePeriods=candidateIntPeriods))
	
	xf,fftVal=getFFT(X,1000);
	fftResult = np.log(abs(fftVal))
	ceps=ifft(fftResult);
	ceps[0] = 0.0
	peaks = [0]*len(ceps)
	k = 3
	nceps = len(ceps)
	while k < (nceps)/2 :
		y1 = ceps[k-1]
		y2 = ceps[k]
		y3 = ceps[k+1]

		if y2 > y1 and y2 > y3 :
			peaks[k] = ceps[k]
		k = k + 1 

	posmax = peaks.index(max(peaks));
	#f0 = 1.0/(float(zeroPaddedFrameSize)*(posmax-1))
	#f0 = 0.001/(posmax + 1)
	f0 = float(fs)/(posmax + 1)

	print "Fundamental Frequency (Hz) through Cepstral Analysis = ", f0
	#plt.plot(f,ceps[0:len(f)])
	#plt.yscale('symlog')
	#plt.show()
	
	
	#f0 = freq_from_autocorr(X,fs)
	#print "Fundamental Frequency through autocorrelation = ", f0
	
	#print "Plotting Power Spectral Density"
	#plt.plot(f,PWSD)
	#plt.show()
	#print "nCandidate Harmonics = ", nCandidatePeriods, candidateIntPeriods
	#freq_from_HPS(X, fs)
	#sys.exit(0)


	return f,PWSD,candidateIntPeriods,pThreshold,f0
	
	
