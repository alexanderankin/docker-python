# Generated from Docker Engine Swagger; regenerate via docker_python_generator.
from __future__ import annotations

from typing import Any
from docker_python.core import Client, Transport
from docker_python.core.models import bind_model_types
from docker_python.core.parameters import UNSET, Unset
from . import commands, models

bind_model_types(models.__name__, globals())


class DockerClient(Client):
    def __init__(self, transport: Transport):
        super().__init__(transport, '1.40')

    def container_list(self, *, all: bool | Unset = UNSET, limit: int | Unset = UNSET, size: bool | Unset = UNSET, filters: str | Unset = UNSET) -> commands.ContainerListCommand:
        return commands.ContainerListCommand(self, all=all, limit=limit, size=size, filters=filters)

    list_containers = container_list

    def container_create(self, *, name: str | Unset = UNSET, body: models.ContainerCreateRequest | Unset = UNSET) -> commands.ContainerCreateCommand:
        return commands.ContainerCreateCommand(self, name=name, body=body)

    def container_inspect(self, *, id: str | Unset = UNSET, size: bool | Unset = UNSET) -> commands.ContainerInspectCommand:
        return commands.ContainerInspectCommand(self, id=id, size=size)

    def container_top(self, *, id: str | Unset = UNSET, ps_args: str | Unset = UNSET) -> commands.ContainerTopCommand:
        return commands.ContainerTopCommand(self, id=id, ps_args=ps_args)

    def container_logs(self, *, id: str | Unset = UNSET, follow: bool | Unset = UNSET, stdout: bool | Unset = UNSET, stderr: bool | Unset = UNSET, since: int | Unset = UNSET, until: int | Unset = UNSET, timestamps: bool | Unset = UNSET, tail: str | Unset = UNSET) -> commands.ContainerLogsCommand:
        return commands.ContainerLogsCommand(self, id=id, follow=follow, stdout=stdout, stderr=stderr, since=since, until=until, timestamps=timestamps, tail=tail)

    def container_changes(self, *, id: str | Unset = UNSET) -> commands.ContainerChangesCommand:
        return commands.ContainerChangesCommand(self, id=id)

    def container_export(self, *, id: str | Unset = UNSET) -> commands.ContainerExportCommand:
        return commands.ContainerExportCommand(self, id=id)

    def container_stats(self, *, id: str | Unset = UNSET, stream: bool | Unset = UNSET) -> commands.ContainerStatsCommand:
        return commands.ContainerStatsCommand(self, id=id, stream=stream)

    def container_resize(self, *, id: str | Unset = UNSET, h: int | Unset = UNSET, w: int | Unset = UNSET) -> commands.ContainerResizeCommand:
        return commands.ContainerResizeCommand(self, id=id, h=h, w=w)

    def container_start(self, *, id: str | Unset = UNSET, detach_keys: str | Unset = UNSET) -> commands.ContainerStartCommand:
        return commands.ContainerStartCommand(self, id=id, detach_keys=detach_keys)

    def container_stop(self, *, id: str | Unset = UNSET, t: int | Unset = UNSET) -> commands.ContainerStopCommand:
        return commands.ContainerStopCommand(self, id=id, t=t)

    def container_restart(self, *, id: str | Unset = UNSET, t: int | Unset = UNSET) -> commands.ContainerRestartCommand:
        return commands.ContainerRestartCommand(self, id=id, t=t)

    def container_kill(self, *, id: str | Unset = UNSET, signal: str | Unset = UNSET) -> commands.ContainerKillCommand:
        return commands.ContainerKillCommand(self, id=id, signal=signal)

    def container_update(self, *, id: str | Unset = UNSET, update: models.ContainerUpdateRequest | Unset = UNSET) -> commands.ContainerUpdateCommand:
        return commands.ContainerUpdateCommand(self, id=id, update=update)

    def container_rename(self, *, id: str | Unset = UNSET, name: str | Unset = UNSET) -> commands.ContainerRenameCommand:
        return commands.ContainerRenameCommand(self, id=id, name=name)

    def container_pause(self, *, id: str | Unset = UNSET) -> commands.ContainerPauseCommand:
        return commands.ContainerPauseCommand(self, id=id)

    def container_unpause(self, *, id: str | Unset = UNSET) -> commands.ContainerUnpauseCommand:
        return commands.ContainerUnpauseCommand(self, id=id)

    def container_attach(self, *, id: str | Unset = UNSET, detach_keys: str | Unset = UNSET, logs: bool | Unset = UNSET, stream: bool | Unset = UNSET, stdin: bool | Unset = UNSET, stdout: bool | Unset = UNSET, stderr: bool | Unset = UNSET) -> commands.ContainerAttachCommand:
        return commands.ContainerAttachCommand(self, id=id, detach_keys=detach_keys, logs=logs, stream=stream, stdin=stdin, stdout=stdout, stderr=stderr)

    def container_attach_websocket(self, *, id: str | Unset = UNSET, detach_keys: str | Unset = UNSET, logs: bool | Unset = UNSET, stream: bool | Unset = UNSET) -> commands.ContainerAttachWebsocketCommand:
        return commands.ContainerAttachWebsocketCommand(self, id=id, detach_keys=detach_keys, logs=logs, stream=stream)

    def container_wait(self, *, id: str | Unset = UNSET, condition: models.ContainerWaitQueryCondition | Unset = UNSET) -> commands.ContainerWaitCommand:
        return commands.ContainerWaitCommand(self, id=id, condition=condition)

    def container_delete(self, *, id: str | Unset = UNSET, v: bool | Unset = UNSET, force: bool | Unset = UNSET, link: bool | Unset = UNSET) -> commands.ContainerDeleteCommand:
        return commands.ContainerDeleteCommand(self, id=id, v=v, force=force, link=link)

    def container_archive_info(self, *, id: str | Unset = UNSET, path: str | Unset = UNSET) -> commands.ContainerArchiveInfoCommand:
        return commands.ContainerArchiveInfoCommand(self, id=id, path=path)

    def container_archive(self, *, id: str | Unset = UNSET, path: str | Unset = UNSET) -> commands.ContainerArchiveCommand:
        return commands.ContainerArchiveCommand(self, id=id, path=path)

    def put_container_archive(self, *, id: str | Unset = UNSET, path: str | Unset = UNSET, no_overwrite_dir_non_dir: str | Unset = UNSET, copy_uidgid: str | Unset = UNSET, input_stream: bytes | Unset = UNSET) -> commands.PutContainerArchiveCommand:
        return commands.PutContainerArchiveCommand(self, id=id, path=path, no_overwrite_dir_non_dir=no_overwrite_dir_non_dir, copy_uidgid=copy_uidgid, input_stream=input_stream)

    def container_prune(self, *, filters: str | Unset = UNSET) -> commands.ContainerPruneCommand:
        return commands.ContainerPruneCommand(self, filters=filters)

    def image_list(self, *, all: bool | Unset = UNSET, filters: str | Unset = UNSET, digests: bool | Unset = UNSET) -> commands.ImageListCommand:
        return commands.ImageListCommand(self, all=all, filters=filters, digests=digests)

    list_images = image_list

    def image_build(self, *, input_stream: bytes | Unset = UNSET, dockerfile: str | Unset = UNSET, t: str | Unset = UNSET, extrahosts: str | Unset = UNSET, remote: str | Unset = UNSET, q: bool | Unset = UNSET, nocache: bool | Unset = UNSET, cachefrom: str | Unset = UNSET, pull: str | Unset = UNSET, rm: bool | Unset = UNSET, forcerm: bool | Unset = UNSET, memory: int | Unset = UNSET, memswap: int | Unset = UNSET, cpushares: int | Unset = UNSET, cpusetcpus: str | Unset = UNSET, cpuperiod: int | Unset = UNSET, cpuquota: int | Unset = UNSET, buildargs: str | Unset = UNSET, shmsize: int | Unset = UNSET, squash: bool | Unset = UNSET, labels: str | Unset = UNSET, networkmode: str | Unset = UNSET, content_type: models.ImageBuildHeaderContentType | Unset = UNSET, x_registry_config: str | Unset = UNSET, platform: str | Unset = UNSET, target: str | Unset = UNSET, outputs: str | Unset = UNSET, version: models.ImageBuildQueryVersion | Unset = UNSET) -> commands.ImageBuildCommand:
        return commands.ImageBuildCommand(self, input_stream=input_stream, dockerfile=dockerfile, t=t, extrahosts=extrahosts, remote=remote, q=q, nocache=nocache, cachefrom=cachefrom, pull=pull, rm=rm, forcerm=forcerm, memory=memory, memswap=memswap, cpushares=cpushares, cpusetcpus=cpusetcpus, cpuperiod=cpuperiod, cpuquota=cpuquota, buildargs=buildargs, shmsize=shmsize, squash=squash, labels=labels, networkmode=networkmode, content_type=content_type, x_registry_config=x_registry_config, platform=platform, target=target, outputs=outputs, version=version)

    def build_prune(self, *, keep_storage: int | Unset = UNSET, all: bool | Unset = UNSET, filters: str | Unset = UNSET) -> commands.BuildPruneCommand:
        return commands.BuildPruneCommand(self, keep_storage=keep_storage, all=all, filters=filters)

    def image_create(self, *, from_image: str | Unset = UNSET, from_src: str | Unset = UNSET, repo: str | Unset = UNSET, tag: str | Unset = UNSET, message: str | Unset = UNSET, input_image: str | Unset = UNSET, x_registry_auth: str | Unset = UNSET, changes: list[str] | Unset = UNSET, platform: str | Unset = UNSET) -> commands.ImageCreateCommand:
        return commands.ImageCreateCommand(self, from_image=from_image, from_src=from_src, repo=repo, tag=tag, message=message, input_image=input_image, x_registry_auth=x_registry_auth, changes=changes, platform=platform)

    def image_inspect(self, *, name: str | Unset = UNSET) -> commands.ImageInspectCommand:
        return commands.ImageInspectCommand(self, name=name)

    def image_history(self, *, name: str | Unset = UNSET) -> commands.ImageHistoryCommand:
        return commands.ImageHistoryCommand(self, name=name)

    def image_push(self, *, name: str | Unset = UNSET, tag: str | Unset = UNSET, x_registry_auth: str | Unset = UNSET) -> commands.ImagePushCommand:
        return commands.ImagePushCommand(self, name=name, tag=tag, x_registry_auth=x_registry_auth)

    def image_tag(self, *, name: str | Unset = UNSET, repo: str | Unset = UNSET, tag: str | Unset = UNSET) -> commands.ImageTagCommand:
        return commands.ImageTagCommand(self, name=name, repo=repo, tag=tag)

    def image_delete(self, *, name: str | Unset = UNSET, force: bool | Unset = UNSET, noprune: bool | Unset = UNSET) -> commands.ImageDeleteCommand:
        return commands.ImageDeleteCommand(self, name=name, force=force, noprune=noprune)

    def image_search(self, *, term: str | Unset = UNSET, limit: int | Unset = UNSET, filters: str | Unset = UNSET) -> commands.ImageSearchCommand:
        return commands.ImageSearchCommand(self, term=term, limit=limit, filters=filters)

    def image_prune(self, *, filters: str | Unset = UNSET) -> commands.ImagePruneCommand:
        return commands.ImagePruneCommand(self, filters=filters)

    def system_auth(self, *, auth_config: models.AuthConfig | Unset = UNSET) -> commands.SystemAuthCommand:
        return commands.SystemAuthCommand(self, auth_config=auth_config)

    def system_info(self) -> commands.SystemInfoCommand:
        return commands.SystemInfoCommand(self)

    def system_version(self) -> commands.SystemVersionCommand:
        return commands.SystemVersionCommand(self)

    def system_ping(self) -> commands.SystemPingCommand:
        return commands.SystemPingCommand(self)

    def system_ping_head(self) -> commands.SystemPingHeadCommand:
        return commands.SystemPingHeadCommand(self)

    def image_commit(self, *, container_config: models.ContainerConfig | Unset = UNSET, container: str | Unset = UNSET, repo: str | Unset = UNSET, tag: str | Unset = UNSET, comment: str | Unset = UNSET, author: str | Unset = UNSET, pause: bool | Unset = UNSET, changes: str | Unset = UNSET) -> commands.ImageCommitCommand:
        return commands.ImageCommitCommand(self, container_config=container_config, container=container, repo=repo, tag=tag, comment=comment, author=author, pause=pause, changes=changes)

    def system_events(self, *, since: str | Unset = UNSET, until: str | Unset = UNSET, filters: str | Unset = UNSET) -> commands.SystemEventsCommand:
        return commands.SystemEventsCommand(self, since=since, until=until, filters=filters)

    def system_data_usage(self) -> commands.SystemDataUsageCommand:
        return commands.SystemDataUsageCommand(self)

    def image_get(self, *, name: str | Unset = UNSET) -> commands.ImageGetCommand:
        return commands.ImageGetCommand(self, name=name)

    def image_get_all(self, *, names: list[str] | Unset = UNSET) -> commands.ImageGetAllCommand:
        return commands.ImageGetAllCommand(self, names=names)

    def image_load(self, *, images_tarball: bytes | Unset = UNSET, quiet: bool | Unset = UNSET) -> commands.ImageLoadCommand:
        return commands.ImageLoadCommand(self, images_tarball=images_tarball, quiet=quiet)

    def container_exec(self, *, exec_config: models.ContainerExecRequest | Unset = UNSET, id: str | Unset = UNSET) -> commands.ContainerExecCommand:
        return commands.ContainerExecCommand(self, exec_config=exec_config, id=id)

    def exec_start(self, *, exec_start_config: models.ExecStartRequest | Unset = UNSET, id: str | Unset = UNSET) -> commands.ExecStartCommand:
        return commands.ExecStartCommand(self, exec_start_config=exec_start_config, id=id)

    def exec_resize(self, *, id: str | Unset = UNSET, h: int | Unset = UNSET, w: int | Unset = UNSET) -> commands.ExecResizeCommand:
        return commands.ExecResizeCommand(self, id=id, h=h, w=w)

    def exec_inspect(self, *, id: str | Unset = UNSET) -> commands.ExecInspectCommand:
        return commands.ExecInspectCommand(self, id=id)

    def volume_list(self, *, filters: str | Unset = UNSET) -> commands.VolumeListCommand:
        return commands.VolumeListCommand(self, filters=filters)

    list_volumes = volume_list

    def volume_create(self, *, volume_config: models.VolumeCreateOptions | Unset = UNSET) -> commands.VolumeCreateCommand:
        return commands.VolumeCreateCommand(self, volume_config=volume_config)

    def volume_inspect(self, *, name: str | Unset = UNSET) -> commands.VolumeInspectCommand:
        return commands.VolumeInspectCommand(self, name=name)

    def volume_delete(self, *, name: str | Unset = UNSET, force: bool | Unset = UNSET) -> commands.VolumeDeleteCommand:
        return commands.VolumeDeleteCommand(self, name=name, force=force)

    def volume_prune(self, *, filters: str | Unset = UNSET) -> commands.VolumePruneCommand:
        return commands.VolumePruneCommand(self, filters=filters)

    def network_list(self, *, filters: str | Unset = UNSET) -> commands.NetworkListCommand:
        return commands.NetworkListCommand(self, filters=filters)

    list_networks = network_list

    def network_inspect(self, *, id: str | Unset = UNSET, verbose: bool | Unset = UNSET, scope: str | Unset = UNSET) -> commands.NetworkInspectCommand:
        return commands.NetworkInspectCommand(self, id=id, verbose=verbose, scope=scope)

    def network_delete(self, *, id: str | Unset = UNSET) -> commands.NetworkDeleteCommand:
        return commands.NetworkDeleteCommand(self, id=id)

    def network_create(self, *, network_config: models.NetworkCreateRequest | Unset = UNSET) -> commands.NetworkCreateCommand:
        return commands.NetworkCreateCommand(self, network_config=network_config)

    def network_connect(self, *, id: str | Unset = UNSET, container: models.NetworkConnectRequest | Unset = UNSET) -> commands.NetworkConnectCommand:
        return commands.NetworkConnectCommand(self, id=id, container=container)

    def network_disconnect(self, *, id: str | Unset = UNSET, container: models.NetworkDisconnectRequest | Unset = UNSET) -> commands.NetworkDisconnectCommand:
        return commands.NetworkDisconnectCommand(self, id=id, container=container)

    def network_prune(self, *, filters: str | Unset = UNSET) -> commands.NetworkPruneCommand:
        return commands.NetworkPruneCommand(self, filters=filters)

    def plugin_list(self, *, filters: str | Unset = UNSET) -> commands.PluginListCommand:
        return commands.PluginListCommand(self, filters=filters)

    list_plugins = plugin_list

    def get_plugin_privileges(self, *, remote: str | Unset = UNSET) -> commands.GetPluginPrivilegesCommand:
        return commands.GetPluginPrivilegesCommand(self, remote=remote)

    def plugin_pull(self, *, remote: str | Unset = UNSET, name: str | Unset = UNSET, x_registry_auth: str | Unset = UNSET, body: list[models.PluginPrivilege] | Unset = UNSET) -> commands.PluginPullCommand:
        return commands.PluginPullCommand(self, remote=remote, name=name, x_registry_auth=x_registry_auth, body=body)

    def plugin_inspect(self, *, name: str | Unset = UNSET) -> commands.PluginInspectCommand:
        return commands.PluginInspectCommand(self, name=name)

    def plugin_delete(self, *, name: str | Unset = UNSET, force: bool | Unset = UNSET) -> commands.PluginDeleteCommand:
        return commands.PluginDeleteCommand(self, name=name, force=force)

    def plugin_enable(self, *, name: str | Unset = UNSET, timeout: int | Unset = UNSET) -> commands.PluginEnableCommand:
        return commands.PluginEnableCommand(self, name=name, timeout=timeout)

    def plugin_disable(self, *, name: str | Unset = UNSET, force: bool | Unset = UNSET) -> commands.PluginDisableCommand:
        return commands.PluginDisableCommand(self, name=name, force=force)

    def plugin_upgrade(self, *, name: str | Unset = UNSET, remote: str | Unset = UNSET, x_registry_auth: str | Unset = UNSET, body: list[models.PluginPrivilege] | Unset = UNSET) -> commands.PluginUpgradeCommand:
        return commands.PluginUpgradeCommand(self, name=name, remote=remote, x_registry_auth=x_registry_auth, body=body)

    def plugin_create(self, *, name: str | Unset = UNSET, tar_context: bytes | Unset = UNSET) -> commands.PluginCreateCommand:
        return commands.PluginCreateCommand(self, name=name, tar_context=tar_context)

    def plugin_push(self, *, name: str | Unset = UNSET) -> commands.PluginPushCommand:
        return commands.PluginPushCommand(self, name=name)

    def plugin_set(self, *, name: str | Unset = UNSET, body: list[str] | Unset = UNSET) -> commands.PluginSetCommand:
        return commands.PluginSetCommand(self, name=name, body=body)

    def node_list(self, *, filters: str | Unset = UNSET) -> commands.NodeListCommand:
        return commands.NodeListCommand(self, filters=filters)

    list_nodes = node_list

    def node_inspect(self, *, id: str | Unset = UNSET) -> commands.NodeInspectCommand:
        return commands.NodeInspectCommand(self, id=id)

    def node_delete(self, *, id: str | Unset = UNSET, force: bool | Unset = UNSET) -> commands.NodeDeleteCommand:
        return commands.NodeDeleteCommand(self, id=id, force=force)

    def node_update(self, *, id: str | Unset = UNSET, body: models.NodeSpec | Unset = UNSET, version: int | Unset = UNSET) -> commands.NodeUpdateCommand:
        return commands.NodeUpdateCommand(self, id=id, body=body, version=version)

    def swarm_inspect(self) -> commands.SwarmInspectCommand:
        return commands.SwarmInspectCommand(self)

    def swarm_init(self, *, body: models.SwarmInitRequest | Unset = UNSET) -> commands.SwarmInitCommand:
        return commands.SwarmInitCommand(self, body=body)

    def swarm_join(self, *, body: models.SwarmJoinRequest | Unset = UNSET) -> commands.SwarmJoinCommand:
        return commands.SwarmJoinCommand(self, body=body)

    def swarm_leave(self, *, force: bool | Unset = UNSET) -> commands.SwarmLeaveCommand:
        return commands.SwarmLeaveCommand(self, force=force)

    def swarm_update(self, *, body: models.SwarmSpec | Unset = UNSET, version: int | Unset = UNSET, rotate_worker_token: bool | Unset = UNSET, rotate_manager_token: bool | Unset = UNSET, rotate_manager_unlock_key: bool | Unset = UNSET) -> commands.SwarmUpdateCommand:
        return commands.SwarmUpdateCommand(self, body=body, version=version, rotate_worker_token=rotate_worker_token, rotate_manager_token=rotate_manager_token, rotate_manager_unlock_key=rotate_manager_unlock_key)

    def swarm_unlockkey(self) -> commands.SwarmUnlockkeyCommand:
        return commands.SwarmUnlockkeyCommand(self)

    def swarm_unlock(self, *, body: models.SwarmUnlockRequest | Unset = UNSET) -> commands.SwarmUnlockCommand:
        return commands.SwarmUnlockCommand(self, body=body)

    def service_list(self, *, filters: str | Unset = UNSET) -> commands.ServiceListCommand:
        return commands.ServiceListCommand(self, filters=filters)

    list_services = service_list

    def service_create(self, *, body: models.ServiceCreateRequest | Unset = UNSET, x_registry_auth: str | Unset = UNSET) -> commands.ServiceCreateCommand:
        return commands.ServiceCreateCommand(self, body=body, x_registry_auth=x_registry_auth)

    def service_inspect(self, *, id: str | Unset = UNSET, insert_defaults: bool | Unset = UNSET) -> commands.ServiceInspectCommand:
        return commands.ServiceInspectCommand(self, id=id, insert_defaults=insert_defaults)

    def service_delete(self, *, id: str | Unset = UNSET) -> commands.ServiceDeleteCommand:
        return commands.ServiceDeleteCommand(self, id=id)

    def service_update(self, *, id: str | Unset = UNSET, body: models.ServiceUpdateRequest | Unset = UNSET, version: int | Unset = UNSET, registry_auth_from: models.ServiceUpdateQueryRegistryAuthFrom | Unset = UNSET, rollback: str | Unset = UNSET, x_registry_auth: str | Unset = UNSET) -> commands.ServiceUpdateCommand:
        return commands.ServiceUpdateCommand(self, id=id, body=body, version=version, registry_auth_from=registry_auth_from, rollback=rollback, x_registry_auth=x_registry_auth)

    def service_logs(self, *, id: str | Unset = UNSET, details: bool | Unset = UNSET, follow: bool | Unset = UNSET, stdout: bool | Unset = UNSET, stderr: bool | Unset = UNSET, since: int | Unset = UNSET, timestamps: bool | Unset = UNSET, tail: str | Unset = UNSET) -> commands.ServiceLogsCommand:
        return commands.ServiceLogsCommand(self, id=id, details=details, follow=follow, stdout=stdout, stderr=stderr, since=since, timestamps=timestamps, tail=tail)

    def task_list(self, *, filters: str | Unset = UNSET) -> commands.TaskListCommand:
        return commands.TaskListCommand(self, filters=filters)

    list_tasks = task_list

    def task_inspect(self, *, id: str | Unset = UNSET) -> commands.TaskInspectCommand:
        return commands.TaskInspectCommand(self, id=id)

    def task_logs(self, *, id: str | Unset = UNSET, details: bool | Unset = UNSET, follow: bool | Unset = UNSET, stdout: bool | Unset = UNSET, stderr: bool | Unset = UNSET, since: int | Unset = UNSET, timestamps: bool | Unset = UNSET, tail: str | Unset = UNSET) -> commands.TaskLogsCommand:
        return commands.TaskLogsCommand(self, id=id, details=details, follow=follow, stdout=stdout, stderr=stderr, since=since, timestamps=timestamps, tail=tail)

    def secret_list(self, *, filters: str | Unset = UNSET) -> commands.SecretListCommand:
        return commands.SecretListCommand(self, filters=filters)

    list_secrets = secret_list

    def secret_create(self, *, body: models.SecretCreateRequest | Unset = UNSET) -> commands.SecretCreateCommand:
        return commands.SecretCreateCommand(self, body=body)

    def secret_inspect(self, *, id: str | Unset = UNSET) -> commands.SecretInspectCommand:
        return commands.SecretInspectCommand(self, id=id)

    def secret_delete(self, *, id: str | Unset = UNSET) -> commands.SecretDeleteCommand:
        return commands.SecretDeleteCommand(self, id=id)

    def secret_update(self, *, id: str | Unset = UNSET, body: models.SecretSpec | Unset = UNSET, version: int | Unset = UNSET) -> commands.SecretUpdateCommand:
        return commands.SecretUpdateCommand(self, id=id, body=body, version=version)

    def config_list(self, *, filters: str | Unset = UNSET) -> commands.ConfigListCommand:
        return commands.ConfigListCommand(self, filters=filters)

    list_configs = config_list

    def config_create(self, *, body: models.ConfigCreateRequest | Unset = UNSET) -> commands.ConfigCreateCommand:
        return commands.ConfigCreateCommand(self, body=body)

    def config_inspect(self, *, id: str | Unset = UNSET) -> commands.ConfigInspectCommand:
        return commands.ConfigInspectCommand(self, id=id)

    def config_delete(self, *, id: str | Unset = UNSET) -> commands.ConfigDeleteCommand:
        return commands.ConfigDeleteCommand(self, id=id)

    def config_update(self, *, id: str | Unset = UNSET, body: models.ConfigSpec | Unset = UNSET, version: int | Unset = UNSET) -> commands.ConfigUpdateCommand:
        return commands.ConfigUpdateCommand(self, id=id, body=body, version=version)

    def distribution_inspect(self, *, name: str | Unset = UNSET) -> commands.DistributionInspectCommand:
        return commands.DistributionInspectCommand(self, name=name)

    def session(self) -> commands.SessionCommand:
        return commands.SessionCommand(self)
