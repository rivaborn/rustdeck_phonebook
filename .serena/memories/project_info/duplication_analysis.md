Duplicate schemas found between src/phonebook/schemas.py and src/phonebook/routes/schemas.py:

1. ComputerCreate class - Both files define similar structure with same fields and validation rules:
   - friendly_name (1-120 chars, strip whitespace)
   - rustdesk_id (1-64 chars, strip whitespace)
   - hostname, local_ip, operating_system, username, location, notes, tags
   - local_ip validation as valid IPv4/IPv6
   - tags validation as comma-separated with 40 char limit per tag
   - whitespace stripping

2. ComputerUpdate class - Both files define similar structure with same fields and validation rules:
   - Same fields as ComputerCreate with Optional types
   - Same validation rules as ComputerCreate

3. ComputerOut class - Both files define similar structure with same fields:
   - All fields from ComputerBase (same field names/optional settings)
   - With id, created_at, updated_at fields added
   - from_attributes = True configuration

4. Both files define casual_greeting function (different implementations)

The duplication suggests that routes/schemas.py may be intended to be the main location for route-specific schemas and that schemas.py contains the base/primary schema definitions that should be consolidated.