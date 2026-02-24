# =========================================================
# GENERALIZAÇÃO CARTOGRÁFICA - CURVAS DE NÍVEL (com Hausdorff)
# Escala 1:25.000 → 1:50.000
# Preservação topológica com hidrografia
# =========================================================

import geopandas as gpd
from shapely.geometry import LineString, Point
from shapely import hausdorff_distance
from shapely.geometry import GeometryCollection
from shapely.ops import split
import numpy as np
import os

# ---------------------------------------------------------
# 1. PARÂMETROS GERAIS
# ---------------------------------------------------------

CURVAS_SHP = r"E:\ENGENHARIA CARTOGRÁFICA\MI_2980-1-SE\REL_Curva_Nivel_L.shp"
RIOS_SHP   = r"E:\ENGENHARIA CARTOGRÁFICA\MI_2980-1-SE\HID_Trecho_Drenagem_L.shp"

SAIDA_GPKG = r"resultado/curvas_50k_generalizadas.gpkg"
CSV_AVALIACAO = r"resultado/avaliacao_hausdorff.csv"

CAMPO_COTA = "COTA"     # campo de altitude
EQUIDIST   = 20         # metros
EPSILON_DP = 10        # tolerância gráfica (em metros)
LIMITE_HD = 10

os.makedirs("resultado", exist_ok=True)

# ---------------------------------------------------------
# 2. LEITURA DOS DADOS
# ---------------------------------------------------------

curvas = gpd.read_file(CURVAS_SHP)
rios   = gpd.read_file(RIOS_SHP)

# ---------------------------------------------------------
# 3. GARANTIA DE CRS PROJETADO (METROS)
# ---------------------------------------------------------

if curvas.crs.is_geographic:
    curvas = curvas.to_crs(epsg=31981)  # ajuste zona UTM
    rios   = rios.to_crs(curvas.crs)

# ---------------------------------------------------------
# 4. SELEÇÃO SEMÂNTICA - CURVAS MÚLTIPLAS DE 20 m
# ---------------------------------------------------------

curvas["mantida"] = curvas[CAMPO_COTA] % EQUIDIST == 0
curvas_sel = curvas[curvas["mantida"]].copy()

# ---------------------------------------------------------
# 5. IDENTIFICAÇÃO DE INTERSEÇÕES COM HIDROGRAFIA
# ---------------------------------------------------------

rios_union = rios.union_all()

def pontos_intersecao(linha, rios_geom):
    inter = linha.intersection(rios_geom)
    if inter.is_empty:
        return []
    if inter.geom_type == "Point":
        return [inter]
    if inter.geom_type == "MultiPoint":
        return list(inter.geoms)
    return []

curvas_sel["fixos"] = curvas_sel.geometry.apply(
    lambda g: pontos_intersecao(g, rios_union)
)

# vértices nas interseções

def inserir_vertices_intersecao(linha, pontos):
    for p in pontos:
        if linha.distance(p) < 1e-6:
            partes = split(linha, p.buffer(0.001))
            if isinstance(partes, GeometryCollection):
                coords = []
                for g in partes.geoms:
                    if g.geom_type == "LineString":
                        coords.extend(list(g.coords))
                linha = LineString(coords)
    return linha

# ---------------------------------------------------------
# 6. DOUGLAS-PEUCKER COM PONTOS FIXOS
# ---------------------------------------------------------
def simplificar_linha_com_fixos(linha, pontos_fixos, epsilon, limite_hd):
    """
    Simplificação DP restrita:
    - preserva interseções
    - controla deslocamento por Hausdorff
    - força vértices coincidentes
    """
    # Caso sem interseções
    if not pontos_fixos:
        linha_simpl = linha.simplify(epsilon, preserve_topology=True)

        hd = linha.hausdorff_distance(linha_simpl)
        if hd > limite_hd:
            return linha

        return linha_simpl

    # Caso com interseções
    segmentos = [linha]

    for p in pontos_fixos:
        novos = []
        for seg in segmentos:
            if seg.distance(p) < 1e-6:
                partes = split(seg, p.buffer(0.001))
                if isinstance(partes, GeometryCollection):
                    novos.extend(
                        [g for g in partes.geoms if g.geom_type == "LineString"]
                    )
                else:
                    novos.extend(partes)
            else:
                novos.append(seg)
        segmentos = novos

    segmentos_simpl = [
        s.simplify(epsilon, preserve_topology=True)
        for s in segmentos if not s.is_empty
    ]

    coords = []
    for s in segmentos_simpl:
        coords.extend(list(s.coords))

    linha_simpl = LineString(coords)

    # 🔹 Inserir vértices exatamente nos rios
    linha_simpl = inserir_vertices_intersecao(linha_simpl, pontos_fixos)

    # 🔹 Validação global por Hausdorff
    hd = linha.hausdorff_distance(linha_simpl)
    if hd > limite_hd:
        return linha

    return linha_simpl

# ---------------------------------------------------------
# 7. APLICAÇÃO DA SIMPLIFICAÇÃO
# ---------------------------------------------------------

geoms_simpl = []
hausdorff_vals = []
aceita_hd = []
verts_orig = []
verts_simpl = []

for idx, row in curvas_sel.iterrows():
    linha = row.geometry
    fixos = row["fixos"]

    linha_s = simplificar_linha_com_fixos(
        linha,
        fixos,
        EPSILON_DP,
        LIMITE_HD
    )

    hd = linha.hausdorff_distance(linha_s)

    geoms_simpl.append(linha_s)
    hausdorff_vals.append(hd)
    aceita_hd.append(hd <= LIMITE_HD)
    verts_orig.append(len(linha.coords))
    verts_simpl.append(len(linha_s.coords))

curvas_sel["geometry"] = geoms_simpl
curvas_sel["hausdorff_m"] = hausdorff_vals
curvas_sel["aceita_hd"] = aceita_hd
curvas_sel["vtx_orig"] = verts_orig
curvas_sel["vtx_simpl"] = verts_simpl

# ---------------------------------------------------------
# 8. LIMPEZA FINAL
# ---------------------------------------------------------

curvas_final = curvas_sel.drop(columns=["mantida", "fixos"])

# ---------------------------------------------------------
# 9. EXPORTAÇÃO
# ---------------------------------------------------------

curvas_final.to_file(
    SAIDA_GPKG,
    layer="curvas_generalizadas",
    driver="GPKG"
)

avaliacao = curvas_final.drop(columns="geometry")
avaliacao.to_csv(CSV_AVALIACAO, index=False)

print("✔ Generalização concluída com sucesso!")
print(f"✔ Curvas: {SAIDA_GPKG}")
print(f"✔ Avaliação Hausdorff: {CSV_AVALIACAO}")
