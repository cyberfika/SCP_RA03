# Resultados experimentais

| Método | Categoria | Instância | Tempo (s) | |SB| | LB-LP | Gap | Cobertura | Observação |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Greedy baseline | Algoritmo guloso | n=16, k=10, p=6 | 24,895 | 105 | 39 | 2,69 | 100,00% | Baseline guloso determinístico com escolha de maior ganho marginal. |
| Stochastic Greedy | Probabilístico / randômico | n=16, k=10, p=6 | 1,208 | 115 | 39 | 2,95 | 100,00% | Amostra 256 por iteração; seed=42; fallback determinístico quando a amostra não cobre novos alvos. |
| GRASP | Metaheurística | n=16, k=10, p=6 | 143,862 | 107 | 39 | 2,74 | 100,00% | 5 construções; RCL=10; poda local=sim; seed=123. |
| Greedy + poda local | Busca local pós-greedy | n=16, k=10, p=6 | 28,268 | 105 | 39 | 2,69 | 100,00% | Removeu 0 candidatos redundantes mantendo cobertura exata. |
