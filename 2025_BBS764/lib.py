import numpy as np
from IPython.display import display, Markdown
import matplotlib.pyplot as plt

def string_to_digraph(annotation, weight=None, default_weight=2.0, **ka):
	"""Convert string annotation to networkx DiGraph
	
	Args:
		annotation (str): String containing edges separated by ' '
						 Each edge contains one or two nodes
						 Two nodes are connected by ->, <- or -|, |-
						 Can handle chained edges like 'A->B->C' or 'A-|B->C'
						 Node capitalization indicates observation status
						 -| or |- indicates negative regulation
		weight (dict, optional): Dictionary mapping edge tuples (start,end) to weights
		default_weight (float, optional): Default weight for edges not in weight dict
						 
	Returns:
		networkx.DiGraph: Directed graph representation with node observation status
		
	Raises:
		TypeError: If annotation is not a string
		ValueError: If annotation is empty or malformed
	"""
	import networkx as nx
	
	# Input validation
	if not isinstance(annotation, str):
		raise TypeError("Annotation must be a string")
	
	annotation = annotation.strip()
	if not annotation:
		raise ValueError("Annotation cannot be empty")
		
	G = nx.DiGraph()
	
	try:
		# Split into individual edge strings
		edge_strings = [s.strip() for s in annotation.split()]
		
		for edge_string in edge_strings:
			if not edge_string:
				continue
				
			# Split on arrows/bars
			nodes = edge_string.replace('->', ' ').replace('<-', ' ').replace('-|', ' ').replace('|-', ' ').split()
			
			# Handle single node case
			if len(nodes) == 1:
				node = nodes[0]
				if any(c in node for c in ['>', '<', '-', '|', ' ']):
					raise ValueError(f"Node cannot contain special characters: {edge_string}")
				if node not in G:
					G.add_node(node, observed=node.isupper())
				continue
				
			# Validate nodes for edge case
			if len(nodes) < 2:
				raise ValueError(f"Invalid edge specification: {edge_string}")
			
			if any(any(c in node for c in ['>', '<', '-', '|', ' ']) for node in nodes):
				raise ValueError(f"Nodes cannot contain special characters: {edge_string}")
			
			# Process each pair of adjacent nodes
			for i in range(len(nodes)-1):
				# Check direction between this pair
				segment = edge_string[edge_string.find(nodes[i]):edge_string.find(nodes[i+1])+1]
				
				# Keep original case for nodes
				node1 = nodes[i][0].upper()+nodes[i][1:]
				node2 = nodes[i+1][0].upper()+nodes[i+1][1:]
				
				# Add nodes with observation status if they don't exist
				if node1 not in G:
					G.add_node(node1, observed=not nodes[i].islower())
				if node2 not in G:
					G.add_node(node2, observed=not nodes[i+1].islower())
				
				# Determine edge direction and sign
				if '->' in segment:
					edge = (node1, node2)
					is_negative = False
				elif '<-' in segment:
					edge = (node2, node1)
					is_negative = False
				elif '-|' in segment:
					edge = (node1, node2)
					is_negative = True
				elif '|-' in segment:
					edge = (node2, node1)
					is_negative = True
				else:
					raise ValueError(f"Missing or invalid edge direction in: {segment}")
				
				# Set edge weight with sign check
				if weight and edge in weight:
					edge_weight = weight[edge]
					if (is_negative and edge_weight > 0) or (not is_negative and edge_weight < 0):
						raise ValueError(f"Edge weight sign {edge_weight} doesn't match annotation for edge {edge}")
				else:
					edge_weight = -default_weight if is_negative else default_weight
					
				G.add_edge(*edge, weight=edge_weight)
					
	except Exception as e:
		raise ValueError(f"Failed to parse annotation: {str(e)}")
				
	return G

