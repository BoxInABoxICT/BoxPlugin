# Development refrence
The database API module has been made with the possibility to expand the number of settings and assistants configurable through this API. Due to the changes nessecary to accomodate new features perhaps not being immediately clear, this document will point out parts of the database API that will require modification when implementing new course settings or assistant features. This refrence assumes these new features have already been implemented into the database model.

## Adding new course settings

### courseSettings.py
Course settings uses an Enum class and two functions to determine what database operation(s) to perform when handling a request:
- `SettingKeys`
- `fetchSwitch()`
- `updateSwitch()`
Add a new key to the `SettingKeys` class and extend the switch functions to contain a case for this new key calling the desired methods.

### configForms.py
The `CourseSettingsForm` class uses two methods to change the setting values on the form:
- `add()`
- `update()`
These functions do not nessecarily require an update, however, in their current implementation they can only update course settings that can be configured by a checkbox (for toggling the setting) and an integer value field.

## Adding new assistant settings

### assistantSettings.py
Assistantsettings uses two functions to determine what database operation(s) to perform when handling a request:
- `fetchSwitch()`
- `updateSwitch()`
They use the imported Enum class `AssistantKey` to evaluate cases, this class will require a new key associated with the new assistant. Both functions should be extended to contain a case for the new assistant key, calling desired methods.

### configForms.py
The `AssistantSettingsForm` class has two functions to add and change assistant values in the form:
- `addObject()`
- `updateObject()`
These are wrapper functions and do not require any modification, if deletion of form objects is desired it would be recommended to create a new wrapper function here.

The `attrParseMap` dictionary associated with `AssistantSettingsForm` will probably require additional mappings for a new assistant to cast values to their desired type based on the provided key.

### formSettingObjects.py
The `AssistantSettingObjects` class has multiple functions using the `AssistantKey` Enum class to execute the correct functions for each assistant. These funcions all require the addition of an extra case for the new assistant. These functions are:
- `add()`
- `update()`
- `remove()`
- `get()`
- `__assistantSwitch()`

`__assistantSwitch()` maps to a private utility function per assistant to correctly format the 'assistant object' to be placed in the class' objects dictionary, a new assitant type will also require such a new function.