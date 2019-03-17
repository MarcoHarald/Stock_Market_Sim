import csv
import numpy as np
import random
import matplotlib.pylab as plt


#  ------------

# initialising Geometric Mean
def geoMean(array):
    val = 1.0
    for prices in range(len(array)):
        val = val*array[prices]
    val = pow(val, 1 / len(array))
    #print('geometric mean is:  ', val)
    return val

def average(array):
    val = sum(array)/len(array)
    #print('mean is:  ', val)
    return val

# determine mu: price Historical, last known price date, how many days back to calculate value
def findMu(price, today, daysBack, gen):

    #mu = price[gen,today]-price[gen,today-daysBack]

    for day in range(1,daysBack):
        downside = 0
        upside = 0
        countUpside = 0
        countDownside = 0

        #print('today price',price[gen,today])
        #print('hist price', price[gen, today - day])

        localChange = price[gen,today]-price[gen,today-day]
        #print('checkmu',localChange)


        if localChange > 0:
            upside = localChange*localChange+upside
            countUpside +=1
        elif localChange < 0:
            downside = localChange*localChange+downside
            countDownside +=1

        weightedChange = pow(upside/max(countUpside,1),0.5)-pow(downside/max(countDownside,1),0.5)
        #print('mu change',weightedChange)
        return weightedChange/price[gen,today]

def movAvg(price, gen, target, bound):
    # find local moving average
    avgPrice = 0
    for day in range(target-bound,target-1):
        avgPrice = price[gen, day]+ avgPrice
    return avgPrice/(bound-1)

# determine sigma: price Historical, last known price date, how many days back to calculate value, mu
def findSigma(price, today, daysBack, mu, gen):
    sigma = 0
    for day in range(daysBack):
        localDeviation = movAvg(price, gen, day, 5)
        localDeviation = pow(localDeviation,2)
        sigma =localDeviation+sigma
    return pow(sigma/daysBack,0.5)/price[gen,today]

#print('findSigma function:',findSigma(realPrices,11,5,findMu(realPrices,11,5)))


def dumb(anArray,aposition,bposition):
    return anArray[aposition,bposition]

# ----------------------------------------------------

csv_file = 'dataBP.csv'
csv_reader = csv.reader(csv_file, delimiter=',')
data = [row for row in csv.reader(open(csv_file))]

# initiate separate arrray
realPrices = np.zeros(len(data))
# save values of closing price [4] to separate array
for i in range(0,len(data)-1):
    realPrices[i] = data[i+1][4]

print('Closing price data saved to separate array.')

#number of scenarios tried
simulations = 100

# initiate price prediction array
gssPrice = np.zeros((simulations,len(realPrices)))

# intial: assign real prices to all simulations
for gen in range(simulations):
    # within each simulation iterate through all previous days to assign true value
    for i in range(len(realPrices)):
        gssPrice[gen, i] = realPrices[i]

#days into future prediction
itrtns = 500
#date today
today = 6200
daysBack = today-1
gen =1


drift = findMu(gssPrice,today,daysBack,gen)
sigma = findSigma(gssPrice,today,daysBack,drift,gen)


print('number of data points:',len(data))
print('drift:',drift,'    sigma:',sigma)


drift = drift/100
sigma = sigma/100

# set bound for moving average operation
avgBound = 20

#exit()
print('-----------TESTING ENDS-----------')
print('phase 2')


# Calculate!
for gen in range(simulations):
    # update with most recent data
    # gssPrice[gen, today] = realPrices[today]

    for t in range(itrtns):
        # keep track of how many day into the future
        day = today+t
        #  print(gssPrice[gen, day]
        # new share price calculation   {{ drift * gssPrice[gen, day] }}
        gssPrice[gen, day + 1] = gssPrice[gen, day] + gssPrice[gen, day] * random.normalvariate(drift, sigma)
    gen = +1

# create log of all prices at certain time into simulation
lastPrice = []
for gen in range(simulations):
    lastPrice += [gssPrice[gen, itrtns+today]]

# find geometric mean of all final values

print('Geometric mean:',geoMean(lastPrice))
print('average:', average(lastPrice))

# find all values of similar result
tier0 = []
tier1 = []
tier2 = []
averagePrediction = average(lastPrice)

margin = 0.01