def draw_digraph(G, axis, node_x=None, node_y=None,expand=0.2,**ka):
	"""
	Draw a directed graph schematically with nodes colored based on observation status.
	
	Args:
		G (nx.DiGraph): A directed graph with 'observed' node attributes
		axis: Matplotlib axis to draw on
		node_x (list, optional): List of x coordinates for nodes in alphabetical order. Defaults to incremental values.
		node_y (list, optional): List of y coordinates for nodes in alphabetical order. Defaults to zeros.
		
	Raises:
		TypeError: If G is not a NetworkX DiGraph
		ValueError: If coordinate lists don't match number of nodes
	"""
	import matplotlib
	import networkx as nx
	
	# Validate input
	if not isinstance(G, nx.DiGraph):
		raise TypeError("Input must be a NetworkX DiGraph")
		
	# Verify all nodes have 'observed' attribute
	for node, attrs in G.nodes(data=True):
		if 'observed' not in attrs:
			raise ValueError(f"Node {node} missing required 'observed' attribute")
	
	try:
		# Get alphabetically sorted nodes
		sorted_nodes = sorted(G.nodes())
		n_nodes = len(sorted_nodes)
		
		# Set default positions if not provided
		if node_x is None:
			node_x = np.linspace(0,1,n_nodes)
		if node_y is None:
			node_y = [0] * n_nodes
			
		# Validate coordinate list lengths
		if len(node_x) != n_nodes or len(node_y) != n_nodes:
			raise ValueError("Coordinate lists must match number of nodes")
			
		# Create position dictionary
		pos = {node: (x, y) for node, x, y in zip(sorted_nodes, node_x, node_y)}
		
		# Draw nodes
		observed_nodes = [node for node, attr in G.nodes(data=True) if attr['observed']]
		unobserved_nodes = [node for node, attr in G.nodes(data=True) if not attr['observed']]
		
		# Draw unobserved nodes in light gray
		nx.draw_networkx_nodes(G, pos, 
							 node_color='white',
							 nodelist=unobserved_nodes,
							 edgecolors='gray',
							 node_size=500,
							 ax=axis)
		
		# Draw observed nodes in black
		nx.draw_networkx_nodes(G, pos,
							 node_color='white',
							 nodelist=observed_nodes, 
							 edgecolors='black',
							 node_size=500,
							 ax=axis)
		
		# Draw edges
		style=matplotlib.patches.ArrowStyle.BarAB(widthA=0,angleA=0,widthB=0.4,angleB=0)
		for arrowstyle,sign in [(style,-1),('-|>',1)]:
			nx.draw_networkx_edges(G, pos, 
								edge_color='black',
								arrows=True,
								arrowsize=20,
								arrowstyle=arrowstyle,
								edgelist=[(u, v) for (u, v, d) in G.edges(data=True) if d['weight']*sign>0],
								ax=axis,min_source_margin=15,min_target_margin=14)
		
		# Add labels
		nx.draw_networkx_labels(G, pos,
							  {node: node for node in unobserved_nodes},
							  font_color='gray',
							  ax=axis)
		nx.draw_networkx_labels(G, pos,
							  {node: node for node in observed_nodes},
							  font_color='black',
							  ax=axis)
		xlim=axis.get_xlim()
		axis.set_xlim(-expand,1+expand)
		ylim=axis.get_ylim()
		axis.set_ylim(-expand,1+expand)
		axis.axis('off')
		axis.set_aspect('equal')
	
		
	except Exception as e:
		raise RuntimeError(f"Error drawing graph: {str(e)}")

def generate_data_from_dag(G, n_samples,discrete={},**ka):
	"""
	Generate simulated data from a Directed Acyclic Graph (DAG) where each node follows
	a Gaussian distribution with variance 1 and mean dependent on its parents.
	
	Args:
		G (networkx.DiGraph): The input DAG
		n_samples (int): Number of samples to generate
		discrete (dict): Dictionary mapping node names to number of discrete categories.
			Nodes in this dict will generate discrete values from 0 to n instead of
			continuous Gaussian values. These nodes must not have any parents.
	
	Returns:
		dict: Dictionary mapping node names to numpy arrays of generated values
		
	Raises:
		ValueError: If input graph is not a DAG or other invalid inputs
		RuntimeError: If there are issues during data generation
	"""
	import numpy as np
	import networkx as nx
	
	# Input validation
	if not isinstance(G, nx.DiGraph):
		raise ValueError("Input graph must be a networkx.DiGraph")
	if not nx.is_directed_acyclic_graph(G):
		raise ValueError("Input graph must be acyclic (a DAG)")
	if not isinstance(n_samples, int) or n_samples <= 0:
		raise ValueError("n_samples must be a positive integer")
		
	
	try:
		# Get topological sort to ensure we generate parent data before children
		sorted_nodes = list(nx.topological_sort(G))
		
		# Initialize data dictionary
		data = {}
		
		# Generate data for each node in topological order
		for node in sorted_nodes:
			parents = list(G.predecessors(node))
			if node in discrete:
				assert len(parents)==0
				assert discrete[node]>0 and isinstance(discrete[node],int)
				data[node]=(np.random.rand(n_samples,discrete[node])>0.5).sum(axis=1)
			else:
				# Base mean is 0 if no parents
				mean = np.zeros(n_samples)
				
				# Add contribution from each parent
				for parent in parents:
					weight = G[parent][node]['weight']
					mean += weight * data[parent]
					
				# Generate samples from Gaussian with computed mean and variance 1
				data[node] = np.random.normal(loc=mean, scale=1.0, size=n_samples)
			
		return data
		
	except Exception as e:
		raise RuntimeError(f"Error generating data: {str(e)}")
	
