package com.autoorigen.autoorigeninspect.data.network

import com.autoorigen.autoorigeninspect.data.network.dto.CrearInspeccionResponse
import com.autoorigen.autoorigeninspect.data.network.dto.DetalleInspeccionResponse
import com.autoorigen.autoorigeninspect.data.network.dto.EventoRequest
import com.autoorigen.autoorigeninspect.data.network.dto.EventoResponse
import com.autoorigen.autoorigeninspect.data.network.dto.ListarInspeccionesResponse
import com.autoorigen.autoorigeninspect.data.network.dto.LoginRequest
import com.autoorigen.autoorigeninspect.data.network.dto.LoginResponse
import com.autoorigen.autoorigeninspect.data.network.dto.MedioResponse
import com.autoorigen.autoorigeninspect.data.network.dto.NuevaInspeccionRequest
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.http.Path

/** Espejo de autoorigen/routes/api.py (sección "Login de mecánico + endpoints
 * de la app Android"). Ver también app-android/AutoorigenInspect/README.md. */
interface ApiService {

    @POST("api/tecnicos/login")
    suspend fun login(@Body body: LoginRequest): LoginResponse

    @POST("api/inspecciones")
    suspend fun crearInspeccion(@Body body: NuevaInspeccionRequest): CrearInspeccionResponse

    @GET("api/inspecciones")
    suspend fun listarInspecciones(): ListarInspeccionesResponse

    @GET("api/inspecciones/{ordenId}")
    suspend fun detalleInspeccion(@Path("ordenId") ordenId: Int): DetalleInspeccionResponse

    @POST("api/inspecciones/{ordenId}/eventos")
    suspend fun agregarEvento(@Path("ordenId") ordenId: Int, @Body body: EventoRequest): EventoResponse

    @Multipart
    @POST("api/inspecciones/{ordenId}/medios")
    suspend fun subirMedio(
        @Path("ordenId") ordenId: Int,
        @Part archivo: MultipartBody.Part,
        @Part("titulo") titulo: RequestBody,
    ): MedioResponse
}
