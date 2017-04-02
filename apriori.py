from itertools import chain, combinations		#for generating powerset of a given set

minSupport = 0.15
minConfidence = 0.6

itemSet = set()
transactions = []		
data = open('dummy.csv', 'rU')	#reading the dataset
for line in data:
	line = line.strip().rstrip(' ')        	#remove any trailing spaces
	line = line.split(' ')
	transaction = frozenset([int(x) for x in line])	#each set in transaction list is immutable
	for item in transaction:
		itemSet.add(frozenset([item]))		#initialize itemSets for k=1
	transactions.append(transaction)	

freqSet = dict()	#dictionary that stores frequency of each itemset

#Pruning the length 1 (k=1) itemsets:-
currentSet = set()
for item in itemSet:
	counter = 0
	for transaction in transactions:
		if item.issubset(transaction):
			counter +=1
	support = float(counter)/len(transactions)
	if(support >= minSupport):
		currentSet.add(item)
		freqSet[item] = counter

largeSet = dict()	#dictionary that stores the itemsets statisfying the minSupport, with the key corresponding to length of itemset

#STEP 1: Generate all itemsets of all lengths that satisfy the minSupport condition:-
k=2
while(currentSet != set([])):
	largeSet[k-1] = currentSet
	currentSet = set([i.union(j) for i in currentSet for j in currentSet if len(i.union(j)) == k])	#generate itemset of k length by taking selective union of elements in itemset of k-1 length

	#pruning the currentSet to accomodate only those which satisfy the minSupport condition:-
	_currenSet = set()
	for item in currentSet:
		counter = 0
		for transaction in transactions:
			if(item.issubset(transaction)):
				counter += 1
		support = float(counter)/len(transactions)
		if(support >= minSupport):
			_currenSet.add(item)
			freqSet[item] = counter
	currentSet = _currenSet
	k += 1

#STEP 2: Identify the rules that satisfy the minConfidence condition:-
rules = []
for key, value in largeSet.items()[1:]:		#value = all itemsets with length=key, such that they satisfy minSupport condition
	for item in value:
		powerSet = map(frozenset, [x for x in chain(*[combinations(item, i + 1) for i, a in enumerate(item)])])	#powerSet of the given item set. It will be directly used for generating binary association rules
		for subset in powerSet:
			_subset = item.difference(subset)		#the complement of the given subset. We are checking the rule: subset-->_subset
			if(len(_subset)>0):
				confidence = float(freqSet[item])/freqSet[subset]
				if(confidence >= minConfidence):
					rules.append(((tuple(subset),tuple(_subset)),confidence))
itemsets = []
for key, value in largeSet.items():
	itemsets.extend([(tuple(item), float(freqSet[item])/len(transactions)) for item in value])

#STEP3: Displaying the results:-
itemsets.sort(key = lambda x: x[1])
print('ITEMS:-')
#print(itemsets)
for item,support in itemsets:
	print(str(item)+"\t\t\t"+str(support))
print('\nRULES:-')
rules.sort(key = lambda x: x[1])
for rule,confidence in rules:
	print(str(rule[0])+"-->"+str(rule[1])+"\t\t\t"+str(confidence))
