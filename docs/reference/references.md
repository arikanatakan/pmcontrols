# References

pmcontrols implements standard, published project-control methods. The
methods, the standards they follow, the reference example used for
validation, and the software it builds on are listed here. Each is also
cited at the point of use in the source and the guides.

## Methods

- Kelley, J. E., and Walker, M. R. (1959). Critical-Path Planning and
  Scheduling. *Proceedings of the Eastern Joint Computer Conference*,
  160-173.
- Kelley, J. E. (1961). Critical-Path Planning and Scheduling: Mathematical
  Basis. *Operations Research*, 9(3), 296-320. The time/cost trade-off solved
  by `crash`.
- Fulkerson, D. R. (1961). A Network Flow Computation for Project Cost
  Curves. *Management Science*, 7(2), 167-178.
- Malcolm, D. G., Roseboom, J. H., Clark, C. E., and Fazar, W. (1959).
  Application of a Technique for Research and Development Program Evaluation
  (PERT). *Operations Research*, 7(5), 646-669. The three-point estimate used
  by `pert`.
- Lipke, W. (2003). Schedule is Different. *The Measurable News*, Summer
  2003, 31-34. Earned schedule (ES, SPI(t), IEAC(t)).

## Standards

- Project Management Institute. *A Guide to the Project Management Body of
  Knowledge (PMBOK Guide)*. PMI. Earned-value cost indicators.
- ANSI/EIA-748, *Earned Value Management Systems*. SAE International.

## Validation example

- Render, B., Stair, R. M., and Hanna, M. E. *Quantitative Analysis for
  Management*. Pearson. The General Foundry network and crash data, used as a
  reference case (see [Validation](validation.md) and
  `tests/validation_cases.json`).

## Software

- Harris, C. R., et al. (2020). Array programming with NumPy. *Nature*, 585,
  357-362.
- Virtanen, P., et al. (2020). SciPy 1.0: Fundamental Algorithms for
  Scientific Computing in Python. *Nature Methods*, 17, 261-272. `crash` uses
  `scipy.optimize.linprog`.
- Huangfu, Q., and Hall, J. A. J. (2018). Parallelizing the dual revised
  simplex method. *Mathematical Programming Computation*, 10, 119-142. HiGHS,
  the solver behind `linprog`.
- The pandas development team. *pandas*. The tidy result tables.
- Hunter, J. D. (2007). Matplotlib: A 2D Graphics Environment. *Computing in
  Science & Engineering*, 9(3), 90-95. The optional `[plot]` charts.
