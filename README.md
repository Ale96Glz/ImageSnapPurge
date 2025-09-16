# ImageSnapPurge - Eliminador de Imágenes Duplicadas

Una aplicación moderna para detectar y eliminar imágenes duplicadas de forma inteligente. Utiliza algoritmos de hash perceptual para identificar duplicados incluso cuando las imágenes han sido modificadas ligeramente.

## ✨ Características

- 🔍 **Detección Inteligente**: Utiliza hash perceptual para detectar duplicados
- 🎨 **Interfaz Moderna**: Diseño elegante y fácil de usar
- 🖼️ **Vista Previa**: Miniaturas de las imágenes para facilitar la identificación
- ⚙️ **Configuración Flexible**: Ajusta el nivel de similitud según tus necesidades
- 🗑️ **Eliminación Segura**: Los archivos se envían a la papelera
- 📊 **Estadísticas**: Información detallada sobre duplicados encontrados
- 🔄 **Auto-selección**: Selección automática inteligente de la mejor imagen

## 🚀 Instalación

### Requisitos
- Python 3.7 o superior
- Windows 10/11, macOS 10.14+, o Linux
- 4GB RAM mínimo

### Instalación desde Código Fuente

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/imagesnappurge.git
   cd imagesnappurge
   ```

2. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecuta la aplicación:**
   ```bash
   python duplicados.py
   ```

## 📖 Uso

1. **Seleccionar Carpeta**: Haz clic en "Seleccionar Carpeta" y elige el directorio a analizar
2. **Ajustar Similitud**: Usa el slider para ajustar el nivel de similitud (0-100%)
3. **Revisar Resultados**: Examina los grupos de duplicados encontrados
4. **Seleccionar Imágenes**: Marca las imágenes que deseas eliminar
5. **Eliminar**: Haz clic en "Eliminar Seleccionados" para enviar a la papelera

### Características Avanzadas

- **Auto-selección Inteligente**: Selecciona automáticamente la imagen con mejor resolución
- **Modo Compacto**: Interfaz más densa para pantallas pequeñas
- **Configuración de Similitud**: Ajusta la sensibilidad de detección

## 🔧 Solución de Problemas

### Error: "No module named 'PyQt5'"
```bash
pip install PyQt5
```

### Error: "No module named 'imagehash'"
```bash
pip install imagehash
```

### Error: "No module named 'send2trash'"
```bash
pip install send2trash
```

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

---

**¡Disfruta de una colección de imágenes libre de duplicados!** 🎉