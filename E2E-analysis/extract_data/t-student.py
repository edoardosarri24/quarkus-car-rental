
import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

# 1. Caricamento Dati
file_path = "results/correlation0/real_e2e_execution_time.csv"
try:
    df = pd.read_csv(file_path)
    # Assumiamo che la colonna si chiami 'duration_ms'. Se diversa, adatta il codice.
    # In base all'header del tuo file, sembra 'duration_ms'.
    data = df['duration_ms'].values
except FileNotFoundError:
    print(f"Errore: File non trovato in {file_path}")
    exit(1)
except KeyError:
    print("Errore: Colonna 'duration_ms' non trovata. Controlla l'header del CSV.")
    # Fallback se non c'è header o ha nome diverso: prendi la prima colonna
    data = df.iloc[:, 0].values

N_total = len(data)
print(f"Totale campioni: {N_total}")

# 2. Suddivisione in Batch (Simulazione di Run multiple)
# Definiamo un numero di batch sufficiente per Student (es. 30)
num_batches = 30
batch_size = N_total // num_batches

# Scartiamo eventuali dati in eccesso alla fine per avere batch uguali
data_trimmed = data[:num_batches * batch_size]
batches = data_trimmed.reshape((num_batches, batch_size))

print(f"Configurazione: {num_batches} batch da {batch_size} campioni ciascuno.")

# 3. Calcolo della CDF per ogni Batch
# Definiamo i punti x su cui valutare la CDF (es. da min a max dei tempi)
x_min = np.min(data)
x_max = np.percentile(data, 99) # Tagliamo gli outlier estremi per il grafico
eval_points = np.linspace(x_min, x_max, 200)

batch_cdfs = []

for batch in batches:
    # Ordiniamo i dati del batch
    sorted_batch = np.sort(batch)
    # Calcoliamo la probabilità empirica per ogni punto di valutazione
    # searchsorted restituisce l'indice dove inserire eval_points per mantenere l'ordine
    # dividendo per batch_size otteniamo la proporzione (CDF)
    cdf_values = np.searchsorted(sorted_batch, eval_points, side='right') / batch_size
    batch_cdfs.append(cdf_values)

batch_cdfs = np.array(batch_cdfs) # Shape: (30, 200)

# 4. Statistica di Student per ogni punto x
# Calcoliamo media e deviazione standard campionaria *tra i batch* per ogni punto x
mean_cdf = np.mean(batch_cdfs, axis=0)
std_error_cdf = np.std(batch_cdfs, axis=0, ddof=1) / np.sqrt(num_batches)

# Gradi di libertà
dof = num_batches - 1
# Valore critico t per intervallo di confidenza al 95% (two-tailed)
confidence_level = 0.95
t_critical = stats.t.ppf((1 + confidence_level) / 2, dof)

# Margine di errore
margin_of_error = t_critical * std_error_cdf

lower_bound = mean_cdf - margin_of_error
upper_bound = mean_cdf + margin_of_error

# 5. Plotting
plt.figure(figsize=(10, 6))

# Plot della media
plt.plot(eval_points, mean_cdf, label='Mean CDF', color='blue', linewidth=2)

# Plot delle bande di confidenza (Area ombreggiata)
plt.fill_between(eval_points, lower_bound, upper_bound, color='blue', alpha=0.2, label=f'{int(confidence_level*100)}% Confidence Interval (Student\'s t)')

# Plot delle singole run (opzionale, per vedere la varianza grezza) - ne plottiamo solo alcune per pulizia
for i in range(min(5, num_batches)): 
    plt.plot(eval_points, batch_cdfs[i], color='gray', alpha=0.3, linewidth=0.5, linestyle='--')

plt.title(f'CDF con Intervallo di Confidenza (Student t-test)\nBatches: {num_batches}, Samples/Batch: {batch_size}')
plt.xlabel('Response Time (ms)')
plt.ylabel('Cumulative Probability (P(X <= x))')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(loc='lower right')

# Salva il grafico
output_file = "cdf_student_confidence.svg"
plt.savefig(output_file, format='svg')
print(f"Grafico salvato in: {output_file}")
