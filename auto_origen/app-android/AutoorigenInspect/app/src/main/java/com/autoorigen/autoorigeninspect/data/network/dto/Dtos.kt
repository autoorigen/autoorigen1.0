package com.autoorigen.autoorigeninspect.data.network.dto

import com.google.gson.annotations.SerializedName

// Los nombres de campo usan @SerializedName para mapear el snake_case que
// devuelve la API Flask (autoorigen/routes/api.py) a propiedades Kotlin
// idiomáticas en camelCase.

data class LoginRequest(
    val usuario: String,
    val password: String,
)

data class TecnicoDto(
    val id: Int,
    val nombre: String,
)

data class LoginResponse(
    val ok: Boolean,
    val token: String? = null,
    val tecnico: TecnicoDto? = null,
    val error: String? = null,
)

data class NuevaInspeccionRequest(
    val placa: String,
    @SerializedName("cliente_nombre") val clienteNombre: String,
    @SerializedName("cliente_telefono") val clienteTelefono: String,
    val marca: String? = null,
    val modelo: String? = null,
    val combustible: String? = null,
    val kilometraje: String? = null,
    @SerializedName("kilometraje_aceite") val kilometrajeAceite: String? = null,
)

data class CrearInspeccionResponse(
    val ok: Boolean,
    @SerializedName("orden_id") val ordenId: Int? = null,
    @SerializedName("vehiculo_id") val vehiculoId: Int? = null,
    val error: String? = null,
)

data class InspeccionResumenDto(
    val id: Int,
    val titulo: String,
    @SerializedName("estado_actual") val estadoActual: String,
    @SerializedName("vehiculo_placa") val vehiculoPlaca: String,
    val marca: String? = null,
    val modelo: String? = null,
    @SerializedName("cliente_nombre") val clienteNombre: String,
    @SerializedName("tecnico_nombre") val tecnicoNombre: String? = null,
    @SerializedName("creado_en") val creadoEn: String,
)

data class ListarInspeccionesResponse(
    val ok: Boolean,
    val inspecciones: List<InspeccionResumenDto>? = null,
    val error: String? = null,
)

data class EventoDto(
    val id: Int,
    val tipo: String,
    val titulo: String,
    val descripcion: String? = null,
    @SerializedName("medio_path") val medioPath: String? = null,
    @SerializedName("creado_por") val creadoPor: String,
    @SerializedName("creado_en") val creadoEn: String,
)

data class InspeccionDetalleDto(
    val id: Int,
    val titulo: String,
    @SerializedName("estado_actual") val estadoActual: String,
    val kilometraje: String? = null,
    @SerializedName("kilometraje_aceite") val kilometrajeAceite: String? = null,
    @SerializedName("vehiculo_placa") val vehiculoPlaca: String,
    val marca: String? = null,
    val modelo: String? = null,
    val anio: String? = null,
    val color: String? = null,
    val combustible: String? = null,
    @SerializedName("cliente_nombre") val clienteNombre: String,
    @SerializedName("cliente_telefono") val clienteTelefono: String,
    @SerializedName("tecnico_nombre") val tecnicoNombre: String? = null,
    @SerializedName("creado_en") val creadoEn: String,
    val eventos: List<EventoDto> = emptyList(),
)

data class DetalleInspeccionResponse(
    val ok: Boolean,
    val inspeccion: InspeccionDetalleDto? = null,
    val error: String? = null,
)

data class EventoRequest(
    val tipo: String,
    val descripcion: String,
)

data class EventoResponse(
    val ok: Boolean,
    @SerializedName("evento_id") val eventoId: Int? = null,
    val error: String? = null,
)

data class MedioResponse(
    val ok: Boolean,
    @SerializedName("evento_id") val eventoId: Int? = null,
    @SerializedName("medio_path") val medioPath: String? = null,
    val error: String? = null,
)
