package com.autoorigen.autoorigeninspect.ui.detalle

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.autoorigen.autoorigeninspect.data.ApiResultado
import com.autoorigen.autoorigeninspect.data.InspeccionRepository
import com.autoorigen.autoorigeninspect.data.SessionManager
import com.autoorigen.autoorigeninspect.data.network.dto.InspeccionDetalleDto
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class DetalleUiState(
    val cargando: Boolean = true,
    val inspeccion: InspeccionDetalleDto? = null,
    val servidorUrl: String = "",
    val token: String? = null,
    val error: String? = null,
)

class DetalleInspeccionViewModel(
    private val repositorio: InspeccionRepository,
    private val sesion: SessionManager,
    private val ordenId: Int,
) : ViewModel() {

    private val _estado = MutableStateFlow(DetalleUiState())
    val estado: StateFlow<DetalleUiState> = _estado.asStateFlow()

    init {
        viewModelScope.launch {
            _estado.value = _estado.value.copy(
                servidorUrl = sesion.servidorUrlActual(),
                token = sesion.tokenActual(),
            )

            when (val resultado = repositorio.detalleInspeccion(ordenId)) {
                is ApiResultado.Exito -> {
                    val respuesta = resultado.datos
                    _estado.value = if (respuesta.ok && respuesta.inspeccion != null) {
                        _estado.value.copy(cargando = false, inspeccion = respuesta.inspeccion)
                    } else {
                        _estado.value.copy(cargando = false, error = respuesta.error ?: "No se pudo cargar la inspección.")
                    }
                }
                is ApiResultado.Error -> {
                    _estado.value = _estado.value.copy(cargando = false, error = resultado.mensaje)
                }
            }
        }
    }
}
