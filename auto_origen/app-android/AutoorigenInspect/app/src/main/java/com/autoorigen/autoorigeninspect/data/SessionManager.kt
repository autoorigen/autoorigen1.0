package com.autoorigen.autoorigeninspect.data

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map

private val Context.dataStore by preferencesDataStore(name = "autoorigen_sesion")

// 10.0.2.2 es la IP con la que el EMULADOR de Android ve el "localhost" de
// la máquina donde corre. En un teléfono físico hay que cambiarla por la IP
// de la red local del taller (la misma que ya usa probar.sh).
private const val URL_POR_DEFECTO = "http://10.0.2.2:5000/"

class SessionManager(private val context: Context) {
    private object Claves {
        val SERVIDOR = stringPreferencesKey("servidor_url")
        val TOKEN = stringPreferencesKey("token")
        val TECNICO_NOMBRE = stringPreferencesKey("tecnico_nombre")
    }

    val servidorUrl: Flow<String> =
        context.dataStore.data.map { it[Claves.SERVIDOR] ?: URL_POR_DEFECTO }

    val token: Flow<String?> =
        context.dataStore.data.map { it[Claves.TOKEN] }

    val tecnicoNombre: Flow<String?> =
        context.dataStore.data.map { it[Claves.TECNICO_NOMBRE] }

    suspend fun servidorUrlActual(): String = servidorUrl.first()
    suspend fun tokenActual(): String? = token.first()

    suspend fun guardarServidor(url: String) {
        context.dataStore.edit { it[Claves.SERVIDOR] = url }
    }

    suspend fun guardarSesion(token: String, nombreTecnico: String) {
        context.dataStore.edit {
            it[Claves.TOKEN] = token
            it[Claves.TECNICO_NOMBRE] = nombreTecnico
        }
    }

    suspend fun cerrarSesion() {
        context.dataStore.edit {
            it.remove(Claves.TOKEN)
            it.remove(Claves.TECNICO_NOMBRE)
        }
    }
}
