# Introduction:
	1. Molecular Docking
		1. Sampling & Scoring
			- Sample available space of ligand within the rigid receptor, necessary to cover conformational landscape to find energy minima
			- Scoring to evaluate sampled conformations
		2. Binding Mode
			- Essential for: binding affinity, lead optimization
		3. Binding Affinity
			- Useful for virtual screening
			- Determine if useful for experimental analysis
		4. Speed of Calculation
			- Fast = key for drug discovery
			- balancing act of speed and accuracy
	2. Scoring Functions
		1. Empirical
			- Background
				- Based on protein-ligand structure properties
				- Combination of Knowledge Based with Force Field
			- Pros
				- less prone to overfitting
				- can extract what contributes to score
			- Cons
				- Hard to determine where errors come from
				- Does not generalize well if tuned parameters
		2. Knowledge Based
			- Background
				- Use known crystal structures for finding occurences of interactions
				- one method: Create PMF using Boltzmann dist, essentially becomes empirical function
			- Pros
				- Generalizes well
				- Quick computation on test time
			- Cons
				- Requires large database of known structures
				- Underestimate solvent effects
				- Difficult to understand meaning
		3. Limit of all of "Normal" SF
	3. Machine Learning for Scoring
		1. Learns arbitrary function
		2. 
		
	4. Related Works
	5. Brief Summary of Method


# Methods:
    1. Data
         1. Redocking
         2. Crossdocking
	Background of Gnina workings
    Gnina/Smina comparison
    Selecting the optimal model (selection of new default ensemble)
    Exploration of Settings (Selecting Default Settings)
        Defined Pocket (Exhaustiveness, CNN Rotations, Min RMSD Filter, Num MC Saved, Number of Modes)
        Whole Protein (Exhaustiveness, Number of Modes)
