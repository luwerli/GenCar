# GenCar – Generalização Cartográfica Automatizada
📌 Descrição

Este repositório apresenta a implementação de rotinas em Python para generalização cartográfica automática de curvas de nível, com foco na simplificação geométrica utilizando o algoritmo Douglas-Peucker.

O objetivo é automatizar a geração de cartas topográficas generalizadas, reduzindo a complexidade geométrica mantendo a coerência espacial e a legibilidade cartográfica.

Área de estudo: Carta topográfica de Rosário do Sul (MI_2980-1-SE).

🎯 Problema

A generalização cartográfica é um processo essencial na produção de mapas em diferentes escalas. A simplificação manual é demorada e sujeita a inconsistências.

Este projeto busca:

Reduzir vértices redundantes
Manter forma e estrutura das curvas
Automatizar o processo de simplificação
Permitir ajuste de tolerância conforme escala

🧠 Metodologia

O algoritmo implementado é baseado no método de Douglas-Peucker, que:

Define uma linha entre os extremos da curva
Calcula a distância perpendicular máxima
Mantém pontos acima da tolerância
Recursivamente simplifica os segmentos
Foram testados diferentes valores de tolerância para avaliar:
Redução percentual de vértices

Impacto visual

Manutenção da morfologia do relevo

🛠 Tecnologias Utilizadas e Softwares

GeoPandas
NumPy
Shapely
Matplotlib
QGIS (validação visual)

📊 Resultados

Redução significativa do número de vértices
Manutenção da coerência geométrica
Automatização do fluxo de generalização
