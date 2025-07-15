from uds_protocole import service_dispatch

def handle_service_request(service_id, params):
    service_id = service_id.lower()
    if service_id.startswith("0x"):
        service_id = service_id
    else:
        service_id = "0x"+service_id
    if service_id not in service_dispatch:
        raise ValueError(f"Service {service_id} not supported")
    
    build_function = service_dispatch[service_id]
    return build_function(params)