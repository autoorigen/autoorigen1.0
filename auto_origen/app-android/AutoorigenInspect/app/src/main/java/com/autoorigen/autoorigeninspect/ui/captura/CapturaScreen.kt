package com.autoorigen.autoorigeninspect.ui.captura

import android.Manifest
import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.video.FileOutputOptions
import androidx.camera.video.Quality
import androidx.camera.video.QualitySelector
import androidx.camera.video.Recorder
import androidx.camera.video.Recording
import androidx.camera.video.VideoCapture
import androidx.camera.video.VideoRecordEvent
import androidx.camera.view.PreviewView
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.weight
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Error
import androidx.compose.material.icons.filled.FiberManualRecord
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.ListItem
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import androidx.lifecycle.viewmodel.compose.viewModel
import com.autoorigen.autoorigeninspect.AutoorigenApp
import com.autoorigen.autoorigeninspect.ui.SimpleViewModelFactory
import com.autoorigen.autoorigeninspect.ui.components.BotonPrincipal
import java.io.File

@Composable
fun CapturaScreen(ordenId: Int, placa: String, alContinuar: () -> Unit) {
    val app = LocalContext.current.applicationContext as AutoorigenApp
    val viewModel: CapturaViewModel = viewModel(
        factory = SimpleViewModelFactory { CapturaViewModel(app.repository, ordenId) },
    )
    val elementos by viewModel.elementos.collectAsState()
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current

    val permisosNecesarios = remember { arrayOf(Manifest.permission.CAMERA, Manifest.permission.RECORD_AUDIO) }
    var permisosConcedidos by remember { mutableStateOf(false) }
    val lanzadorPermisos = rememberLauncherForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) { resultados ->
        permisosConcedidos = resultados.values.all { it }
    }
    LaunchedEffect(Unit) {
        val yaConcedidos = permisosNecesarios.all {
            ContextCompat.checkSelfPermission(context, it) == PackageManager.PERMISSION_GRANTED
        }
        if (yaConcedidos) permisosConcedidos = true else lanzadorPermisos.launch(permisosNecesarios)
    }

    val previewView = remember { PreviewView(context) }
    val imageCapture = remember { ImageCapture.Builder().build() }
    val recorder = remember { Recorder.Builder().setQualitySelector(QualitySelector.from(Quality.HD)).build() }
    val videoCapture = remember { VideoCapture.withOutput(recorder) }
    var grabacionActiva by remember { mutableStateOf<Recording?>(null) }
    var proveedorCamara by remember { mutableStateOf<ProcessCameraProvider?>(null) }

    DisposableEffect(permisosConcedidos) {
        if (!permisosConcedidos) return@DisposableEffect onDispose {}

        val futuro = ProcessCameraProvider.getInstance(context)
        futuro.addListener(
            {
                val cameraProvider = futuro.get()
                proveedorCamara = cameraProvider
                val preview = Preview.Builder().build().also { it.setSurfaceProvider(previewView.surfaceProvider) }
                try {
                    cameraProvider.unbindAll()
                    cameraProvider.bindToLifecycle(
                        lifecycleOwner, CameraSelector.DEFAULT_BACK_CAMERA, preview, imageCapture, videoCapture,
                    )
                } catch (e: Exception) {
                    // La pantalla sigue usable aunque falle el bind (ej. sin cámara trasera).
                }
            },
            ContextCompat.getMainExecutor(context),
        )

        onDispose { proveedorCamara?.unbindAll() }
    }

    fun tomarFoto(titulo: String) {
        val archivo = File(context.cacheDir, "AO_${System.currentTimeMillis()}.jpg")
        val opciones = ImageCapture.OutputFileOptions.Builder(archivo).build()
        imageCapture.takePicture(
            opciones,
            ContextCompat.getMainExecutor(context),
            object : ImageCapture.OnImageSavedCallback {
                override fun onImageSaved(output: ImageCapture.OutputFileResults) {
                    viewModel.subirArchivo(archivo, esVideo = false, titulo = titulo)
                }
                override fun onError(exception: ImageCaptureException) { /* se refleja como fallo de subida si el archivo no llega a crearse */ }
            },
        )
    }

    fun alternarGrabacionVideo() {
        val grabacionEnCurso = grabacionActiva
        if (grabacionEnCurso != null) {
            grabacionEnCurso.stop()
            grabacionActiva = null
            return
        }
        val archivo = File(context.cacheDir, "AO_${System.currentTimeMillis()}.mp4")
        val opcionesSalida = FileOutputOptions.Builder(archivo).build()
        val pendiente = videoCapture.output.prepareRecording(context, opcionesSalida).let {
            if (ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
                it.withAudioEnabled()
            } else it
        }
        grabacionActiva = pendiente.start(ContextCompat.getMainExecutor(context)) { evento ->
            if (evento is VideoRecordEvent.Finalize) {
                if (!evento.hasError()) {
                    viewModel.subirArchivo(archivo, esVideo = true, titulo = "Video de la inspección")
                }
            }
        }
    }

    Column(modifier = Modifier.fillMaxSize()) {
        TopAppBar(title = { Text("Fotos y video — $placa") })

        if (permisosConcedidos) {
            AndroidView(factory = { previewView }, modifier = Modifier.fillMaxWidth().height(320.dp))
        } else {
            Column(
                modifier = Modifier.fillMaxWidth().height(320.dp).padding(16.dp),
                verticalArrangement = Arrangement.Center,
            ) {
                Text("Se necesita permiso de cámara y micrófono para continuar.")
            }
        }

        Row(
            modifier = Modifier.fillMaxWidth().padding(12.dp),
            horizontalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            OutlinedButton(onClick = { tomarFoto("Foto de la placa") }, modifier = Modifier.weight(1f)) {
                Icon(Icons.Filled.CameraAlt, contentDescription = null)
                Text(" Foto de la placa")
            }
        }
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 12.dp),
            horizontalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Button(onClick = { tomarFoto("Foto de la inspección") }, modifier = Modifier.weight(1f)) {
                Icon(Icons.Filled.CameraAlt, contentDescription = null)
                Text(" Tomar foto")
            }
            Button(onClick = { alternarGrabacionVideo() }, modifier = Modifier.weight(1f)) {
                Icon(if (grabacionActiva != null) Icons.Filled.Stop else Icons.Filled.FiberManualRecord, contentDescription = null)
                Text(if (grabacionActiva != null) " Detener video" else " Grabar video")
            }
        }

        LazyColumn(modifier = Modifier.weight(1f).padding(horizontal = 8.dp)) {
            items(elementos, key = { it.id }) { elemento ->
                ListItem(
                    headlineContent = { Text(elemento.titulo) },
                    supportingContent = {
                        Text(
                            when {
                                elemento.error != null -> "Error: ${elemento.error}"
                                elemento.subiendo -> "Subiendo…"
                                elemento.subido -> "Subido"
                                else -> ""
                            },
                        )
                    },
                    trailingContent = {
                        when {
                            elemento.subiendo -> CircularProgressIndicator(modifier = Modifier.height(20.dp))
                            elemento.error != null -> Icon(Icons.Filled.Error, contentDescription = null, tint = MaterialTheme.colorScheme.error)
                            elemento.subido -> Icon(Icons.Filled.CheckCircle, contentDescription = null, tint = MaterialTheme.colorScheme.primary)
                        }
                    },
                )
            }
        }

        BotonPrincipal(
            texto = "Continuar a observaciones",
            onClick = alContinuar,
            modifier = Modifier.padding(16.dp),
        )
    }
}
