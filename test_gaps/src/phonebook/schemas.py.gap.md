# src/phonebook/schemas.py

## Overall
NONE — no dedicated test file exists for this module.

## Must Test (Highest Risk First)
1. **HIGH** `ComputerCreate.validate_friendly_name`: test validation of 1-120 character limit and whitespace stripping
2. **HIGH** `ComputerCreate.validate_rustdesk_id`: test validation of 1-64 character limit and whitespace stripping  
3. **HIGH** `ComputerCreate.validate_local_ip`: test IPv4/IPv6 validation and None handling
4. **HIGH** `ComputerCreate.validate_tags`: test comma-separated tag validation with 40 char limit and whitespace handling
5. **HIGH** `ComputerUpdate.validate_friendly_name`: test optional field validation with 1-120 character limit
6. **HIGH** `ComputerUpdate.validate_rustdesk_id`: test optional field validation with 1-64 character limit
7. **HIGH** `ComputerUpdate.validate_local_ip`: test optional field IPv4/IPv6 validation
8. **HIGH** `ComputerUpdate.validate_tags`: test optional field tag validation with 40 char limit
9. **MEDIUM** `ComputerCreate.strip_whitespace`: test all TEXT field stripping behavior
10. **MEDIUM** `ComputerUpdate.strip_whitespace`: test all TEXT field stripping behavior

## Mock Strategy
- `ipaddress.ip_address`: mock to raise ValueError for invalid IPs in validation tests
- `pydantic.BaseModel`: no mocking needed, test validation through instantiation
- `phonebook.models.Computer`: not directly mocked, but may need to be stubbed in integration tests

The core validation logic is in Pydantic validators, so testing involves instantiating models with various inputs to verify validation errors and correct field processing.
