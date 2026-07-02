# Matrix-chain multiplication (minimum cost)

Given `dims`, a list of `m+1` positive integers, you must multiply a chain of `m` matrices where the
i-th matrix has dimensions `dims[i-1] x dims[i]`. Multiplying a `p x q` matrix by a `q x r` matrix
costs `p*q*r` scalar multiplications. Write `min_matrix_mult(dims)` returning the **minimum total
scalar multiplications** over all valid parenthesizations. With 0 or 1 matrices the cost is `0`.

## Examples

```
min_matrix_mult([10, 20, 30]) == 6000
min_matrix_mult([10, 20, 30, 40]) == 18000
min_matrix_mult([5]) == 0
min_matrix_mult([5, 10]) == 0
```
