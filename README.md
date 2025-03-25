
# TechFinder Website - E-Commerce

**TechFinder** es una tienda de tecnología creada con Django y SQLite, diseñada como una plataforma simple que implementa las funciones básicas de un sistema CRUD (Crear, Leer, Actualizar, Eliminar). Este proyecto permite la gestión de productos y usuarios dentro de una tienda virtual.

## Características

- **Gestión de usuarios**: Permite crear usuarios, editar sus datos, verlos y asignarles permisos.
- **Gestión de productos**: Permite añadir, editar, eliminar y ver productos disponibles en la tienda.
- **Gestión y filtrado**: Permite filtrar elementos del sitio web usando la barra lateral
- **Carrito de compras**: Da la posibilidad de añadir productos al carrito de compras y ver el total.
- **Productos**: Se incluyen dispositivos previamente cargados en la base de datos, pero puedes añadir más productos o eliminar los existentes según consideres necesario.

## Crear un usuario con permisos elevados

Para crear un usuario con permisos elevados (administrador), sigue los siguientes pasos:

1. **Crea un usuario mediante el formulario estándar** en la interfaz de administración.
2. **Accede a la base de datos** (SQLite) y cambia los siguientes parámetros en la tabla `auth_user`:

   - `is_superuser`: Asegúralo como `True`.
   - `permissions`: Establece el valor como `1`.
   - `is_active`: Asegúralo como `True`.
   - `is_staff`: Asegúralo como `True`.

   Con estos valores configurados, tendrás un usuario con privilegios máximos.

   **Usuario de ejemplo con privilegios máximos:**
   - **Correo**: `emir@alejandro.com`
   - **Contraseña**: `sivengahombre1`

   Puedes crear más usuarios con privilegios de administrador siguiendo los pasos anteriores.

## Requisitos del sistema

