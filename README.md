
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

    En el directorio raiz del proyecto, donde están archivos cómo **"requiriments.txt"** ejecuta en la powershell los siguiente comandos:



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

   - Se recomienda usar **localhost** o **0.0.0.0** para evitar problemas con configuraciones adicionales.
   - Puede usarse cualquier otro puerto pero en este caso se hará con el: **8000**
   - Si se ejecuta el servidor en **0.0.0.0** se debe acceder a http://localhost:8000
   - Si deseas usar una IP personalizada, modifica el archivo `settings.py` y agrega tu IP en la variable `ALLOWED_HOSTS`:

     ```python
     ALLOWED_HOSTS = ['192.168.1.110', 'localhost']
     ```

   Puedes configurar tu IP manualmente o dejarla en `localhost` si no deseas modificar nada más.

## Problemas conocidos

- **Carrito de compras**: El carrito funciona correctamente cuando no se aplican filtros. Si aplicas filtros, el carrito no permite añadir productos debido a un error de lógica en el código.
- **Slider de productos**: Inicialmente funcionaba, pero actualmente no lo hace más. Solo el slider de "máximo" funciona, y el de "mínimo" está desactivado.

## Conclusión

Este es un proyecto simple de E-Commerce desarrollado con Django y SQLite, donde puedes gestionar productos y usuarios. Aunque tiene algunos errores conocidos, las funciones principales de añadir, editar y eliminar productos y usuarios están implementadas.

¡Disfruta usando el proyecto! Si necesitas agregar más dispositivos, puedes hacerlo desde la interfaz o directamente en la base de datos.

---

**Licencias:**

Este proyecto es **Software de Código Abierto (OSS)**. Puedes clonarlo o forkeado sin problemas y utilizarlo según tus necesidades. Si decides contribuir o modificar el proyecto, ¡bienvenido sea!

