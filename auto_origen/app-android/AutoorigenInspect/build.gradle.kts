// Nivel raíz: solo declara los plugins para que estén disponibles en :app,
// sin aplicarlos aquí (apply false).
plugins {
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.kotlin.android) apply false
    alias(libs.plugins.kotlin.compose) apply false
}
