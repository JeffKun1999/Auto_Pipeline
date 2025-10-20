import os
import hashlib
from compare_pdfs import calculate_hash # Importamos la función que queremos probar

# --- Prueba para la función calculate_hash ---

def test_calculate_hash_successfully():
    """
    Verifica que la función calculate_hash devuelve el hash MD5 correcto
    para un archivo conocido.
    """
    # 1. Preparación (Setup)
    file_content = b"Hola Mundo"
    expected_hash = hashlib.md5(file_content).hexdigest()
    test_file = "test_file.tmp"

    with open(test_file, "wb") as f:
        f.write(file_content)

    # 2. Ejecución (Action)
    actual_hash = calculate_hash(test_file)

    # 3. Verificación (Assertion)
    assert actual_hash is not None
    assert actual_hash == expected_hash

    # 4. Limpieza (Teardown)
    os.remove(test_file)

def test_calculate_hash_file_not_found():
    """
    Verifica que la función devuelve None cuando el archivo no existe.
    """
    # 1. Preparación y 2. Ejecución
    hash_result = calculate_hash("un_archivo_que_no_existe.pdf")

    # 3. Verificación
    assert hash_result is None