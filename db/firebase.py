import firebase_admin
from firebase_admin import credentials, firestore

# Inicialización de Firebase
cred = credentials.Certificate("db/firebase.json") 
firebase_admin.initialize_app(cred)
db = firestore.client()

def create_project(nombre_proyecto):
    """Crea un nuevo proyecto en Firestore."""
    proyecto_ref = db.collection("proyectos").document(nombre_proyecto)
    proyecto_ref.set({
        "nombre": nombre_proyecto,
        "timestamp_creacion": firestore.SERVER_TIMESTAMP
    })
    print(f"Proyecto creado: {nombre_proyecto}")

def get_project(nombre_proyecto):
    """Obtiene un proyecto de Firestore."""
    proyecto_ref = db.collection("proyectos").document(nombre_proyecto)
    proyecto = proyecto_ref.get()
    if proyecto.exists:
        return proyecto.to_dict()
    else:
        print(f"El proyecto {nombre_proyecto} no existe")
        return None

def add_contact(ws_id, phone_number, display_name):
    """Añade un contacto a un usuario en Firestore."""
    user_ref = db.collection("users").where("ws_id", "==", ws_id).limit(1).get()
    if not user_ref:
        print(f"No se encontró ningún usuario con el ws_id {ws_id}")
        return
    user_doc = user_ref[0].reference
    contact_ref = user_doc.collection("contacts").document()
    contact_ref.set({
        "nombre": display_name,
        "phone_number": phone_number
    })
    print(f"Contacto añadido para el usuario con ws_id {ws_id}: {display_name}")

def get_contact_ref(ws_id, phone_number):
    """Obtiene la referencia de un contacto."""
    user_ref = db.collection("users").where("ws_id", "==", ws_id).limit(1).get()
    if not user_ref:
        print(f"No se encontró ningún usuario con el ws_id {ws_id}")
        return None
    user_doc = user_ref[0].reference
    contact_query = (
        user_doc.collection("contacts")
        .where("phone_number", "==", phone_number)
        .limit(1)
    )
    contact_docs = contact_query.get()
    if not contact_docs:
        print(f"No se encontró ningún contacto con el número {phone_number} para el usuario con ws_id {ws_id}")
        print("Creando nuevo contacto...")
        nuevo_contacto_ref = user_doc.collection("contacts").document()
        nuevo_contacto_ref.set({
            "phone_number": phone_number
        })
        return nuevo_contacto_ref
    return contact_docs[0].reference

def add_message(ws_id, phone_number, message, is_sender):
    """Añade un mensaje a la conversación."""
    contact_ref = get_contact_ref(ws_id, phone_number)
    if not contact_ref:
        return

    user_ref = db.collection("users").where("ws_id", "==", ws_id).limit(1).get()
    if not user_ref:
        print(f"No se encontró ningún usuario con el ws_id {ws_id}")
        return
    user_doc = user_ref[0].reference

    message_ref = user_doc.collection("messages").document()
    message_ref.set({
        "contact_ref": contact_ref,
        "text": message,
        "is_sender": is_sender,
        "platform": "whatsapp",
        "timestamp": firestore.SERVER_TIMESTAMP,
    })
    print(f"Mensaje {'del usuario' if is_sender else 'del bot'} añadido para el contacto {phone_number} del usuario con ws_id {ws_id}")

def add_contact_message(ws_id, phone_number, message):
    """Añade un mensaje del bot a la conversación."""
    add_message(ws_id, phone_number, message, False)

def add_chat_message(ws_id, phone_number, message):
    """Añade un mensaje del usuario a la conversación."""
    add_message(ws_id, phone_number, message, True)

def get_conversation(ws_id, phone_number):
    """Obtiene la conversación de un usuario con un contacto específico."""
    contact_ref = get_contact_ref(ws_id, phone_number)
    if not contact_ref:
        return None

    user_ref = db.collection("users").where("ws_id", "==", ws_id).limit(1).get()
    if not user_ref:
        print(f"No se encontró ningún usuario con el ws_id {ws_id}")
        return None
    user_doc = user_ref[0].reference

    mensajes_ref = (
        user_doc.collection("messages")
        .where("contact_ref", "==", contact_ref)
        .order_by("timestamp")
    )
    return mensajes_ref.get()
