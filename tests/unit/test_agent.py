import pytest
from unittest.mock import AsyncMock, MagicMock
from langchain_core.messages import AIMessage, HumanMessage
from backend.src.orchestrator.settings.agent_settings import AjoverAgent

@pytest.mark.asyncio
async def test_agent_calls_tool_correctly_on_technical_query(mocker):
    """
    Prueba de integración para verificar que el agente invoca la herramienta
    cuando el LLM lo solicita.
    """
    # 1. ARRANGE (Preparar)
    
    # Mockear el LLM (esto ya estaba correcto)
    mock_model = MagicMock()
    llm_tool_call_response = AIMessage(
        content="",
        tool_calls=[{"name": "tool_pdf_search", "args": {"query": "datos de la teja"}, "id": "call_abc123"}]
    )
    final_response = AIMessage(content="La teja tiene estas especificaciones...")
    mock_model.ainvoke = AsyncMock(side_effect=[llm_tool_call_response, final_response])
    mock_model.bind_tools.return_value = mock_model

    # --- LA SECCIÓN CORREGIDA Y SIMPLIFICADA ---
    # En lugar de mockear con patch, creamos un mock perfecto de la herramienta.
    # Un "Tool" de LangChain es un objeto que tiene un `.name` y un método asíncrono `.ainvoke`.
    mock_tool = MagicMock()
    mock_tool.name = "tool_pdf_search"  # El nombre DEBE coincidir con lo que el LLM mockeado devuelve
    mock_tool.ainvoke = AsyncMock(return_value="Resultado de búsqueda mockeado.")
    # --- FIN DE LA SECCIÓN CORREGIDA ---

    # Crear una instancia del agente, pero pasándole nuestra herramienta mockeada
    agent_under_test = AjoverAgent(
        model=mock_model,
        tools=[mock_tool],  # <-- Le pasamos el objeto mock, no la herramienta real
        system_prompt="Test prompt"
    )

    # 2. ACT (Actuar)
    initial_state = {
        "messages": [HumanMessage(content="¿cuáles son los datos de la teja?")]
    }
    await agent_under_test.graph.ainvoke(initial_state)

    # 3. ASSERT (Verificar)
    
    # La verificación clave: ¿Se llamó al método 'ainvoke' de nuestra herramienta mockeada?
    mock_tool.ainvoke.assert_awaited_once_with({"query": "datos de la teja"})
    
    # Verificar que el método '.ainvoke' del LLM fue invocado dos veces
    assert mock_model.ainvoke.call_count == 2
