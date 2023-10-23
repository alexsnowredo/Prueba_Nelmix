import httpx

# URL base de la API
base_url = "http://127.0.0.1:8000"

# Función para hacer una solicitud GET a la API y mostrar la respuesta
async def get_request(endpoint):
    async with httpx.AsyncClient() as client:
        response = await client.get(base_url + endpoint)
        if response.status_code == 200:
            print(response.json())
        else:
            print(f"Error: {response.status_code}")
            print(response.text)

# Función para hacer una solicitud POST a la API y mostrar la respuesta
async def post_request(endpoint, data):
    async with httpx.AsyncClient() as client:
        response = await client.post(base_url + endpoint, json=data)
        if response.status_code == 200:
            print(response.json())
        else:
            print(f"Error: {response.status_code}")
            print(response.text)

# Menú interactivo
async def main():
    while True:
        print("\nSeleccione una opción:")
        print("1. Obtener información del hotel")
        print("2. Obtener información de las habitaciones")
        print("3. Reservar un autobús")
        print("4. Obtener lista de pasajeros de autobús")
        print("5. Hacer checkout")
        print("6. Validar reserva de pasajero")
        print("0. Salir")
        option = input("Opción: ")

        if option == "1":
            await get_request("/hotel_info")
        elif option == "2":
            await get_request("/rooms")
        elif option == "3":
            id_habitacion = int(input("Ingrese el ID de la habitación: "))
            id_bus = int(input("Ingrese el ID del autobús: "))
            fecha_inicio = input("Ingrese la fecha de inicio (YYYY-MM-DD HH:MM:SS): ")
            fecha_fin = input("Ingrese la fecha de fin (YYYY-MM-DD HH:MM:SS): ")
            await post_request("/bus", {
                "id_habitacion": id_habitacion,
                "id_bus": id_bus,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin
            })
        elif option == "4":
            await get_request("/bus_passengers")
        elif option == "5":
            id_habitacion = int(input("Ingrese el ID de la habitación para hacer checkout: "))
            await post_request("/checkout", {"room_number": id_habitacion})
        elif option == "6":
            id_habitacion = int(input("Ingrese el ID de la habitación: "))
            id_bus = int(input("Ingrese el ID del autobús: "))
            await post_request("/validate_passenger", {"id_habitacion": id_habitacion, "id_bus": id_bus})
        elif option == "0":
            break
        else:
            print("Opción no válida. Por favor, seleccione una opción válida.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
