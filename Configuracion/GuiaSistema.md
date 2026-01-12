# **PARTE 1**

De momento solo tenemos la conexión mediante la misma red ahora si queremos una conexión desde datos moviles necesitamos descargar NGROK.

#### **PAGINA:**

dashboard.ngrok.com/signup

* Getting Started > Setup & Installation > Windows > Download > Download for Windows (64-Bit)

Después de descargar el zip, extraer y el .exe ponerlo en la carpeta principal, al lado de main.py, ejecutarlo, se abrira un cmd y dentro ejecutar el codigo que aparece con el token.

* **ngrok config add-authtoken $YOUR_AUTHTOKEN**

#### **COMO OBTENER EL AUTHTOKEN:**

Getting Started > Your Authtoken > Command Line

* ngrok config add-authtoken $YOUR_AUTHTOKEN

Luego para activar el servidor

* ngrok http 8000

![1768177118672](images/GuiaBackend/1768177118672.png)

Con la información de Forwarding tendremos el url para enviar los datos a la base de datos

[IMPLEMENTAR LO ANTERIOR A LA APP DE ATAJO](GuiaAtajo.md#parte-2)

