package com.autoorigen.autoorigeninspect.ui.historial

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.autoorigen.autoorigeninspect.data.ApiResultado
import com.autoorigen.autoorigeninspect.data.InspeccionRepository
import com.autoorigen.autoorigeninspect.data.network.dto.InspeccionResumenDto
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class HistorialUiState(
    val cargando: Boolean = true,
    val inspecciones: List<InspeccionResumenDto> = emptyList(),
    val error: String? = null,
)

class HistorialViewModel(private val repositorio: InspeccionRepository) : ViewModel() {
    private val _estado = MutableStateFlow(HistorialUiState())
    val estado: StateFlow<HistorialUiState> = _estado.asStateFlow()

    init {
        cargar()
    }

    fun cargar() {
        viewModelScope.launch {
            _estado.value = _estado.value.copy(cargando = true, error = null)
            when (val resultado = repositorio.listarInspecciones()) {
                is ApiResultado.Exito -> {
                    val respuesta = resultado.datos
                    _estado.value = if (respuesta.ok) {
                        HistorialUiState(cargando = false, inspecciones = respuesta.inspecciones ?: emptyList())
                    } else {
                        HistorialUiState(cargando = false, error = respuesta.error ?: "No se pudo cargar el historial.")
                    }
                }
                is ApiResultado.Error -> {
                    _estado.value = HistorialUiState(cargando = false, error = resultado.mensaje)
                }
            }
        }
    }
}
