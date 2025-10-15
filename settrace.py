import sys
import inspect
import os
import time
from contextlib import ContextDecorator

SPLITTER_LINE = lambda: "-" * 100 + "\n"


class TraceAll(ContextDecorator):
    def __init__(self, logfile, base_dir=None):
        """
        logfile: Caminho do arquivo de log
        base_dir: Diretório base do seu código (para ignorar libs externas)
        """
        self.logfile = logfile
        self._previous_trace = None
        self.base_dir = os.path.abspath(base_dir or os.getcwd())
        self._indent = 0
        self._start_times = {}
        print(f"BaseDir -> '{self.base_dir}'")

    def __enter__(self):
        self._previous_trace = sys.gettrace()
        sys.settrace(self._trace_calls)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        sys.settrace(self._previous_trace)
        return False  # não suprime exceções

    def _trace_calls(self, frame, event, arg):
        print(f"Frame: {frame.f_code.co_name}, Event: {event}")
        if event == "call":
            filename = os.path.abspath(frame.f_code.co_filename)
            # Loga apenas funções do diretório base
            if not filename.startswith(self.base_dir):
                print("Ignoring external call")
                return None
            print("Tracing function")
            return self._trace_functions
        return None

    def _trace_functions(self, frame, event, arg):
        filename = os.path.abspath(frame.f_code.co_filename)
        if not filename.startswith(self.base_dir):
            print("_trace_functions: Ignoring external function")
            return None

        func_name = frame.f_code.co_name
        key = (filename, frame.f_code.co_firstlineno, func_name)
        print(f"_trace_functions: {func_name}, Event: {event} Key: {key}")
        if event in ("call", "line"):
            self._indent += 1
            args_info = inspect.getargvalues(frame)
            args_repr = {
                k: repr(args_info.locals[k])
                for k in args_info.args
            }

            # Marca o início da função
            self._start_times[key] = time.perf_counter()

            doc = inspect.getdoc(frame.f_code)
            print(f"Docstring: {doc}")
            if not doc:
                # Tenta pegar via inspect.getdoc(func_obj) se possível
                func_obj = frame.f_globals.get(func_name)
                doc = inspect.getdoc(func_obj)
            if doc:
                doc = doc.strip()

            with open(self.logfile, "a", encoding="utf-8") as f:
                # f.write(SPLITTER_LINE())
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}]  ")
                print(f"Logging call to {func_name}")
                f.write("  " * self._indent + f"→ Chamada: {func_name}()\n")
                for k, v in args_repr.items():
                    f.write("  " * self._indent + f"  {k} = {v}\n")
                if doc:
                    f.write("  " * self._indent + f"  📘 Doc: {doc}\n")

            return self._trace_functions

        elif event == "return":
            start_time = self._start_times.pop(key, None)
            elapsed = (time.perf_counter() - start_time) * 1000 if start_time else 0.0

            with open(self.logfile, "a", encoding="utf-8") as f:
                print(f"Logging return from {func_name}")
                f.write("  " * self._indent + f"← Retorno: {repr(arg)}\n")
                f.write("  " * self._indent + f"⏱️ Tempo: {elapsed:.3f} ms\n")
                f.write(f"{SPLITTER_LINE()}\n")
            self._indent -= 1
            return None

        return None
