"""Console script for vmware_workstation_cli."""

import json
import sys
from pathlib import Path

import click
import requests
from requests.auth import HTTPBasicAuth

from .version import __timestamp__, __version__

header = f"{__name__.split('.')[0]} v{__version__} {__timestamp__}"

POWER_STATES = ["on", "off", "shutdown", "suspend", "pause", "unpause"]


class API:
    def __init__(self, debug, host, port, username, password):
        self.vms = None
        self.debug = debug
        self.auth = HTTPBasicAuth(username, password)
        self.base_uri = f"http://{host}:{port}/api"

    def get(self, url):
        url = self.base_uri + url
        response = requests.get(url, auth=self.auth)
        response.raise_for_status()
        return response.json()

    def put(self, url, args):
        url = self.base_uri + url
        headers = {
            "Content-Type": "application/vnd.vmware.vmw.rest-v1+json",
            "Accept": "application/vnd.vmware.vmw.rest-v1+json",
        }
        response = requests.put(
            url, headers=headers, auth=self.auth, data=args
        )
        if not response.ok:
            breakpoint()
            click.echo(f"Error: {response.json()}", err=True)
            response.raise_for_status()
        return response.json()

    def vm_id(self, name):
        if self.vms is None:
            self.list()
        return self.vms[name]["id"]

    def list(self, verbose=False):
        vms = self.get("/vms")
        self.vms = {}
        for vm in vms:
            path = vm["path"].replace("\\", "/")
            name = Path(path).stem
            self.vms[name] = vm
        if verbose:
            for k, v in self.vms.items():
                v.update(self.get(f"/vms/{v['id']}/power"))
            ret = self.vms
        else:
            ret = list(self.vms.keys())
        return ret

    def status(self, name):
        vmid = self.vm_id(name)
        ret = self.vms[name]
        ret.update(self.get(f"/vms/{vmid}/power"))
        return ret

    def set_power_state(self, name, state):
        vmid = self.vm_id(name)
        result = self.put(f"/vms/{vmid}/power", state.encode())
        return result


@click.group
@click.version_option(message=header)
@click.option(
    "-h", "--host", type=str, default="localhost", help="REST server hostname"
)
@click.option("-p", "--port", type=int, default=8697, help="REST server port")
@click.option(
    "-u",
    "--username",
    type=str,
    envvar="VMWARE_API_USERNAME",
    help="VMware REST API username",
)
@click.option(
    "-P",
    "--password",
    type=str,
    envvar="VMWARE_API_PASSWORD",
    help="VMware REST API password",
)
@click.option("-d", "--debug", is_flag=True, help="debug mode")
@click.pass_context
def cli(ctx, debug, host, port, username, password):
    """cli for vmware_workstation_cli."""

    def exception_handler(
        exception_type, exception, traceback, debug_hook=sys.excepthook
    ):

        if debug:
            debug_hook(exception_type, exception, traceback)
        else:
            click.echo(f"{exception_type.__name__}: {exception}", err=True)

    sys.excepthook = exception_handler

    ctx.obj = API(debug, host, port, username, password)
    return 0


def output(data):
    click.echo(json.dumps(data, indent=2))


@cli.command
@click.option("-v", "--verbose", is_flag=True, help="detailed output")
@click.pass_context
def ls(ctx, verbose):
    """list virtual machines"""
    output(ctx.obj.list(verbose))


@cli.command
@click.argument("name", type=str)
@click.pass_context
def status(ctx, name):
    """output virtual machine status"""
    output(ctx.obj.status(name))


@cli.command
@click.argument("name", type=str)
@click.argument("state", type=click.Choice(POWER_STATES), default="on")
@click.pass_context
def power(ctx, name, state):
    """start virtual machine"""
    output(ctx.obj.set_power_state(name, state))


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
