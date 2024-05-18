class TreeNode:
    def __init__(self,value = None):
        self.alfa = float('-inf')
        self.beta = float('inf')
        self.value = value
        self.children = []
        self.parent = None
    def is_leaf(self):
        return len(self.children) == 0

def minimax(node, depth, isMaxLevel, alpha, beta):
    if depth == 0 or node.is_leaf():
        return node.value
    # maxPlayer determine if it is a max level
    if isMaxLevel:
        max_eval = float('-inf')
        for child in node.children:
            current_eval = minimax(child, depth - 1, False, alpha, beta)
            max_eval = max(max_eval, current_eval)
            alpha = max(alpha, max_eval)
            child.alpha = alpha
            print(f'Value = {child.value}, Alpha={alpha} Beta={beta}')
            if beta <= alpha:
                print(f'Pruning : {beta}<={alpha}')
                break
        return max_eval
    else:
        minval = float('inf')
        for child in node.children:
            value = minimax(child, depth - 1, True, alpha, beta)
            minval = min(minval, value)
            beta = min(beta, minval)
            child.beta = beta
            print(f'Value = {child.value}, Alpha={alpha} Beta={beta}')
            if beta <= alpha:
                print(f'Pruning : {beta}<={alpha}')
                break
        return minval

def build_sample_tree() -> TreeNode:
    root = TreeNode()
    left_tree = TreeNode(5.0)
    left_tree.parent = root
    right_tree = TreeNode()
    right_tree.parent = root

    right_tree_subtree_right = TreeNode()
    right_tree_subtree_left = TreeNode()

    right_tree_subtree_right.parent = right_tree
    right_tree_subtree_left.parent = right_tree

    right_tree_subtree_left_right_right = TreeNode()
    right_tree_subtree_left_right_right.children = [TreeNode(4.0), TreeNode(2.0)]
    right_tree_subtree_left.children = [TreeNode(1.0), right_tree_subtree_left_right_right]
    
    right_tree_subtree_right = TreeNode()
    right_tree_subtree_right_right = TreeNode()
    right_tree_subtree_right.children = [ TreeNode(5.0), right_tree_subtree_right_right]
    right_tree_subtree_right_right.children = [ TreeNode(4.0), TreeNode(3.0)]
    # add subtree
    right_tree.children = [ right_tree_subtree_left, right_tree_subtree_right]
    root.children = [left_tree, right_tree]
    return root
    


if __name__=="__main__":    
    root = build_sample_tree()
    best_value = minimax(root, 6, True, float('-inf'), float('+inf'))
    print(best_value)
    

    