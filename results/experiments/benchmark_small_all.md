# Resultados experimentais

| Método | Categoria | Instância | Tempo (s) | |SB| | LB-LP | Gap | Cobertura | Observação |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Greedy baseline | Algoritmo guloso | n=12, k=7, p=4 | 0,075 | 27 | 15 | 1,80 | 100,00% | Baseline guloso determinístico com escolha de maior ganho marginal. |
| Stochastic Greedy | Probabilístico / randômico | n=12, k=7, p=4 | 0,057 | 29 | 15 | 1,93 | 100,00% | Amostra 256 por iteração; seed=42; fallback determinístico quando a amostra não cobre novos alvos. |
| GRASP | Metaheurística | n=12, k=7, p=4 | 0,516 | 29 | 15 | 1,93 | 100,00% | 5 construções; RCL=10; poda local=sim; seed=123. |
| Greedy + poda local | Busca local pós-greedy | n=12, k=7, p=4 | 0,078 | 27 | 15 | 1,80 | 100,00% | Removeu 0 candidatos redundantes mantendo cobertura exata. |
| Relaxação Lagrangiana | Relaxação / lower bound | n=12, k=7, p=4 | 1,179 | 27 | 15 | 1,80 | 100,00% | Relaxação Lagrangiana demonstrativa; 40 iterações; melhor bound lagrangiano=14.14; solução reparada por greedy. |
| Column Generation | Programação linear / pricing | n=12, k=7, p=4 | 1,071 | 45 | 15 | 3,00 | 100,00% | Column Generation relaxado; 25 rodadas de pricing; valor LP=15.61; solução arredondada e reparada. |
