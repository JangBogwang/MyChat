2025-12-30 10:43:36 /usr/local/lib/python3.11/site-packages/pydantic/_internal/_config.py:373: UserWarning: Valid config keys have changed in V2:
2025-12-30 10:43:36 * 'orm_mode' has been renamed to 'from_attributes'
2025-12-30 10:43:36   warnings.warn(message, UserWarning)
2025-12-30 10:43:38 Process SpawnProcess-1:
2025-12-30 10:43:38 Traceback (most recent call last):
2025-12-30 10:43:38   File "/usr/local/lib/python3.11/multiprocessing/process.py", line 314, in _bootstrap
2025-12-30 10:43:38     self.run()
2025-12-30 10:43:38   File "/usr/local/lib/python3.11/multiprocessing/process.py", line 108, in run
2025-12-30 10:43:38     self._target(*self._args, **self._kwargs)
2025-12-30 10:43:38   File "/usr/local/lib/python3.11/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
2025-12-30 10:43:38     target(sockets=sockets)
2025-12-30 10:43:38   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 67, in run
2025-12-30 10:43:38     return asyncio.run(self.serve(sockets=sockets))
2025-12-30 10:43:38            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-12-30 10:43:38   File "/usr/local/lib/python3.11/asyncio/runners.py", line 190, in run
2025-12-30 10:43:38     return runner.run(main)
2025-12-30 10:43:38            ^^^^^^^^^^^^^^^^
2025-12-30 10:43:38   File "/usr/local/lib/python3.11/asyncio/runners.py", line 118, in run
2025-12-30 10:43:38     return self._loop.run_until_complete(task)
2025-12-30 10:43:38            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-12-30 10:43:38   File "/usr/local/lib/python3.11/asyncio/base_events.py", line 654, in run_until_complete
2025-12-30 10:43:38     return future.result()
2025-12-30 10:43:38            ^^^^^^^^^^^^^^^
2025-12-30 10:43:38   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 71, in serve
2025-12-30 10:43:38     await self._serve(sockets)
2025-12-30 10:43:38   File "/usr/local/lib/python3.11/site-packages/uvicorn/server.py", line 78, in _serve
2025-12-30 10:43:38     config.load()
2025-12-30 10:43:38   File "/usr/local/lib/python3.11/site-packages/uvicorn/config.py", line 436, in load
2025-12-30 10:43:38     self.loaded_app = import_from_string(self.app)
2025-12-30 10:43:38                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-12-30 10:43:38   File "/usr/local/lib/python3.11/site-packages/uvicorn/importer.py", line 19, in import_from_string
2025-12-30 10:43:38     module = importlib.import_module(module_str)
2025-12-30 10:43:38              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-12-30 10:43:38   File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module
2025-12-30 10:43:38     return _bootstrap._gcd_import(name[level:], package, level)
2025-12-30 10:43:38            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-12-30 10:43:38   File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
2025-12-30 10:43:38   File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
2025-12-30 10:43:38   File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
2025-12-30 10:43:38   File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
2025-12-30 10:43:38   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
2025-12-30 10:43:38   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
2025-12-30 10:43:38   File "/app/app/main.py", line 2, in <module>
2025-12-30 10:43:38     from app.routers import chat_router
2025-12-30 10:43:38   File "/app/app/routers/chat_router.py", line 10, in <module>
2025-12-30 10:43:38     from app.config.Settings import settings
2025-12-30 10:43:38   File "/app/app/config/Settings.py", line 12, in <module>
2025-12-30 10:43:38     settings = Settings()
2025-12-30 10:43:38                ^^^^^^^^^^
2025-12-30 10:43:38   File "/usr/local/lib/python3.11/site-packages/pydantic_settings/main.py", line 152, in __init__
2025-12-30 10:43:38     super().__init__(
2025-12-30 10:43:38   File "/usr/local/lib/python3.11/site-packages/pydantic/main.py", line 253, in __init__
2025-12-30 10:43:38     validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
2025-12-30 10:43:38                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-12-30 10:43:38 pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
2025-12-30 10:43:38 main_sender
2025-12-30 10:43:38   Extra inputs are not permitted [type=extra_forbidden, input_value='MyChat', input_type=str]
2025-12-30 10:43:38     For further information visit https://errors.pydantic.dev/2.11/v/extra_forbidden