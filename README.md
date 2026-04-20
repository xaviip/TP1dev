# API de Fixture y ProDe - Mundial 2026

> Trabajo Práctico de **Introducción al Desarrollo de Software**  
> API REST para gestionar un fixture de fútbol con sistema de predicciones y ranking.

---

## Tabla de Contenidos

- [Contexto](#contexto)
- [Requisitos y Entorno](#requisitos-y-entorno)
- [Instalación](#instalación)
- [Ejecución](#ejecución)
- [Endpoints de la API](#endpoints-de-la-api)
- [Sistema de Puntajes](#sistema-de-puntajes)
- [Arquitectura](#arquitectura)
- [Equipo](#equipo)

---

## Contexto

Este proyecto es una **API REST** que gestiona un fixture de fútbol, extendida con un sistema **ProDe**. Los usuarios predicen resultados de partidos antes de que se jueguen y consultan un ranking según sus aciertos.

---

## Requisitos y Entorno

| Componente      | Detalle     |
|-----------------|-------------|
| Lenguaje        | Python 3.14 |
| Framework       | Flask       |
| Base de Datos   | MySQL       |
| Testing         | Postman     |
| Entorno virtual | `.venv`     |

- **Finales de línea:** LF

---

## Instalación

**1. Clonar el repositorio**
```bash
git clone https://github.com/xaviip/TP1dev.git
cd TP1dev
```

**2. Activar el entorno virtual**
```bash
# Linux / Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**3. Instalar dependencias**
```bash
pip install -r requirements.txt
```

**4. Inicializar la base de datos**

Ejecutar `init_db.sql` en MySQL. Esto crea la base de datos `fixture` con las tablas:
- `usuarios`
- `partidos`
- `predicciones`

---

##  Ejecución

```bash
python app.py
```

La API quedará disponible en: **http://127.0.0.1:5000**

---

## Endpoints de la API

### Partidos 

| Método | Endpoint         | Descripción               |
|--------|------------------|---------------------------|
| `POST` | `/partidos`      | Crea un partido           |
| `GET`  | `/partidos`      | Lista todos los partidos  |
| `GET`  | `/partidos/<id>` | Obtiene un partido por ID |
| `PUT`  | `/partidos/<id>` | Reemplazar un partido     |
| `DEL`  | `/partidos/<id>` | Eliminar partido          |

### Resultados
| Método | Endpoint                   | Descripción                                |
|--------|----------------------------|--------------------------------------------|
| `PUT`  | `/partidos/<id>/resultado` | Actualiza el resultado final de un partido |

---

### Usuarios _(ProDe)_

| Método   | Endpoint         | Descripción                              |
|----------|------------------|------------------------------------------|
| `POST`   | `/usuarios`      | Crea un usuario. Body: `nombre`, `email` |
| `GET`    | `/usuarios`      | Lista usuarios _(paginación HATEOAS)_    |
| `GET`    | `/usuarios/<id>` | Obtiene un usuario por ID                |
| `PUT`    | `/usuarios/<id>` | Reemplaza los datos de un usuario        |
| `DELETE` | `/usuarios/<id>` | Elimina un usuario                       |

---

### Predicciones _(ProDe)_

| Método | Endpoint                    | Descripción                              |
|--------|-----------------------------|------------------------------------------|
| `POST` | `/partidos/<id>/prediccion` | Registrar una predicción para un partido |

**Requisitos:**
- El partido debe existir y **no haberse jugado**.
- Solo se permite **una predicción por usuario**.

**Body:**
```json
{
  "id_usuario": 1,
  "local": 2,
  "visitante": 1
}
```

---

### Ranking _(ProDe)_

| Método | Endpoint   | Descripción                                                                  |
|--------|------------|------------------------------------------------------------------------------|
| `GET`  | `/ranking` | Ranking de usuarios por puntos _(paginación HATEOAS con `limit` y `offset`)_ |

**Respuesta:** `id_usuario`, `puntos`.

---

## Sistema de Puntajes

| Puntos | Condición                                                              |
|:------:|------------------------------------------------------------------------|
| **3**  | Resultado exacto: acierta ganador/empate **y** marcador exacto         |
| **1**  | Resultado correcto: acierta ganador/empate, pero con distinto marcador |
| **0**  | Incorrecto: no acierta ni ganador ni empate                            |

---

## Arquitectura

| Archivo        | Responsabilidad                                                     |
|----------------|---------------------------------------------------------------------|
| `app.py`       | Rutas, controladores, Flask, validaciones                           |
| `db.py`        | Persistencia, base de datos, consultas SQL parametrizadas           |
| `init_db.sql`  | DB en SQL para la creación de las tablas y la base de datos fixture |
| `swagger.yaml` | Contrato a seguir en la API                                         |


**Decisiones de diseño:**

- **Seguridad:** Todas las consultas SQL usan parámetros para prevenir inyección SQL.
- **HATEOAS:** Implementado en las listas `/usuarios` y `/ranking` con links: `_self`, `_next`, `_prev`, `_first`, `_last`.
- **Swagger:** Nombres de campos fieles al contrato (ej. `local`, `visitante`).

---


## Documentación Interactiva (Swagger)

Para interactuar con la API de manera visual sin necesidad de escribir código cliente ni usar herramientas como **Postman**:

1. Copia todo el contenido del archivo swagger.yaml.
2. Ve a Swagger Editor.
3. Pega el contenido en el panel izquierdo.
4. En el panel derecho verás la interfaz gráfica. Usa el botón `Try it out` en cada endpoint para probar tu API local en tiempo real.


---

##  Equipo

| Integrantes         | Padrón |
|---------------------|--------|
| Patricio López      | 115353 | 
| Abril Chiara Berlot | 114287 |
| Karla Torres        | 114908 |
| Camila Delfino      | 113552 |
| Sofía Belén Machuca | 113873 |

### Participación nula/IA
| Integrantes                 | Padrón |
|-----------------------------|--------|
| Jhordan Huancaruna Villegas | 115732 |
| José Antonio Toro Rivas     | 115216 |

