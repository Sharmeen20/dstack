from typing import List

from dstack import Provider, Job


class PythonProvider(Provider):
    def __init__(self):
        super().__init__(schema="providers/python/schema.yaml")
        # Drop the deprecated `python` and `python_script` properties, and make `script` required in the schema
        self.script = self.workflow.data.get("python_script") or self.workflow.data["script"]
        # TODO: Handle numbers such as 3.1 (e.g. require to use strings)
        self.version = str(self.workflow.data.get("version") or self.workflow.data.get("python") or "3.10")
        self.args = self.workflow.data.get("args")
        self.requirements = self.workflow.data.get("requirements")
        self.environment = self.workflow.data.get("environment") or {}
        self.artifacts = self.workflow.data.get("artifacts")
        self.working_dir = self.workflow.data.get("working_dir")
        self.resources = self._resources()
        self.image = self._image()

    def create_jobs(self) -> List[Job]:
        return [Job(
            image=self.image,
            commands=self._commands(),
            environment=self.environment,
            working_dir=self.working_dir,
            resources=self.resources,
            artifacts=self.artifacts
        )]

    def _image(self) -> str:
        cuda_is_required = self.resources and self.resources.gpu
        return f"dstackai/python:{self.version}-cuda-11.1" if cuda_is_required else f"python:{self.version}"

    def _commands(self):
        commands = []
        if self.requirements:
            commands.append("pip install -r " + self.requirements)
        args_init = ""
        if self.args:
            if isinstance(self.args, str):
                args_init += " " + self.args
            if isinstance(self.args, list):
                args_init += " " + ",".join(map(lambda arg: "\"" + arg.replace('"', '\\"') + "\"", self.args))
        commands.append(
            f"python {self.script}{args_init}"
        )
        return commands


if __name__ == '__main__':
    provider = PythonProvider()
    provider.start()
