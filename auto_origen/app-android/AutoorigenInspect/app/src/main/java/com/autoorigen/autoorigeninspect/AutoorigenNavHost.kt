package com.autoorigen.autoorigeninspect

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.autoorigen.autoorigeninspect.ui.captura.CapturaScreen
import com.autoorigen.autoorigeninspect.ui.detalle.DetalleInspeccionScreen
import com.autoorigen.autoorigeninspect.ui.historial.HistorialScreen
import com.autoorigen.autoorigeninspect.ui.home.HomeScreen
import com.autoorigen.autoorigeninspect.ui.login.LoginScreen
import com.autoorigen.autoorigeninspect.ui.nueva.NuevaInspeccionScreen
import com.autoorigen.autoorigeninspect.ui.observaciones.ObservacionesScreen

object Rutas {
    const val LOGIN = "login"
    const val HOME = "home"
    const val NUEVA_INSPECCION = "nueva_inspeccion"
    const val CAPTURA = "captura/{ordenId}/{placa}"
    const val OBSERVACIONES = "observaciones/{ordenId}"
    const val HISTORIAL = "historial"
    const val DETALLE = "detalle/{ordenId}"

    fun captura(ordenId: Int, placa: String) = "captura/$ordenId/$placa"
    fun observaciones(ordenId: Int) = "observaciones/$ordenId"
    fun detalle(ordenId: Int) = "detalle/$ordenId"
}

@Composable
fun AutoorigenNavHost(navController: NavHostController = rememberNavController()) {
    NavHost(navController = navController, startDestination = Rutas.LOGIN) {

        composable(Rutas.LOGIN) {
            LoginScreen(
                alEntrar = {
                    navController.navigate(Rutas.HOME) {
                        popUpTo(Rutas.LOGIN) { inclusive = true }
                    }
                },
            )
        }

        composable(Rutas.HOME) {
            HomeScreen(
                alTocarNuevaInspeccion = { navController.navigate(Rutas.NUEVA_INSPECCION) },
                alTocarHistorial = { navController.navigate(Rutas.HISTORIAL) },
                alCerrarSesion = {
                    navController.navigate(Rutas.LOGIN) {
                        popUpTo(Rutas.HOME) { inclusive = true }
                    }
                },
            )
        }

        composable(Rutas.NUEVA_INSPECCION) {
            NuevaInspeccionScreen(
                alCrear = { ordenId, placa ->
                    navController.navigate(Rutas.captura(ordenId, placa)) {
                        popUpTo(Rutas.NUEVA_INSPECCION) { inclusive = true }
                    }
                },
                alCancelar = { navController.popBackStack() },
            )
        }

        composable(
            route = Rutas.CAPTURA,
            arguments = listOf(
                navArgument("ordenId") { type = NavType.IntType },
                navArgument("placa") { type = NavType.StringType },
            ),
        ) { entrada ->
            val ordenId = entrada.arguments?.getInt("ordenId") ?: 0
            val placa = entrada.arguments?.getString("placa") ?: ""
            CapturaScreen(
                ordenId = ordenId,
                placa = placa,
                alContinuar = { navController.navigate(Rutas.observaciones(ordenId)) },
            )
        }

        composable(
            route = Rutas.OBSERVACIONES,
            arguments = listOf(navArgument("ordenId") { type = NavType.IntType }),
        ) { entrada ->
            val ordenId = entrada.arguments?.getInt("ordenId") ?: 0
            ObservacionesScreen(
                ordenId = ordenId,
                alFinalizar = {
                    navController.navigate(Rutas.HOME) {
                        popUpTo(Rutas.HOME) { inclusive = true }
                    }
                },
            )
        }

        composable(Rutas.HISTORIAL) {
            HistorialScreen(
                alVolver = { navController.popBackStack() },
                alTocarInspeccion = { ordenId -> navController.navigate(Rutas.detalle(ordenId)) },
            )
        }

        composable(
            route = Rutas.DETALLE,
            arguments = listOf(navArgument("ordenId") { type = NavType.IntType }),
        ) { entrada ->
            val ordenId = entrada.arguments?.getInt("ordenId") ?: 0
            DetalleInspeccionScreen(ordenId = ordenId, alVolver = { navController.popBackStack() })
        }
    }
}
