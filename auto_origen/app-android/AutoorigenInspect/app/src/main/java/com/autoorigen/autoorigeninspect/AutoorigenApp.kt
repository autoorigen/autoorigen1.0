package com.autoorigen.autoorigeninspect

import android.app.Application
import com.autoorigen.autoorigeninspect.data.InspeccionRepository
import com.autoorigen.autoorigeninspect.data.SessionManager

/** Punto único donde viven SessionManager y el repositorio — sin Hilt/Dagger,
 * no hace falta para el tamaño de esta app; cada ViewModel los recibe desde
 * aquí a través de SimpleViewModelFactory. */
class AutoorigenApp : Application() {
    lateinit var sessionManager: SessionManager
        private set
    lateinit var repository: InspeccionRepository
        private set

    override fun onCreate() {
        super.onCreate()
        sessionManager = SessionManager(this)
        repository = InspeccionRepository(sessionManager)
    }
}
