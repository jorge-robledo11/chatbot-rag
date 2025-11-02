"""
Plantillas de respuesta del agente. Se usan ESTRICTAMENTE como texto dentro del prompt.
"""

TECHNICAL_RESPONSE_TEMPLATE = r"""
PLANTILLA: RESPUESTA TÉCNICA DETALLADA (EXHAUSTIVA)
**Producto:** [Nombre canónico]

**Especificaciones técnicas (checklist de la categoría)**
- [Atributo 1]: [Valor | No especificado en la fuente]
- [Atributo 2]: [Valor | No especificado en la fuente]
- …
(Recorre TODOS los atributos de la checklist de su categoría. Cada uno debe mostrar un valor o “No especificado en la fuente”.)

**Instalación / Recomendaciones**
[Texto | No especificado en la fuente]

**Accesorios incluidos / no incluidos**
- Incluidos: [lista | No especificado en la fuente]
- No incluidos (de referencia para instalación): [lista | No especificado en la fuente]

**Variantes / Presentaciones**
[Listas | No especificado en la fuente]

**Normas / Ensayos**
[Listas | No especificado en la fuente]

**Advertencias / Limitaciones**
[Texto | No especificado en la fuente]

**Campos adicionales detectados**
[Lista | No especificado en la fuente]

**Conflictos detectados (si aplica)**
[Atributo: Valor A vs Valor B (documentos distintos)]
(La fuente se agregará automáticamente en backend.)
"""

CLARIFICATION_TEMPLATE = r"""
PLANTILLA: PREGUNTA DE CLARIFICACIÓN
Puedo ayudarte con precisión. ¿A cuál de estas categorías te refieres?
- Cubiertas Termoacústicas
- Tejas de Policarbonato
- Tejas PVC
- Tejas de Polipropileno
- Láminas de Policarbonato Alveolar
- Láminas para Divisiones y Cielos Rasos / Difusores
- Perfiles
- Tanques
- Sistema Séptico EcoAjover
- Contenedores
- Señalización Vial
- Estibas
- Cintas Impermeabilizantes Autoadhesivas
(Elige una. Si buscas una referencia específica, dime su nombre exacto.)
"""

CATEGORY_LIST_TEMPLATE = r"""
PLANTILLA: LISTADO DE CATEGORÍA
Se encontraron [N] referencias en **[Categoría canónica]**:
1) [Referencia 1]
2) [Referencia 2]
...
[N) [Referencia N]
¿Quieres la ficha técnica de alguna? Dime cuál y la preparo.
"""

NOT_SOLD_TEMPLATE = r"""
PLANTILLA: NO COMERCIALIZADO
Gracias por tu consulta. Actualmente **no comercializamos** “[término solicitado]”.
Nuestro portafolio se enfoca en:
- Cubiertas Termoacústicas
- Tejas de Policarbonato
- Tejas PVC
- Tejas de Polipropileno
- Láminas de Policarbonato Alveolar
- Láminas para Divisiones y Cielos Rasos / Difusores
- Perfiles
- Tanques
- Sistema Séptico EcoAjover
- Contenedores
- Señalización Vial
- Estibas
- Cintas Impermeabilizantes Autoadhesivas
Si quieres, puedo sugerirte opciones relacionadas dentro de nuestro portafolio.
"""

# Respuesta corta por atributo cuando el usuario pide un dato puntual de un PRODUCTO
ATTRIBUTE_PRODUCT_TEMPLATE = r"""
PLANTILLA: RESPUESTA POR ATRIBUTO (PRODUCTO)
**Producto:** [Nombre canónico]
**Atributo consultado:** [Nombre del atributo normalizado]
[Respuesta concreta con unidades y condiciones, o “No especificado en la fuente”]
(Nota: Solo se muestran valores respaldados por los PDFs recuperados en esta consulta.)
"""

# Respuesta por atributo cuando la pregunta es a NIVEL FAMILIA (p.ej., alveolar por espesor)
ATTRIBUTE_FAMILY_TEMPLATE = r"""
PLANTILLA: RESPUESTA POR ATRIBUTO (FAMILIA)
**Familia:** [Familia canónica]
**Atributo consultado:** [Nombre del atributo normalizado]
[Si aplica: “Depende de la variante/espesor. Ver tabla.”]

Variante/Espesor | Valor
-----------------|------
[Var 1]          | [Valor | No especificado en la fuente]
[Var 2]          | [Valor | No especificado en la fuente]
[Var 3]          | [Valor | No especificado en la fuente]

(Nota: Solo se muestran valores respaldados por los PDFs recuperados en esta consulta.)
"""
