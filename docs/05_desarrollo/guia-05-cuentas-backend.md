# Guía 5 — Las cuentas: registro, login con JWT y el primer rol admin

> **Qué construirás hoy:** las cuentas de Maura — el backend completo de la
> etapa 2: registro de clientas, login que emite un JWT de larga vida, el
> perfil protegido por token y el primer endpoint protegido por rol
> (`/api/admin/estado`), más la siembra de las dos cuentas demo.
> **Al terminar tendrás:** tu API autenticando clientas (AUTH-01, AUTH-02), un
> admin demo sembrado por variables de entorno y un 403 verificable para la
> clienta (AUTH-03, D-33) — todo implementando el contrato 0.2.0 sin
> desviarse (D-15, ADR-007).
> **Necesitas:** las guías 1 a 4 completas — el backend en capas con la tabla
> `productos` sembrada (re-siembra imprime doce `[=]`), la API encendida con
> `uv run fastapi dev app/main.py` y `/docs` respondiendo. Abre
> `docs/04_arquitectura/contrato_api.yaml` en una pestaña: hoy es la vara que
> mide cada paso.

---

## Los términos de hoy (antes de copiar nada)

| Término | Qué es, en una frase |
|---|---|
| **Hash (Argon2)** | La transformación de unidireccional que guarda la contraseña: del hash no se puede recuperar la clave, y verificarla cuesta tiempo y memoria a propósito (frena la fuerza bruta) |
| **JWT (JSON Web Token)** | Un "recibo firmado" que viaja por el cable y lleva identidad: claims + firma HS256 que solo el backend puede producir y verificar |
| **Claims** | Los pares clave-valor que viven dentro del token (`sub`, `rol`, `exp`, `iat`): la identidad y su vigencia, firmadas de una vez |
| **Form OAuth2** | La forma `application/x-www-form-urlencoded` de enviar credenciales en el login (el campo se llama `username` aunque transporte un email) — la que hace funcionar el botón Authorize de `/docs` |
| **Secreto de firma** | El string que solo conoce el backend y que firma/verifica los JWT: vive en el `.env`, jamás en el código ni en la guía |
| **Upsert de usuarios** | "Actualizar o insertar" una cuenta por su email — la misma idempotencia del seed de productos, ahora con credenciales (D-23, D-24) |

---

## Paso 1 — Tres piezas nuevas (y ninguna de las vetadas)

🧠 **El desarrollador piensa:** *tres paquetes, tres razones. **`pyjwt`** firma y
verifica JWT — es la librería que usa hoy el tutorial oficial de FastAPI, y
reemplaza a `python-jose`, que quedó fuera del stack con CVEs abiertas.
**`pwdlib[argon2]`** hashea contraseñas con `PasswordHash.recommended()`
(Argon2) — el mismo recomendado por el tutorial, en reemplazo de `passlib`,
sin mantenimiento desde 2020. Y **`python-multipart`** parsea el formulario
del login: sin él, `OAuth2PasswordRequestForm` no puede leer el body
`form-encoded` (ya viene dentro de `fastapi[standard]`, pero el tutorial lo
instala explícito y hoy lo hacemos nuestro). La regla que no se negocia: las
librerías legadas no se mencionan ni como alternativa — existen y están
vetadas, y saber POR QUÉ es parte del oficio.*

Desde `backend/`, ejecuta:

```
uv add pyjwt "pwdlib[argon2]" python-multipart
```

Tu `pyproject.toml` gana las tres dependencias congeladas en `uv.lock`
(RNF-04).

✅ **Mini-verificación:** desde `backend/`, ejecuta:

```
uv run python -c "import jwt; print(jwt.__version__)"
```

Debe imprimir `2.15.x` — PyJWT instalado y con la versión del stack. (Las
otras dos ya se usan en los pasos 6 y 7: si una faltara, `uv` lo habría
gritado aquí mismo.)

---

## Paso 2 — El `.env` y `Settings`: el secreto que no se escribe

🧠 **El desarrollador piensa:** *firmar tokens exige un secreto, y un secreto
en el código es un secreto filtrado (RNF-05). Tres decisiones. Primera: el
secreto se GENERA, no se inventa — un one-liner de Python que funciona igual
en PowerShell, cmd y Git Bash (D-12); el `openssl rand -hex 32` del tutorial
supone un openssl que Windows no siempre tiene. Segunda: `Settings` gana
`secret_key` **sin valor por defecto** — si el `.env` no existe, pydantic
lanza su error al importar y la app no parte. Eso es **fail-fast**: un
secreto "con default" es un secreto que un día se olvida cambiar. Tercera:
las credenciales demo del seed (D-23, D-24) también viven ahí, porque
"cada alumno reinicia su admin sin miedo" empieza por "el admin no está
escrito en la guía". Y un detalle que faltaba: hasta ahora `Settings` leía
variables de entorno del shell, pero nunca un archivo `.env` — hoy que
existe uno, le enseñamos a leerlo con `env_file`.*

Desde `backend/`, genera tu secreto (agnóstico de terminal, D-12):

```
uv run python -c "import secrets; print(secrets.token_hex(32))"
```

Copia ese string. Ahora crea **`backend/.env.example`** — la plantilla que SÍ
se sube al repositorio, solo con placeholders:

```
# Copia este archivo como .env y reemplaza cada valor por el TUYO.
# El .env ya está gitignoreado desde la guía 1: lo que se versiona es
# este ejemplo, jamás el secreto real.
SECRET_KEY=pega-aqui-el-resultado-del-comando-token-hex
ADMIN_EMAIL=admin@maura.cl
ADMIN_PASSWORD=elige-una-clave-para-tu-admin-demo
CLIENTE_EMAIL=clienta@maura.cl
CLIENTE_PASSWORD=elige-una-clave-para-tu-clienta-demo
```

Copia tu plantilla a **`backend/.env`** y pega TU secreto generado y TUS dos
claves demo (mínimo 8 caracteres, igual que pediremos a las clientas —
RN-05). Después extiende **`app/config.py`**:

