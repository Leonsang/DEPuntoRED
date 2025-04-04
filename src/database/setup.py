import os
import logging
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from .models import Base, Cliente, Venta

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

def init_database():
    """Inicializa la base de datos con las tablas y datos de prueba"""
    try:
        # Crear conexión
        engine = create_engine(os.getenv('DB_URL'))
        
        # Crear tablas
        Base.metadata.create_all(engine)
        
        # Crear sesión
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Verificar si ya hay datos
        if session.query(Cliente).count() == 0:
            # Insertar datos de prueba
            clientes = [
                Cliente(nombre='Juan', apellido='Pérez'),
                Cliente(nombre='María', apellido='Gómez'),
                Cliente(nombre='Carlos', apellido='López'),
                Cliente(nombre='Ana', apellido='Martínez'),
                Cliente(nombre='Pedro', apellido='Rodríguez')
            ]
            
            session.add_all(clientes)
            session.commit()
            
            # Obtener IDs de clientes
            cliente_ids = {c.nombre: c.id for c in clientes}
            
            # Insertar ventas
            ventas = [
                Venta(
                    cliente_id=cliente_ids['Juan'],
                    producto='Producto A',
                    fecha=datetime.now() - timedelta(days=1),
                    monto=100.50
                ),
                Venta(
                    cliente_id=cliente_ids['Juan'],
                    producto='Producto B',
                    fecha=datetime.now() - timedelta(days=1),
                    monto=200.75
                ),
                Venta(
                    cliente_id=cliente_ids['María'],
                    producto='Producto A',
                    fecha=datetime.now() - timedelta(days=1),
                    monto=150.25
                ),
                Venta(
                    cliente_id=cliente_ids['María'],
                    producto='Producto C',
                    fecha=datetime.now() - timedelta(days=1),
                    monto=300.00
                ),
                Venta(
                    cliente_id=cliente_ids['Carlos'],
                    producto='Producto B',
                    fecha=datetime.now() - timedelta(days=1),
                    monto=250.50
                ),
                Venta(
                    cliente_id=cliente_ids['Carlos'],
                    producto='Producto C',
                    fecha=datetime.now() - timedelta(days=1),
                    monto=175.25
                ),
                Venta(
                    cliente_id=cliente_ids['Ana'],
                    producto='Producto A',
                    fecha=datetime.now() - timedelta(days=1),
                    monto=125.75
                ),
                Venta(
                    cliente_id=cliente_ids['Ana'],
                    producto='Producto B',
                    fecha=datetime.now() - timedelta(days=1),
                    monto=225.00
                ),
                Venta(
                    cliente_id=cliente_ids['Pedro'],
                    producto='Producto C',
                    fecha=datetime.now() - timedelta(days=1),
                    monto=275.50
                )
            ]
            
            session.add_all(ventas)
            session.commit()
            
            logger.info("Datos de prueba insertados exitosamente")
        
        session.close()
        logger.info("Base de datos inicializada correctamente")
        
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {str(e)}")
        raise

def get_session():
    """Retorna una sesión de base de datos"""
    engine = create_engine(os.getenv('DB_URL'))
    Session = sessionmaker(bind=engine)
    return Session() 