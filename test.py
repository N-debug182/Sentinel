
def landslide_probability(elevation, rainfall_24h, humidity, tree_cover):
    # --- Step 1: Normalisation ---
    elevation_norm = min(elevation / 1000, 1)          # clamp to 1
    rainfall_norm = min(rainfall_24h / 200, 1)
    humidity_norm = min(humidity / 100, 1)
    tree_norm = min(1 - (tree_cover / 100), 1)

    # --- Step 2: Weighted score ---
    risk_score = (
        0.35 * rainfall_norm +
        0.25 * humidity_norm +
        0.30 * elevation_norm +
        0.10 * tree_norm
    )

    # --- Step 3: Convert to probability ---
    probability = 1 / (1 + math.exp(-8 * (risk_score - 0.4)))

    # --- Step 4: Determine danger zone ---
    if probability < 0.25:
        zone = "SAFE"
    elif probability < 0.45:
        zone = "CAUTION"
    elif probability < 0.65:
        zone = "WARNING"
    else:
        zone = "DANGER – EVACUATE"

    return probability, zone

prob,zone = landslide_probability(elevation, rainfall_24h, humidity, tree_cover):

print(f"Probability: {prob:.2f}")
print(f"Zone: {zone}")
