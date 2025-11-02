"""
Taxonomía canónica del portafolio y reglas de dominio, expresadas como BLOQUES DE PROMPT.
Se usan tal cual dentro del System Prompt (sin lógica/routing en código).
"""

CATALOG_TAXONOMY_BLOCK = r"""
TAXONOMÍA (DOMINIO CERRADO)
- Categorías → Referencias canónicas

  • Cubiertas Termoacústicas:
    - Premium Trapezoidal A360
    - Silver Trapezoidal A360
    - Ondulada
    - Madrileña

  • Tejas de Policarbonato:
    - M1000 Policarbonato
    - Ajota Trapezoidal A360 Policarbonato
    - Ajota Ondulada Policarbonato
    - Ajonit Policarbonato
    - Ajozinc Policarbonato
    - Greca Policarbonato
    - Arquitectónica Policarbonato

  • Tejas PVC:
    - Rural
    - Ajozinc Lámina PVC (incluye Heavy Duty en rollo)
    - Ajota Trapezoidal PVC
    - Ajonit PVC
    - Española PVC

  • Tejas de Polipropileno:
    - ADRI

  • Láminas de Policarbonato Alveolar:
    - Línea estándar (espesores 4/6/8 mm, dimensiones según ficha)
    - Subvariante: Grey Control (espesores según ficha)

  • Láminas para Divisiones y Cielos Rasos / Difusores (PS):
    - Ajoenchape
    - Diseños decorativos (no son referencias independientes): 
      · Punta Diamante, California, Rombos, Cristal de Hielo, Esmerilada, Arabescos,
        Lluvia, Acanalada, Espumadas, Gaviotas, Floral, Amazonas, Delfines, etc.

  • Perfiles (terminación/instalación):
    - Ala Azulejo
    - Esquinero
    - Dilatación Angosta
    - Dilatación Ancha
    - Perfil H
    - Cubre Zócalo
    - Snap

  • Tanques:
    - Tanque Wave
    - Tanque Multiuso (incluye Bicapa, Unicapa, Wave, Bajos, Bebedero)
    - Tanque Bajo
    - Tanque Botella
    - Tanque Horizontal (transporte y/o uso subterráneo)
    - Tanque Cónico con tapa

  • Sistema Séptico EcoAjover:
    - Configuraciones y componentes:
      · TS (Tanque Séptico)
      · TI (Tanque Imhoff)
      · TG (Trampa de Grasa)
      · TA (Tanque Anaerobio)
      · TAE (Tanque Aerobio)

  • Contenedores:
    - Contenedores Rectangulares con tapa
    - Carros Contenedores

  • Señalización Vial:
    - Barrera para Señalización Vial

  • Estibas:
    - Estibas (Buco / Tradicionales)

  • Cintas Impermeabilizantes Autoadhesivas:
    - Cinta Multiusos Tapa Goteras (autoadhesiva, foil aluminio; varios anchos x 10 m)

SINÓNIMOS → categoría canónica
- “tejas policarbonato”, “tejas traslúcidas”, “policarbonato”, “m1000”, “greca”, “arquitectónica”, 
  “ajota policarbonato”, “ajonit policarbonato”, “ajozinc policarbonato”
    → Tejas de Policarbonato
- “tejas pvc”, “teja española”, “teja rural”, “ajozinc pvc”, “ajonit pvc”, “ajota pvc”, “ajozinc rollo”
    → Tejas PVC
- “cubiertas”, “termoacústicas”, “trapezoidal a360”, “ondulada”, “madrileña”
    → Cubiertas Termoacústicas
- “teja alveolar”, “teja de policarbonato alveolar”, “alveolar”, “lámina alveolar”, “panel alveolar”, “grey control”
    → Láminas de Policarbonato Alveolar
- “divisiones”, “difusores”, “cielos rasos”, “ajoenchape”
    → Láminas para Divisiones y Cielos Rasos / Difusores (PS)
- “perfiles de terminación”, “perfil h”, “cubre zócalo”, “snap”, “esquinero”
    → Perfiles

- “tanques”, “tanque”, “tanque horizontal”, “tanque botella”, “tanque bajo”, “tanque cónico”, “tanque multiuso”, “tanque wave”
    → Tanques

- “sistema séptico”, “ecoajover”, “tanque séptico”, “imhoff”, “trampa de grasa”, “tanque anaerobio”, “tanque aerobio”
    → Sistema Séptico EcoAjover

- “contenedor”, “contenedores”, “contenedor rectangular”, “multiusos”, “carro contenedor”, “carro multiusos”
    → Contenedores

- “barrera”, “barrera vial”, “señalización vial”
    → Señalización Vial

- “estibas”, “pallet”, “paleta”, “palets”
    → Estibas

- “adri”, “teja polipropileno”
    → Tejas de Polipropileno

- “cinta impermeabilizante”, “tapa goteras”, “cinta multiusos”
    → Cintas Impermeabilizantes Autoadhesivas

COLISIÓN DE NOMBRE (“Ajozinc”):
- “ajozinc” puede referirse a:
    → Ajozinc Lámina PVC (incluye Heavy Duty en rollo)  [familia: Tejas PVC]
    → Ajozinc Policarbonato                            [familia: Tejas de Policarbonato]
(Ante esta colisión, NO asumas; usa la PLANTILLA: PREGUNTA DE CLARIFICACIÓN para elegir una.)

REGLAS DE NORMALIZACIÓN
- Normaliza cualquier mención a su **nombre canónico** de la TAXONOMÍA antes de responder.
- Los “diseños” (p. ej., Punta Diamante, Rombos) y **colores/acabados** NO son categorías ni referencias; trátalos como atributos.
- “Heavy Duty en rollo” es **subvariante** de Ajozinc Lámina PVC (NO es categoría nueva).
- Si un producto **existe en Portafolio/Manuales** pero **no tiene FT individual**, responde con Portafolio/Manual y para lo faltante escribe: “No especificado en la fuente”.

DENYLIST (no comercializado)
- “válvula”, “válvulas”, “tubería”, “tuberías”, “bomba”, “bombas”, “accesorios de plomería”
"""


