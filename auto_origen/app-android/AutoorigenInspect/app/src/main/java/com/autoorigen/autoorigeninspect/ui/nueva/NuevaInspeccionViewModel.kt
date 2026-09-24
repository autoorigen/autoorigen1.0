package com.autoorigen.autoorigeninspect.ui.nueva

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.autoorigen.autoorigeninspect.data.ApiResultado
import com.autoorigen.autoorigeninspect.data.InspeccionRepository
import com.autoorigen.autoorigeninspect.data.network.dto.NuevaInspeccionRequest
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class NuevaInspeccionUiState(
    val placa: String = "",
    val clienteNombre: String = "",
    val clienteTelefono: String = "",
    val marca: String = "",
    val modelo: String = "",
    val combustible: String? = null, // "gasolina" | "hibrido" | "electrico"
    val kilometraje: String = "",
    val kilometrajeAceite: String = "",
    val guardando: Boolean = false,
    val error: String? = null,
)

class NuevaInspeccionViewModel(private val repositorio: InspeccionRepository) : ViewModel() {
    private val _estado = MutableStateFlow(NuevaInspeccionUiState())
    val estado: StateFlow<NuevaInspeccionUiState> = _estado.asStateFlow()

    fun onPlacaCambia(v: String) { _estado.value = _estado.value.copy(placa = v.uppercase(), error = null) }
    fun onClienteNombreCambia(v: String) { _estado.value = _estado.value.copy(clienteNombre = v, error = null) }
    fun onClienteTelefonoCambia(v: String) { _estado.value = _estado.value.copy(clienteTelefono = v, error = null) }
    fun onMarcaCambia(v: String) { _estado.value = _estado.value.copy(marca = v) }
    fun onModeloCambia(v: String) { _estado.value = _estado.value.copy(modelo = v) }
    fun onCombustibleCambia(v: String) { _estado.value = _estado.value.copy(combustible = v) }
    fun onKilometrajeCambia(v: String) { _estado.value = _estado.value.copy(kilometraje = v) }
    fun onKilometrajeAceiteCambia(v: String) { _estado.value = _estado.value.copy(kilometrajeAceite = v) }

    fun crearRegistro(alCrear: (ordenId: Int, placa: String) -> Unit) {
        val actual = _estado.value
        if (actual.placa.isBlank() || actual.clienteNombre.isBlank() || actual.clienteTelefono.isBlank()) {
            _estado.value = actual.copy(error = "Placa, nombre del cliente y teléfono son obligatorios.")
            return
        }

        viewModelScope.launch {
            _estado.value = actual.copy(guardando = true, error = null)
            val resultado = repositorio.crearInspeccion(
                NuevaInspeccionRequest(
                    placa = actual.placa.trim(),
                    clienteNombre = actual.clienteNombre.trim(),
                    clienteTelefono = actual.clienteTelefono.trim(),
                    marca = actual.marca.trim().ifBlank { null },
                    modelo = actual.modelo.trim().ifBlank { null },
                    combustible = actual.combustible,
                    kilometraje = actual.kilometraje.trim().ifBlank { null },
                    kilometrajeAceite = actual.kilometrajeAceite.trim().ifBlank { null },
                ),
            )
            when (resultado) {
                is ApiResultado.Exito -> {
                    val respuesta = resultado.datos
                    if (respuesta.ok && respuesta.ordenId != null) {
                        _estado.value = _estado.value.copy(guardando = false)
                        alCrear(respuesta.ordenId, actual.placa.trim())
                    } else {
                        _estado.value = _estado.value.copy(
                            guardando = false,
                            error = respuesta.error ?: "No se pudo crear el registro.",
                        )
                    }
                }
                is ApiResultado.Error -> {
                    _estado.value = _estado.value.copy(guardando = false, error = resultado.mensaje)
                }
            }
        }
    }
}