for gen in range(simulations):
    if averagePrediction*(1 + margin) > gssPrice[gen, itrtns + today] > averagePrediction*(1 - margin):
        tier1 += [gen]
    elif averagePrediction*(1 + margin) < gssPrice[gen, itrtns + today]:
        tier0 += [gen]
    elif averagePrediction*(1 - margin) > gssPrice[gen, itrtns + today]:
        tier2 += [gen]

print(f'Simulations within {margin} of average prediction {tier1}')

# create log of all prices at certain time into simulation
cPrice = []
for gen in range(simulations):
    cPrice += [gssPrice[gen, itrtns+today-50]]

# calculate moving average for values in selected streams
avgPrices = np.zeros((len(tier1), len(realPrices)))

print('tier1 length',len(tier1))

# PRINT SIMPLE GRAPH
#set lower limit of x axis
bound = today
# create time axis
t = []
for i in range(bound,itrtns+today):
    t += [i]

# create predicted price axis
for gen in tier1:
    avgPrice = []
    counter = 0
    for i in range(bound, itrtns + today):
        avgPrice += [movAvg(gssPrice, gen, i, avgBound)]
        avgPrices[counter, i-bound] = avgPrice[i-bound]
    counter = counter + 1
    plt.plot(t, avgPrice)

#create actual price axis
realPrice = []
for i in range(bound,itrtns+today):
    realPrice += [realPrices[i]]
plt.plot(t, realPrice, 'b', label='Real Price')

plt.legend(loc='upper left')
plt.ylabel('Price ($)', fontsize=10)
plt.xlabel('Time (days)', fontsize=10)
plt.show()


# ------------------------

# PRINT SIMPLE GRAPH
# create time axis
t = []
for i in range(today,itrtns+today):
    t += [i]

# create predicted price axis
for sims in tier1:
    predPrice0 = []
    for i in range(today, itrtns+today):
        predPrice0 += [gssPrice[sims, i]]
    plt.plot(t, predPrice0)

#create actual price axis
realPrice = []
for i in range(today,itrtns+today):
    realPrice += [realPrices[i]]
plt.plot(t, realPrice, 'b', label='Real Price')

plt.legend(loc='upper left')
plt.ylabel('Price ($)', fontsize=10)
plt.xlabel('Time (days)', fontsize=10)
plt.show()


exit()

# PRINT Quantile Distribution
# create time axis
xAxis = []
for i in range(simulations):
    xAxis += [i]

# create price axis (ordering the prices: increasing magnitude)
orderedPrices = np.sort(lastPrice)

#find geometric mean

plt.plot(xAxis, orderedPrices)
plt.ylabel('Final Price ($)', fontsize=10)
plt.xlabel('# of simulations', fontsize=10)
plt.show()

# PRINT CDF
# create price axis (ordering the prices: increasing magnitude)
cumul = np.zeros(len(orderedPrices))
for i in range(0, len(orderedPrices)):
    cumul[i] = 1.0 - float(i) / float(simulations)

plt.plot(orderedPrices, cumul)
plt.ylabel('fraction above', fontsize=10)
plt.xlabel('share price', fontsize=10)
plt.show()

#  ------------

day = 3
daysBack = 5
today = 10
mu = 2

localDeviation = realPrices[day] - mu * day - realPrices[today - daysBack]
print('dev:',localDeviation)

# ------------

#quantifying the variables: sigma & drift
stupid = np.array([[13,35,51,19,77],[42,26,40,84,66]])
print('testing arrays in functions',dumb(stupid,1,2))

# ------------

print('randomness:', day,random.normalvariate(0, sigma))
print('sigma:', sigma)
print('drift:', drift)
print('price:', gen, day, gssPrice[gen, day], gssPrice[gen, day + 1])


print('today is:',today)
print('len(realPrices):',len(realPrices))
print('gen is:',gen)
print('test price today',gssPrice[gen,today])
print('actual price today',realPrices[today])

print('length of gssPrice',len(gssPrice-2))


# --------------

# create predicted price axis
predPrice = []
for i in range(0,itrtns+today):
    predPrice += [gssPrice[40, i]]

# create predicted price axis
predPrice2 = []
for i in range(0,itrtns+today):
    predPrice2 += [gssPrice[50, i]]

plt.plot(t, predPrice2, 'g', label='3° Quintile (Predicted Price)')
plt.plot(t, predPrice3, 'y', label='4° Quintile (Predicted Price)')

#finding avg value
for prices in range(len(array)):
    val = val + prices
val = val / len(array)





