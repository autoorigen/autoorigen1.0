package com.autoorigen.autoorigeninspect.ui.login

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.autoorigen.autoorigeninspect.AutoorigenApp
import com.autoorigen.autoorigeninspect.ui.SimpleViewModelFactory
import com.autoorigen.autoorigeninspect.ui.components.BotonPrincipal
import com.autoorigen.autoorigeninspect.ui.components.CampoTexto

@Composable
fun LoginScreen(alEntrar: () -> Unit) {
    val app = LocalContext.current.applicationContext as AutoorigenApp
    val viewModel: LoginViewModel = viewModel(
        factory = SimpleViewModelFactory { LoginViewModel(app.repository, app.sessionManager) },
    )
    val estado by viewModel.estado.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text("AUTOORIGEN", style = MaterialTheme.typography.titleLarge)
        Text(
            "AutoorigenInspect — acceso de mecánicos",
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier.padding(top = 4.dp, bottom = 32.dp),
        )

        Column(
            modifier = Modifier.widthIn(max = 420.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            CampoTexto(
                valor = estado.servidorUrl,
                etiqueta = "URL del servidor (ej. http://192.168.1.10:5000/)",
                onValorCambia = viewModel::onServidorUrlCambia,
                teclado = KeyboardType.Uri,
            )
            CampoTexto(
                valor = estado.usuario,
                etiqueta = "Usuario",
                onValorCambia = viewModel::onUsuarioCambia,
            )
            CampoTexto(
                valor = estado.password,
                etiqueta = "Contraseña",
                onValorCambia = viewModel::onPasswordCambia,
                esPassword = true,
            )

            estado.error?.let {
                Text(it, color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.bodyMedium)
            }

            BotonPrincipal(
                texto = "Entrar",
                onClick = { viewModel.entrar(alEntrar) },
                cargando = estado.cargando,
            )
        }
    }
}
