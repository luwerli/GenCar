# =========================================================
# GENERALIZAÇÃO CARTOGRÁFICA - CURVAS DE NÍVEL
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
SAIDA_SHP  = r"resultado\curvas_50k_generalizadas_v2.shp"

CAMPO_COTA = "COTA"     # campo de altitude
EQUIDIST   = 20         # metros
EPSILON_DP = 10        # tolerância gráfica (em metros)

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

# ---------------------------------------------------------
# 6. DOUGLAS-PEUCKER COM PONTOS FIXOS
# ---------------------------------------------------------

def simplificar_linha_com_fixos(linha, pontos_fixos, epsilon):
    """
    Douglas-Peucker com preservação de pontos fixos (rios)
    Compatível com Shapely 2.x
    """

    # Caso simples: sem pontos fixos
    if not pontos_fixos:
        return linha.simplify(epsilon, preserve_topology=True)

    segmentos = [linha]

    for p in pontos_fixos:
        novos_segmentos = []

        for seg in segmentos:
            if seg.distance(p) < 1e-6:
                resultado = split(seg, p.buffer(0.01))

                # 🔹 Tratamento correto do GeometryCollection
                if isinstance(resultado, GeometryCollection):
                    novos_segmentos.extend(
                        [g for g in resultado.geoms if g.geom_type == "LineString"]
                    )
                else:
                    novos_segmentos.extend(resultado)

            else:
                novos_segmentos.append(seg)

        segmentos = novos_segmentos

    # Simplificação segmento a segmento
    segmentos_simplificados = [
        s.simplify(epsilon, preserve_topology=True)
        for s in segmentos
        if not s.is_empty
    ]

    # Reconstrução mantendo continuidade
    coords = []
    for s in segmentos_simplificados:
        coords.extend(list(s.coords))

    return LineString(coords)

# ---------------------------------------------------------
# 7. APLICAÇÃO DA SIMPLIFICAÇÃO
# ---------------------------------------------------------

geoms_simplificadas = []

for idx, row in curvas_sel.iterrows():
    linha = row.geometry
    fixos = row["fixos"]

    linha_simpl = simplificar_linha_com_fixos(
        linha,
        fixos,
        EPSILON_DP
    )

    geoms_simplificadas.append(linha_simpl)

curvas_sel["geometry"] = geoms_simplificadas

# ---------------------------------------------------------
# 8. LIMPEZA FINAL
# ---------------------------------------------------------

curvas_final = curvas_sel.drop(columns=["mantida", "fixos"])

# ---------------------------------------------------------
# 9. EXPORTAÇÃO
# ---------------------------------------------------------

curvas_final.to_file(SAIDA_SHP)

print("✔ Generalização concluída com sucesso!")
print(f"Arquivo salvo em: {SAIDA_SHP}")
