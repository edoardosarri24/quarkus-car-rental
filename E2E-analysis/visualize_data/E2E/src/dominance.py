import numpy as np

def get_pdf(durations, n_bins=50, range_values=None):
    durations.sort()
    if range_values is None:
        hist, bins = np.histogram(durations, bins=n_bins)
    else:
        hist, bins = np.histogram(durations, bins=n_bins, range=range_values)
    return hist/len(durations), bins


def pairwise_dominance(durations1, durations2, minValue=None, maxValue=None, n_steps=100):
    if minValue == None:
        minValue = np.min([min(durations1), min(durations2)])
    if maxValue == None:
        maxValue = np.max([max(durations1), max(durations2)])
    pdf1, bins1 = get_pdf(durations1, n_steps, range_values=(minValue, maxValue))
    pdf2, bins2 = get_pdf(durations2, n_steps, range_values=(minValue, maxValue))
    cdf2 = [pdf2[0]]

    for index in range(1, n_steps):
        cdf2.append(cdf2[index-1] + pdf2[index])

    dominance = 0
    dt = bins1[1]-bins1[0]

    for index in range(n_steps):
        dominance += (1-cdf2[index]) * pdf1[index]

    return dominance