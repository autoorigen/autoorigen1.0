package com.autoorigen.autoorigeninspect.data

/** Resultado uniforme de una llamada a la API: éxito con datos, o un
 * mensaje de error ya listo para mostrar en pantalla (de red o del
 * backend). Evita que cada pantalla tenga que lidiar con excepciones. */
sealed class ApiResultado<out T> {
    data class Exito<T>(val datos: T) : ApiResultado<T>()
    data class Error(val mensaje: String) : ApiResultado<Nothing>()
}
