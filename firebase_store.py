from firebase_admin import credentials, firestore, get_app, initialize_app


PORTFOLIO_DOCUMENT = 'portfolio/current'


class SnapshotConflictError(RuntimeError):
    pass


def create_firestore_client(project_id, service_account_path):
    try:
        app = get_app()
    except ValueError:
        app = initialize_app(
            credentials.Certificate(str(service_account_path)),
            {'projectId': project_id},
        )
    return firestore.client(app=app)


def read_portfolio_snapshot(db):
    document = db.document(PORTFOLIO_DOCUMENT).get()
    if not document.exists:
        return None, 0

    stored = document.to_dict() or {}
    payload = stored.get('payload')
    revision = stored.get('revision')
    if not isinstance(payload, dict) or type(revision) is not int or revision < 1:
        raise ValueError('El documento de Firebase no contiene una cartera válida.')
    return payload, revision


def write_portfolio_snapshot(db, payload, expected_revision):
    document_ref = db.document(PORTFOLIO_DOCUMENT)

    @firestore.transactional
    def commit(transaction):
        current = document_ref.get(transaction=transaction)
        stored_revision = 0
        if current.exists:
            stored_revision = (current.to_dict() or {}).get('revision')
            if type(stored_revision) is not int:
                raise ValueError('La revisión guardada en Firebase no es válida.')
        if stored_revision != expected_revision:
            raise SnapshotConflictError(
                'La cartera cambió desde la última lectura; recarga antes de guardar.'
            )

        next_revision = stored_revision + 1
        transaction.set(document_ref, {
            'payload': payload,
            'revision': next_revision,
            'updated_at': firestore.SERVER_TIMESTAMP,
        })
        return next_revision

    return commit(db.transaction())