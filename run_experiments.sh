#!/bin/bash
# Progetto Artificial Intelligence - Daniele Materia
# Script per eseguire un esperimento completo: esegue il programma 10 volte per ogni istanza e calcola le statistiche sui risultati
CARTELLA="wfvs-instances-progetto-AI"
SCRIPT_PYTHON="hybrid_gen_algorithm.py"
SALVA_RIS="y"
RESULTS_FILE="results.csv"
STATS_FILE="experiment_stats.csv"

if [ ! -d "$CARTELLA" ]; then
    echo "Errore: La cartella '$CARTELLA' non esiste."
    exit 1
fi

if [ ! -f "$SCRIPT_PYTHON" ]; then
    echo "Errore: Il file '$SCRIPT_PYTHON' non esiste."
    exit 1
fi

# ripeti 10 volte l'esecuzione del programma
for i in {1..10}; do
    for file in "$CARTELLA"/*; do
        if [ -f "$file" ]; then
            echo "Eseguo: python $SCRIPT_PYTHON \"$file\" $SALVA_RIS"
            python "$SCRIPT_PYTHON" "$file" "$SALVA_RIS"
        fi
    done
done

# esegui script per calcolare le statistiche
echo "Eseguo: python calculate_results_stats.py $RESULTS_FILE $STATS_FILE"
python calculate_results_stats.py $RESULTS_FILE $STATS_FILE