package com.autoorigen.autoorigeninspect.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider

/** Fábrica genérica de un solo uso: evita repetir una clase Factory por cada
 * ViewModel cuando lo único que cambia son los parámetros del constructor. */
class SimpleViewModelFactory(private val crear: () -> ViewModel) : ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T = crear() as T
}
