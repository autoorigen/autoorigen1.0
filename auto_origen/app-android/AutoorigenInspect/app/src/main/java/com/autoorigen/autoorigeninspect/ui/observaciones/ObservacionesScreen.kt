package com.autoorigen.autoorigeninspect.ui.observaciones

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.autoorigen.autoorigeninspect.AutoorigenApp
import com.autoorigen.autoorigeninspect.ui.SimpleViewModelFactory
import com.autoorigen.autoorigeninspect.ui.components.BotonPrincipal
import com.autoorigen.autoorigeninspect.ui.components.CampoTexto

@Composable
fun ObservacionesScreen(ordenId: Int, alFinalizar: () -> Unit) {
    val app = LocalContext.current.applicationContext as AutoorigenApp
    val viewModel: ObservacionesViewModel = viewModel(
        factory = SimpleViewModelFactory { ObservacionesViewModel(app.repository, ordenId) },
    )
    val estado by viewModel.estado.collectAsState()

    Column(modifier = Modifier.fillMaxSize()) {
        TopAppBar(title = { Text("Observaciones") })

        Column(
            modifier = Modifier.fillMaxSize().padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            Text(
                "Último paso antes de cerrar esta inspección.",
                style = MaterialTheme.typography.bodyMedium,
            )

            CampoTexto(
                valor = estado.observacionMecanico,
                etiqueta = "Observación del mecánico",
                onValorCambia = viewModel::onObservacionMecanicoCambia,
                soloUnaLinea = false,
                modifier = Modifier.padding(bottom = 4.dp),
            )
            CampoTexto(
                valor = estado.comentarioCliente,
                etiqueta = "Comentario del cliente",
                onValorCambia = viewModel::onComentarioClienteCambia,
                soloUnaLinea = false,
            )

            estado.error?.let {
                Text(it, color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.bodyMedium)
            }

            BotonPrincipal(
                texto = "Finalizar inspección",
                onClick = { viewModel.finalizar(alFinalizar) },
                cargando = estado.guardando,
            )
        }
    }
}
