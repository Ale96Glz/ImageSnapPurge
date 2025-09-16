# ImageSnapPurge - Eliminador de Imágenes Duplicadas

Una aplicación moderna y eficiente para detectar y eliminar imágenes duplicadas en tu computadora. Utiliza algoritmos avanzados de hash perceptual para encontrar imágenes similares, incluso si han sido modificadas ligeramente.

## 🚀 Características

### Detección Inteligente
- **Hash Perceptual (pHash)**: Detecta imágenes similares incluso con diferentes formatos, tamaños o compresión
- **Múltiples niveles de similitud**: Desde "Muy baja" hasta "Exacto" para ajustar la sensibilidad
- **Algoritmo Union-Find**: Agrupa eficientemente imágenes similares
- **Soporte múltiples formatos**: PNG, JPG, JPEG, BMP, GIF

### Interfaz Moderna
- **Diseño compacto y elegante**: UI optimizada para máxima productividad
- **Vista previa de miniaturas**: Visualiza todas las imágenes en cada grupo
- **Modo compacto**: Ajusta el tamaño de las miniaturas y espaciado
- **Paginación inteligente**: Navega fácilmente entre grupos de duplicados
- **Scroll vertical y horizontal**: Navegación fluida por grandes colecciones

### Funcionalidades Avanzadas
- **Auto-selección inteligente**: Mantiene automáticamente la imagen de mejor resolución
- **Eliminación segura**: Envía archivos a la papelera del sistema (recuperables)
- **Mover archivos**: Reubica duplicados en otra carpeta
- **Selección masiva**: Seleccionar todas, deseleccionar, invertir selección
- **Estadísticas en tiempo real**: Contador de grupos, imágenes y duplicados

### Configuración Flexible
- **Búsqueda recursiva**: Incluir o excluir subcarpetas
- **Control de similitud**: Slider con 21 niveles de precisión
- **Tamaños de miniatura**: Pequeñas, medianas o grandes
- **Progreso en tiempo real**: Barra de progreso con cancelación

## 📦 Instalación

### Requisitos del Sistema
- Windows 10/11
- Python 3.7+ (si ejecutas desde código fuente)
- 4GB RAM mínimo (8GB recomendado para colecciones grandes)

### Instalación desde Código Fuente

1. **Clona o descarga el repositorio**
```bash
git clone <url-del-repositorio>
cd Duplicados
```

2. **Instala las dependencias**
```bash
pip install -r requirements.txt
```

3. **Ejecuta la aplicación**
```bash
python duplicados.py
```

### Ejecutable Portable (Recomendado)

Descarga el archivo `ImageSnapPurge.exe` desde la sección de releases y ejecútalo directamente. No requiere instalación.

## 🎯 Uso

### 1. Seleccionar Carpeta
- Haz clic en "📁 Seleccionar carpeta" para elegir la ubicación a analizar
- Marca "Excluir subcarpetas" si solo quieres analizar la carpeta principal

### 2. Configurar Búsqueda
- **Nivel de similitud**: Ajusta el slider (0-20)
  - 0-5: Muy estricto (solo duplicados exactos)
  - 6-10: Moderado (pequeñas diferencias)
  - 11-15: Permisivo (imágenes similares)
  - 16-20: Muy permisivo (incluso con modificaciones)
- **Modo compacto**: Activa para vista más densa
- **Tamaño de miniaturas**: Ajusta según tu preferencia

### 3. Revisar Resultados
- Los grupos de duplicados aparecen uno debajo del otro
- Cada imagen muestra una miniatura y su nombre de archivo
- Usa la paginación para navegar entre grupos

### 4. Seleccionar y Eliminar
- **Selección manual**: Haz clic en las imágenes que quieres eliminar
- **Auto-selección**: Usa "⭐ Mantener mejor" para selección automática
- **Selección masiva**: Usa los botones de seleccionar todas/deseleccionar
- **Eliminar**: Los archivos se envían a la papelera (recuperables)

## ⚙️ Configuración Avanzada

### Niveles de Similitud Detallados

| Nivel | Rango | Uso Recomendado |
|-------|-------|-----------------|
| **Muy baja** | 0-5 | Duplicados exactos, mismo archivo |
| **Baja** | 6-10 | Misma imagen, diferente compresión |
| **Media** | 11-15 | Imágenes similares, recortes menores |
| **Alta** | 16-20 | Imágenes relacionadas, modificaciones |
| **Exacto** | 20 | Solo duplicados idénticos |

### Modo Compacto
- Reduce el espaciado entre elementos
- Miniaturas más pequeñas
- Texto más compacto
- Ideal para pantallas pequeñas o muchas imágenes

## 🔧 Solución de Problemas

### La aplicación no inicia
- Verifica que tienes Python 3.7+ instalado
- Ejecuta `pip install -r requirements.txt` para instalar dependencias
- En Windows, ejecuta como administrador si hay problemas de permisos

### No detecta duplicados
- Aumenta el nivel de similitud (mueve el slider hacia la derecha)
- Verifica que las imágenes están en formatos soportados
- Asegúrate de que la carpeta contiene imágenes

### Rendimiento lento
- Reduce el nivel de similitud para menos comparaciones
- Activa el modo compacto
- Cierra otras aplicaciones para liberar memoria

### Errores de permisos
- Ejecuta la aplicación como administrador
- Verifica que tienes permisos de lectura en la carpeta origen
- Asegúrate de que tienes permisos de escritura para eliminar archivos

## 📊 Rendimiento

### Tiempos Estimados (en una PC moderna)
- **1,000 imágenes**: 30-60 segundos
- **5,000 imágenes**: 2-5 minutos
- **10,000 imágenes**: 5-10 minutos
- **50,000+ imágenes**: 20-60 minutos

### Factores que Afectan el Rendimiento
- Nivel de similitud (más permisivo = más lento)
- Tamaño de las imágenes
- Velocidad del disco duro
- Cantidad de RAM disponible

## 🛡️ Seguridad

- **Eliminación segura**: Los archivos se envían a la papelera, no se eliminan permanentemente
- **Sin conexión a internet**: La aplicación funciona completamente offline
- **Sin recopilación de datos**: No se envían datos a servidores externos
- **Código abierto**: Puedes revisar el código fuente completo

## 🔄 Actualizaciones

### Versión Actual: 1.0.0
- Detección de duplicados con hash perceptual
- Interfaz moderna y responsiva
- Auto-selección inteligente
- Eliminación segura a papelera
- Soporte para múltiples formatos

### Próximas Características
- Soporte para más formatos (WebP, TIFF, HEIC)
- Caché de hashes para búsquedas más rápidas
- Filtros por fecha de modificación
- Vista de comparación lado a lado
- Exportar reportes de duplicados

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Si encuentras un bug o tienes una idea para mejorar:

1. Abre un issue describiendo el problema o sugerencia
2. Fork el repositorio
3. Crea una rama para tu feature
4. Envía un pull request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🙏 Agradecimientos

- **PIL (Pillow)**: Para el procesamiento de imágenes
- **ImageHash**: Para los algoritmos de hash perceptual
- **PyQt5**: Para la interfaz gráfica
- **send2trash**: Para la eliminación segura de archivos

## 📞 Soporte

Si tienes problemas o preguntas:
- Abre un issue en GitHub
- Revisa la sección de solución de problemas
- Consulta la documentación del código

---

**ImageSnapPurge** - Mantén tu colección de imágenes organizada y libre de duplicados. 🖼️✨
