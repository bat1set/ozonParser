import os
import sys
import subprocess
import venv
import platform

class VirtualEnvManager:
    def __init__(self, mod='default', libs=None, name_venv='.venv'):
        if libs is None:
            libs = []

        self._mod = mod
        self._libs = libs
        self._name_venv = name_venv
        self._venv_path = os.path.join(os.getcwd(), self._name_venv)
        self._is_venv_active = self._check_virtual_environment()

        if self._mod == 'default':
            self._default_mode()
        elif self._mod == 'noneVenv':
            self._none_venv_mode()
        elif self._mod == 'noneCheckVenv':
            self._none_check_venv_mode()
        else:
            print(f"Неизвестный режим: {self._mod}")
            input("Нажмите Enter, чтобы продолжить...")
            sys.exit(1)

    def _default_mode(self):
        if not self._is_venv_active:
            if not self._venv_exists():
                self._create_virtual_environment()
            self._activate_virtual_environment()
        self._install_libraries()

    def _none_venv_mode(self):
        self._install_libraries()

    def _none_check_venv_mode(self):
        self._install_libraries()

    def _check_virtual_environment(self):
        return sys.prefix != sys.base_prefix

    def _venv_exists(self):
        return os.path.isdir(self._venv_path)

    def _create_virtual_environment(self):

        try:
            venv.create(self._venv_path, with_pip=True)
            print(f"Виртуальное окружение '{self._name_venv}' создано.")
        except Exception as e:
            print(f"Ошибка при создании виртуального окружения: {e}")
            input("Нажмите Enter, чтобы продолжить...")
            sys.exit(1)

    def _activate_virtual_environment(self):
        try:
            activate_script = self._get_activate_script()
            if platform.system() == 'Windows':
                subprocess.call(f'{activate_script} && pip install --upgrade pip', shell=True)
            else:
                subprocess.call(f'source {activate_script} && pip install --upgrade pip', shell=True)
            print(f"Виртуальное окружение '{self._name_venv}' активировано.")
        except Exception as e:
            print(f"Ошибка при активации виртуального окружения: {e}")
            input("Нажмите Enter, чтобы продолжить...")
            sys.exit(1)

    def _get_activate_script(self):
        if platform.system() == 'Windows':
            return os.path.join(self._venv_path, 'Scripts', 'activate')
        else:
            return os.path.join(self._venv_path, 'bin', 'activate')

    def _install_libraries(self):
        try:
            if self._libs:
                if self._is_venv_active or self._mod in ['noneVenv', 'noneCheckVenv']:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + self._libs)
                else:
                    pip_path = os.path.join(self._venv_path, 'Scripts' if platform.system() == 'Windows' else 'bin', 'pip')
                    subprocess.check_call([pip_path, 'install'] + self._libs)
                print(f"Библиотеки {self._libs} установлены.")
        except Exception as e:
            print(f"Ошибка при установке библиотек: {e}")
            input("Нажмите Enter, чтобы продолжить...")
            sys.exit(1)