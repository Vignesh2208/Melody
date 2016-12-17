from utils import *
from read_msu_datasets import *
import read_microgrid_datasets
from read_microgrid_datasets import *
import itertools
from hmm_model import *
import math
import warnings

warnings.simplefilter("ignore")



runPeriods = [9]
maxMixtures = 10
windowSize = 1

usePCA = True
testFourierExtrapolation = True
testArimaForecasting = True
testHMMForecasting = False

model_orders = {
	"MSU" :
			[
			(5,0,0),
			(5,0,0),
			(5,0,0),
			(5,0,0),
		   	],

	"all_taps" :
			[
			(5, 0, 5),
			(2, 0, 3),
			(4, 0, 0),
			(0, 0, 0),
			(0, 0, 2)
			],

	"tap_config_1" :
			[
			(1, 1, 0),
			(4, 0, 0),
			(4, 0, 0)
			],
	"tap_config_2" :
			[
			(2, 0, 5),
			(0, 0, 2)
			],

	"tap_config_3" :
			[
			(5, 0, 2)
			]

}


scriptDir = os.path.dirname(os.path.realpath(__file__))
covType = 'full'
scenario_name = "all_taps"



def estimate_best_model_order(diffSignal,nLags,i,modelOrder,windowSize):


	# acf = stattools.acf(x=diffSignal,nlags=nLags,fft=True)
	# pacf = stattools.pacf(x=diffSignal,nlags=nLags)
    #
	# fig, axarr = plt.subplots(nrows=2, ncols=1)
    #
	# axarr[0].plot(acf,marker='+',label="ACF",linestyle='-.',color="red")
	# axarr[0].set_title("Auto-Correlation Function for PCA Signal : " + str(i+1))
	# axarr[0].set_xlabel("Lags")
	# axarr[0].set_ylabel("ACF")
	# axarr[0].set_xlim([0,nLags + 5])
	# axarr[0].grid(True)
    #
	# axarr[1].plot(pacf, marker='+', label="PACF", linestyle='-.', color="green")
	# axarr[1].set_title("Partial Auto-Correlation Function for PCA Signal : " + str(i+1))
	# axarr[1].set_xlabel("Lags")
	# axarr[1].set_ylabel("PACF")
	# axarr[1].set_xlim([0, nLags + 5])
	# axarr[1].grid(True)
    #
	# plt.tight_layout()
	# plt.show()



	# arima_model = statsmodels.tsa.arima_model.ARIMA(currSignal,(modelOrder[i][0],modelOrder[i][1],modelOrder[i][2]))

	min_err = 100000
	best_model = (1,0,0)
	for p in xrange(0,6) :
		for d in xrange(0,2) :
			for q in xrange(0,6) :
				try:
					arima_model = statsmodels.tsa.arima_model.ARIMA(diffSignal, (p,d,q))
					res = arima_model.fit(transParams=True)
					#trainDataRMS, detection_time = getRMSErrs(diffSignal, res, windowSize)
					#max_train_rms_err = max(trainDataRMS)

					if res.aic < min_err :
						min_err = res.aic
						best_model = (p,d,q)

				except:
					pass

	#boxPlotData.append(trainDataRMS)
	#plt.boxplot(boxPlotData[0])
	#plt.show()
	#sys.exit(0)

	print "Best Model = ", best_model
	return best_model

