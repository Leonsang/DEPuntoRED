from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Cliente(Base):
    """Modelo para la tabla de clientes"""
    __tablename__ = 'clientes'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)

    def __repr__(self):
        return f"<Cliente(id={self.id}, nombre='{self.nombre}', apellido='{self.apellido}')>"

class Venta(Base):
    """Modelo para la tabla de ventas"""
    __tablename__ = 'ventas'

    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    producto = Column(String(100), nullable=False)
    fecha = Column(Date, nullable=False)
    monto = Column(Numeric(10, 2), nullable=False)

    def __repr__(self):
        return f"<Venta(id={self.id}, cliente_id={self.cliente_id}, producto='{self.producto}', fecha='{self.fecha}', monto={self.monto})>" 