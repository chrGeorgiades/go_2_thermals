

# Conversion Functions
def freq_to_ghz(freq):
    return round(freq / 1_000_000, 1)

def ghz_to_freq(ghz):
    return int(round(ghz * 1_000_000, 1))

def temp_to_celsius(temp):
    return int(temp / 1_000)