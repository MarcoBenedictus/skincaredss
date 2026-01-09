install dependencies : 
pip install pandas numpy streamlit


there is a way to make the catalog bigger, that is by adding keywords
the drawback : there will be certain products dominating because they "include" most of the ingredients while the others does not.

brightening_keywords = [
    # Core Brightening
    'niacinamide', 'vitamin c', 'ascorbic', 'arbutin', 'licorice', 'glycyrrhiza', 'kojic', 'azelaic', 'retinol',
    # Acids (AHAs/BHAs)
    'glycolic', 'lactic', 'citric', 'malic', 'mandelic', 'tartaric', 'tranexamic', 'ferulic',
    # Antioxidants & Extracts
    'glutathione', 'mulberry', 'morus', 'turmeric', 'curcuma', 'rice', 'oryza', 'papaya', 'papain', 
    'grape', 'vitis', 'soy', 'galactomyces', 'bifida', 'ferment', 'resveratrol', 'bearberry'
]

anti_aging_keywords = [
    # Core Anti-Aging
    'retinol', 'retinyl', 'bakuchiol', 'peptide', 'oligopeptide', 'polypeptide', 'argireline', 'matrixyl',
    # Hydration & Plumping
    'hyaluronic', 'hyaluronate', 'ceramide', 'squalane', 'collagen', 'adenosine', 'glycerin',
    # Repair & Protection
    'tocopherol', 'coq10', 'ubiquinone', 'snail', 'allantoin', 'panthenol',
    # Botanicals
    'ginseng', 'panax', 'camellia', 'green tea', 'centella', 'madecassoside', 'asiaticoside', 'copper', 
    'yeast', 'saccharomyces'
]