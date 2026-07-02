# 2D trapping rain water

Given a 2D `grid` of non-negative integer heights, compute the total volume of water trapped after
rain. Water escapes off any edge of the grid (border cells hold no water); an interior cell traps
water up to the lowest height along the highest-constrained path to the border. Write
`trap_water_2d(grid)` returning the total trapped volume as an int.

## Examples

```
trap_water_2d([[1, 1, 1], [1, 0, 1], [1, 1, 1]]) == 1
trap_water_2d([[9, 9, 9], [9, 0, 9], [9, 9, 9]]) == 9
trap_water_2d([[3, 3, 3, 3], [3, 0, 0, 3], [3, 3, 3, 3]]) == 6
trap_water_2d([[1, 2], [3, 4]]) == 0
```
