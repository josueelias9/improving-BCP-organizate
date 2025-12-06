# clean_architecture_example.py

from abc import ABC, abstractmethod

# ====================================================================
# 1. PUERTOS (ABSTRACCIONES/INTERFACES) - Capa Interior
#    Representa los Use Case Input Port y Use Case Output Port.
# ====================================================================

class UseCaseInputPort(ABC):
    """
    Define el contrato que el Interactor debe implementar.
    (Llamado por el Controller).
    """
    @abstractmethod
    def execute(self, request_data: dict):
        """Método para ejecutar la lógica de negocio."""
        pass

class UseCaseOutputPort(ABC):
    """
    Define el contrato que el Presenter debe implementar.
    (Llamado por el Interactor).
    """
    @abstractmethod
    def present(self, response_data: dict):
        """Método para presentar los datos después de la ejecución."""
        pass

# ====================================================================
# 2. INTERACTOR (CASO DE USO) - Capa de Dominio
#    Implementa el Input Port y usa el Output Port.
# ====================================================================

class GetUserInfoInteractor(UseCaseInputPort):
    """
    Contiene la lógica de negocio central para obtener información de un usuario.
    """
    def __init__(self, output_port: UseCaseOutputPort):
        # La dependencia apunta a la abstracción (Output Port), no a la implementación concreta.
        self.output_port = output_port

    def execute(self, request_data: dict):
        # 1. Obtener datos de la solicitud
        user_id = request_data.get("user_id")

        # 2. Lógica de Negocio (simulada)
        print(f"  [Interactor]: Ejecutando lógica para User ID: {user_id}")
        
        if user_id == 101:
            # Resultado exitoso
            user_data = {"id": 101, "name": "Alice Smith", "email": "alice@example.com"}
        else:
            # Resultado con error
            user_data = {"error": "User not found"}
            
        # 3. Flujo de control: Llama al método 'present' del Output Port.
        #    Esto invierte la dependencia del flujo de control.
        self.output_port.present(user_data)

# ====================================================================
# 3. PRESENTER (PRESENTACIÓN) - Capa de Presentación
#    Implementa el Output Port.
# ====================================================================

class UserPresenter(UseCaseOutputPort):
    """
    Formatea los datos resultantes del Interactor para ser consumidos por la Vista/UI.
    """
    def __init__(self):
        self.view_model = None  # Almacenará el resultado formateado para la UI

    def present(self, response_data: dict):
        # 1. Recibir el resultado del Interactor (a través del Output Port)
        print("  [Presenter]: Formateando datos recibidos.")
        
        # 2. Lógica de Presentación/Formateo
        if "error" in response_data:
            self.view_model = {"status": "Error", "message": response_data["error"], "data": None}
        else:
            self.view_model = {
                "status": "Success",
                "display_name": f"{response_data['name']} ({response_data['email']})",
                "data": response_data
            }

        print(f"  [Presenter]: ViewModel actualizado.")
        return self.view_model

# ====================================================================
# 4. CONTROLLER (CONTROLADOR) - Capa Externa/Adaptador
#    Usa el Input Port.
# ====================================================================

class UserController:
    """
    Recibe la entrada del usuario (ej. una solicitud HTTP) y la dirige al Use Case.
    """
    def __init__(self, input_port: UseCaseInputPort):
        # La dependencia apunta a la abstracción (Input Port).
        self.input_port = input_port

    def handle_request(self, raw_request: dict):
        print("\n" + "="*50)
        print(f"▶ [Controller]: Solicitud recibida: {raw_request}")
        
        # 1. Mapear datos crudos a Request DTO
        request_data = {"user_id": raw_request.get("id")}
        
        # 2. Flujo de Control: Llama al método 'execute' del Input Port.
        self.input_port.execute(request_data)
        
        print("◀ [Controller]: Fin del manejo de la solicitud.")
        print("="*50)

# ====================================================================
# 5. ENSAMBLAJE Y EJECUCIÓN
#    (Simulación de la Inversión de Control/Inyección de Dependencias)
# ====================================================================

if __name__ == "__main__":
    
    # 1. Inicializar el Presenter (Implementa el Output Port)
    presenter = UserPresenter()

    # 2. Inicializar el Interactor (Requiere el Output Port)
    interactor = GetUserInfoInteractor(output_port=presenter)

    # 3. Inicializar el Controller (Requiere el Input Port)
    controller = UserController(input_port=interactor)

    # --- SIMULACIÓN DEL FLUJO DE CONTROL (Caso de éxito) ---
    request_success = {"id": 101}
    controller.handle_request(request_success)
    
    print("\n[Resultado final en la UI (Presenter's ViewModel)]")
    print(presenter.view_model)
    
    # --- SIMULACIÓN DEL FLUJO DE CONTROL (Caso de error) ---
    request_failure = {"id": 999}
    controller.handle_request(request_failure)

    print("\n[Resultado final en la UI (Presenter's ViewModel)]")
    print(presenter.view_model)