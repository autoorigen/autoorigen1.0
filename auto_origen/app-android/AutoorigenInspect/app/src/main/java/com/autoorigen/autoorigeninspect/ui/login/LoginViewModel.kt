package com.autoorigen.autoorigeninspect.ui.login

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.autoorigen.autoorigeninspect.data.ApiResultado
import com.autoorigen.autoorigeninspect.data.InspeccionRepository
import com.autoorigen.autoorigeninspect.data.SessionManager
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class LoginUiState(
    val servidorUrl: String = "",
    val usuario: String = "",
    val password: String = "",
    val cargando: Boolean = false,
    val error: String? = null,
)

class LoginViewModel(
    private val repositorio: InspeccionRepository,
    private val sesion: SessionManager,
) : ViewModel() {

    private val _estado = MutableStateFlow(LoginUiState())
    val estado: StateFlow<LoginUiState> = _estado.asStateFlow()

    init {
        viewModelScope.launch {
            _estado.value = _estado.value.copy(servidorUrl = sesion.servidorUrlActual())
        }
    }

    fun onServidorUrlCambia(valor: String) {
        _estado.value = _estado.value.copy(servidorUrl = valor, error = null)
    }

    fun onUsuarioCambia(valor: String) {
        _estado.value = _estado.value.copy(usuario = valor, error = null)
    }

    fun onPasswordCambia(valor: String) {
        _estado.value = _estado.value.copy(password = valor, error = null)
    }

    fun entrar(alExito: () -> Unit) {
        val actual = _estado.value
        if (actual.servidorUrl.isBlank() || actual.usuario.isBlank() || actual.password.isBlank()) {
            _estado.value = actual.copy(error = "Completa la URL del servidor, el usuario y la contraseña.")
            return
        }

        viewModelScope.launch {
            _estado.value = actual.copy(cargando = true, error = null)
            sesion.guardarServidor(actual.servidorUrl.trim())

            when (val resultado = repositorio.login(actual.usuario.trim(), actual.password)) {
                is ApiResultado.Exito -> {
                    val respuesta = resultado.datos
                    if (respuesta.ok && respuesta.token != null && respuesta.tecnico != null) {
                        sesion.guardarSesion(respuesta.token, respuesta.tecnico.nombre)
                        _estado.value = _estado.value.copy(cargando = false)
                        alExito()
                    } else {
                        _estado.value = _estado.value.copy(
                            cargando = false,
                            error = respuesta.error ?: "Usuario o contraseña incorrectos.",
                        )
                    }
                }
                is ApiResultado.Error -> {
                    _estado.value = _estado.value.copy(cargando = false, error = resultado.mensaje)
                }
            }
        }
    }
}
