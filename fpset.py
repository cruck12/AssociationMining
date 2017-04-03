from itertools import chain, combinations		#for generating powerset of a given set

minSupport = 0.025
minConfidence = 0.6
	
data = open('dummy.csv', 'rU')	#reading the dataset








#DEFINING THE TREE CLASSES

class Fnode(object) :
	def __init__(self, value, count, parent):
        """
        Create the node.
        """
        self.value = value
        self.count = count
        self.parent = parent
        self.link = None
        self.children = []


    def hasChild(self, value)
    	for node in self.children
    		if node.value = value
    			return True

    	return False

    def getChild(self, value)
    	for node in self.children
    		if node.value = value
    			return node

    	return None

    def addChild(self, value)
    	child = Fnode(value, 1, self)
    	self.children.append(child)

    	return child


class Ftree(object):

	def __init__(self, data, minSupport, root_value, root_count):
        """
        Initialize the tree.
        """
        self.frequent = self.find_frequent_items(data, minSupport)
        self.headers = self.build_header_table(self.frequent)

        self.root = self.build_fptree(
            data, root_value,
            root_count, self.frequent, self.headers)

    @staticmethod
    def find_frequent_items(data, minSupport):
        """
        Create a dictionary of items with occurrences above the threshold.
        """
        # items = {}

		itemSet = set()
		transactions = []	

        freqSet = dict()	#dictionary that stores frequency of each itemset


		for line in data:
			line = line.strip().rstrip(' ')        	#remove any trailing spaces
			line = line.split(' ')
			transaction = frozenset([int(x) for x in line])	#each set in transaction list is immutable
			for item in transaction:
				itemSet.add(frozenset([item]))		#initialize itemSets for k=1
				if frozenset([item]) in freqSet:
					freqSet[frozenset([item])] += 1
				else:
					freqSet[frozenset([item])] = 1
			transactions.append(transaction)


        # for transaction in transactions:
        #     for item in transaction:
        #         if item in items:
        #             items[item] += 1
        #         else:
        #             items[item] = 1


        # for key in list(freqSet.keys()):
        #     if items[key] < threshold:
        #         del items[key]

		#Pruning the length 1 (k=1) itemsets:-
		currentSet = set()
		for item in freqSet:
			support = float(freqSet[item])/len(transactions)
			if(support >= minSupport):
				currentSet.add(item)
			else:
				del freqSet[item]

        return freqSet


    @staticmethod
    def build_header_table(frequent):
        """
        Build the header table.
        """
        headers = {}
        for key in frequent.keys():
            headers[key] = None

        return headers


    def build_fptree(self, data, root_value,
                     root_count, frequent, headers):
        """
        Build the FP tree and return the root node.
        """
        root = FPNode(root_value, root_count, None)

        transactions = []

        for line in data:
			line = line.strip().rstrip(' ')        	#remove any trailing spaces
			line = line.split(' ')
			transaction = frozenset([int(x) for x in line])	#each set in transaction list is immutable
			transactions.append(transaction)


        for transaction in transactions:
            sorted_items = [x for x in transaction if x in frequent]
            sorted_items.sort(key=lambda x: frequent[x], reverse=True)
            if len(sorted_items) > 0:
                self.insert_tree(sorted_items, root, headers)

        return root



    def insert_tree(self, freqSet, node, headers):
        """
        Recursively grow FP tree.
        """
        first = freqSet[0]
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
        remaining_items = freqSet[1:]
        if len(remaining_items) > 0:
            self.insert_tree(remaining_items, child, headers)


    def tree_has_single_path(self, node):
        """
        If there is a single path in the tree,
        return True, else return False.
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


    def generate_pattern_list(self):
        """
        Generate a list of patterns with support counts.
        """
        patterns = {}
        items = self.frequent.keys()

        # If we are in a conditional tree,
        # the suffix is a pattern on its own.
        if self.root.value is None:
            suffix_value = []
        else:
            suffix_value = [self.root.value]
            patterns[tuple(suffix_value)] = self.root.count

        for i in range(1, len(freqSet) + 1):
            for subset in itertools.combinations(freqSet, i):
                pattern = tuple(sorted(list(subset) + suffix_value))
                patterns[pattern] = \
                    min([self.frequent[x] for x in subset])

        return patterns



def find_frequent_patterns(data, minSupport):
    """
    Given a set of transactions, find the patterns in it
    over the specified support threshold.
    """
    tree = FPTree(data, minSupport, None, None)
    return tree.mine_patterns(minSupport)

