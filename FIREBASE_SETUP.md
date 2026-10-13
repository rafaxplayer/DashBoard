# Conectar la app a Firebase

## Streamlit

1. En Firebase Console, abre la configuración del proyecto **Mis Inversiones** y copia el **ID del proyecto**. El nombre visible no sirve como `project_id`.
2. En Google Cloud Console, crea un cliente OAuth de tipo **Web application**. Añade `http://localhost:8501` a los orígenes autorizados y `http://localhost:8501/oauth2callback` a los URI de redirección.
3. Copia `.streamlit/secrets.toml.example` como `.streamlit/secrets.toml`. Completa el ID del proyecto, el correo Google permitido, el ID OAuth y el secreto OAuth. Genera un `cookie_secret` nuevo con:

   ```powershell
   .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

4. Crea una cuenta de servicio dedicada para Streamlit, asígnale el rol **Cloud Datastore User** y descarga su clave JSON. Guárdala como `.streamlit/firebase-service-account.json`. Ambos archivos locales están excluidos de Git. No compartas ni incluyas esta clave en Android.
5. Instala dependencias y ejecuta la app:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   .\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
   ```

Streamlit pide iniciar sesión con Google y solo admite el correo verificado configurado en `owner_email`. Si el documento no existe, muestra un botón para importar el JSON local una vez; no sobrescribe una cartera que ya exista en Firestore. Firestore será la base compartida y el JSON quedará como respaldo local.

Mientras la sesión está abierta, Streamlit escucha los cambios de `portfolio/current` en Firestore y actualiza la vista automáticamente (comprobación visual cada dos segundos). Los cambios guardados desde Android aparecen sin recargar manualmente la página.

Si falla la lectura de Firestore, la app muestra el JSON local con un aviso y entra en modo de solo lectura: altas, ediciones, borrados e importación quedan desactivados para no pisar cambios cloud al reconectar. El botón **Reintentar conexión con Firebase** vuelve a probar Firestore. El primer inicio de sesión Google requiere internet; el respaldo aplica cuando ya hay una sesión autenticada.

Si publicas Streamlit en un servidor, cambia `auth.redirect_uri` y los URI autorizados de Google al dominio HTTPS real.

## Documento compartido con Android

La app guarda la cartera en `portfolio/current`:

```text
{
  payload: {
    investments: [...],
    banks: [...],
    reserved_investments: [...]
  },
  revision: integer,
  updated_at: timestamp
}
```

Android debe iniciar sesión con Firebase Authentication usando Google y leer/escribir ese documento mediante transacciones. Al abrir un formulario, conserva la revisión leída; al guardar, compara esa revisión con la actual y solo escribe si coinciden, incrementando `revision` en uno. Envía `updated_at` con `FieldValue.serverTimestamp()` para cumplir las reglas. Ante una discrepancia, recarga y pide reaplicar el cambio. Así una edición abierta en Streamlit no puede borrar silenciosamente una modificación más reciente de Android, ni al revés.

Este documento es adecuado para la cartera personal actual; Firestore limita cada documento a 1 MiB. Si los datos crecen, conviene separar las inversiones en documentos individuales manteniendo el control de conflictos.

## Reglas de Firestore para Android

En Firebase Console, registra la aplicación Android con su `applicationId`, huellas SHA-1/SHA-256 y `google-services.json`; habilita Google en Firebase Authentication. Publica estas reglas reemplazando el correo por el mismo valor verificado de `owner_email`:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    function isOwner() {
      return request.auth != null
        && request.auth.token.email == 'YOUR_GOOGLE_EMAIL'
        && request.auth.token.email_verified == true;
    }

    function validPayload() {
      return request.resource.data.payload is map
        && request.resource.data.payload.keys().hasOnly([
          'investments', 'banks', 'reserved_investments'
        ])
        && request.resource.data.payload.investments is list
        && request.resource.data.payload.banks is list
        && request.resource.data.payload.reserved_investments is list
        && request.resource.data.updated_at == request.time;
    }

    match /portfolio/current {
      allow read: if isOwner();
      allow create: if isOwner()
        && request.resource.data.keys().hasOnly(['payload', 'revision', 'updated_at'])
        && validPayload()
        && request.resource.data.revision == 1;
      allow update: if isOwner()
        && request.resource.data.keys().hasOnly(['payload', 'revision', 'updated_at'])
        && validPayload()
        && request.resource.data.revision == resource.data.revision + 1;
      allow delete: if false;
    }
  }
}
```

El SDK Admin de Streamlit evita las reglas de cliente de Firestore, por eso el servidor también valida el inicio de sesión y restringe el correo autorizado. Android nunca debe contener la clave de la cuenta de servicio.