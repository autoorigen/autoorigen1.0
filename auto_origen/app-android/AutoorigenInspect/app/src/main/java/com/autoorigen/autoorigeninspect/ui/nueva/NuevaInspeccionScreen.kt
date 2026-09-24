package com.autoorigen.autoorigeninspect.ui.nueva

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.autoorigen.autoorigeninspect.AutoorigenApp
import com.autoorigen.autoorigeninspect.ui.SimpleViewModelFactory
import com.autoorigen.autoorigeninspect.ui.components.BotonPrincipal
import com.autoorigen.autoorigeninspect.ui.components.BotonSecundario
import com.autoorigen.autoorigeninspect.ui.components.CampoTexto

private val OPCIONES_COMBUSTIBLE = listOf("gasolina" to "Gasolina", "hibrido" to "Híbrido", "electrico" to "Eléctrico")

@Composable
fun NuevaInspeccionScreen(alCrear: (ordenId: Int, placa: String) -> Unit, alCancelar: () -> Unit) {
    val app = LocalContext.current.applicationContext as AutoorigenApp
    val viewModel: NuevaInspeccionViewModel = viewModel(
        factory = SimpleViewModelFactory { NuevaInspeccionViewModel(app.repository) },
    )
    val estado by viewModel.estado.collectAsState()

    Column(modifier = Modifier.fillMaxSize()) {
        TopAppBar(title = { Text("Nueva inspección — registro del carro") })

        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            Text(
                "La placa es el identificador principal del vehículo.",
                style = MaterialTheme.typography.bodyMedium,
            )

            CampoTexto(estado.placa, "Placa", viewModel::onPlacaCambia)
            CampoTexto(estado.clienteNombre, "Nombre del cliente", viewModel::onClienteNombreCambia)
            CampoTexto(
                estado.clienteTelefono, "Teléfono del cliente", viewModel::onClienteTelefonoCambia,
                teclado = KeyboardType.Phone,
            )
            CampoTexto(estado.marca, "Marca (ej. Toyota)", viewModel::onMarcaCambia)
            CampoTexto(estado.modelo, "Modelo (ej. Corolla)", viewModel::onModeloCambia)

            Text("Combustible", style = MaterialTheme.typography.bodyMedium)
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OPCIONES_COMBUSTIBLE.forEach { (valor, etiqueta) ->
                    FilterChip(
                        selected = estado.combustible == valor,
                        onClick = { viewModel.onCombustibleCambia(valor) },
                        label = { Text(etiqueta) },
                    )
                }
            }

            CampoTexto(
                estado.kilometraje, "Kilometraje del vehículo", viewModel::onKilometrajeCambia,
                teclado = KeyboardType.Number,
            )
            CampoTexto(
                estado.kilometrajeAceite, "Kilometraje del aceite", viewModel::onKilometrajeAceiteCambia,
                teclado = KeyboardType.Number,
            )

            estado.error?.let {
                Text(it, color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.bodyMedium)
            }

            BotonPrincipal(
                texto = "Continuar a fotos y video",
                onClick = { viewModel.crearRegistro(alCrear) },
                cargando = estado.guardando,
            )
            BotonSecundario(texto = "Cancelar", onClick = alCancelar, habilitado = !estado.guardando)
        }
    }
}