```python
"""Configuración tipada de la API.

TODO lo configurable vive en un solo lugar: pydantic-settings carga
valores por defecto de desarrollo y permite sobreescribirlos con
variables de entorno (p. ej. DATABASE_URL, CORS_ORIGINS). Los secretos
jamás van en el código.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Ajustes del backend. En producción se sobreescriben por entorno."""

    # El .env entra en acción: la guía 1 lo dejó gitignoreado esperando
    # este momento (variables de entorno Y archivo, sin activar nada).
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str = "sqlite:///./maura.db"
    cors_origins: list[str] = ["http://localhost:5173"]

    # --- Etapa 2: cuentas JWT (ADR-009) ---
    secret_key: str  # SIN default: sin .env la app no parte (fail-fast)
    token_dias: int = 7  # vida del token (D-20)
    # Cuentas demo del seed (D-23, D-24): credenciales por entorno,
    # jamás escritas en el código ni en la guía.
    admin_email: str
    admin_password: str
    cliente_email: str
    cliente_password: str


settings = Settings()
```

✅ **Mini-verificación:** desde `backend/`, ejecuta:

```
uv run python -c "from app.config import settings; print(settings.token_dias, settings.admin_email)"
```

Debe imprimir `7` y TU `ADMIN_EMAIL` (p. ej. `admin@maura.cl`) — el `.env`
existe para pydantic-settings. Y comprueba el fail-fast al revés:
comenta momentáneamente la línea `SECRET_KEY` de tu `.env` y vuelve a
ejecutar el comando: pydantic lanza un `ValidationError` nombrando
`secret_key` — la app se nieza a partir sin secreto. Descoméntala antes
de seguir. (`git status` no debe listar `.env`: el `.gitignore` de la
guía 1 ya lo excluye — si aparece, para y arréglalo.)

---

## Paso 3 — `models/usuario.py`: el enum del rol, segunda vuelta del gotcha

🧠 **El desarrollador piensa:** *la tabla `usuarios` traduce el diccionario de
datos del diseño (§2.2: email 255 único e índice, hash 255, rol enum) — pero
el corazón del paso es un viejo conocido: **el gotcha del enum de la guía
3**. SQLAlchemy persiste los NOMBRES de los miembros: si declaro
`ADMIN = "admin"`, la base guarda `ADMIN`… y el contrato promete el enum
`[cliente, admin]` en minúsculas (`contrato_api.yaml`, schema
`UsuarioPublico`). La vacuna es la misma de `FamiliaAromatica`: **nombre ==
valor**. Segunda vuelta del mismo bug, misma cura — y ojo con el `email`:
lleva `unique=True, index=True` porque es la **clave natural del upsert** de
cuentas (D-23, D-24), exactamente como el `sku` lo era del catálogo. El
`hashed_password` guarda el string `$argon2id$...` que produce pwdlib —
y por regla (RN-07) ningún schema lo va a exponer jamás.*

Crea **`backend/app/models/usuario.py`**:

```python
"""Modelo Usuario y enum RolUsuario (tabla `usuarios`)."""

import enum

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RolUsuario(str, enum.Enum):
    """Rol de la cuenta. Misma lección que FamiliaAromatica en la guía 3:
    SQLAlchemy persiste los NOMBRES, por eso nombre == valor — la BD guarda
    "cliente"/"admin", los strings exactos del enum del contrato (RF-08)."""

    cliente = "cliente"
    admin = "admin"


class Usuario(Base):
    """Una cuenta: clienta registrada o admin. La clave natural es el email
    (único e índice) — el seed de cuentas converge por él (D-23, D-24)."""

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))  # "$argon2id$..." (RN-07: jamás sale)
    rol: Mapped[RolUsuario] = mapped_column(Enum(RolUsuario), default=RolUsuario.cliente)

    def __repr__(self) -> str:
        return f"<Usuario {self.email} ({self.rol.value})>"
```

✅ **Mini-verificación:** desde `backend/`, ejecuta:

```
uv run python -c "from app.models.usuario import RolUsuario, Usuario; print([m.name for m in RolUsuario]); print([c.name for c in Usuario.__table__.columns])"
```

Debe imprimir `['cliente', 'admin']` y `['id', 'email', 'hashed_password', 'rol']`
— los nombres EXACTOS del enum del contrato (ábrela y compara con el `enum:
[cliente, admin]` de `UsuarioPublico`) y las cuatro columnas del diccionario
de datos, ni una más.

---

## Paso 4 — `schemas/usuario.py`: el contrato, implementado

🧠 **El desarrollador piensa:** *igual que en la guía 4: abro
`contrato_api.yaml` 0.2.0 y escribo sus schemas en Pydantic — nada más
(D-15). `RegistroCreate` trae la regla de contraseña como validación
declarativa: `EmailStr` (que funciona porque `email-validator` viene dentro
de `fastapi[standard]`) y `min_length=8` — RN-05 hecha firma: el 422 nace
sin escribir un solo `if`, y la regla vive donde el framework y el lector la
buscan. ¿Y la composición obligatoria (mayúscula, número, símbolo)? NO
existe, a propósito: la recomendación actual privilegia la longitud sobre la
complejidad — las reglas de composición producen claves predecibles
("Clave2026!") y frustran más de lo que frenan. Fíjate lo que NO hay en
ningún schema: `hashed_password`. El contrato no lo expone y Pydantic filtra
por omisión — el hash se calcula y se guarda en el servidor, y ninguna
respuesta lo incluye, ni por error (RN-07). Es la misma lección de `activo`
en la guía 4, ahora con la consecuencia más seria del sistema.*

Crea **`backend/app/schemas/usuario.py`**:

