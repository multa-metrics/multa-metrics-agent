import threading
import time
import traceback

import psutil


class BaseHardware:
    class Meta:
        """
        attr: model_key -> Key to represent the model data.
        attr: data_function -> Function to be called from psutil. Elements is formatted as string.
        attr: attributes -> Attributes to get from the call to 'data_function'. Elements are formatted as a list of strings.
        attr: extra_fields -> Additional function calls to psutil. List of function names. Elements are formatted as {"key_name": "function_name"}.
        attr: extra_advanced_fields -> Additional advanced function calls to psutil. Includes key naming, args and kwargs. Elements are formatted as {"name": "", "function": "", "args": [], "kwargs": {}}
        attr: fields_include -> Fields to include in the serialization to Python dictionary. Used to add attributes generated in 'parse()'. Elements are formatted as a list of strings.
        attr: fields_exclude -> Fields to exclude in the serialization to Python dictionary. Used to remove attributes. Elements are formatted as a list of strings.
        attr: background_functions -> Functions that will be run in separate threads every a certain amount of seconds.
        """
        model_key = None

        data_function = None
        attributes = []

        extra_fields = {}
        extra_advanced_fields = []

        fields_include = []
        fields_exclude = []

        background_functions = []
        background_shared_memory_store_enabled = None
        background_shared_memory_store_frequency = None

    def __init__(self, shared_memory_reference):
        self._shared_memory = shared_memory_reference

        self._data = None
        self._extra_data = {}
        self._extra_advanced_data = {}

        self.Meta.data_function = getattr(self.Meta, "data_function", None)

        self.Meta.attributes = getattr(self.Meta, "attributes", [])
        for attribute in self.Meta.attributes:
            setattr(self, attribute, None)

        self.Meta.extra_fields = getattr(self.Meta, "extra_fields", {})
        for key_name, function_name in self.Meta.extra_fields.items():
            setattr(self, key_name, None)

        self.Meta.extra_advanced_fields = getattr(self.Meta, "extra_advanced_fields", [])
        for field_definition in self.Meta.extra_advanced_fields:
            setattr(self, field_definition['name'], None)

        self.Meta.fields_include = getattr(self.Meta, "fields_include", [])
        self.Meta.fields_exclude = getattr(self.Meta, "fields_exclude", [])

        self.Meta.background_functions = getattr(self.Meta, "background_functions", [])

        self.Meta.background_shared_memory_store_enabled = getattr(
            self.Meta, "background_shared_memory_store_enabled", None
        ) or self._shared_memory is not None

        self.Meta.background_shared_memory_store_frequency = getattr(
            self.Meta, "background_shared_memory_store_frequency", 1
        )

    def configure_setting(self, setting, value):
        if hasattr(self.Meta, setting):
            setattr(self.Meta, setting, value)

    def retrieve(self):
        """
        Flow of the data aggregation. First retrieve data from 'data_function'. Then call functions from 'extra_fields',
        and for the last call functions from 'extra_advanced_fields'.
        Then set the data aggregated from all this functions as model attributes.
        Finally perform custom parsing on the model attributes to add new fields or enrich existing ones.
        """
        self.get_data()
        self.get_extra_data()
        self.get_extra_advanced_data()

        self.set()

        self.parse()

    def get_data(self):
        if self.Meta.data_function is None:
            return

        if callable(getattr(psutil, self.Meta.data_function)) is False:
            raise RuntimeError("Required callable for 'data_function'!")

        try:
            self._data = getattr(psutil, self.Meta.data_function)()
        except Exception:
            print(traceback.format_exc())
            raise RuntimeError(f"Function {self.Meta.data_function} failed to run!")

    def get_extra_data(self):
        for key_name, function_name in self.Meta.extra_fields.items():
            if function_name is None:
                raise RuntimeError(f"Key value '{key_name}' needs to be defined!")

            if callable(getattr(psutil, function_name)) is False:
                raise RuntimeError(f"Key value '{key_name}' needs to be a callable!")

            try:
                self._extra_data[key_name] = getattr(psutil, function_name)()
            except Exception:
                print(traceback.format_exc())
                raise RuntimeError(f"Function {function_name} failed to run!")

    def get_extra_advanced_data(self):
        for field_definition in self.Meta.extra_advanced_fields:
            key_name = field_definition.get("name")
            function_name = field_definition.get("function")
            function_args = field_definition.get("args", [])
            function_kwargs = field_definition.get("kwargs", {})

            if function_name is None:
                raise RuntimeError(f"Function value in '{key_name}' needs to be defined!")

            if callable(getattr(psutil, function_name)) is False:
                raise RuntimeError(f"Function value '{key_name}' needs to be a callable!")

            try:
                self._extra_advanced_data[key_name] = getattr(psutil, function_name)(*function_args, **function_kwargs)
            except Exception:
                print(traceback.format_exc())
                raise RuntimeError(f"Function {function_name} failed to run!")

    def set(self):
        for attribute in self.Meta.attributes:
            setattr(self, attribute, getattr(self._data, attribute, None))

        for key_name, function_name in self.Meta.extra_fields.items():
            setattr(self, key_name, self._extra_data.get(key_name, None))

        for field_definition in self.Meta.extra_advanced_fields:
            key_name = field_definition.get("name")
            setattr(self, key_name, self._extra_advanced_data.get(key_name, None))

    def parse(self):
        """
        Used for internal data parsing... Non-invasive use if not defined...
        """
        pass

    @staticmethod
    def namedtuple_to_dict(attribute):
        """
        Performs converting namedtuples to python dictionaries.
        """
        # If attribute is a namedtuple, convert it to a dict.
        if isinstance(attribute, tuple) and hasattr(attribute, "_asdict"):
            # response[attribute_name] = dict(attribute._asdict())
            response_dict = dict(attribute._asdict())

        # If attribute is a dictionary containing namedtuple, convert it to a dict that will contain dictionaries.
        elif isinstance(attribute, dict):
            response_dict = dict()
            for key, value in attribute.items():
                if isinstance(value, tuple) and hasattr(value, "_asdict"):
                    response_dict[key] = dict(value._asdict())

                elif isinstance(value, list):
                    response_list = list()
                    for element in value:
                        if isinstance(element, tuple) and hasattr(element, "_asdict"):
                            response_list.append(dict(element._asdict()))
                        else:
                            response_list.append(element)
                    response_dict[key] = response_list

                else:
                    response_dict[key] = value

        # For rest of scenarios, just assign property to response dictionary.
        else:
            return attribute

        return response_dict

    def to_dict(self):
        """
        Convert the model to a Python dictionary using a 'best effort' approach to convert all namedtuples from psutil to a dictionary.
        Will perform cleanup on the desired included fields 'fields_include' and will exclude the specified fields in 'fields_exclude'.
        """
        response = dict()
        for attribute in self.Meta.attributes:
            if attribute in self.Meta.fields_exclude:
                continue

            response[attribute] = getattr(self, attribute)

        for field_name in self.Meta.extra_fields.keys():
            if field_name in self.Meta.fields_exclude:
                continue
            response[field_name] = self.namedtuple_to_dict(getattr(self, field_name))

        for field_definition in self.Meta.extra_advanced_fields:
            field_name = field_definition["name"]
            if field_name in self.Meta.fields_exclude:
                continue
            response[field_name] = self.namedtuple_to_dict(getattr(self, field_name))

        for field_name in self.Meta.fields_include:
            response[field_name] = getattr(self, field_name)
            # response[field_name] = self.namedtuple_to_dict(getattr(self, field_name))
            # data = self.namedtuple_to_dict(getattr(self, field_name))

        return response

    def background_functions_start(self, function_):
        function_name = function_.get("name", False)
        if isinstance(function_name, str) is True:
            if hasattr(self, function_name):
                background_function = getattr(self, function_name)
                background_function_thread = threading.Thread(target=background_function)
                background_function_thread.start()

    def background_shared_memory_collect(self):
        while True and isinstance(self.Meta.model_key, str) is True and isinstance(
            self.Meta.background_shared_memory_store_frequency, int
        ):
            self.retrieve()
            self._shared_memory.shared_memory_model_write(self.Meta.model_key, self.to_dict())

            time.sleep(self.Meta.background_shared_memory_store_frequency)

    def background_shared_memory_collect_start(self):
        if self.Meta.background_shared_memory_store_enabled is True:
            background_function_thread = threading.Thread(target=self.background_shared_memory_collect)
            background_function_thread.start()

    def background_functions_run(self):
        for function_definition in self.Meta.background_functions:
            self.background_functions_start(function_=function_definition)

        self.background_shared_memory_collect_start()
