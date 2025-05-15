## Problem Specification
Given
- Set of potential locations $V$
- Root (start) node $r \in V$
- Sink (end) node $e \in V, e \neq r$
- Travel Cost matrix $T$: $T_{ij}$ is the cost to travel between $v_i, v_j \in V$
- Vertices we can stay at, $V_{stay} \subset V$, and the associated cost vector of stay $C$: $T_i$, $ 0 \leq T_i \leq \infty$ is the cost to stay at $v_i \in V$ (possibly infinite, if it is not possible to stay at $v_i$).

We seek to maximize the number of locations visited, while minimizing the total cost of travel + stay over a $D$ day trip, subject to the constraints:

- We don't want to revisit vertices, except ones in $V_{stay}$. In practice we'll just make $D$ copies of these vertices, so no vertex will be revisited.
- We must return to a stay vertex at the end of each day.
- We disallow any leg of the journey from being longer than $L$
- We can't visit more than 2 vertices in a day.

## ILP formulation
Define decision variables:
- $x_{ij}^d \in \{0, 1\}$: Use directed arc from $i \to j, i,j \in V$ on day $d$
- $y_j^d \in \{0, 1\}$: indicates if we visited $j$ on day $d$, i.e, $y_j^d = \max\limits_{i \in V} x_{ij}^d = \max\limits_{i \in V} x_{ji}^d$.
- $D = \{1, ..., 5\}$

Constraints:

1. $\sum_{j} x_{rj}^1 = 1, \sum_{i} x_{ir}^1 = 1$ (start at $r$, never revisit)
2. $\sum_i x_{is}^5 = 1, \sum_{j} x_{sj} = 0$, (end at $s$, never leave)
3. $\sum_{j}x_{i j}^d =\sum_{j}x_{j i}^d =y_i^d
\quad\forall i\in V\setminus\{r,e\},\;d\in D.$ (continuity, we must leave any place we enter except start and end)
4.  $\sum_{j\in V_{\text{stay}}} \sum_{i} x_{ij}^{d}=1, d=1,\dots,D$ (stay only at one place per night)
5.  $\sum_{i\in V}x_{i j}^{d} =\sum_{k\in V}x_{j k}^{d+1}
\quad\forall\,j\in V_{\text{stay}},\;d=1\ldots4.$ (end day on stay vertex, start next day from that vertex)
6. $\sum_{i\in V}x_{ij}^{d}=\sum_{k\in V}x_{jk}^{d+1} \forall j\in V_{\text{stay}},\;d=1,\dots,D-1$ (start from previous day's stay vertex)
7. $\sum_{i\in V\setminus V_{\text{stay}}}y_i^{d}\le 2 \; \forall d\in D$ (daily visit limit)
8.  $\sum_{d\in D}y_i^{d}\le 1 \; \forall i\in V\setminus V_{\text{stay}}$ (No repeat visits to non-stay spots )
9.  $x_{ij}^d = 0 \forall d \; \forall i,j \; \text{s.t}\; T_{ij} > L$ (no leg longer than $L$)
10. Per day subtour prevention

Objective:
\[
\max \;\Bigl[\;
\underbrace{\sum_{d\in D}\sum_{i\notin\{r,e\}} y_i^{d}}_{\text{total distinct spots visited (clones count by day)}}\;-\;
\alpha\Bigl(
\underbrace{\sum_{d\in D}\sum_{(i,j)\in A}T_{ij}\,x_{ij}^{d}}_{\text{driving cost}}
+\;
\underbrace{\sum_{d\in D}\sum_{i\in V_{\text{stay}}} s_i\,y_i^{d}}_{\text{overnight cost}}
\Bigr)\Bigr],
\]