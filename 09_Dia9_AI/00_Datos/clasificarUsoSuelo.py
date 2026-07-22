"""
Clasificación de uso de suelo con Random Forest (pixel-wise).

1. Calcula NDVI / NDWI a partir de Sentinel-2
2. Genera etiquetas semilla por reglas espectrales (entrenamiento)
3. Entrena RandomForest y predice el mapa completo
4. Exporta raster clasificado + métricas
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import array_bounds
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

OUT = Path(__file__).resolve().parent
TIF = OUT / "sentinel2_cdmx_subset.tif"
CLASS_TIF = OUT / "landcover_rf_cdmx.tif"
METRICS = OUT / "rf_metrics.json"
PROBA_TIF = OUT / "landcover_rf_confianza.tif"

# Clases de negocio
CLASES = {
    1: "Vegetacion",
    2: "Urbano",
    3: "Suelo_desnudo",
    4: "Agua",
}
COLORS = {
    1: "#2ECC71",  # verde
    2: "#E74C3C",  # urbano
    3: "#F5CBA7",  # suelo
    4: "#3498DB",  # agua
}


def load_bands(path: Path):
    with rasterio.open(path) as src:
        blue = src.read(1).astype(np.float32)
        green = src.read(2).astype(np.float32)
        red = src.read(3).astype(np.float32)
        nir = src.read(4).astype(np.float32)
        profile = src.profile.copy()
        transform = src.transform
        crs = src.crs
    # Reflectancia Sentinel a menudo 0–10000
    scale = 10000.0
    blue, green, red, nir = blue / scale, green / scale, red / scale, nir / scale
    # nodata / extremos
    valid = (blue > 0) & (green > 0) & (red > 0) & (nir > 0)
    valid &= (blue < 1.5) & (nir < 1.5)
    return blue, green, red, nir, valid, profile, transform, crs


def indices(blue, green, red, nir):
    ndvi = (nir - red) / (nir + red + 1e-6)
    ndwi = (green - nir) / (green + nir + 1e-6)
    brightness = (blue + green + red) / 3.0
    return ndvi, ndwi, brightness


def seed_labels(ndvi, ndwi, brightness, valid):
    """Etiquetas semilla (heurística espectral) para entrenar el RF."""
    labels = np.zeros(ndvi.shape, dtype=np.uint8)
    # Agua: NDWI alto
    labels[valid & (ndwi > 0.15)] = 4
    # Vegetación: NDVI alto
    labels[valid & (ndvi > 0.35) & (labels == 0)] = 1
    # Urbano: bajo NDVI, brillo medio-alto, no agua
    labels[valid & (ndvi < 0.15) & (brightness > 0.08) & (brightness < 0.35) & (labels == 0)] = 2
    # Suelo desnudo: NDVI bajo-medio, brillo alto
    labels[valid & (ndvi < 0.25) & (brightness >= 0.18) & (labels == 0)] = 3
    # Relleno residual válido como urbano denso
    labels[valid & (labels == 0) & (ndvi < 0.30)] = 2
    labels[valid & (labels == 0)] = 1
    return labels


def sample_training(features, labels, valid, n_per_class=4000, seed=42):
    rng = np.random.default_rng(seed)
    X_list, y_list = [], []
    for c in CLASES:
        idx = np.argwhere(valid & (labels == c))
        if len(idx) == 0:
            continue
        take = min(n_per_class, len(idx))
        choice = idx[rng.choice(len(idx), size=take, replace=False)]
        rows, cols = choice[:, 0], choice[:, 1]
        X_list.append(features[rows, cols])
        y_list.append(np.full(take, c, dtype=np.uint8))
    X = np.vstack(X_list)
    y = np.concatenate(y_list)
    return X, y


def main() -> None:
    if not TIF.exists():
        from descargarSentinel2 import descargar

        descargar()

    blue, green, red, nir, valid, profile, transform, crs = load_bands(TIF)
    ndvi, ndwi, brightness = indices(blue, green, red, nir)

    # Feature cube: (H, W, F)
    feats = np.stack([blue, green, red, nir, ndvi, ndwi, brightness], axis=-1)
    seed = seed_labels(ndvi, ndwi, brightness, valid)

    X, y = sample_training(feats, seed, valid)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=120,
        max_depth=18,
        min_samples_leaf=3,
        n_jobs=-1,
        random_state=42,
        class_weight="balanced_subsample",
    )
    print(f"Entrenando RF con {len(X_train):,} muestras...")
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    report = classification_report(
        y_test, y_pred, target_names=[CLASES[c] for c in sorted(CLASES)], output_dict=True
    )
    cm = confusion_matrix(y_test, y_pred, labels=sorted(CLASES)).tolist()
    importances = dict(
        zip(
            ["blue", "green", "red", "nir", "ndvi", "ndwi", "brightness"],
            [float(x) for x in clf.feature_importances_],
        )
    )
    metrics = {
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "accuracy": float(report["accuracy"]),
        "report": report,
        "confusion_matrix": cm,
        "feature_importances": importances,
        "classes": CLASES,
    }
    METRICS.write_text(json.dumps(metrics, indent=2, ensure_ascii=False))
    print(f"Accuracy test: {metrics['accuracy']:.3f}")
    print("Importancias:", importances)

    # Predicción full raster
    h, w, f = feats.shape
    flat = feats.reshape(-1, f)
    valid_flat = valid.reshape(-1)
    pred_flat = np.zeros(h * w, dtype=np.uint8)
    conf_flat = np.zeros(h * w, dtype=np.float32)

    pred_valid = clf.predict(flat[valid_flat])
    proba = clf.predict_proba(flat[valid_flat])
    pred_flat[valid_flat] = pred_valid
    conf_flat[valid_flat] = proba.max(axis=1)

    pred = pred_flat.reshape(h, w)
    conf = conf_flat.reshape(h, w)

    out_profile = profile.copy()
    out_profile.update(count=1, dtype="uint8", nodata=0, compress="lzw")
    with rasterio.open(CLASS_TIF, "w", **out_profile) as dst:
        dst.write(pred, 1)
        dst.write_colormap(
            1,
            {
                0: (0, 0, 0, 0),
                1: (46, 204, 113, 255),
                2: (231, 76, 60, 255),
                3: (245, 203, 167, 255),
                4: (52, 152, 219, 255),
            },
        )

    conf_profile = profile.copy()
    conf_profile.update(count=1, dtype="float32", nodata=-1, compress="lzw")
    with rasterio.open(PROBA_TIF, "w", **conf_profile) as dst:
        conf_out = np.where(valid, conf, -1).astype(np.float32)
        dst.write(conf_out, 1)

    # Resumen de área
    pixel_m2 = abs(transform.a * transform.e)
    print("\nÁrea clasificada (km²):")
    for c, name in CLASES.items():
        area = (pred == c).sum() * pixel_m2 / 1e6
        print(f"  {name}: {area:.2f}")

    print(f"\nMapa: {CLASS_TIF}")
    print(f"Confianza: {PROBA_TIF}")
    print(f"Métricas: {METRICS}")


if __name__ == "__main__":
    main()