```python
"""Schemas Pydantic de cuentas — espejan docs/04_arquitectura/contrato_api.yaml 0.2.0.

El contrato se aprobó ANTES que este código (API-first, ADR-007): estos
schemas lo implementan, no lo inventan. Ningún schema incluye el campo
hashed_password: el hash jamás cruza la frontera (RN-07).
"""

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.usuario import RolUsuario


class RegistroCreate(BaseModel):
    """Lo que envía el formulario de registro (AUTH-01)."""

    email: EmailStr
    password: str = Field(min_length=8)  # RN-05: mínimo 8, SIN composición obligatoria (D-25)


class UsuarioPublico(BaseModel):
    """La cuenta tal como la ve el mundo: id, email y rol (AUTH-01, AUTH-02)."""

    model_config = ConfigDict(from_attributes=True)  # mapear desde el ORM

    id: int
    email: EmailStr
    rol: RolUsuario


class Token(BaseModel):
    """El JWT que abre los endpoints protegidos (AUTH-02)."""

    access_token: str
    token_type: str = "bearer"
```

✅ **Mini-verificación:** desde `backend/`, ejecuta:

```
uv run python -c "from app.schemas.usuario import UsuarioPublico, RegistroCreate; print(UsuarioPublico.model_json_schema()['required']); print(RegistroCreate.model_json_schema()['required'])"
```

Debe imprimir `['id', 'email', 'rol']` y `['email', 'password']` — compáralos
con las listas `required` de `UsuarioPublico` y `RegistroCreate` en
`contrato_api.yaml`: iguales, campo por campo. Y `hashed_password` no
aparece en ninguna lista de ningún schema: el hash no tiene schema porque no
tiene frontera (RN-07).

---

## Paso 5 — `repositories/usuario.py`: la puerta única a `usuarios`

🧠 **El desarrollador piensa:** *el almacén D2 del diseño hecho clase, igual
que `ProductoRepository` en la guía 4: sesión inyectada, `select`
parameterizado (inyección SQL imposible por construcción), cero reglas de
negocio. Tres consultas bastan: `por_id` (las dependencias de seguridad del
paso siguiente buscan a la dueña del token por su `sub`), `por_email` (la
clave del upsert y del login) y `crear` (que commitea como el CRUD del
tutorial oficial: la transacción de "nacer una cuenta" se cierra aquí, en la
capa que habla con la base). El servicio decidirá qué significan; el
repositorio solo ejecuta.*

Crea **`backend/app/repositories/usuario.py`**:

```python
"""Acceso a datos de Usuario: select parameterizado, sesión inyectada.

Única capa (con models/ y database.py) que toca SQLAlchemy — regla de
dependencia de docs/04_arquitectura/ §4. Jamás strings SQL concatenadas.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.usuario import RolUsuario, Usuario


class UsuarioRepository:
    """Repositorio del agregado Usuario con la sesión inyectada."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def por_id(self, usuario_id: int) -> Usuario | None:
        """Una cuenta por id, o None — lo usan las dependencias de seguridad."""
        return self.db.scalar(select(Usuario).where(Usuario.id == usuario_id))

    def por_email(self, email: str) -> Usuario | None:
        """Una cuenta por email, o None — la clave natural del login y del upsert."""
        return self.db.scalar(select(Usuario).where(Usuario.email == email))

    def crear(self, email: str, hashed_password: str, rol: RolUsuario) -> Usuario:
        """Inserta la cuenta y cierra su transacción (patrón del CRUD oficial)."""
        usuario = Usuario(email=email, hashed_password=hashed_password, rol=rol)
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)  # recarga el id asignado por la base
        return usuario
```

✅ **Mini-verificación:** desde `backend/`, ejecuta:

```
uv run python -c "from app.database import SessionLocal; from app.repositories.usuario import UsuarioRepository; repo = UsuarioRepository(SessionLocal()); print(type(repo).__name__)"
```

Debe imprimir `UsuarioRepository` — la capa importa y se construye con la
sesión inyectada. (La tabla `usuarios` todavía no existe en tu base: la crea
el `create_all` del seed en el paso 10 — por eso esta verificación no
consulta, solo construye. Consultar de verdad llega con datos de verdad.)

---

## Paso 6 — `app/security.py`: hash, token y las dos dependencias

🧠 **El desarrollador piensa:** *este módulo es transversal — lo usan los
routers y los servicios, así que vive en la raíz de `app/`, fuera de las
cuatro capas (como `database.py`). Cuatro piezas. **El hash:**
`PasswordHash.recommended()` de pwdlib es Argon2 con parámetros revisados —
salt automática, formato `$argon2id$...`, lento a propósito (cada verificación
cuesta; romperlo por fuerza bruta cuesta millones de veces más). El helper
`verify_password` respeta el orden de pwdlib: **la contraseña plana PRIMERO,
el hash después** — invertirlos rompe TODOS los logins con un `False`
sistemático y el síntoma engañoso de "el seed está mal". **El token:**
`create_access_token` construye el payload con `sub` como string del id
(la convención JWT que el tutorial pide), el claim `rol` leído de
`usuario.rol` SIN condición alguna — cualquier token emitido lleva el rol
desde el primero (AUTH-03, ADR-011) —, `exp` timezone-aware a `token_dias`
(7 días, D-20) e `iat`; PyJWT convierte los datetimes a enteros UNIX al
firmar HS256. **La dependencia de sesión:** `OAuth2PasswordBearer` apuntando
al login hace que `/docs` muestre el botón Authorize — y `get_current_user`
decodifica con la lista EXPLÍCITA de algoritmos (`algorithms=["HS256"]`,
jamás confiar en el `alg` que el propio token declara), captura toda la
jerarquía de errores de token con `InvalidTokenError` (que incluye la
expiración) y responde SIEMPRE el 401 genérico con el header
`WWW-Authenticate: Bearer` — sin pistas de si el problema fue la firma, la
expiración o el usuario borrado. **La dependencia de rol:**
`get_current_admin` se cuelga de la anterior y valida el rol EN EL SERVIDOR:
token válido sin rol admin → 403. El cliente jamás decide roles.*

Crea **`backend/app/security.py`**:

