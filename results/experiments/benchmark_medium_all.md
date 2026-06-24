# Resultados experimentais

| Método | Categoria | Instância | Tempo (s) | |SB| | LB-LP | Gap | Cobertura | Observação |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Greedy baseline | Algoritmo guloso | n=15, k=9, p=6 | 10,035 | 140 | 60 | 2,33 | 100,00% | Baseline guloso determinístico com escolha de maior ganho marginal. |
| Stochastic Greedy | Probabilístico / randômico | n=15, k=9, p=6 | 0,743 | 152 | 60 | 2,53 | 100,00% | Amostra 256 por iteração; seed=42; fallback determinístico quando a amostra não cobre novos alvos. |
| GRASP | Metaheurística | n=15, k=9, p=6 | 48,813 | 143 | 60 | 2,38 | 100,00% | 5 construções; RCL=10; poda local=sim; seed=123. |
| Greedy + poda local | Busca local pós-greedy | n=15, k=9, p=6 | 10,755 | 140 | 60 | 2,33 | 100,00% | Removeu 0 candidatos redundantes mantendo cobertura exata. |
| Relaxação Lagrangiana | Relaxação / lower bound | n=15, k=9, p=6 | 23,948 | 140 | 60 | 2,33 | 100,00% | Relaxação Lagrangiana demonstrativa; 40 iterações; melhor bound lagrangiano=59.58; solução reparada por greedy. |
| Column Generation | Programação linear / pricing | n=15, k=9, p=6 | 18,551 | 171 | 60 | 2,85 | 100,00% | Column Generation relaxado; 25 rodadas de pricing; valor LP=111.19; solução arredondada e reparada. |
