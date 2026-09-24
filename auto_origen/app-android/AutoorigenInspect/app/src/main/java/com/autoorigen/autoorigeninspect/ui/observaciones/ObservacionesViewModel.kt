package com.autoorigen.autoorigeninspect.ui.observaciones

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.autoorigen.autoorigeninspect.data.ApiResultado
import com.autoorigen.autoorigeninspect.data.InspeccionRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class ObservacionesUiState(
    val observacionMecanico: String = "",
    val comentarioCliente: String = "",
    val guardando: Boolean = false,
    val error: String? = null,
)

class ObservacionesViewModel(
    private val repositorio: InspeccionRepository,
    private val ordenId: Int,
) : ViewModel() {

    private val _estado = MutableStateFlow(ObservacionesUiState())
    val estado: StateFlow<ObservacionesUiState> = _estado.asStateFlow()

    fun onObservacionMecanicoCambia(v: String) { _estado.value = _estado.value.copy(observacionMecanico = v) }
    fun onComentarioClienteCambia(v: String) { _estado.value = _estado.value.copy(comentarioCliente = v) }

    fun finalizar(alTerminar: () -> Unit) {
        val actual = _estado.value
        if (actual.observacionMecanico.isBlank() && actual.comentarioCliente.isBlank()) {
            alTerminar()
            return
        }

        viewModelScope.launch {
            _estado.value = actual.copy(guardando = true, error = null)

            if (actual.observacionMecanico.isNotBlank()) {
                val resultado = repositorio.agregarEvento(ordenId, "observacion_mecanico", actual.observacionMecanico.trim())
                if (resultado is ApiResultado.Error) {
                    _estado.value = _estado.value.copy(guardando = false, error = resultado.mensaje)
                    return@launch
                }
            }
            if (actual.comentarioCliente.isNotBlank()) {
                val resultado = repositorio.agregarEvento(ordenId, "comentario_cliente", actual.comentarioCliente.trim())
                if (resultado is ApiResultado.Error) {
                    _estado.value = _estado.value.copy(guardando = false, error = resultado.mensaje)
                    return@launch
                }
            }

            _estado.value = _estado.value.copy(guardando = false)
            alTerminar()
        }
    }
}
