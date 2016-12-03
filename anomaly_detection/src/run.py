from utils import *
from read_msu_datasets import *
import read_microgrid_datasets
from read_microgrid_datasets import *
import itertools
from hmm_model import *



runPeriods = [9]
maxMixtures = 10
windowSize = 60

usePCA = True
testFourierExtrapolation = True
testArimaForecasting = True
testHMMForecasting = False


scriptDir = os.path.dirname(os.path.realpath(__file__))
covType = 'full'
if __name__ == "__main__" :

	data,nMaxAttackSamples = read_microgrid_datasets.extract_features()
	#data,nMaxAttackSamples = read_MSU_DataSet_Samples(scriptDir)
	trainData = data['Train']
	attackData = []
	fundamentalPeriods = []
	modelOrder = []
	

	boxPlotData = {}
	boxPlotLabels = ['Train']
	powerSpectralDensity = {}
	

	for attackType in data['Attack'].keys() :
		attackData.append((attackType,data['Attack'][attackType]))
		boxPlotLabels.append(attackType)
	
	if usePCA == True :
		covType =  'diag'
		optDimensionality = extractOptPCADimensionality(data['Train'])
		print "PCA 99 percentile optDimensionality = ", optDimensionality
		pca = PCA(n_components=optDimensionality)
		pca.fit(data['Train'])
		trainData = pca.transform(data['Train'])
		attackData = []
		

		for attackType in data['Attack'].keys() :
			attackData.append((attackType,pca.transform(data['Attack'][attackType])))	
			
		
	
	if testFourierExtrapolation == True :
	
		nSignals = len(trainData[0])
		fundamentalPeriods = [0]*nSignals
		nLags = 100
		
		# Step-0 Extract fundamental Periods of each signal
		for i in xrange(0,nSignals) :
			currSignal = np.array(map(itemgetter(i),trainData))
			print "Extracting Fundamental periods for signal ", i, " ..."
			f,PWSD,candidatePeriods,pThreshold,f0 = getPeriodHints(X=currSignal,fs=1.0)

			if f0 != 0 :
				fundamentalPeriods[i] = int(1.0/float(f0))
			else:
				fundamentalPeriods[i] = 0
			powerSpectralDensity[i] = (f,PWSD,pThreshold)


		"""
		if nSignals % 2 == 0 :
			nrows = nSignals/2
		else :
			nrows = int(nSignals/2) + 1

		ncols = 2
		fig, axarr = plt.subplots(nrows=nrows, ncols=ncols)
		for i in xrange(0,nrows) :
			for j in xrange(0,ncols) :
				signal_no = i*ncols + j

				if nrows == 1 and signal_no in powerSpectralDensity.keys():
					axarr[j].plot(powerSpectralDensity[signal_no][0],powerSpectralDensity[signal_no][1], label="Power Spectral Density")
					axarr[j].plot(powerSpectralDensity[signal_no][0],[powerSpectralDensity[signal_no][2]]*len(powerSpectralDensity[signal_no][0]), label="Threshold")
					axarr[j].set_title('Periodicity Test with Threshold for PCA Signal:' + str(signal_no + 1), fontsize=10)
					axarr[j].grid(True)

				elif signal_no in powerSpectralDensity.keys():
					axarr[i,j].plot(powerSpectralDensity[signal_no][0],powerSpectralDensity[signal_no][1], label="Power Spectral Density")
					axarr[i,j].plot(powerSpectralDensity[signal_no][0],[powerSpectralDensity[signal_no][2]]*len(powerSpectralDensity[signal_no][0]), label="Threshold")
					axarr[i,j].set_title('Periodicity Test with Threshold for PCA Signal:' + str(signal_no + 1), fontsize=10)
					axarr[i,j].grid(True)
				else:
					if nrows == 1 :
						axarr[j].axis('off')
					else:
						axarr[i,j].axis('off')

		for ax in axarr.flatten():
			ax.set_yscale('log')
		plt.tight_layout()
		plt.show()
		"""
		
	if testArimaForecasting == True :

		nSignals = len(trainData[0])
		nLags = 100
		modelOrder = [0]*nSignals
		print "nSignals = ",nSignals
		
		for i in xrange(0,nSignals) :			
			currSignal = np.array(map(itemgetter(i),trainData))
			diffSignal = np.array([0.0]*len(currSignal))

			# Step 1 de-seasonalize signal
			for j in xrange(fundamentalPeriods[i],len(currSignal)) :
				if fundamentalPeriods[i] == 0 :
					diffSignal[j] = currSignal[j]
				else:
					diffSignal[j] = (currSignal[j] - currSignal[j-fundamentalPeriods[i]]) #- (currSignal[j-9] - currSignal[j-10])



			# Step 2 estimate model order by looking at acf/pacf of signal
			"""
			print "Plot Acf/Pacf for signal ", i , " ..."
			
			acf = stattools.acf(x=np.array(map(itemgetter(i),trainData)),nlags=nLags,fft=True)
			pacf = stattools.pacf(x=np.array(map(itemgetter(i),trainData)),nlags=nLags)
			plt.plot(diffSignal[0:nLags],marker='+',label="ACF")
			plt.plot(pacf,marker='^',label="PACF",linestyle='--')
			plt.title("ACF/PACF for Signal " + str(i))
			plt.xlabel("Lags")
			plt.ylabel("Auto Correlation/Partial Auto Correlation")
			plt.xticks(np.arange(0, nLags + 5 , int(nLags/20)))
			plt.legend(loc='upper right',shadow=True)
			plt.show()
			sys.exit(0)
			"""
			
			"""
			print "Estimating Acf for differenced signal ", i, " ..."


			#spacf_orig = stattools.pacf(x=currSignal,nlags=nLags)
			pacf_orig = stattools.acf(x=diffSignal,nlags=nLags,fft=True)
			pacf = stattools.pacf(x=diffSignal,nlags=nLags)
			plt.plot(pacf_orig,marker='+',label="PACF Orig",linestyle='-.',color="red")
			plt.plot(pacf,marker='^',label="PACF Diff",linestyle='--',color="green")
			plt.title("PACF for Original and Differenced Signal No: " + str(i))
			plt.xlabel("Lags")
			plt.ylabel("Partial Auto Correlation")
			plt.xticks(np.arange(0, nLags + 5 , int(nLags/20)))
			plt.legend(loc='upper right',shadow=True)
			plt.show()
			#sys.exit(0)
			"""

			
			# Step 3: use model order to do ARMA forcecasting	
			# (AR order, difference order, MA Order)
			
			difference_order = 0	
			""" Old one
			modelOrder[0] = (1,difference_order,10)
			modelOrder[1] = (1,difference_order,9)
			modelOrder[2] = (1,difference_order,10)
			modelOrder[3] = (1,difference_order,10)
			"""



			modelOrder[i] = (5,difference_order,0)

			"""
			modelOrder[0] = (5,difference_order,0)
			modelOrder[1] = (5,difference_order,0)
			modelOrder[2] = (5,difference_order,0)
			modelOrder[3] = (5,difference_order,0)
			"""
			
			#arima_model = statsmodels.tsa.arima_model.ARIMA(currSignal,(modelOrder[i][0],modelOrder[i][1],modelOrder[i][2]))
			arima_model = statsmodels.tsa.arima_model.ARIMA(diffSignal,(modelOrder[i][0],modelOrder[i][1],modelOrder[i][2]))
			res = arima_model.fit()


			boxPlotData[i] = []	
			trainDataRMS= getRMSErrs(diffSignal,res,windowSize)
			boxPlotData[i].append(trainDataRMS)
			
			for k in xrange(0,len(attackData)) :
				attackType = attackData[k][0]
				attackSignal = np.array(map(itemgetter(i),attackData[k][1]))
				res.model.data.endog = attackSignal

				diffAttackSignal = np.array([0.0]*len(attackSignal))
				for j in xrange(1,len(attackSignal)) :
					if fundamentalPeriods[i] == 0 :
						diffAttackSignal[j] = attackSignal[j]
					else:
						diffAttackSignal[j] = (attackSignal[j] - attackSignal[j-fundamentalPeriods[i]])

				if difference_order == 0 :
					boxPlotData[i].append(getRMSErrs(diffAttackSignal,res,windowSize))
				else:
					boxPlotData[i].append(getRMSErrs(diffAttackSignal,res,windowSize))

		if nSignals % 2 == 0 :
			nrows = nSignals/2
		else :
			nrows = int(nSignals/2) + 1
			
			
		ncols = 2

		print boxPlotData
		fig, axarr = plt.subplots(nrows=nrows, ncols=ncols)
		for i in xrange(0,nrows) :
			for j in xrange(0,ncols) :
				signal_no = i*ncols + j
				if nrows == 1 and signal_no in boxPlotData.keys():
					axarr[j].boxplot(boxPlotData[signal_no], labels=boxPlotLabels)
					axarr[j].set_title('RMS Error - PCA signal ' + str(signal_no + 1), fontsize=10)
					axarr[j].grid(True)

				elif signal_no in boxPlotData.keys():
					axarr[i,j].boxplot(boxPlotData[signal_no], labels=boxPlotLabels)
					axarr[i,j].set_title('RMS Error - PCA signal ' + str(signal_no + 1), fontsize=10)
					axarr[i,j].grid(True)
				else:
					if nrows == 1 :
						axarr[j].axis('off')
					else:
						axarr[i,j].axis('off')

		for ax in axarr.flatten():
			ax.set_yscale('log')
		plt.tight_layout()
		plt.show()

	
	

	if testHMMForecasting == True :
		trainMeans = []
		trainErrs = []
		trainScores = []
		attackMeans = {}
		attackErrs = {}
		attackScores = {}
		start = 1
		period = []
		for start in runPeriods :
			sysPeriod = start
			period.append(sysPeriod)
			

			print "Training HMM for SysPeriod = ",sysPeriod		
			observations, nOptMixtures = trainGMMs(trainData,sysPeriod=sysPeriod,nMaxMixtures=maxMixtures,cvType=covType)
			Hmm = trainHMM(observations=observations,trainSamples=trainData,nMixtures=nOptMixtures,nStages=sysPeriod,cvType=covType)
					
			
			print "Scoring Samples ..."
			mu,err,scores = scoreSamples(trainData,Hmm,windowSize)
			trainMeans.append(mu)
			trainErrs.append(err)
			trainScores.append(scores)

			for i in xrange(0,len(attackData)) :
				attackType = attackData[i][0]
				print "attack Type = ", attackType
				mu,err,scores = scoreSamples(attackData[i][1],Hmm,windowSize,debug=False)
				
				if attackType not in attackMeans.keys() :
					attackMeans[attackType] = []
					attackErrs[attackType] = []
					attackScores[attackType] = []
				attackMeans[attackType].append(mu)
				attackErrs[attackType].append(err)
				attackScores[attackType].append(scores)


			start =  start + 1
			
		

		if len(runPeriods) > 1 :
			trainLine = plt.errorbar(period,trainMeans,yerr=trainErrs,label="Train Samples",linestyle='--',marker="d",color="red")
			attackPlotLines = []
		 
			marker = itertools.cycle(('+', '^', 'x', '*', 'o','.',',')) 
			color = itertools.cycle(("black","green","blue","m"))
			linestyle = itertools.cycle(('-','-.','--'))
			
			for attackType in attackMeans.keys() :
				currLine = plt.errorbar(period,attackMeans[attackType],yerr=attackErrs[attackType],label=attackType + " Attack",linestyle=linestyle.next(),marker=marker.next(),color=color.next())
				attackPlotLines.append(currLine)
			plt.yscale('symlog')
			plt.title("Log Likelihood Variation for Window Size = 60 sec")
			plt.xlabel("Number of States")
			plt.ylabel("HMM average log likelihood")
			plt.xticks(np.arange(min(period), max(period) + 5 , 1.0))
			plt.legend(loc='upper right',shadow=True)
			plt.grid(True)
			plt.show()

		elif len(runPeriods) == 1 :
			boxPlotLabels = ['Train']
			boxPlotData = []
			boxPlotData.append(trainScores[0])
			for attackType in attackMeans.keys() :
				boxPlotLabels.append(attackType)
				boxPlotData.append(attackScores[attackType][0])
			plt.boxplot(boxPlotData, labels=boxPlotLabels)
			plt.yscale('symlog')
			plt.ylabel("Per Window Log likelihood")
			plt.title('Per Window Log Likelihood - (epsilon=0.01,n=60)', fontsize=15)
			plt.grid(True)
			plt.show()

				

	