def normalize_data(data,discrete={},**ka):
	"""
	Normalize each vector in the data dictionary to have 0 mean and unit variance.
	
	Args:
		data: Dictionary mapping names to numpy arrays
		
	Returns:
		dict: Dictionary with normalized arrays
		
	Raises:
		ValueError: If input is not a dictionary or contains non-numeric arrays
		RuntimeError: If normalization fails due to zero standard deviation
	"""
	import numpy as np
	if not isinstance(data, dict):
		raise ValueError("Input must be a dictionary")
		
	normalized = {}
	for name, vector in data.items():
		if name in discrete:
			normalized[name]=vector
			continue
		try:
			mean = np.mean(vector)
			std = np.std(vector)
			if std == 0:
				raise RuntimeError(f"Cannot normalize {name} - standard deviation is 0")
			normalized[name] = (vector - mean) / std
		except Exception as e:
			raise RuntimeError(f"Error normalizing {name}: {str(e)}")
			
	return normalized

def draw_panel(nets,figsize=(3,3),n_samples=1000,draw_distribution=True,draw_network=True,draw_data=[],max_width=5,discrete={},**ka):
	import matplotlib.pyplot as plt
	import itertools
	assert all(len(x)==2 for x in draw_data)
	if max_width is None or max_width<len(nets):
		max_width=len(nets)

	t1=(len(draw_data)+int(draw_network))
	fig,axes=plt.subplots(t1,max_width,figsize=(figsize[0]*max_width,figsize[1]*t1))
	assert len(draw_data)>0 or draw_network
	if axes.ndim==1:
		axes=axes.reshape(t1,max_width)
	for j,(net,kwargs) in enumerate(nets):
		g=string_to_digraph(net,**kwargs)
		i=0
		#Write networkx.DiGraph to the decomposition of conditional probability
		if draw_distribution:
			ax=axes[0,j]
			nodes=sorted(g.nodes)
			s='$P('+','.join(nodes)+')='+''.join(['P('+x+('|'+','.join(g.predecessors(x)) if len(list(g.predecessors(x)))>0 else '')+')' for x in nodes])+'$'
			ax.set_title(s)
		if draw_network:
			ax=axes[i,j]
			draw_digraph(g,ax,**kwargs)
			i+=1
		for var2 in draw_data:
			ax=axes[i,j]
			data=generate_data_from_dag(g,n_samples,discrete=discrete)
			data=normalize_data(data,discrete=discrete)
			if any(x in discrete for x in var2):
				assert var2[0] in discrete and var2[1] not in discrete, 'Discrete variables must be on the x-axis'
				t1=ax.violinplot([data[var2[1]][data[var2[0]] == val] for val in sorted(set(data[var2[0]]))], positions=range(1, len(set(data[var2[0]]))+1), showmedians=True)
				for pc in t1['bodies']:
					pc.set_facecolor('gray')
					pc.set_alpha(0.5)
					pc.set_edgecolor('black')
				[t1[x].set_colors('black') for x in ['cbars','cmins','cmaxes','cmedians']]
				ax.set_xticks(range(1, len(set(data[var2[0]]))+1))
				ax.set_xticklabels(sorted(set(data[var2[0]])))
			else:
				ax.scatter(data[var2[0]],data[var2[1]],alpha=0.2,marker='.',lw=0,color='black')
				ax.set_xticks([])
				ax.set_xlim(-5,5)
				ax.set_aspect('equal')
			ax.spines['top'].set_visible(False)
			ax.spines['right'].set_visible(False)
			ax.set_yticks([])
			ax.set_ylim(-5,5)
			ax.set_xlabel(var2[0])
			ax.set_ylabel(var2[1])
			i+=1
	for i,j in itertools.product(range(len(axes)),range(len(nets),max_width)):
		ax=axes[i,j]
		ax.axis('off')
	return fig,axes