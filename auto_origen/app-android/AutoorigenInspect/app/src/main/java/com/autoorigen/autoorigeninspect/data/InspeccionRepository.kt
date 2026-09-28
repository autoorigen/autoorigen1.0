package com.autoorigen.autoorigeninspect.data

import com.autoorigen.autoorigeninspect.data.network.ApiClient
import com.autoorigen.autoorigeninspect.data.network.dto.CrearInspeccionResponse
import com.autoorigen.autoorigeninspect.data.network.dto.DetalleInspeccionResponse
import com.autoorigen.autoorigeninspect.data.network.dto.EventoRequest
import com.autoorigen.autoorigeninspect.data.network.dto.EventoResponse
import com.autoorigen.autoorigeninspect.data.network.dto.ListarInspeccionesResponse
import com.autoorigen.autoorigeninspect.data.network.dto.LoginRequest
import com.autoorigen.autoorigeninspect.data.network.dto.LoginResponse
import com.autoorigen.autoorigeninspect.data.network.dto.MedioResponse
import com.autoorigen.autoorigeninspect.data.network.dto.NuevaInspeccionRequest
import com.google.gson.Gson
import java.io.File
import java.io.IOException
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import retrofit2.HttpException

/**
 * Capa única entre la UI y Retrofit. Cada función arma el ApiService con la
 * URL/token guardados en SessionManager y devuelve un ApiResultado listo
 * para que la pantalla lo muestre, sin excepciones sueltas.
 */
class InspeccionRepository(private val sesion: SessionManager) {

    private suspend fun <T> llamar(bloque: suspend (servicio: com.autoorigen.autoorigeninspect.data.network.ApiService) -> T): ApiResultado<T> {
        val servicio = ApiClient.obtenerServicio(sesion.servidorUrlActual(), sesion.tokenActual())
        return try {
            ApiResultado.Exito(bloque(servicio))
        } catch (e: HttpException) {
            ApiResultado.Error(extraerError(e) ?: "Error del servidor (${e.code()}).")
        } catch (e: IOException) {
            ApiResultado.Error("No se pudo conectar con el servidor. Revisa la URL y la red.")
        }
    }

    private fun extraerError(e: HttpException): String? = try {
        val cuerpo = e.response()?.errorBody()?.string()
        if (cuerpo.isNullOrBlank()) null
        else Gson().fromJson(cuerpo, Map::class.java)?.get("error") as? String
    } catch (ex: Exception) {
        null
    }

    suspend fun login(usuario: String, password: String): ApiResultado<LoginResponse> =
        llamar { it.login(LoginRequest(usuario, password)) }

    suspend fun crearInspeccion(datos: NuevaInspeccionRequest): ApiResultado<CrearInspeccionResponse> =
        llamar { it.crearInspeccion(datos) }

    suspend fun listarInspecciones(): ApiResultado<ListarInspeccionesResponse> =
        llamar { it.listarInspecciones() }

    suspend fun detalleInspeccion(ordenId: Int): ApiResultado<DetalleInspeccionResponse> =
        llamar { it.detalleInspeccion(ordenId) }

    suspend fun agregarEvento(ordenId: Int, tipo: String, descripcion: String): ApiResultado<EventoResponse> =
        llamar { it.agregarEvento(ordenId, EventoRequest(tipo, descripcion)) }

    suspend fun subirMedio(
        ordenId: Int, archivo: File, titulo: String, esVideo: Boolean, esVideoIngreso: Boolean = false,
    ): ApiResultado<MedioResponse> {
        val tipoMedia = if (esVideo) "video/mp4".toMediaTypeOrNull() else "image/jpeg".toMediaTypeOrNull()
        val cuerpoArchivo = archivo.asRequestBody(tipoMedia)
        val parte = MultipartBody.Part.createFormData("archivo", archivo.name, cuerpoArchivo)
        val cuerpoTitulo = titulo.toRequestBody("text/plain".toMediaTypeOrNull())
        val cuerpoIngreso = (if (esVideoIngreso) "1" else "0").toRequestBody("text/plain".toMediaTypeOrNull())
        return llamar { it.subirMedio(ordenId, parte, cuerpoTitulo, cuerpoIngreso) }
    }
}
