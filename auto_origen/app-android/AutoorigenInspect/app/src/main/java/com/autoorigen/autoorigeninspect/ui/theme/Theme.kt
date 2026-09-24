package com.autoorigen.autoorigeninspect.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val AutoorigenDarkColors = darkColorScheme(
    primary = Ignition,
    onPrimary = Color(0xFF120800),
    secondary = Ignition2,
    background = Ink,
    onBackground = Paper,
    surface = InkPanel2,
    onSurface = Paper,
    surfaceVariant = InkPanel,
    onSurfaceVariant = PaperDim,
    outline = Steel,
    error = ErrorRed,
)

// La app siempre usa el tema oscuro de la marca — el taller la usa en un
// entorno de trabajo, no depende del modo claro/oscuro del teléfono.
@Composable
fun AutoorigenInspectTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = AutoorigenDarkColors,
        typography = AutoorigenTypography,
        content = content,
    )
}
