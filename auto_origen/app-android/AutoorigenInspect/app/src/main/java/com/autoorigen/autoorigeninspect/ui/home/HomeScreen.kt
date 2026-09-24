package com.autoorigen.autoorigeninspect.ui.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Logout
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.autoorigen.autoorigeninspect.AutoorigenApp
import com.autoorigen.autoorigeninspect.ui.components.BotonPrincipal
import com.autoorigen.autoorigeninspect.ui.components.BotonSecundario
import kotlinx.coroutines.launch

@Composable
fun HomeScreen(
    alTocarNuevaInspeccion: () -> Unit,
    alTocarHistorial: () -> Unit,
    alCerrarSesion: () -> Unit,
) {
    val app = LocalContext.current.applicationContext as AutoorigenApp
    val nombreTecnico by app.sessionManager.tecnicoNombre.collectAsState(initial = null)
    val alcance = rememberCoroutineScope()

    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text("AUTOORIGEN", style = MaterialTheme.typography.titleLarge)
        Text(
            nombreTecnico?.let { "Hola, $it" } ?: "AutoorigenInspect",
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier.padding(top = 4.dp, bottom = 40.dp),
        )

        Column(modifier = Modifier.widthIn(max = 420.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
            BotonPrincipal(
                texto = "Nueva inspección",
                onClick = alTocarNuevaInspeccion,
            )
            BotonSecundario(
                texto = "Revisión de inspecciones anteriores",
                onClick = alTocarHistorial,
            )

            TextButton(onClick = { alcance.launch { app.sessionManager.cerrarSesion(); alCerrarSesion() } }) {
                Icon(Icons.Filled.Logout, contentDescription = null, modifier = Modifier.padding(end = 6.dp))
                Text("Cerrar sesión")
            }
        }
    }
}