```python
"""Seguridad transversal: hash Argon2, JWT HS256 y dependencias de sesión/rol.

Módulo transversal (como database.py): lo consumen routers y servicios.
El secreto vive en Settings (.env) y jamás se escribe en código.
"""

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_session
from app.models.usuario import RolUsuario, Usuario
from app.repositories.usuario import UsuarioRepository

password_hash = PasswordHash.recommended()  # Argon2 con parámetros por defecto

# Apunta al login: /docs mostrará el botón Authorize (form OAuth2).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def verify_password(plain: str, hashed: str) -> bool:
    # OJO al orden de pwdlib: la contraseña plana PRIMERO, el hash después.
    return password_hash.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def create_access_token(usuario: Usuario) -> str:
    """Firma el JWT: sub (string del id), rol, exp e iat — HS256."""
    expira = datetime.now(timezone.utc) + timedelta(days=settings.token_dias)
    payload = {
        "sub": str(usuario.id),          # string único (convención del tutorial)
        "rol": usuario.rol.value,        # SIN condición: el rol viaja desde el
                                         # primer token (AUTH-03, ADR-011)
        "exp": expira,                   # 7 días, timezone-aware (D-20)
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_session),
) -> Usuario:
    """Dependencia: la cuenta que vive dentro del token, o 401 genérico."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales incorrectas",  # 401 genérico (D-26, RN-06)
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Lista EXPLÍPITA de algoritmos: jamás confiar en el alg del token.
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:  # base de la jerarquía: incluye la expiración
        raise credentials_exception
    usuario = UsuarioRepository(db).por_id(int(user_id))
    if usuario is None:
        raise credentials_exception
    return usuario


def get_current_admin(
    current: Usuario = Depends(get_current_user),
) -> Usuario:
    """Dependencia: la sesión actual debe tener rol admin — o 403."""
    if current.rol != RolUsuario.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requiere rol admin",  # el detail del 403 del contrato
        )
    return current
```

✅ **Mini-verificación:** desde `backend/`, ejecuta:

```
uv run python -c "from app.security import get_password_hash, verify_password; h = get_password_hash('una-clave-larga'); print(h[:9], verify_password('una-clave-larga', h), verify_password('otra-clave', h))"
```

Debe imprimir `$argon2id True False` — tres cosas a la vez: el hash produce
el formato Argon2 (con salt distinta en cada corrida), la verificación
correcta pasa, y la incorrecta falla. Si algún día inviertes el orden de
`verify_password`, este mismo comando imprimirá `False` para TODO —
ensayarlo hoy es la mejor vacuna contra el error número 1 del final.

---

## Paso 7 — `services/cuentas.py`: la señal de duplicado y el 401 genérico

🧠 **El desarrollador piensa:** *dos casos de uso, dos decisiones de
seguridad que NO son de HTTP. **Registrar:** el servicio devuelve la cuenta
nueva, o `None` como señal de "ese email ya existe" — traducir esa señal al
409 con el copy del contrato es trabajo del router (que sí conoce HTTP).
Registrar devuelve el 409 CLARO ("Ese email ya tiene cuenta, inicia sesión",
D-26): saber si un email existe no le sirve a quien se está registrando —
el sistema se lo dice —, pero sí a quien está tanteando cuentas ajenas.
**Autenticar:** aquí vive la asimetría anti-enumeración completa. El login
responde SIEMPRE el mismo 401 genérico ("Credenciales incorrectas"),
cualquiera sea la causa… y además tarda lo mismo diga lo que diga: cuando el
email NO existe, verificamos la contraseña contra un **hash dummy** — un
hash de una clave inventada, calculado al importar el módulo. Sin ese
trabajo inútil deliberado, "email inexistente" respondería en milisegundos
y "email con cuenta" tardaría el costo real del Argon2: midiendo tiempos,
un atacante enumeraría cuentas sin leer ni una respuesta. Con él, ambos
caminos pagan el mismo Argon2 y la respuesta no cuenta nada (RN-06).*

Crea **`backend/app/services/cuentas.py`**:

```python
"""Casos de uso de cuentas: registrar y autenticar. El service NO conoce HTTP.

Autenticar devuelve None tanto si el email no existe como si la clave no
calza — y en el primer caso igual verifica contra un hash dummy para que
ambos caminos tarden lo mismo (anti-enumeración por tiempo, RN-06).
"""

from pydantic import EmailStr

from app.models.usuario import RolUsuario, Usuario
from app.repositories.usuario import UsuarioRepository
from app.schemas.usuario import RegistroCreate
from app.security import get_password_hash, verify_password

# Hash de una clave inventada, calculado una sola vez al importar: contra
# él se "verifica" cuando el email no existe — el login no deja medir qué
# emails tienen cuenta por tiempo de respuesta (patrón del tutorial oficial).
DUMMY_HASH = get_password_hash("no-es-una-clave-de-nadie")


class CuentasService:
    """Orquesta el registro y el login de cuentas."""

    def __init__(self, repo: UsuarioRepository) -> None:
        self.repo = repo

    def registrar(self, datos: RegistroCreate) -> Usuario | None:
        """Crea la cuenta (rol cliente, RF-08) o None si el email ya existe.

        El None es una SEÑAL: el router la traduce al 409 con el copy
        locked del contrato (D-26). La clave se hashea aquí, una sola vez,
        y jamás sale del servidor (RN-07).
        """
        if self.repo.por_email(datos.email) is not None:
            return None  # el router decide el 409
        return self.repo.crear(
            email=datos.email,
            hashed_password=get_password_hash(datos.password),
            rol=RolUsuario.cliente,
        )

    def autenticar(self, email: EmailStr, password: str) -> Usuario | None:
        """La cuenta si las credenciales calzan, o None — siempre igual de lento."""
        usuario = self.repo.por_email(email)
        if usuario is None:
            verify_password(password, DUMMY_HASH)  # trabajo inútil deliberado
            return None
        if not verify_password(password, usuario.hashed_password):
            return None
        return usuario
```

✅ **Mini-verificación:** desde `backend/`, ejecuta:

```
uv run python -c "from app.services.cuentas import DUMMY_HASH; print(DUMMY_HASH[:9])"
```