if __name__ == "__main__" :

	if scenario_name == "MSU":
		data, nMaxAttackSamples = read_MSU_DataSet_Samples(scriptDir)
	else:
		data,nMaxAttackSamples = read_microgrid_datasets.extract_features(scenario_name=scenario_name)


	with open("model_order_" + scenario_name,"w") as f :
		pass



	trainData = data['Train']
	attackData = []
	fundamentalPeriods = []
	modelOrder = []
	

	boxPlotData = {}
	detectionTimeData = {}
	nCrossValidationAttempts = 0
	boxPlotLabels = ['Train']
	detectionTimeLabels = []
	powerSpectralDensity = {}
	nFP = 0.0
	nFN = 0.0
	nTP = 0.0
	nTN = 0.0

	for attackType in data['Attack'].keys() :
		attackData.append((attackType,data['Attack'][attackType]))

		if "Normal" in attackType or "normal" in attackType :
			nCrossValidationAttempts = nCrossValidationAttempts + 1
		boxPlotLabels.append(attackType)
		detectionTimeLabels.append(attackType)


	if usePCA == True :
		covType = 'diag'
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
				#if i == 0 :
				#	fundamentalPeriods[i] = 2
				#else :
				fundamentalPeriods[i] = int(round(1.0/float(f0)))
			else:
				fundamentalPeriods[i] = 0
			powerSpectralDensity[i] = (f,PWSD,pThreshold)
			print "Fundamental Period = ", fundamentalPeriods[i]


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
		nLags = 20
		modelOrder = [0]*nSignals
		print "Number of PCA Signals = ",nSignals
		print "Fitting ARMA Models ..."
		
		for i in xrange(0,nSignals) :



			currSignal = np.array(map(itemgetter(i),trainData))
			diffSignal = np.array([0.0]*len(currSignal))

			# Step 1 de-seasonalize signal
			for j in xrange(fundamentalPeriods[i],len(currSignal)) :
				if fundamentalPeriods[i] == 0 :
					diffSignal[j] = currSignal[j]
				else:
					diffSignal[j] = (currSignal[j] - currSignal[j-fundamentalPeriods[i]]) #- (currSignal[j-9] - currSignal[j-10])
					#if model_orders[scenario_name][i][1] == 1 and j > fundamentalPeriods[i] :
					#	diffSignal[j] = diffSignal[j] - (currSignal[j-1] - currSignal[j-fundamentalPeriods[i]-1])




			# Step 2 estimate model order by looking at acf/pacf of signal


			print "Fitting Model for PCA signal ", i + 1, " ..."

			# Step 3: use model order to do ARMA forcecasting	
			# (AR order, difference order, MA Order)

			if scenario_name == "MSU":
				modelOrder = model_orders[scenario_name][i]
			else:
				#modelOrder = estimate_best_model_order(diffSignal, nLags, i,modelOrder,windowSize)
				modelOrder = model_orders[scenario_name][i]
				with open("model_order_" + scenario_name, "a") as fptr:
					fptr.write(str(modelOrder) + ",\n")


			#arima_model = statsmodels.tsa.arima_model.ARIMA(currSignal,(modelOrder[i][0],modelOrder[i][1],modelOrder[i][2]))
			arima_model = statsmodels.tsa.arima_model.ARIMA(diffSignal,(modelOrder[0],modelOrder[1],modelOrder[2]))
			res = arima_model.fit(transParams=True)


			boxPlotData[i] = []	
			trainDataRMS,detection_time,n_detections = getRMSErrs(diffSignal,res,windowSize)
			max_train_rms_err = max(trainDataRMS)
			mean_train_rms_err = mean(trainDataRMS)
			std_dev_train_rms_err = stdev(trainDataRMS)

			#detection_threshold = mean_train_rms_err + 2*std_dev_train_rms_err
			detection_threshold = 1.05*max_train_rms_err
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


				attackDataRMS,detection_time,n_detections = getRMSErrs(diffAttackSignal,res,windowSize,threshold=detection_threshold)


				if attackType not in detectionTimeData.keys():
					detectionTimeData[attackType] = (detection_time,n_detections)
				elif detection_time != -1:
					if detectionTimeData[attackType][0] == -1 :
						detectionTimeData[attackType] = (detection_time,n_detections)
					elif detection_time < detectionTimeData[attackType][0] :
						detectionTimeData[attackType] = (detection_time,detectionTimeData[attackType][1] + n_detections)

					else:
						detectionTimeData[attackType] = (detectionTimeData[attackType][0],detectionTimeData[attackType][1] + n_detections)

				boxPlotData[i].append(attackDataRMS)

		for attackType in detectionTimeData.keys() :
			if "Normal" in attackType or "normal" in attackType :
				if detectionTimeData[attackType][0] == -1 :
					nTN = nTN + 1.0
				else:
					nFP = nFP + 1.0
			else:
				if detectionTimeData[attackType][0] == -1 :
					nFN = nFN + 1.0
				else:
					nTP = nTP + 1.0

		if nSignals % 2 == 0 :
			nrows = nSignals/2
		else :
			nrows = int(nSignals/2) + 1
			
			
		ncols = 2

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


		print "################################################"
		print "Output Statistics"
		print "################################################"

		if nTP + nFN == 0 :
			tp_rate = "Not Applicable"
		else:
			tp_rate =nTP/(nTP + nFN)

		if nFP + nTN == 0 :
			fp_rate = "Not Applicable"
		else:
			fp_rate =nFP/(nFP + nTN)

		if nTN + nFP == 0 :
			tn_rate = "Not Applicable"
		else:
			tn_rate = nTN/(nTN + nFP)

		if tp_rate == "Not Applicable" :
			fn_rate = "Not Applicable"
		else:
			fn_rate = 1.0 - tp_rate

		if tp_rate == "Not Applicable" or fp_rate == "Not Applicable" or tp_rate + fp_rate == 0:
			precision = "Not Applicable"
		else:
			precision = tp_rate/(tp_rate + fp_rate)

		if tp_rate == "Not Applicable" or fn_rate == "Not Applicable" or tp_rate + fn_rate == 0 :
			recall = "Not Applicable"
		else:
			recall = tp_rate/(tp_rate + fn_rate)


		with open(scenario_name + "_output.txt","w") as f:
			f.write("True Positive Rate:      " + str(tp_rate) + "\n")
			f.write("False Positive Rate:     " + str(fp_rate) + "\n")
			f.write("True Negative Rate:      " + str(tn_rate) + "\n")
			f.write("False Negative Rate:     " + str(fn_rate) + "\n")
			f.write("Precision:               " + str(precision) + "\n")
			f.write("Recall:                  " + str(recall) + "\n")



			if len(detectionTimeLabels) > 0 :

				f.write("\n")
				f.write("######################################################\n")
				f.write("Earliest Detection Time (multiply by sampling rate ts) ...\n")
				f.write("######################################################\n")
				for attackType in detectionTimeLabels :
					if attackType in detectionTimeData.keys() and detectionTimeData[attackType][0] != -1 :
						f.write(attackType + ":           " + str(detectionTimeData[attackType][0]) +  " Total Number of point anomalies = " +  str(detectionTimeData[attackType][1])+ "\n")
					else:
						f.write(attackType +  ":            NOT DETECTED\n")


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

				

	
