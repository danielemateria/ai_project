# Progetto Artificial Intelligence - Daniele Materia
# script per il calcolo delle statistiche sui risultati ottenuti dagli esperimenti
import pandas as pd
import sys

df = pd.read_csv(sys.argv[1])
df = df.reset_index()
min_indices = df.groupby('instance_name')['best_fitness'].idxmin()

df = df.loc[min_indices].sort_values('instance_name')
df["instance_name"] = df["instance_name"].str.split("_").str[:3].str.join("_")

stats = (
    df.groupby("instance_name", group_keys=False)
    .agg(
        best_fitness_mean=("best_fitness", "mean"),
        best_fitness_std=("best_fitness", "std"),
        fitness_evaluations_mean=("fitness_evaluations", "mean"),
        execution_time_mean=("execution_time", "mean")
    )
    .reset_index()
)

stats["best_fitness_std"] = stats["best_fitness_std"].round(2)
stats["fitness_evaluations_mean"] = stats["fitness_evaluations_mean"].astype(int)
stats["execution_time_mean"] = stats["execution_time_mean"].round(2)
stats.to_csv(sys.argv[2], index=False)