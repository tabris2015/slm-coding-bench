# Topological sort

Write a function `topological_sort(num_nodes, edges)` for a directed graph whose
nodes are the integers `0, 1, ..., num_nodes - 1`. Each edge is a two-element
list `[u, v]` meaning node `u` must come before node `v` in the ordering.

Return **any** valid topological ordering of all the nodes as a list of length
`num_nodes` (every node appears exactly once, and for every edge `[u, v]` node
`u` appears before node `v`).

If the graph contains a cycle (so no valid ordering exists), return an empty list
`[]`.

## Notes

- Many valid orderings may exist; returning any one of them is accepted.
- A graph with no edges has any permutation as a valid order.
- Self-loops (`[u, u]`) form a cycle, so the result must be `[]`.

## Examples

```
topological_sort(2, [[0, 1]])               # -> [0, 1]
topological_sort(3, [[0, 1], [0, 2]])       # -> e.g. [0, 1, 2] (any valid order)
topological_sort(2, [[0, 1], [1, 0]])       # -> [] (cycle)
topological_sort(3, [])                      # -> any permutation of [0, 1, 2]
```
