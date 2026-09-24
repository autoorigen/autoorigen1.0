package com.autoorigen.autoorigeninspect.ui.historial

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.ListItem
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.autoorigen.autoorigeninspect.AutoorigenApp
import com.autoorigen.autoorigeninspect.ui.SimpleViewModelFactory

@Composable
fun HistorialScreen(alVolver: () -> Unit, alTocarInspeccion: (ordenId: Int) -> Unit) {
    val app = LocalContext.current.applicationContext as AutoorigenApp
    val viewModel: HistorialViewModel = viewModel(
        factory = SimpleViewModelFactory { HistorialViewModel(app.repository) },
    )
    val estado by viewModel.estado.collectAsState()

    Column(modifier = Modifier.fillMaxSize()) {
        TopAppBar(
            title = { Text("Inspecciones anteriores") },
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
            estado.inspecciones.isEmpty() -> Box(modifier = Modifier.fillMaxSize().padding(20.dp), contentAlignment = Alignment.Center) {
                Text("Todavía no hay inspecciones registradas.")
            }
            else -> LazyColumn {
                items(estado.inspecciones, key = { it.id }) { inspeccion ->
                    ListItem(
                        headlineContent = { Text("${inspeccion.vehiculoPlaca} — ${inspeccion.marca ?: ""} ${inspeccion.modelo ?: ""}".trim()) },
                        supportingContent = {
                            Text(
                                "${inspeccion.clienteNombre} · Etapa: ${inspeccion.estadoActual}" +
                                    (inspeccion.tecnicoNombre?.let { " · $it" } ?: ""),
                            )
                        },
                        modifier = Modifier.clickable { alTocarInspeccion(inspeccion.id) },
                    )
                    HorizontalDivider()
                }
            }
        }
    }
}