Debe imprimir `$argon2id` — el hash dummy existe y es un Argon2 de verdad:
el login de un email inexistente pagará el mismo costo de verificación que
el de una cuenta real. (El comportamiento completo, con cuentas sembradas,
se prueba en el paso 11.)

---

## Paso 8 — Los routers: registro 201, login OAuth2, perfil y `/api/admin/estado`

🧠 **El desarrollador piensa:** *la frontera HTTP, y hoy con una novedad: un
endpoint que RECIBE algo que no es JSON. **El login usa el formulario OAuth2
del tutorial** (`OAuth2PasswordRequestForm`): el body viaja
`application/x-www-form-urlencoded` y el campo se llama `username` aunque
transporte el email — el propio contrato lo documenta. ¿Por qué esta forma y
no un JSON uniforme? Porque `OAuth2PasswordBearer(tokenUrl="api/auth/login")`
+ form OAuth2 hacen que `/docs` muestre el botón **Authorize**: pegas las
credenciales del seed una vez y pruebas `/api/auth/perfil` y
`/api/admin/estado` con el token puesto, desde el propio panel — la
comparación contrato ↔ `/docs` del cierre de fase se hace sola. **El
registro, en cambio, SÍ es JSON** (`RegistroCreate`): es un endpoint de
negocio propio, no un flujo OAuth2. Y la lección de G-01-4, ahora con tres
códigos: cada `HTTPException` lanzada a mano NO aparece en OpenAPI si no se
declara — todos los endpoints declaran sus `responses` 401/403/409 en la
firma, para que `/docs` liste exactamente lo que el contrato promete (sin
declaración, la fila contrato ↔ `/docs` acusaría un desvío que no existe).*

Crea **`backend/app/routers/auth.py`**:

```python
"""Endpoints de cuentas: registro, login y perfil — implementan contrato_api.yaml 0.2.0.

El login usa el form OAuth2 del tutorial oficial (username transporta el
email): habilita el botón Authorize de /docs. Los responses 401/409 se
declaran en la firma para que /docs los documente (lección G-01-4).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_session
from app.models.usuario import Usuario
from app.repositories.usuario import UsuarioRepository
from app.schemas.producto import Error  # el cuerpo de error vive en schemas/producto desde la guía 4
from app.schemas.usuario import RegistroCreate, Token, UsuarioPublico
from app.security import create_access_token, get_current_user
from app.services.cuentas import CuentasService

router = APIRouter(tags=["Autenticación"])


@router.post(
    "/registro",
    response_model=UsuarioPublico,
    status_code=status.HTTP_201_CREATED,  # creado: el contrato dice 201, no 200
    responses={
        409: {"description": "El email ya tiene cuenta", "model": Error},
        422: {
            "description": "Cuerpo mal formado (email sin formato, contraseña menor a 8)",
            "model": Error,
        },
    },
)
def registrar(
    datos: RegistroCreate,
    db: Session = Depends(get_session),
) -> UsuarioPublico:
    """POST /api/auth/registro — crea una cuenta de clienta (AUTH-01)."""
    servicio = CuentasService(UsuarioRepository(db))
    usuario = servicio.registrar(datos)
    if usuario is None:
        # 409 CLARO, con el copy locked del contrato (D-26): quien se
        # registra necesita saber que ya tiene cuenta.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ese email ya tiene cuenta, inicia sesión",
        )
    return usuario


@router.post(
    "/login",
    response_model=Token,
    responses={
        401: {
            "description": "Email o contraseña incorrectos — genérico deliberado (D-26)",
            "model": Error,
        }
    },
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_session),
) -> Token:
    """POST /api/auth/login — inicia sesión y devuelve el token (AUTH-02).

    El form OAuth2 llama `username` al campo que transporta el email
    (el contrato lo documenta): así el botón Authorize de /docs funciona.
    """
    servicio = CuentasService(UsuarioRepository(db))
    usuario = servicio.autenticar(form_data.username, form_data.password)
    if usuario is None:
        # 401 GENÉRICO: sin revelar si el email existe (RN-06, D-26).
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(usuario))


@router.get(
    "/perfil",
    response_model=UsuarioPublico,
    responses={
        401: {
            "description": "Sin sesión, o token inválido/expirado",
            "model": Error,
        }
    },
)
def perfil(actual: Usuario = Depends(get_current_user)) -> UsuarioPublico:
    """GET /api/auth/perfil — la cuenta que vive dentro del token (AUTH-02)."""
    return actual
```

Y crea **`backend/app/routers/admin.py`**:

```python
"""Endpoints de administración protegidos por rol (AUTH-03, D-33).

El endpoint demo /api/admin/estado reusa el catálogo existente: cero SQL
nuevo, toda la lección está en la dependencia get_current_admin.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_session
from app.models.usuario import Usuario
from app.repositories.producto import ProductoRepository
from app.schemas.producto import Error  # el cuerpo de error vive en schemas/producto desde la guía 4
from app.security import get_current_admin
from app.services.catalogo import CatalogService

router = APIRouter(tags=["Administración"])


@router.get(
    "/estado",
    responses={
        401: {
            "description": "Sin sesión, o token inválido/expirado",
            "model": Error,
        },
        403: {
            "description": "Con sesión, pero sin rol admin",
            "model": Error,
        },
    },
)
def estado(
    actual: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_session),
) -> dict[str, int]:
    """GET /api/admin/estado — conteos triviales del catálogo (D-33).

    `actual` no se usa: la dependencia está por lo que VALIDA, no por lo
    que aporta. El 403 lo produce get_current_admin EN EL SERVIDOR.
    """
    aromas = CatalogService(ProductoRepository(db)).listar()
    return {
        "productos": len(aromas),
        "familias": len({aroma.familia for aroma in aromas}),
    }
```

Registra ambos en **`backend/app/main.py`** — el import junto a los
existentes:

```python
from app.routers import admin, auth, productos, salud
```

…y los registros junto al de productos, al final del archivo:

```python
app.include_router(salud.router, prefix="/api/salud")
app.include_router(productos.router, prefix="/api/productos")
app.include_router(auth.router, prefix="/api/auth")
app.include_router(admin.router, prefix="/api/admin")
```

