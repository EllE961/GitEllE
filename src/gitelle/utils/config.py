"""
Configuration utility functions for GitEllE.
"""
import os
import configparser
from pathlib import Path
from typing import Dict, Optional, Union


class Config:
    """
    Represents a Git configuration file.

    Git configurations can be stored at three levels:
    - System level (/etc/gitconfig)
    - Global level (~/.gitconfig)
    - Repository level (.gitelle/config)
    """

    def __init__(self, path: Union[str, Path] = None):
        """
        Initialize a configuration.

        Args:
            path: The path to the configuration file (default: None)
        """
        self.path = Path(path) if path else None
        self.config = configparser.ConfigParser()

        if self.path and self.path.exists():
            self.read()

    def read(self) -> None:
        """Read the configuration from disk."""
        self.config.read(self.path)

    def write(self) -> None:
        """Write the configuration to disk."""
        with open(self.path, "w") as f:
            self.config.write(f)

    def get(self, section: str, option: str,
            default: str = None) -> Optional[str]:
        """
        Get a configuration value.

        Args:
            section: The configuration section
            option: The configuration option
            default: The default value to return if the option is not found

        Returns:
            The configuration value or the default
        """
        try:
            return self.config.get(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default

    def set(self, section: str, option: str, value: str) -> None:
        """
        Set a configuration value.

        Args:
            section: The configuration section
            option: The configuration option
            value: The value to set
        """
        if not self.config.has_section(section):
            self.config.add_section(section)

        self.config.set(section, option, value)

    def remove_option(self, section: str, option: str) -> bool:
        """
        Remove a configuration option.

        Args:
            section: The configuration section
            option: The configuration option

        Returns:
            True if the option was removed, False otherwise
        """
        try:
            return self.config.remove_option(section, option)
        except configparser.NoSectionError:
            return False

    def remove_section(self, section: str) -> bool:
        """
        Remove a configuration section.

        Args:
            section: The configuration section

        Returns:
            True if the section was removed, False otherwise
        """
        return self.config.remove_section(section)

    def get_sections(self) -> list:
        """
        Get all configuration sections.

        Returns:
            A list of section names
        """
        return self.config.sections()

    def get_options(self, section: str) -> list:
        """
        Get all options in a section.

        Args:
            section: The configuration section

        Returns:
            A list of option names
        """
        try:
            return self.config.options(section)
        except configparser.NoSectionError:
            return []

    def get_items(self, section: str) -> list:
        """
        Get all items in a section.

        Args:
            section: The configuration section

        Returns:
            A list of (option, value) tuples
        """
        try:
            return self.config.items(section)
        except configparser.NoSectionError:
            return []


def get_user_name() -> Optional[str]:
    """
    Get the user's name from the Git configuration.

    Returns:
        The user's name or None if not configured
    """
    # First, try to get from environment variable
    name = os.environ.get("GIT_AUTHOR_NAME")
    if name:
        return name

    # Then, try to get from global config
    global_config_path = Path.home() / ".gitconfig"
    if global_config_path.exists():
        config = Config(global_config_path)
        name = config.get("user", "name")
        if name:
            return name

    return None


def get_user_email() -> Optional[str]:
    """
    Get the user's email from the Git configuration.

    Returns:
        The user's email or None if not configured
    """
    # First, try to get from environment variable
    email = os.environ.get("GIT_AUTHOR_EMAIL")
    if email:
        return email

    # Then, try to get from global config
    global_config_path = Path.home() / ".gitconfig"
    if global_config_path.exists():
        config = Config(global_config_path)
        email = config.get("user", "email")
        if email:
            return email

    return None