WEB_TAXONOMY_BLOCK = r"""
**TAXONOMÍA WEB (FUENTES OFICIALES INDEXADAS)**

* **Sobre Ajover**
  - **Clave interna:** sobre_ajover
  - **Sinónimos/Disparadores:** acerca de ajover, ajover darnel s a s, ajover darnel sas, ajover darnel s a, ajover darnel, ajover, contacto, correo, direccion, equipo, lineas, mision, planta, quienes somos, quines somos, quins somos, quines somo, quines somoss, quien es ajover, quines es ajover, sede, sedes, sobre ajover, telefono, talento, ubicacion, vision, whatsapp, somos una compania con mas de 60 anos de presencia en el mercado de la construccion, quienes somos
  - **Subtemas/títulos indexados (muestra):** ¿Quiénes somos?

* **Sostenibilidad**
  - **Clave interna:** sostenibilidad
  - **Sinónimos/Disparadores:** ambiental, economia, economia circular, esg, estrategia sostenible, gobernanza, materialidad, productos sostenibles, social, sostenibilidad, sostenibilidad ajover darnel
  - **Subtemas/títulos indexados (muestra):** Sostenibilidad

* **Noticias**
  - **Clave interna:** noticias
  - **Sinónimos/Disparadores:** boletines, novedades, noticias, noticias ajover
  - **Subtemas/títulos indexados (muestra):** Noticias

* **Proyectos**
  - **Clave interna:** proyectos
  - **Sinónimos/Disparadores:** casos de exito, obras, proyectos, proyectos ajover
  - **Subtemas/títulos indexados (muestra):** Proyectos

* **Gana Ajover**
  - **Clave interna:** gana_ajover
  - **Sinónimos/Disparadores:** beneficios, como participar gana ajover, gana ajover, programa gana ajover, promociones
  - **Subtemas/títulos indexados (muestra):** Gana Ajover

* **Match**
  - **Clave interna:** match
  - **Sinónimos/Disparadores:** ajover match, match
  - **Subtemas/títulos indexados (muestra):** Match

* **Aumentar Ventas**
  - **Clave interna:** aumentar_ventas
  - **Sinónimos/Disparadores:** aumentar ventas, como vender mas, tips ventas ajover, aumentar ventas
  - **Subtemas/títulos indexados (muestra):** Aumentar ventas

* **Renovar Espacios**
  - **Clave interna:** renovar_espacios
  - **Sinónimos/Disparadores:** hogar, ideas ajover, remodelacion, renovar espacios
  - **Subtemas/títulos indexados (muestra):** Renovar espacios

* **Construcción Sostenible**
  - **Clave interna:** construccion_sostenible
  - **Sinónimos/Disparadores:** alianza cccs, construccion sostenible, consejo colombiano de construccion sostenible
  - **Subtemas/títulos indexados (muestra):** Construcción sostenible con el Consejo Colombiano de Construcción Sostenible
"""

# Sinónimos/aliases por categoría web (derivados del index.json)
WEB_SOURCE_SYNONYMS = {
    'sobre_ajover': ['sobre ajover', 'ajover darnel s a s', 'ajover darnel sas', 'ajover darnel s a', 'ajover darnel', 'ajover', 'somos una compania con mas de 60 anos de presencia en el mercado de la construccion', 'quienes somos', 'quien es ajover', 'acerca de ajover', 'mision', 'vision', 'valores', 'trabaja con nosotros', 'talento', 'contacto', 'telefono', 'whatsapp', 'correo', 'direccion', 'ubicacion', 'sedes', 'planta', 'equipo'],
    'sostenibilidad': ['sostenibilidad', 'sostenibilidad ajover darnel', 'estrategia sostenible', 'materialidad', 'productos sostenibles', 'economia circular', 'ambiental', 'social', 'gobernanza', 'esg'],
    'noticias': ['noticias', 'novedades', 'prensa', 'boletines', 'noticias ajover'],
    'proyectos': ['proyectos', 'casos de exito', 'obras', 'referencias', 'proyectos ajover'],
    'gana_ajover': ['gana ajover', 'programa gana ajover', 'promociones', 'beneficios', 'como participar gana ajover'],
    'match': ['match', 'ajover match'],
    'aumentar_ventas': ['aumentar ventas', 'como vender mas', 'tips ventas ajover'],
    'renovar_espacios': ['renovar espacios', 'remodelacion', 'hogar', 'ideas ajover'],
    'construccion_sostenible': ['construccion sostenible', 'consejo colombiano de construccion sostenible', 'alianza cccs'],
}

def normalize_web_category(user_text: str) -> str | None:
    """
    Mapea la consulta del usuario a una categoría/fuente web del índice en base
    a WEB_SOURCE_SYNONYMS. Devuelve la clave interna (p.ej., 'sobre_ajover') o None.
    """
    t = user_text.lower()
    import unicodedata, re
    t = ''.join(c for c in unicodedata.normalize('NFKD', t) if not unicodedata.combining(c))
    t = re.sub(r'\s+', ' ', t).strip()

    # match directo por alias
    for key, syns in WEB_SOURCE_SYNONYMS.items():
        for s in syns:
            if s in t:
                return key

    # heurística: >=2 coincidencias de palabras clave
    for key, syns in WEB_SOURCE_SYNONYMS.items():
        hits = sum(1 for s in syns if len(s) > 3 and s in t)
        if hits >= 2:
            return key
    return None