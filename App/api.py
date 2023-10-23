import random
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
from datetime import datetime

# Configuración de la base de datos SQLite
DATABASE_URL = "sqlite:///./Data/hotel.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

# Definición de modelos de la base de datos
class Hotel(Base):
    __tablename__ = "hotel"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    direccion = Column(String)
    telefono = Column(String)

class Habitacion(Base):
    __tablename__ = "habitacion"
    id = Column(Integer, primary_key=True, index=True)
    tipo_habitacion = Column(String)
    precio = Column(Integer)
    disponibilidad = Column(Boolean, default=True)

class Autobus(Base):
    __tablename__ = "autobus"
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String, index=True, unique=True)
    tipo_autobus = Column(String, ForeignKey("tipo_autobus.id"))

class TipoAutobus(Base):
    __tablename__ = "tipo_autobus"
    id = Column(String, primary_key=True, index=True)
    capacidad = Column(Integer)

class HabitacionReserva(Base):
    __tablename__ = "habitacion_reserva"
    id = Column(Integer, primary_key=True, index=True)
    id_habitacion = Column(Integer, ForeignKey("habitacion.id"))
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime)

class AutobusReserva(Base):
    __tablename__ = "autobus_reserva"
    id = Column(Integer, primary_key=True, index=True)
    id_bus = Column(Integer, ForeignKey("autobus.id"))
    id_habitacion = Column(Integer, ForeignKey("habitacion.id"))
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime)


Base.metadata.create_all(bind=engine)

# Modelos Pydantic para validar datos
class RoomCreate(BaseModel):
    tipo_habitacion: str
    precio: int
    disponibilidad: bool

class BusCreate(BaseModel):
    numero: str
    tipo_autobus: str

class BusReservation(BaseModel):
    id_habitacion: int
    id_bus: int

class HotelInfo(BaseModel):
    nombre: str
    direccion: str
    telefono: str

class RoomInfo(BaseModel):
    id: int
    tipo_habitacion: str
    precio: int
    disponibilidad: bool

class BusPassenger(BaseModel):
    id_habitacion: int
    id_bus: int

class CheckoutConfirmation(BaseModel):
    mensaje: str

class PassengerValidationData(BaseModel):
    id_habitacion: int
    id_bus: int

class PassengerValidation(BaseModel):
    mensaje: str

# Función para obtener una instancia de sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rutas de la API

# Ruta 1: /hotel_info
@app.get("/hotel_info", response_model=HotelInfo)
def get_hotel_info(db: Session = Depends(get_db)):
    hotel = db.query(Hotel).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    # Devuelve un diccionario con las claves y valores adecuados
    return {
        "nombre": hotel.nombre,
        "direccion": hotel.direccion,
        "telefono": hotel.telefono
    }

# Ruta 2: /rooms
@app.get("/rooms", response_model=List[RoomInfo])
def get_available_rooms(db: Session = Depends(get_db)):
    rooms = db.query(Habitacion).all()
    if not rooms:
        raise HTTPException(status_code=404, detail="Rooms not found")

    # Devuelve una lista de diccionarios con las habitaciones
    room_info_list = []
    for room in rooms:
        room_info_list.append({
            "id": room.id,
            "tipo_habitacion": room.tipo_habitacion,
            "precio": room.precio,
            "disponibilidad": room.disponibilidad
        })

    return room_info_list


# Ruta 3: /bus
@app.post("/bus", response_model=BusReservation)
def reserve_bus_seat(reservation: BusReservation, db: Session = Depends(get_db)):
    room = db.query(Habitacion).filter(Habitacion.id == reservation.id_habitacion).first()
    bus = db.query(Autobus).filter(Autobus.id == reservation.id_bus).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")

    if not room.disponibilidad:
        raise HTTPException(status_code=400, detail="The room is not available")

    nueva_reserva = AutobusReserva(**reservation.dict(), fecha_inicio=datetime.now())
    db.add(nueva_reserva)
    db.commit()
    db.refresh(nueva_reserva)

    room.disponibilidad = False
    db.commit()

    return nueva_reserva

# Ruta 4: /bus_passengers
@app.get("/bus_passengers", response_model=List[BusPassenger])
def get_bus_passengers(db: Session = Depends(get_db)):
    passengers = db.query(AutobusReserva).all()
    if not passengers:
        raise HTTPException(status_code=404, detail="No passengers found")
    return passengers

# Ruta 5: /checkout
@app.post("/checkout", response_model=CheckoutConfirmation)
def checkout(room_number: int, db: Session = Depends(get_db)):
    room = db.query(Habitacion).filter(Habitacion.id == room_number).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    room.disponibilidad = True
    db.commit()

    return {"mensaje": f"Checkout successful for room {room_number}"}

# Ruta 6: /validate_passenger
@app.post("/validate_passenger", response_model=PassengerValidation)
def validate_passenger(validation_data: PassengerValidationData, db: Session = Depends(get_db)):
    room = db.query(Habitacion).filter(Habitacion.id == validation_data.id_habitacion).first()
    bus = db.query(Autobus).filter(Autobus.id == validation_data.id_bus).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")

    return {"mensaje": f"Passenger validated for room {room.id} and bus {bus.id}"}

def init_data(db):
    try:

        db.add(Hotel(nombre="Hotel Ejemplo", direccion="Calle Ejemplo 123", telefono="123-456-7890"))
    
        # Usaremos un conjunto para realizar un seguimiento de los números de autobús generados
        numeros_de_autobus_generados = set()
        
        for i in range(50):
            tipo_habitacion = random.choice(["Habitación Estándar", "Habitación Premium", "Suite"])
            precio = random.randint(80, 300)
            disponibilidad = random.choice([True, False])
            db.add(Habitacion(tipo_habitacion=tipo_habitacion, precio=precio, disponibilidad=disponibilidad))
            
            # Generar un número de autobús único
            while True:
                numero = f"Bus{i+1:03d}"
                if numero not in numeros_de_autobus_generados:
                    numeros_de_autobus_generados.add(numero)
                    break
            
            tipo_autobus = random.choice(["Autobús Grande", "Autobús Pequeño"])
            capacidad = random.randint(20, 60)
            db.add(Autobus(numero=numero, tipo_autobus=tipo_autobus))
            db.add(TipoAutobus(id=f"Tipo-{tipo_autobus}-{i+1:03d}", capacidad=capacidad))
        
        db.commit()
    except Exception as e:
        print(f"Error in init_data: {str(e)}")
db = SessionLocal()
init_data(db)
db.close()
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