✅ **Mini-verificación:** enciende la API (`uv run fastapi dev app/main.py`
desde `backend/`) y abre **http://localhost:8000/docs**:

1. Aparecen los tags nuevos **Autenticación** y **Administración**, con
   `POST /api/auth/registro`, `POST /api/auth/login`, `GET /api/auth/perfil`
   y `GET /api/admin/estado` — los 4 paths del contrato 0.2.0.
2. Despliega `POST /api/auth/registro`: lista **201**, **409** y **422** con
   sus descripciones y el schema `Error`. Sin el `responses` de la firma, el
   409 no estaría — esa es la lección G-01-4 por segunda vez.
3. `GET /api/admin/estado` lista **200**, **401** y **403**; y el endpoint
   muestra el candado 🔒 con `bearerAuth (JWT)`: el botón **Authorize** ya
   existe — lo usamos en el paso 11.

---

## Paso 9 — `main.py`: CORS crece con la API (GET + POST)

🧠 **El desarrollador piensa:** *la guía 1 fijó `allow_methods=["GET"]` — y
era lo correcto: la API de la fase 1 era pública y de solo lectura. Hoy
llegan el registro y el login, y el primer `POST` cross-origin muerde el
mismo día si el CORS no creció primero: el navegador manda el preflight
`OPTIONS`, el middleware rechaza el método y la consuela muestra un error
CORS que NADA tiene que ver con tu código de cuentas. ¿Por qué no lo viste
venir? Porque en desarrollo el proxy de Vite hace que las llamadas sean
same-origin y el CORS ni actúa — el olvido es invisible hasta que la SPA
llama a la API desde otro origen. La cura es una línea: `POST` se suma a la
lista EXPLÍCITA (jamás el comodín `["*"]` de métodos — la misma disciplina
de orígenes de ADR-002). `allow_headers=["*"]` ya cubre `Authorization`,
que el Bearer del paso 11 necesita. Narrarlo así: **el CORS crece con la
API** — cada verbo nuevo que la SPA necesite cruzar origen, se declara.*

En **`backend/app/main.py`**, actualiza el middleware:

```python
# CORS con orígenes y métodos EXPLÍCITOS desde settings (ADR-002). La fase
# 1 solo leía (GET); la etapa 2 trae los primeros POST (registro y login):
# CORS crece con la API, siempre lista explícita — jamás comodín.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],  # incluye Authorization: Bearer ...
)
```

✅ **Mini-verificación (el preflight, provocado a propósito):** con la API
encendida, desde `backend/` ejecuta:

```
uv run python -c "import httpx; r = httpx.request('OPTIONS', 'http://localhost:8000/api/auth/login', headers={'Origin': 'http://localhost:5173', 'Access-Control-Request-Method': 'POST'}); print(r.status_code)"
```

Debe imprimir `200` — el preflight que el navegador mandará antes del
primer POST acepta el método. Con `allow_methods=["GET"]` habría respondido
`400 Disallowed CORS method`: puedes comprobarlo comentando el `"POST"` un
segundo. Ese 400 en la consola del navegador es exactamente el error que
este paso evita (la SPA real lo sufre en la guía 6).

---

## Paso 10 — El seed de cuentas: upsert por email

🧠 **El desarrollador piensa:** *el mismo mecanismo del seed de productos,
cambiando la clave: **upsert por email** — consultar por email; si no
existe, crear e imprimir `[+]`; si existe, RESTAURAR contraseña y rol al
valor del `.env` e imprimir `[=]`. Re-ejecutar el seed REINICIA las
credenciales demo: si una prueba cambió la clave del admin, re-siembras y
la clave vuelve — "cada alumno reinicia su admin sin miedo" (D-23). Es una
feature deliberada, la misma restauración canónica del stock en la guía 3.
Dos detalles: la clave se hashea en el seed (nunca se guarda plana), y el
upsert también fija el `rol` del existente — el claim de rol sale del
usuario en cada emisión, y re-sembrar deja la cuenta EXACTAMENTE como el
`.env` dice (ADR-011). Argon2 es lento a propósito: hashear dos claves toma
fracciones de segundo — imperceptible aquí, carísimo para quien quiera
fuerza bruta. ¿Orden? Usuarios DESPUÉS de productos: hoy no hay llaves
entre ellas, pero la costumbre se toma ahora (la etapa 3 conecta pedidos
con productos y clientas).*

En **`backend/app/seed.py`**, agrega los imports (junto a los existentes):

```python
from app.config import settings
from app.models.usuario import RolUsuario, Usuario
from app.security import get_password_hash
```

Agrega la función después de `upsert_producto`:

```python
def upsert_usuario(sesion: Session, email: str, password: str, rol: RolUsuario) -> str:
    """Crea la cuenta ("[+]") o restaura credenciales y rol ("[=]").

    Re-ejecutar el seed REINICIA la contraseña demo al valor del .env —
    cada alumno reinicia su admin sin miedo (D-23). El rol también se
    fija: el claim sale del usuario en cada emisión (ADR-011).
    """
    existente = sesion.scalar(select(Usuario).where(Usuario.email == email))
    hash_nuevo = get_password_hash(password)
    if existente is None:
        sesion.add(Usuario(email=email, hashed_password=hash_nuevo, rol=rol))
        return "[+]"
    existente.hashed_password = hash_nuevo  # restaura la contraseña demo
    existente.rol = rol                     # y fija el rol que el .env dice
    return "[=]"
```

Y extiende `main()` — el bloque de usuarios DESPUÉS del ciclo de productos,
antes del `commit`:

```python
def main() -> None:
    # El schema y el seed existen ANTES de cualquier verificación de
    # endpoints: la creación de tablas vive aquí, no en main.py.
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as sesion:
        marcas = []
        for datos in PRODUCTOS_DEMO:
            marca = upsert_producto(sesion, datos)
            marcas.append(marca)
            print(f"{marca} {datos['sku']} — {datos['nombre']}")
        # Cuentas demo DESPUÉS de productos (la etapa 3 conectará pedidos
        # con ambos). Credenciales desde el .env: jamás en el código
        # (D-23, D-24).
        cuentas_demo = [
            (settings.admin_email, settings.admin_password, RolUsuario.admin),
            (settings.cliente_email, settings.cliente_password, RolUsuario.cliente),
        ]
        for email, password, rol in cuentas_demo:
            marca = upsert_usuario(sesion, email, password, rol)
            marcas.append(marca)
            print(f"{marca} {email} ({rol.value})")
        sesion.commit()
    print(
        f"Seed listo: {marcas.count('[+]')} creados [+], "
        f"{marcas.count('[=]')} actualizados [=] "
        f"({len(PRODUCTOS_DEMO)} productos + {len(cuentas_demo)} cuentas)"
    )


if __name__ == "__main__":
    main()
```

✅ **Mini-verificación (siembra e idempotencia):** desde `backend/`, ejecuta
`uv run python -m app.seed`. La primera corrida imprime los doce `[=]` de
los productos (ya existían de la guía 3) MÁS dos líneas nuevas:

```
[+] admin@maura.cl (admin)
[+] clienta@maura.cl (cliente)
Seed listo: 2 creados [+], 12 actualizados [=] (12 productos + 2 cuentas)
```

(con TUS emails del `.env`). Re-ejecuta el MISMO comando: las dos líneas
`[+]` se vuelven `[=]` — las cuentas existían y sus credenciales se
RESTAURARON al valor del `.env`. Pruébalo de verdad: cambia la clave del
admin en tu `.env`, re-siembra y haz login con la clave nueva — funciona,
porque el seed la restauró. Eso es la feature, no un descuido.

---

## Paso 11 — La prueba de fuego: login, token decodificado y 200 vs 403

Con la API encendida y el seed corrido. Los tres golpes de la etapa, en
orden:

✅ **Mini-verificación (login de ambos roles, form encodeado):** desde
`backend/`, ejecuta (todo en una línea — lee TUS credenciales del propio
`Settings`, así no hay secretos en la consola ni en la guía):

```
uv run python -c "import httpx; from app.config import settings; r = httpx.post('http://localhost:8000/api/auth/login', data={'username': settings.cliente_email, 'password': settings.cliente_password}); print(r.status_code, r.json()['token_type'])"
```

Debe imprimir `200 bearer`. Cambia `cliente_email`/`cliente_password` por
`admin_email`/`admin_password`: también `200 bearer`. Ese `data={...}` de
httpx es EXACTAMENTE el form `application/x-www-form-urlencoded` del
contrato — el campo `username` transporta el email. Y una clave mala
(cambia `settings.cliente_password` por `'mala-clave'`): `401` con
`{'detail': 'Credenciales incorrectas'}` — el genérico, sin pistas.

✅ **Mini-verificación (el token, decodificado OFFLINE):** los claims del
token se leen sin enviarlo a NINGÚN sitio — ni a jwt.io ni a nadie: un
token pegado en una página web es un token compartido con esa página.

```
uv run python -c "import httpx, jwt; from app.config import settings; token = httpx.post('http://localhost:8000/api/auth/login', data={'username': settings.cliente_email, 'password': settings.cliente_password}).json()['access_token']; print(jwt.decode(token, options={'verify_signature': False}))"
```

Debe imprimir un diccionario con los cuatro claims — algo como
`{'sub': '2', 'rol': 'cliente', 'exp': 1791313xx, 'iat': 1790709xxx}`.
Tres lecturas: `sub` es el id como STRING (la convención del tutorial), el
`rol` viaja desde el primer token (AUTH-03, ADR-011 — ni un login quedó
fuera), y `exp` menos `iat` da **604800 segundos = exactamente 7 días**
(D-20). (Para la clienta `sub` es `'2'` en una base recién sembrada: el
admin se crea primero. Si quieres verlo bonito y SIN compartir tu token,
jwt.io existe — pero con token de sandbox y sabiendo lo que estás haciendo;
el default de esta guía es offline.)

✅ **Mini-verificación (AUTH-03: 200 vs 403):** con el token de CADA rol,
llama al endpoint protegido. El admin:

```
uv run python -c "import httpx; from app.config import settings; token = httpx.post('http://localhost:8000/api/auth/login', data={'username': settings.admin_email, 'password': settings.admin_password}).json()['access_token']; r = httpx.get('http://localhost:8000/api/admin/estado', headers={'Authorization': f'Bearer {token}'}); print(r.status_code, r.json())"
```

Debe imprimir `200 {'productos': 12, 'familias': 4}` (los conteos triviales
de D-33 sobre TU catálogo). Ahora cambia las cuatro variables por las de la
clienta: `403 {'detail': 'Requiere rol admin'}` — el token de la clienta es
PERFECTAMENTE válido (pasa `get_current_user`), pero su claim de rol no
alcanza en `get_current_admin`. Un 401 dice "no te conozco"; un 403 dice
"te conozco, y no puedes pasar". El mismo par de golpes, sin consola:
botón **Authorize** en `/docs`, credenciales del admin, `Try it out` en
`GET /api/admin/estado` → 200; Authorize de nuevo con la clienta → 403.
Ese botón existe gracias al form OAuth2 del paso 8.

---

## ❌ El error que este archivo evita

**1. El orden de la verificación de hash.** pwdlib es
`verify(password, hash)` — la contraseña plana PRIMERO:

```python
# ❌ False sistemático para TODO el mundo: el login nunca funciona
password_hash.verify(guardado, recibido)  # hash primero: orden invertido

# ✅ contraseña PRIMERO, hash después
password_hash.verify(recibido, guardado)
```

El síntoma es el más engañoso de la etapa: TODOS los logins fallan con 401
pese a un seed impecable — y uno culpa al seed, al `.env`, al token…
El helper `verify_password(plain, hashed)` del paso 6 existe para que el
orden se escriba una vez y bien.

**2. El enum del rol con nombres que no son los del contrato.**