- **Python**: Se recomienda usar la última versión de Python. Yo estoy utilizando la versión `3.12.8`.
  
  Si no tienes Python, puedes descargarlo desde [https://www.python.org/downloads/](https://www.python.org/downloads/).

## Instalación

1. **Clona el repositorio** (ó descarga el .zip y extraelo):

   ```bash
   git clone https://github.com/universeneko/techfinder
   cd techfinder-website
   ```
   
   **Importante**: En la powershell es necesario habilitar la ejecución de scripts antes de proceder a ejecutar de los comandos de python.
   
   Puedes hacerlo con los siguientes comandos:
   ```bash
   Set-ExecutionPolicy RemoteSigned
   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
   ```
   
   ---

2. **Crea un entorno virtual en el directorio raíz del proyecto**:

    Haz `cd` al directorio raiz

    En el directorio raiz del proyecto, donde están archivos cómo **"requiriments.txt"** ejecuta en la powershell los siguientes comandos:



   ```bash
   python -m venv .venv
    ```
    
    Este comando no muestra **ningún** mensaje, pero mientras no salte ningún error todo va bien.
    
    Luego hay que ejecutar un segundo comando para habilitar el entorno virtual, dependiendo del sistema operativo hay que ejecutar un comando diferente.
    
    **Para Windows**:
    ```bash
   .venv\Scripts\activate
   ```
   
    **Para macOS/Linux**:
   ```bash
   source venv/bin/activate
   ```   
---

3. **Instala las dependencias**:

   Con el entorno virtual activado, ejecuta:

   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecuta las migraciones**: (Esto ya está hecho no se requiere este paso)

   Si aún no se ha hecho, ejecuta:

   ```bash
   python manage.py migrate
   ```
---
5. **Ejecuta el servidor**:

   Para ejecutar el servidor, usa:

   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

   - Se recomienda usar **localhost** o **0.0.0.0** para evitar problemas o configuraciones adicionales.
   - Puede usarse cualquier otro puerto pero en este caso se hará con el: **8000**
   - Si se ejecuta el servidor en **0.0.0.0** se debe acceder a http://localhost:8000
   - Si deseas usar una IP personalizada, modifica el archivo `settings.py` y agrega tu IP en la variable `ALLOWED_HOSTS`:

     ```python
     ALLOWED_HOSTS = ['192.168.1.110', 'localhost']
     ```

   Puedes configurar tu IP manualmente o dejarla en `localhost` si no deseas modificar nada más.

## Problemas conocidos

- **Carrito de compras**: El carrito funciona correctamente cuando no se aplican filtros. Si aplicas filtros, el carrito no permite añadir productos debido a un error de lógica en el código.

## Conclusión

Este es un proyecto simple de E-Commerce desarrollado con Django y SQLite, donde puedes gestionar productos y usuarios. Aunque tiene un error conocido, las funciones principales de añadir, editar y eliminar productos y usuarios están implementadas.

¡Disfruta usando el proyecto! Si necesitas agregar más dispositivos, puedes hacerlo desde la interfaz o directamente en la base de datos.

---
# TechFinder API - Uso con Bruno IDE

## Requisitos Previos
Para utilizar la API correctamente, es necesario contar con la última versión del proyecto. Se recomienda:
- Descargar los archivos actualizados.
- Eliminar la versión anterior o sobrescribir los archivos nuevos (instalación limpia).
- Ejecutar los comandos necesarios desde el paso 1 hasta el último para habilitar el servidor.

## Configuración de la API
Una vez que el servidor esté en ejecución:
- La API está configurada por defecto en `http://192.168.1.110`.
- Si se ejecuta en otra IP, es necesario actualizar todas las URLs en los archivos de Bruno.
- Se recomienda configurar la IP del host como estática para evitar cambios frecuentes.

---

## Instalación y Configuración de Bruno

### 1. Descarga de Bruno
Bruno puede descargarse desde su [sitio oficial](https://www.usebruno.com/downloads).
- **Versión portable**: Ideal para pruebas rápidas.*
- **Versión instalador**: Recomendado para uso permanente.

*Se ha probado la versión portable con éxito.

### 2. Importación de la Colección en Bruno
1. Abrir Bruno y dirigirse a la pestaña **Collection**.
2. Hacer clic en **Open Collection**.
3. Navegar hasta el directorio `/api/techfinder` y seleccionarlo.
4. Una vez importado, aparecerá un menú desplegable llamado **techfinder**, donde se encuentran todas las solicitudes disponibles.

---

## Autenticación y Uso de la API

### 1. Generar un Token Bearer
Para autenticar las solicitudes:
1. Usar la petición **api_token_gen**.
2. Se enviarán automáticamente los datos de usuario y contraseña preconfigurados.
3. La API responderá con dos tokens.
4. Copiar el valor del token **"access"** (el string largo entre comillas).

⚠️ **Importante:** Este token es válido por **5 minutos**. Si expira, genera uno nuevo.

### 2. Configurar el Token en las Peticiones
Para incluir el token en las peticiones:
- En la sección **Headers** de cada petición, agrega la propiedad:
- En todas ya se encuentra agregada pero hace falta cambiar el token por el generado recien.
  ```plaintext
  Authorization: Bearer [API Token]
  ```
  (Reemplazar `[API Token]` con el valor copiado, sin comillas).

---

## Ejemplo de Edición de un Dispositivo
Para modificar un dispositivo con la request **device_editor**, se pueden enviar solo los campos que se desean actualizar.

### Ejemplo de Payload:
```json
{
    "nombre": "Nuevo Nombre del Producto",
    "descripcion": "Nueva Descripción",
    "precio": 500.0,
    "stock": 10,
    "tipo": "Smartphone",
    "sistema_operativo": "Android",
    "imagen_url": "https://example.com/imagen.jpg"
}
```

- Si solo se envía **"nombre"**, solo se actualizará ese campo sin afectar los demás.
- La API es flexible y permite editar solo los campos necesarios.

## Ejemplo de Subida de Imágenes en `device_adder`

Al agregar un nuevo dispositivo a través de la API `device_adder`, se puede incluir una imagen del producto de dos formas:

1. **Adjuntar la imagen en la petición** (como un archivo en formato `PNG` con proporción `1:1`).
2. **Proporcionar una URL de la imagen**, permitiendo que el sistema la descargue automáticamente y la almacene en el directorio `media/products/`.

### Requisitos de la imagen:
- **Formato:** PNG  
- **Relación de aspecto:** 1:1 (cuadrada)  
- **Método de envío:** Archivo en la petición o URL válida  

Si se proporciona una URL, el servidor gestionará la descarga y almacenamiento de la imagen en `media/products/`. Asegúrate de que la URL sea accesible y que la imagen cumpla con los requisitos de formato.  

Ejemplo de JSON con URL de imagen:  

```json
{
  "nombre": "iPhone 15",
  "descripcion": "Última generación de Apple",
  "precio": "1200.99",
  "stock": 10,
  "tipo": "smartphone",
  "sistema_operativo": "iOS",
  "imagen_url": "https://cablenet.com.cy/wp-content/uploads/iPhone_15_Pro_Max_White_Titanium_Hero_Alt_Screen__USEN.png"
}
```


---

## Conclusión
Una vez configurado el token, es posible realizar todas las peticiones y visualizar las respuestas sin inconvenientes.

¡Listo para interactuar con la API en Bruno!


---

**Licencias:**

Este proyecto es **Software de Código Abierto (OSS)**. Puedes clonarlo o forkeado sin problemas y utilizarlo según tus necesidades. Si decides contribuir o modificar el proyecto, ¡bienvenido sea!

