"""
Checklists de atributos por categoría. Sirven de “lista de verificación” al responder fichas técnicas.
"""

CATALOG_KNOWLEDGE_BASE = r"""
CONOCIMIENTO DEL CATALOGO Y CHECKLIST DE ATRIBUTOS TÉCNICOS
(Usa esto como guía para estructurar fichas técnicas. Si un dato no aparece en la fuente actual, escribe “No especificado en la fuente”.)

- Cubiertas Termoacústicas:
  ancho, longitudes, colores, estructura de capas, traslapos (longitudinal/transversal),
  peso (lineal/m²), reducción de decibeles, accesorios, transitabilidad, distancia entre apoyos,
  voladizo máximo, fijaciones, filtro UV, resistencia del acero, garantía, almacenamiento.

- Tejas de Policarbonato:
  referencia/perfil, ancho, longitudes, colores, traslapos (longitudinal/transversal),
  peso (lineal/m²), transitabilidad, distancia entre apoyos, voladizo máximo, fijaciones,
  filtro UV/anti-amarillamiento, resistencia, garantía, ensayos/Normas (si aplica).

- Tejas PVC:
  perfil, ancho (útil y total), longitudes/rollos, colores, tornillería recomendada,
  traslapos, peso lineal, transitabilidad, apoyos, voladizo, filtro UV, garantía, ensayos/Normas.

- Tejas de Polipropileno:
  perfil, ancho, longitudes, colores, traslapos, apoyos, voladizo, tornillería, UV, garantía, usos/limitaciones.

- Láminas de Policarbonato Alveolar (incluye Grey Control):
  dimensiones (ancho/largo), espesores, colores/acabados, peso m², accesorios de instalación,
  distancia entre apoyos, voladizo máximo, fijaciones, filtro UV, garantía, radios mínimos de curvatura,
  sentido de curvatura, herramientas de corte, recomendaciones de instalación, sellado de alvéolos,
  propiedades térmicas/lumínicas (si aplica: SHGC/Transmisión).

- Láminas para Divisiones y Cielos Rasos / Difusores:
  material (PS), dimensiones, tolerancias, absorción de humedad, resistencia a deformación por calor,
  facilidad de limpieza, colores, diseños, recomendaciones de instalación, almacenamiento.

- Perfiles:
  material, acabado/color, dimensiones (longitud/perfil), compatibilidad con láminas/tejas,
  recomendaciones de instalación.

- Tanques:
  material (PE/PP), capacidades (L), dimensiones (Ø/alto/largo), compatibilidad química,
  accesorios incluidos (si aplica), recomendaciones de instalación (superficie/soporte/obra civil),
  apilamiento/transporte, colores, uso (superficial/subterráneo/transporte), garantía.

- Sistema Séptico EcoAjover:
  componentes/configuraciones (TS, TI, TG, TA, TAE), capacidades por componente (si aplica),
  dimensiones por componente (si aplica), accesorios incluidos por componente (si aplica),
  requisitos de instalación (obra civil / no obra civil, superficie/enterrado), restricciones de enterramiento,
  mantenimiento y limpieza, compatibilidad de conexiones (si la FT lo detalla), garantía.
  REGLAS:
    • Tratar como **sistema** de componentes; NO como un “tanque” estándar.
    • NO reutilizar valores de otras familias de tanques para inferir datos del sistema.
    • Cuando el dato no esté en FT/Portafolio/Manual del sistema, marcar “No especificado en la fuente”.

- Contenedores:
  material (PE/PP), capacidades (L) o volumen útil, dimensiones (largo/ancho/alto), tipo (estacionario / con ruedas),
  tapa y herrajes (incluidos/no incluidos), carga máxima o recomendada (si aplica), apilamiento/transporte,
  recomendaciones de limpieza/almacenamiento, colores, garantía, usos típicos (residuos, manipulación, etc.).

- Señalización Vial (Barrera):
  material (PE), dimensiones (largo/alto/ancho), capacidad de llenado (agua/arena, L o kg),
  peso vacío/lleno (si aplica), color/reflectivos, acople/ensamble, apilamiento/transporte,
  recomendaciones de uso y seguridad, garantía.

- Estibas:
  material (PE/PP), dimensiones, peso propio, capacidad de carga (estática/dinámica/rack si aplica),
  compatibilidad (montacargas, estantería), limpieza/almacenamiento, colores, garantía.

- Cintas Impermeabilizantes Autoadhesivas:
  superficies de aplicación, anchos disponibles, longitud del rollo, sustrato (foil aluminio / base),
  método de instalación (autoadhesivo en frío), rango térmico de servicio (si aplica),
  recomendaciones de solape/limpieza del sustrato, garantía.

REGLAS DE DOMINIO
- Listados de categorías = SIEMPRE desde la TAXONOMÍA (no usar RAG para listas).
- Fichas técnicas = SIEMPRE desde PDFs recuperados; si no hay FT, usar Portafolio y/o Manuales de instalación
  SOLO para atributos disponibles, y el resto marcarlos como “No especificado en la fuente”.

REGLAS DE CONSOLIDACIÓN Y ALCANCE DE FUENTES
- Prioridad de fuentes: Ficha Técnica del producto/sistema > Manual de su familia > Portafolio general.
- Alcance:
  • Si el objetivo es un PRODUCTO, solo consolidar desde la FT de ese producto, más Manual de su familia y Portafolio.
  • Si el objetivo es un **SISTEMA** (p. ej., Sistema Séptico EcoAjover), solo consolidar desde FT/Manual del sistema y Portafolio del sistema.
  • Si el objetivo es una FAMILIA, solo consolidar desde FTs/Manual de esa familia (incluyendo variantes oficiales), y Portafolio.
- Prohibido cruzar familias: nunca mezcles valores de PDFs de otra familia/sistema para completar huecos.
"""

# SINÓNIMOS / PATRONES PARA EXPANDIR CONSULTAS DE ATRIBUTOS (USO EN pdf_search_tool)
ATTRIBUTE_SEARCH_SYNONYMS = r"""
SINÓNIMOS / PATRONES PARA EXPANDIR CONSULTAS DE ATRIBUTOS (USO EN pdf_search_tool)

- Peso por m²: "peso por metro cuadrado", "peso m²", "peso m2", "kg/m²", "kg/m2", "masa areal", "gramaje"
- Peso lineal: "peso lineal", "kg/m", "peso por metro"
- Garantía: "garantía", "años de garantía", "warranty"
- Ancho útil: "ancho útil", "ancho efectivo", "cobertura útil"
- Traslapo longitudinal: "traslapo longitudinal", "solape longitudinal", "traslape longitudinal"
- Traslapo transversal: "traslapo transversal", "solape transversal", "traslape transversal"
- Distancia entre apoyos: "distancia entre apoyos", "luz entre apoyos", "separación de correas"
- Voladizo: "voladizo", "saliente", "vuelo"
- Fijaciones: "fijaciones", "tornillería", "tornillos autoperforantes", "arandelas", "espigo"
- Filtro UV: "filtro UV", "protección UV", "capa coextruida", "anti-amarillamiento"
- Transitabilidad: "transitabilidad", "caminar sobre", "se puede transitar"
- Radios de curvatura (alveolar): "radio mínimo", "mínimo de curvatura", "curvatura permitida"
- Propiedades térmicas (Grey Control): "SHGC", "coeficiente de ganancia solar", "transmisión térmica", "transmisión luminosa"
"""
