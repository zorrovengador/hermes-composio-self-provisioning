# Hermes + Composio Self-Provisioning

Assets para probar un Hermes independiente que configura su propio entorno Composio y genera OAuth para Google Workspace.

## Alcance de la prueba

1. Usar un Hermes nuevo y aislado.
2. Usar inicialmente una API key exclusiva de un proyecto Composio de prueba.
3. Crear una sesión Composio para un `user_id` estable.
4. Generar un Connect Link OAuth.
5. Verificar una conexión autorizada.
6. Opcionalmente, probar después la creación automática de un proyecto mediante Organization API Key.

## Seguridad

- No guardar API keys, OAuth codes, refresh tokens ni headers MCP en este repositorio.
- El consentimiento OAuth lo realiza el usuario en Google/Microsoft.
- Empezar con permisos de lectura y una instancia desechable.
- La Organization API Key tiene privilegios superiores a una Project API Key; no usarla en producción sin revisar el aislamiento.

## Instalación en un Hermes nuevo

Copiar esta skill en `$HERMES_HOME/skills/composio-self-provisioning/` y ejecutar:

```bash
uv pip install composio
python scripts/composio_bootstrap.py --help
```

Variables requeridas para la fase 1:

```text
COMPOSIO_API_KEY
COMPOSIO_USER_ID
```

Nunca pegues esos valores en el prompt ni los subas a GitHub.

## Fase 1: sesión y Connect Link

```bash
python scripts/composio_bootstrap.py session --toolkit gmail
```

El script muestra únicamente la URL de autorización. El usuario la abre, inicia sesión en Google y autoriza. Después se consulta el estado:

```bash
python scripts/composio_bootstrap.py status --toolkit gmail
```

## Fase 2: proyecto automático

Solo en una instancia desechable y después de validar la fase 1:

```bash
COMPOSIO_ORG_API_KEY='...' python scripts/composio_bootstrap.py create-project --name 'hermes-client-test'
```

Por seguridad, la respuesta nunca imprime la API key del proyecto. El script la guarda en el archivo secreto indicado por `--project-key-file`, con permisos 0600.

## Estado

Este repositorio es un arnés de prueba, no una capa multi-tenant completa ni un producto de producción.