```python
# ❌ La BD guardaría "CLIENTE": SQLAlchemy persiste los NOMBRES
class RolUsuario(str, enum.Enum):
    CLIENTE = "cliente"

# ✅ nombre == valor: la BD guarda el slug del contrato
class RolUsuario(str, enum.Enum):
    cliente = "cliente"
```

Es la segunda vuelta del gotcha de `FamiliaAromatica` (guía 3): la versión
❌ compila, siembra y parece funcionar — hasta que el claim `rol` viaja como
`RolUsuario.CLIENTE`… y el enum `[cliente, admin]` del contrato diverge.

**3. El 422 de contraseña corta en el login.** El `min_length=8` vive SOLO
en `RegistroCreate` (RN-05). El form OAuth2 del login NO valida esquema de
contraseña: una clave de 7 caracteres en el login no es "dato mal formado"
— es una credencial que no calza, y responde **401** genérico como cualquier
otra. Si el login respondiera 422 por clave corta, estaría contando
gratuitamente que ese email SÍ existe y su clave era corta: fuga + error de
semántica en un solo golpe.

**4. Mezclar 401/403/409 (y el 422).** La tabla única — literalmente la del
contrato, ahora en uso:

| Código | Quién lo produce | Cuándo |
|---|---|---|
| **422** | Pydantic (automático, la firma) | Dato mal formado: email sin formato, contraseña < 8 en el registro |
| **401** | `security.py` y el router del login | Credenciales incorrectas, token ausente/inválido/expirado — SIEMPRE genérico (RN-06) |
| **403** | `get_current_admin` | Token VÁLIDO, pero sin el rol que el endpoint exige (D-33) |
| **409** | El router del registro (señal del service) | Email ya registrado — claro a propósito (D-26) |

401 es "no te conozco"; 403 es "te conozco y no puedes"; 409 es "eso ya
existe"; 422 es "eso no tiene ni forma de ser". Cuatro frases, cuatro
códigos — y el contrato ya los tenía escritos.

---

## ✅ Verificación de la guía 5

Desde `backend/`, con la API encendida y el seed corrido:

1. `uv run python -m app.seed` → dos `[=]` de cuentas (tras la primera
   corrida con `[+]`); re-ejecutar restaura credenciales — idempotencia de
   cuentas (D-23, D-24).
2. **http://localhost:8000/docs** lista los 4 paths nuevos con SUS códigos:
   registro 201/409/422, login 200/401, perfil 200/401, admin/estado
   200/401/403 — y el botón Authorize (candado bearerAuth) existe.
3. Registro en `/docs` con un email nuevo → **201** con
   `{"id": ..., "email": ..., "rol": "cliente"}` — SIN `hashed_password`
   en la respuesta (RN-07). Repite el MISMO email → **409** con
   `"Ese email ya tiene cuenta, inicia sesión"`.
4. Registro con contraseña de 7 caracteres → **422** automático (nadie
   escribió ese `if`: vive en la firma, RN-05).
5. Login de la clienta y del admin → `200` con token; decodificado offline,
   los claims `sub`/`rol`/`exp`/`iat` con `exp − iat = 604800` (7 días,
   D-20).
6. `/api/admin/estado` con el token del admin → `200` con los conteos; con
   el de la clienta → `403 Requiere rol admin` (AUTH-03, D-33).
7. El preflight del paso 9 responde `200` — el primer POST cross-origin de
   la guía 6 no morirá por CORS.

(La comparación completa contrato ↔ `/docs` — los 8 paths, tags y schemas —
es la Gran verificación final de la guía 8, como en la fase 1.)

## 📝 Punto de control (respóndelas sin mirar la guía)

1. ¿Por qué el login responde SIEMPRE el mismo 401 genérico mientras el
   registro sí dice con claridad que el email ya existe? Nombra el ataque
   que la asimetría evita y el truco extra que hace que ambos caminos
   tarden lo mismo.
2. ¿Qué claims lleva el token y quién decide el rol — el cliente o el
   servidor? Si a un usuario le cambian el rol hoy, ¿qué pasa con los
   tokens que ya tiene emitidos, y por cuánto tiempo?
3. ¿Por qué el login usa un formulario OAuth2 (con un campo llamado
   `username`) en vez de JSON como el registro? ¿Qué habilita exactamente
   en `/docs`, y por qué ese botón importa para la verificación de fase?

## Lo que acabas de aprender

- Hash Argon2 con pwdlib: verificación lenta a propósito, salt automática y el orden `verify(password, hash)` que no se negocia
- JWT con PyJWT: claims `sub`/`rol`/`exp`/`iat`, firma HS256, decodificación con lista explícita de algoritmos y `exp` timezone-aware a 7 días (ADR-009, D-20)
- El claim de rol construido SIN condición: cualquier token emitido lleva el rol (AUTH-03, ADR-011)
- El form OAuth2 del login (`username` transporta el email): el precio pequeño que compra el botón Authorize de `/docs`
- Dependencias de seguridad: `get_current_user` (401 genérico con `WWW-Authenticate: Bearer`) y `get_current_admin` (403) — el servidor decide, el cliente jamás
- `UsuarioPublico` sin hash en NINGÚN endpoint: Pydantic filtra por omisión, la frontera es el schema (RN-07, Pitfall de `activo` en segunda vuelta)
- La asimetría anti-enumeración: 409 claro en registro, 401 genérico + hash dummy en login (RN-06, D-26)
- `responses` declaradas en la firma para que `/docs` documente 401/403/409 — la lección G-01-4, ahora con tres códigos
- CORS que crece con la API: `["GET", "POST"]` explícito antes del primer POST cross-origin
- Seed de cuentas por upsert de email con credenciales del `.env`: restauración como feature y roles fijados en cada re-siembra (D-23, D-24)

**Siguiente:** guia-06-sesion-frontend.md — la sesión en la SPA: el store
que recuerda a la clienta entre recargas, el login y el registro, el
navbar que la saluda… y el interceptor que blinda toda la app contra el 401.
