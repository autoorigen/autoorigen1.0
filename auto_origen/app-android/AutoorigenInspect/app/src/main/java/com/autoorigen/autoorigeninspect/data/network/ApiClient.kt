package com.autoorigen.autoorigeninspect.data.network

import java.util.concurrent.TimeUnit
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

/**
 * Construye (y reutiliza) el ApiService para la URL/token actuales. Como la
 * URL del servidor y el token pueden cambiar en tiempo real (el mecánico los
 * configura desde la app, no van fijos en el build), se reconstruye solo
 * cuando alguno de los dos cambia respecto a la última vez.
 */
object ApiClient {
    @Volatile private var retrofit: Retrofit? = null
    @Volatile private var baseUrlActual: String? = null
    @Volatile private var tokenActual: String? = null

    fun obtenerServicio(baseUrl: String, token: String?): ApiService {
        val urlNormalizada = if (baseUrl.endsWith("/")) baseUrl else "$baseUrl/"

        if (retrofit == null || baseUrlActual != urlNormalizada || tokenActual != token) {
            val logging = HttpLoggingInterceptor().apply { level = HttpLoggingInterceptor.Level.BASIC }
            val cliente = OkHttpClient.Builder()
                .addInterceptor(logging)
                .addInterceptor { cadena ->
                    val peticion = cadena.request().newBuilder().apply {
                        if (!token.isNullOrBlank()) addHeader("Authorization", "Bearer $token")
                    }.build()
                    cadena.proceed(peticion)
                }
                .connectTimeout(20, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .writeTimeout(60, TimeUnit.SECONDS) // subir video puede tardar un poco más
                .build()

            retrofit = Retrofit.Builder()
                .baseUrl(urlNormalizada)
                .client(cliente)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
            baseUrlActual = urlNormalizada
            tokenActual = token
        }

        return retrofit!!.create(ApiService::class.java)
    }
}
