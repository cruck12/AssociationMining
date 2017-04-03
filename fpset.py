import itertools
from itertools import chain, combinations
import time
time_init = time.time()

minSupport = 0.025
minConfidence = 0.6
	
data = open('retail.csv', 'rU')	#reading the dataset


class FPNode(object):

	def __init__(self, value, count, parent):

		self.value = value
		self.count = count
		self.parent = parent
		self.link = None
		self.children = []

# check if node has a particular child
	def has_child(self, value):
		for node in self.children:
			if node.value == value:
				return True

		return False

# get the child node if exists
	def get_child(self, value):
		for node in self.children:
			if node.value == value:
				return node

		return None

	def add_child(self, value):
		child = FPNode(value, 1, self)
		self.children.append(child)
		return child


class FPTree(object):

	def __init__(self, transactions, threshold, root_value, root_count):
		"""
		Transactions -- list of iterable items 
		"""
		self.frequent = self.find_frequent_items(transactions, threshold)
		self.headers = self.build_header_table(self.frequent)
		self.root = self.build_fptree(
			transactions, root_value,
			root_count, self.frequent, self.headers)

	@staticmethod
	def find_frequent_items(transactions, threshold):

		# Return the counts of items in the dataset
		items = {}

		for transaction in transactions:
			for item in transaction:
				if item in items:
					items[item] += 1
				else:
					items[item] = 1

		for key in list(items.keys()):
			if items[key] < threshold:
				del items[key]

		return items

	@staticmethod
	def build_header_table(frequent):
		headers = {}
		for key in frequent.keys():
			headers[key] = None

		return headers

	def build_fptree(self, transactions, root_value,
					 root_count, frequent, headers):
		root = FPNode(root_value, root_count, None)

		for transaction in transactions:
			sorted_items = [x for x in transaction if x in frequent]
			sorted_items.sort(key=lambda x: frequent[x], reverse=True)
			if len(sorted_items) > 0:
				self.insert_tree(sorted_items, root, headers)

		return root

	def insert_tree(self, items, node, headers):
		first = items[0]
		child = node.get_child(first)
		if child is not None:
			child.count += 1
		else:
			# Add new child.
			child = node.add_child(first)

			# Link it to header structure.
			if headers[first] is None:
				headers[first] = child
			else:
				current = headers[first]
				while current.link is not None:
					current = current.link
				current.link = child

		# Call function recursively.
		remaining_items = items[1:]
		if len(remaining_items) > 0:
			self.insert_tree(remaining_items, child, headers)

	def tree_has_single_path(self, node):
		"""
		Check if there is only a single path in the tree
		"""
		num_children = len(node.children)
		if num_children > 1:
			return False
		elif num_children == 0:
			return True
		else:
			return True and self.tree_has_single_path(node.children[0])

	def mine_patterns(self, threshold):
		"""
		Mine the constructed FP tree for frequent patterns.
		"""
		if self.tree_has_single_path(self.root):
			return self.generate_pattern_list()
		else:
			return self.zip_patterns(self.mine_sub_trees(threshold))

	def zip_patterns(self, patterns):
		"""
		Append suffix to patterns in dictionary if we are in a conditional FP tree.
		"""
		suffix = self.root.value

		if suffix is not None:
			# We are in a conditional tree.
			new_patterns = {}
			for key in patterns.keys():
				new_patterns[tuple(sorted(list(key) + [suffix]))] = patterns[key]

			return new_patterns

		return patterns

	def generate_pattern_list(self):
		patterns = {}
		items = self.frequent.keys()

		# If we are in a conditional tree,
		# the suffix is a pattern on its own.
		if self.root.value is None:
			suffix_value = []
		else:
			suffix_value = [self.root.value]
			patterns[tuple(suffix_value)] = self.root.count

		for i in range(1, len(items) + 1):
			for subset in itertools.combinations(items, i):
				pattern = tuple(sorted(list(subset) + suffix_value))
				patterns[pattern] = \
					min([self.frequent[x] for x in subset])

		return patterns

	def mine_sub_trees(self, threshold):
		"""
		Generate subtrees and mine them for patterns.
		"""
		patterns = {}
		mining_order = sorted(self.frequent.keys(),
							  key=lambda x: self.frequent[x])

		# Get items in tree in reverse order of occurrences.
		for item in mining_order:
			suffixes = []
			conditional_tree_input = []
			node = self.headers[item]

			# Follow node links to get a list of
			# all occurrences of a certain item.
			while node is not None:
				suffixes.append(node)
				node = node.link

			# For each occurrence of the item, 
			# trace the path back to the root node.
			for suffix in suffixes:
				frequency = suffix.count
				path = []
				parent = suffix.parent

				while parent.parent is not None:
					path.append(parent.value)
					parent = parent.parent

				for i in range(frequency):
					conditional_tree_input.append(path)

			# Now we have the input for a subtree,
			# so construct it and grab the patterns.
			subtree = FPTree(conditional_tree_input, threshold,
							 item, self.frequent[item])
			subtree_patterns = subtree.mine_patterns(threshold)

			# Insert subtree patterns into main patterns dictionary.
			for pattern in subtree_patterns.keys():
				if pattern in patterns:
					patterns[pattern] += subtree_patterns[pattern]
				else:
					patterns[pattern] = subtree_patterns[pattern]

		return patterns


def find_frequent_patterns(transactions, support_threshold):
	tree = FPTree(transactions, support_threshold, None, None)
	return tree.mine_patterns(support_threshold)



def generate_association_rules(patterns, confidence_threshold):

	rules = {}
	for itemset in patterns.keys():
		upper_support = patterns[itemset]

		for i in range(1, len(itemset)):
			for antecedent in itertools.combinations(itemset, i):
				antecedent = tuple(sorted(antecedent))
				consequent = tuple(sorted(set(itemset) - set(antecedent)))

				if antecedent in patterns:
					lower_support = patterns[antecedent]
					confidence = float(upper_support) / lower_support

					if confidence >= confidence_threshold:
						rules[antecedent,consequent] = (confidence)

	return rules



transactions = []
itemSet = set()
freqSet = dict()	#dictionary that stores frequency of each itemset

for line in data:
	line = line.strip().rstrip(' ')        	#remove any trailing spaces
	line = line.split(' ')
	transaction = frozenset([int(x) for x in line])	#each set in transaction list is immutable
	# for item in transaction:
	# 	itemSet.add(frozenset([item]))		#initialize itemSets for k=1
	# 	if frozenset([item]) in freqSet:
	# 		freqSet[frozenset([item])] += 1
	# 	else:
	# 		freqSet[frozenset([item])] = 1
	transactions.append(transaction)

patterns = find_frequent_patterns(transactions, minSupport*len(transactions))
print(time.time()-time_init)

rules = generate_association_rules(patterns, minConfidence)

print('ITEMS:-')
for k, v in patterns.items():
	print (str(k) + '              ' + str( (float(v)/len(transactions)))) 
# # print(patterns)
print('\nRULES:-')
for k, v in rules.items():
	print (str(k) + '               ' + str(v))
