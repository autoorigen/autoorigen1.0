package com.autoorigen.autoorigeninspect.ui.captura

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.autoorigen.autoorigeninspect.data.ApiResultado
import com.autoorigen.autoorigeninspect.data.InspeccionRepository
import java.io.File
import java.util.UUID
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class ElementoCapturado(
    val id: String,
    val esVideo: Boolean,
    val titulo: String,
    val subiendo: Boolean = true,
    val subido: Boolean = false,
    val error: String? = null,
)

class CapturaViewModel(
    private val repositorio: InspeccionRepository,
    private val ordenId: Int,
) : ViewModel() {

    private val _elementos = MutableStateFlow<List<ElementoCapturado>>(emptyList())
    val elementos: StateFlow<List<ElementoCapturado>> = _elementos.asStateFlow()

    fun subirArchivo(archivo: File, esVideo: Boolean, titulo: String, esVideoIngreso: Boolean = false) {
        val id = UUID.randomUUID().toString()
        _elementos.value = _elementos.value + ElementoCapturado(id = id, esVideo = esVideo, titulo = titulo)

        viewModelScope.launch {
            when (val resultado = repositorio.subirMedio(ordenId, archivo, titulo, esVideo, esVideoIngreso)) {
                is ApiResultado.Exito -> {
                    val ok = resultado.datos.ok
                    actualizar(id) {
                        it.copy(subiendo = false, subido = ok, error = if (ok) null else resultado.datos.error)
                    }
                }
                is ApiResultado.Error -> actualizar(id) { it.copy(subiendo = false, error = resultado.mensaje) }
            }
        }
    }

    private fun actualizar(id: String, transformar: (ElementoCapturado) -> ElementoCapturado) {
        _elementos.value = _elementos.value.map { if (it.id == id) transformar(it) else it }
    }
}
