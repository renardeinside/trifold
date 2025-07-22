import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class BuildHook(BuildHookInterface):
    """Custom build hook for Databricks Apps.

    This hook is used to:
    1. build the UI assets for the Databricks Apps project
    2. Prepare the wheel for Databricks Apps by copying it to a ./.build folder
    3. Write a requirements.txt file in the ./.build folder with the name of the wheel

    Please note that Ui assets are build before the wheel is built.
    """

    def initialize(self, version: str, build_data: dict[str, Any]):
        ui_path = Path("src/trifold/ui")

        self.app.display_info(
            f"✨ Running custom build hook for project {self.metadata.name}"
        )
        self.app.display_info(f"🔨 Building UI assets in {ui_path.absolute()}...")

        if not ui_path.exists():
            self.app.display_error(f"❌ UI path {ui_path} does not exist.")
            raise FileNotFoundError(f"UI path {ui_path} does not exist.")

        self.app.display_info(
            f"📦 Running yarn build in UI directory {ui_path.absolute()}..."
        )

        is_windows = os.name == "nt"
        try:
            result = subprocess.run(
                ["yarn", "build"],
                capture_output=True,
                cwd=ui_path.absolute(),
                check=True,
                text=True,
                shell=is_windows,  # Use shell=True on Windows
            )

            # Display stdout if there's any output
            if result.stdout.strip():
                self.app.display_info("📋 Yarn build output:")
                for line in result.stdout.strip().split("\n"):
                    self.app.display_info(f"  {line}")

        except subprocess.CalledProcessError as e:
            self.app.display_error("❌ Yarn build failed!")

            # Display stderr line by line
            if e.stderr and e.stderr.strip():
                self.app.display_error("Error output:")
                for line in e.stderr.strip().split("\n"):
                    self.app.display_error(f"  {line}")

            # Display stdout as well, in case there are useful messages there
            if e.stdout and e.stdout.strip():
                self.app.display_info("Standard output:")
                for line in e.stdout.strip().split("\n"):
                    self.app.display_info(f"  {line}")

            # Re-raise the exception
            raise

    def finalize(
        self, version: str, build_data: dict[str, Any], artifact_path: str
    ) -> None:
        self.app.display_info(
            f"✨ Running Databricks Apps build hook for project {self.metadata.name} in directory {Path.cwd()}"
        )
        # remove the ./.build folder if it exists
        build_dir = Path(".build")
        self.app.display_info(f"📂 Resulting build directory: {build_dir.absolute()}")

        if build_dir.exists():
            self.app.display_info(f"🗑️ Removing {build_dir}")
            shutil.rmtree(build_dir)
            self.app.display_info(f"✅ Removed {build_dir}")

        # copy the artifact_path to the ./.build folder
        build_dir.mkdir(exist_ok=True)
        self.app.display_info(f"📋 Copying {artifact_path} to {build_dir}")
        shutil.copy(artifact_path, build_dir)

        # write the name of the artifact to a requirements.txt file in the ./.build folder

        requirements_file = build_dir / "requirements.txt"
        self.app.display_info(
            f"📝 Writing requirements.txt to {requirements_file.absolute()}"
        )

        requirements_file.write_text(Path(artifact_path).name, encoding="utf-8")

        self.app.display_info(
            f"🎉 Apps-compatible build written to {build_dir.absolute()}"
        )
