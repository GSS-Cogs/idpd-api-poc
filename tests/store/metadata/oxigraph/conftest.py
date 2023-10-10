# Test setup that will run for tests in this _specific_ directory.
# Please keep this here as if we're not running tests against
# oxigraph we don't need to be spinning up an oxigraph container.

import sys
import pytest
from pathlib import Path

import docker
from docker import DockerClient

repo_root = Path(__file__).parent.parent.parent.parent.parent
devdata = Path(repo_root)
sys.path.append(str(devdata.absolute()))

from devdata import create_devdata

def oxigraph_test_store():
    """
    Spins up oxigraph for testing.

    Note: As a precaution against interfereing with anyones
    local setup this oxigraph is exposed on port 7879
    rather than the standard 7878
    """
    docker_client: DockerClient = docker.from_env()

    # Frontend service
    oxigraph_container = docker_client.containers.run(
        name="oxigraph_test"
        "oxigraph:latest",
        ports={"7878": "7879"},
        publish_all_ports=True,
        network_mode="bridge",
        detach=True
    )
    container_info = docker_client.containers.get("oxigraph_test")
    create_devdata.populate(oxigraph_url="http://localhost:7879")
