# Reglas por defecto de Android Studio. minifyEnabled está en false para esta
# app interna, así que estas reglas solo importan si más adelante activas R8.
-keepattributes Signature
-keepattributes *Annotation*
-keep class com.autoorigen.autoorigeninspect.data.network.dto.** { *; }
