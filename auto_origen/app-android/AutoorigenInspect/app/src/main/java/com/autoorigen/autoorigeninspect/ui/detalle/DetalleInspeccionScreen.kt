package com.autoorigen.autoorigeninspect.ui.detalle

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Videocam
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import coil.compose.AsyncImage
import coil.request.ImageRequest
import com.autoorigen.autoorigeninspect.AutoorigenApp
import com.autoorigen.autoorigeninspect.data.network.dto.EventoDto
import com.autoorigen.autoorigeninspect.ui.SimpleViewModelFactory

private val ETIQUETAS_TIPO = mapOf(
    "nota" to "Nota", "cambio_estado" to "Cambio de etapa", "hallazgo" to "Hallazgo",
    "foto" to "Foto", "video" to "Video",
    "observacion_mecanico" to "Observación del mecánico", "comentario_cliente" to "Comentario del cliente",
)

@Composable
fun DetalleInspeccionScreen(ordenId: Int, alVolver: () -> Unit) {
    val app = LocalContext.current.applicationContext as AutoorigenApp
    val viewModel: DetalleInspeccionViewModel = viewModel(
        factory = SimpleViewModelFactory { DetalleInspeccionViewModel(app.repository, app.sessionManager, ordenId) },
    )
    val estado by viewModel.estado.collectAsState()

    Column(modifier = Modifier.fillMaxSize()) {
        TopAppBar(
            title = { Text(estado.inspeccion?.vehiculoPlaca ?: "Inspección") },
            navigationIcon = {
                IconButton(onClick = alVolver) {
                    Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Volver")
                }
            },
        )

        when {
            estado.cargando -> Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
            estado.error != null -> Box(modifier = Modifier.fillMaxSize().padding(20.dp), contentAlignment = Alignment.Center) {
                Text(estado.error ?: "", color = MaterialTheme.colorScheme.error)
            }
            estado.inspeccion != null -> {
                val inspeccion = estado.inspeccion!!
                LazyColumn(modifier = Modifier.fillMaxSize().padding(16.dp)) {
                    item {
                        Text(
                            "${inspeccion.marca ?: ""} ${inspeccion.modelo ?: ""}".trim(),
                            style = MaterialTheme.typography.titleMedium,
                        )
                        Text("Cliente: ${inspeccion.clienteNombre} · ${inspeccion.clienteTelefono}", style = MaterialTheme.typography.bodyMedium)
                        Text("Etapa: ${inspeccion.estadoActual}", style = MaterialTheme.typography.bodyMedium)
                        inspeccion.combustible?.let { Text("Combustible: $it", style = MaterialTheme.typography.bodyMedium) }
                        inspeccion.kilometraje?.let { Text("Kilometraje: $it", style = MaterialTheme.typography.bodyMedium) }
                        inspeccion.kilometrajeAceite?.let { Text("Kilometraje del aceite: $it", style = MaterialTheme.typography.bodyMedium) }
                        inspeccion.tecnicoNombre?.let { Text("Inspeccionado por: $it", style = MaterialTheme.typography.bodyMedium) }
                        Text(
                            "Línea de tiempo",
                            style = MaterialTheme.typography.titleMedium,
                            modifier = Modifier.padding(top = 20.dp, bottom = 8.dp),
                        )
                    }

                    items(inspeccion.eventos, key = { it.id }) { evento ->
                        EventoCard(evento = evento, servidorUrl = estado.servidorUrl, token = estado.token)
                    }
                }
            }
        }
    }
}

@Composable
private fun EventoCard(evento: EventoDto, servidorUrl: String, token: String?) {
    Card(modifier = Modifier.fillMaxWidth().padding(vertical = 6.dp)) {
        Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text(
                "${ETIQUETAS_TIPO[evento.tipo] ?: evento.tipo} · ${evento.creadoEn.take(16).replace("T", " ")}",
                style = MaterialTheme.typography.labelMedium,
            )
            Text(evento.titulo, style = MaterialTheme.typography.bodyLarge)
            evento.descripcion?.let { Text(it, style = MaterialTheme.typography.bodyMedium) }

            if (evento.medioPath != null) {
                val urlBase = if (servidorUrl.endsWith("/")) servidorUrl else "$servidorUrl/"
                val url = "${urlBase}api/inspecciones/medios/${evento.medioPath}"

                if (evento.tipo == "video") {
                    Row(modifier = Modifier.fillMaxWidth().padding(top = 6.dp)) {
                        Icon(Icons.Filled.Videocam, contentDescription = null)
                        Text(" Video disponible en el servidor", style = MaterialTheme.typography.bodyMedium)
                    }
                } else {
                    val solicitud = ImageRequest.Builder(LocalContext.current)
                        .data(url)
                        .apply { if (!token.isNullOrBlank()) addHeader("Authorization", "Bearer $token") }
                        .crossfade(true)
                        .build()
                    AsyncImage(
                        model = solicitud,
                        contentDescription = evento.titulo,
                        contentScale = ContentScale.Crop,
                        modifier = Modifier.fillMaxWidth().height(180.dp).padding(top = 6.dp),
                    )
                }
            }
        }
    }
}
