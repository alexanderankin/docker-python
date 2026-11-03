# Generated from Docker Engine Swagger; regenerate via docker_python_generator.
from __future__ import annotations

from docker_python.core import Client, Transport
from docker_python.core.models import bind_model_types
from docker_python.core.parameters import UNSET, Unset
from . import commands, models

bind_model_types(models.__name__, globals())


class DockerClient(Client):
    def __init__(self, transport: Transport):
        super().__init__(transport, '1.44')

    def container_list(self, *, all: models.ContainerListQueryAll | Unset = UNSET, limit: models.ContainerListQueryLimit | Unset = UNSET, size: models.ContainerListQuerySize | Unset = UNSET, filters: models.ContainerListQueryFilters | Unset = UNSET) -> commands.ContainerListCommand:
        return commands.ContainerListCommand(self, all=all, limit=limit, size=size, filters=filters)

    list_containers = container_list

    def container_create(self, *, name: models.ContainerCreateQueryName | Unset = UNSET, platform: models.ContainerCreateQueryPlatform | Unset = UNSET, body: models.ContainerCreateRequest | Unset = UNSET) -> commands.ContainerCreateCommand:
        return commands.ContainerCreateCommand(self, name=name, platform=platform, body=body)

    def container_inspect(self, *, id: models.ContainerInspectPathId | Unset = UNSET, size: models.ContainerInspectQuerySize | Unset = UNSET) -> commands.ContainerInspectCommand:
        return commands.ContainerInspectCommand(self, id=id, size=size)

    def container_top(self, *, id: models.ContainerTopPathId | Unset = UNSET, ps_args: models.ContainerTopQueryPsArgs | Unset = UNSET) -> commands.ContainerTopCommand:
        return commands.ContainerTopCommand(self, id=id, ps_args=ps_args)

    def container_logs(self, *, id: models.ContainerLogsPathId | Unset = UNSET, follow: models.ContainerLogsQueryFollow | Unset = UNSET, stdout: models.ContainerLogsQueryStdout | Unset = UNSET, stderr: models.ContainerLogsQueryStderr | Unset = UNSET, since: models.ContainerLogsQuerySince | Unset = UNSET, until: models.ContainerLogsQueryUntil | Unset = UNSET, timestamps: models.ContainerLogsQueryTimestamps | Unset = UNSET, tail: models.ContainerLogsQueryTail | Unset = UNSET) -> commands.ContainerLogsCommand:
        return commands.ContainerLogsCommand(self, id=id, follow=follow, stdout=stdout, stderr=stderr, since=since, until=until, timestamps=timestamps, tail=tail)

    def container_changes(self, *, id: models.ContainerChangesPathId | Unset = UNSET) -> commands.ContainerChangesCommand:
        return commands.ContainerChangesCommand(self, id=id)

    def container_export(self, *, id: models.ContainerExportPathId | Unset = UNSET) -> commands.ContainerExportCommand:
        return commands.ContainerExportCommand(self, id=id)

    def container_stats(self, *, id: models.ContainerStatsPathId | Unset = UNSET, stream: models.ContainerStatsQueryStream | Unset = UNSET, one_shot: models.ContainerStatsQueryOneShot | Unset = UNSET) -> commands.ContainerStatsCommand:
        return commands.ContainerStatsCommand(self, id=id, stream=stream, one_shot=one_shot)

    def container_resize(self, *, id: models.ContainerResizePathId | Unset = UNSET, h: models.ContainerResizeQueryH | Unset = UNSET, w: models.ContainerResizeQueryW | Unset = UNSET) -> commands.ContainerResizeCommand:
        return commands.ContainerResizeCommand(self, id=id, h=h, w=w)

    def container_start(self, *, id: models.ContainerStartPathId | Unset = UNSET, detach_keys: models.ContainerStartQueryDetachKeys | Unset = UNSET) -> commands.ContainerStartCommand:
        return commands.ContainerStartCommand(self, id=id, detach_keys=detach_keys)

    def container_stop(self, *, id: models.ContainerStopPathId | Unset = UNSET, signal: models.ContainerStopQuerySignal | Unset = UNSET, t: models.ContainerStopQueryT | Unset = UNSET) -> commands.ContainerStopCommand:
        return commands.ContainerStopCommand(self, id=id, signal=signal, t=t)

    def container_restart(self, *, id: models.ContainerRestartPathId | Unset = UNSET, signal: models.ContainerRestartQuerySignal | Unset = UNSET, t: models.ContainerRestartQueryT | Unset = UNSET) -> commands.ContainerRestartCommand:
        return commands.ContainerRestartCommand(self, id=id, signal=signal, t=t)

    def container_kill(self, *, id: models.ContainerKillPathId | Unset = UNSET, signal: models.ContainerKillQuerySignal | Unset = UNSET) -> commands.ContainerKillCommand:
        return commands.ContainerKillCommand(self, id=id, signal=signal)

    def container_update(self, *, id: models.ContainerUpdatePathId | Unset = UNSET, update: models.ContainerUpdateRequest | Unset = UNSET) -> commands.ContainerUpdateCommand:
        return commands.ContainerUpdateCommand(self, id=id, update=update)

    def container_rename(self, *, id: models.ContainerRenamePathId | Unset = UNSET, name: models.ContainerRenameQueryName | Unset = UNSET) -> commands.ContainerRenameCommand:
        return commands.ContainerRenameCommand(self, id=id, name=name)

    def container_pause(self, *, id: models.ContainerPausePathId | Unset = UNSET) -> commands.ContainerPauseCommand:
        return commands.ContainerPauseCommand(self, id=id)

    def container_unpause(self, *, id: models.ContainerUnpausePathId | Unset = UNSET) -> commands.ContainerUnpauseCommand:
        return commands.ContainerUnpauseCommand(self, id=id)

    def container_attach(self, *, id: models.ContainerAttachPathId | Unset = UNSET, detach_keys: models.ContainerAttachQueryDetachKeys | Unset = UNSET, logs: models.ContainerAttachQueryLogs | Unset = UNSET, stream: models.ContainerAttachQueryStream | Unset = UNSET, stdin: models.ContainerAttachQueryStdin | Unset = UNSET, stdout: models.ContainerAttachQueryStdout | Unset = UNSET, stderr: models.ContainerAttachQueryStderr | Unset = UNSET) -> commands.ContainerAttachCommand:
        return commands.ContainerAttachCommand(self, id=id, detach_keys=detach_keys, logs=logs, stream=stream, stdin=stdin, stdout=stdout, stderr=stderr)

    def container_attach_websocket(self, *, id: models.ContainerAttachWebsocketPathId | Unset = UNSET, detach_keys: models.ContainerAttachWebsocketQueryDetachKeys | Unset = UNSET, logs: models.ContainerAttachWebsocketQueryLogs | Unset = UNSET, stream: models.ContainerAttachWebsocketQueryStream | Unset = UNSET, stdin: models.ContainerAttachWebsocketQueryStdin | Unset = UNSET, stdout: models.ContainerAttachWebsocketQueryStdout | Unset = UNSET, stderr: models.ContainerAttachWebsocketQueryStderr | Unset = UNSET) -> commands.ContainerAttachWebsocketCommand:
        return commands.ContainerAttachWebsocketCommand(self, id=id, detach_keys=detach_keys, logs=logs, stream=stream, stdin=stdin, stdout=stdout, stderr=stderr)

    def container_wait(self, *, id: models.ContainerWaitPathId | Unset = UNSET, condition: models.ContainerWaitQueryCondition | Unset = UNSET) -> commands.ContainerWaitCommand:
        return commands.ContainerWaitCommand(self, id=id, condition=condition)

    def container_delete(self, *, id: models.ContainerDeletePathId | Unset = UNSET, v: models.ContainerDeleteQueryV | Unset = UNSET, force: models.ContainerDeleteQueryForce | Unset = UNSET, link: models.ContainerDeleteQueryLink | Unset = UNSET) -> commands.ContainerDeleteCommand:
        return commands.ContainerDeleteCommand(self, id=id, v=v, force=force, link=link)

    def container_archive_info(self, *, id: models.ContainerArchiveInfoPathId | Unset = UNSET, path: models.ContainerArchiveInfoQueryPath | Unset = UNSET) -> commands.ContainerArchiveInfoCommand:
        return commands.ContainerArchiveInfoCommand(self, id=id, path=path)

    def container_archive(self, *, id: models.ContainerArchivePathId | Unset = UNSET, path: models.ContainerArchiveQueryPath | Unset = UNSET) -> commands.ContainerArchiveCommand:
        return commands.ContainerArchiveCommand(self, id=id, path=path)

    def put_container_archive(self, *, id: models.PutContainerArchivePathId | Unset = UNSET, path: models.PutContainerArchiveQueryPath | Unset = UNSET, no_overwrite_dir_non_dir: models.PutContainerArchiveQueryNoOverwriteDirNonDir | Unset = UNSET, copy_uidgid: models.PutContainerArchiveQueryCopyUIDGID | Unset = UNSET, input_stream: models.PutContainerArchiveRequest | Unset = UNSET) -> commands.PutContainerArchiveCommand:
        return commands.PutContainerArchiveCommand(self, id=id, path=path, no_overwrite_dir_non_dir=no_overwrite_dir_non_dir, copy_uidgid=copy_uidgid, input_stream=input_stream)

    def container_prune(self, *, filters: models.ContainerPruneQueryFilters | Unset = UNSET) -> commands.ContainerPruneCommand:
        return commands.ContainerPruneCommand(self, filters=filters)

    def image_list(self, *, all: models.ImageListQueryAll | Unset = UNSET, filters: models.ImageListQueryFilters | Unset = UNSET, shared_size: models.ImageListQuerySharedSize | Unset = UNSET, digests: models.ImageListQueryDigests | Unset = UNSET) -> commands.ImageListCommand:
        return commands.ImageListCommand(self, all=all, filters=filters, shared_size=shared_size, digests=digests)

    list_images = image_list

    def image_build(self, *, input_stream: models.ImageBuildRequest | Unset = UNSET, dockerfile: models.ImageBuildQueryDockerfile | Unset = UNSET, t: models.ImageBuildQueryT | Unset = UNSET, extrahosts: models.ImageBuildQueryExtrahosts | Unset = UNSET, remote: models.ImageBuildQueryRemote | Unset = UNSET, q: models.ImageBuildQueryQ | Unset = UNSET, nocache: models.ImageBuildQueryNocache | Unset = UNSET, cachefrom: models.ImageBuildQueryCachefrom | Unset = UNSET, pull: models.ImageBuildQueryPull | Unset = UNSET, rm: models.ImageBuildQueryRm | Unset = UNSET, forcerm: models.ImageBuildQueryForcerm | Unset = UNSET, memory: models.ImageBuildQueryMemory | Unset = UNSET, memswap: models.ImageBuildQueryMemswap | Unset = UNSET, cpushares: models.ImageBuildQueryCpushares | Unset = UNSET, cpusetcpus: models.ImageBuildQueryCpusetcpus | Unset = UNSET, cpuperiod: models.ImageBuildQueryCpuperiod | Unset = UNSET, cpuquota: models.ImageBuildQueryCpuquota | Unset = UNSET, buildargs: models.ImageBuildQueryBuildargs | Unset = UNSET, shmsize: models.ImageBuildQueryShmsize | Unset = UNSET, squash: models.ImageBuildQuerySquash | Unset = UNSET, labels: models.ImageBuildQueryLabels | Unset = UNSET, networkmode: models.ImageBuildQueryNetworkmode | Unset = UNSET, content_type: models.ImageBuildHeaderContentType | Unset = UNSET, x_registry_config: models.ImageBuildHeaderXRegistryConfig | Unset = UNSET, platform: models.ImageBuildQueryPlatform | Unset = UNSET, target: models.ImageBuildQueryTarget | Unset = UNSET, outputs: models.ImageBuildQueryOutputs | Unset = UNSET, version: models.ImageBuildQueryVersion | Unset = UNSET) -> commands.ImageBuildCommand:
        return commands.ImageBuildCommand(self, input_stream=input_stream, dockerfile=dockerfile, t=t, extrahosts=extrahosts, remote=remote, q=q, nocache=nocache, cachefrom=cachefrom, pull=pull, rm=rm, forcerm=forcerm, memory=memory, memswap=memswap, cpushares=cpushares, cpusetcpus=cpusetcpus, cpuperiod=cpuperiod, cpuquota=cpuquota, buildargs=buildargs, shmsize=shmsize, squash=squash, labels=labels, networkmode=networkmode, content_type=content_type, x_registry_config=x_registry_config, platform=platform, target=target, outputs=outputs, version=version)

    def build_prune(self, *, keep_storage: models.BuildPruneQueryKeepStorage | Unset = UNSET, all: models.BuildPruneQueryAll | Unset = UNSET, filters: models.BuildPruneQueryFilters | Unset = UNSET) -> commands.BuildPruneCommand:
        return commands.BuildPruneCommand(self, keep_storage=keep_storage, all=all, filters=filters)

    def image_create(self, *, from_image: models.ImageCreateQueryFromImage | Unset = UNSET, from_src: models.ImageCreateQueryFromSrc | Unset = UNSET, repo: models.ImageCreateQueryRepo | Unset = UNSET, tag: models.ImageCreateQueryTag | Unset = UNSET, message: models.ImageCreateQueryMessage | Unset = UNSET, input_image: models.ImageCreateRequest | Unset = UNSET, x_registry_auth: models.ImageCreateHeaderXRegistryAuth | Unset = UNSET, changes: models.ImageCreateQueryChanges | Unset = UNSET, platform: models.ImageCreateQueryPlatform | Unset = UNSET) -> commands.ImageCreateCommand:
        return commands.ImageCreateCommand(self, from_image=from_image, from_src=from_src, repo=repo, tag=tag, message=message, input_image=input_image, x_registry_auth=x_registry_auth, changes=changes, platform=platform)

    def image_inspect(self, *, name: models.ImageInspectPathName | Unset = UNSET) -> commands.ImageInspectCommand:
        return commands.ImageInspectCommand(self, name=name)

    def image_history(self, *, name: models.ImageHistoryPathName | Unset = UNSET) -> commands.ImageHistoryCommand:
        return commands.ImageHistoryCommand(self, name=name)

    def image_push(self, *, name: models.ImagePushPathName | Unset = UNSET, tag: models.ImagePushQueryTag | Unset = UNSET, x_registry_auth: models.ImagePushHeaderXRegistryAuth | Unset = UNSET) -> commands.ImagePushCommand:
        return commands.ImagePushCommand(self, name=name, tag=tag, x_registry_auth=x_registry_auth)

    def image_tag(self, *, name: models.ImageTagPathName | Unset = UNSET, repo: models.ImageTagQueryRepo | Unset = UNSET, tag: models.ImageTagQueryTag | Unset = UNSET) -> commands.ImageTagCommand:
        return commands.ImageTagCommand(self, name=name, repo=repo, tag=tag)

    def image_delete(self, *, name: models.ImageDeletePathName | Unset = UNSET, force: models.ImageDeleteQueryForce | Unset = UNSET, noprune: models.ImageDeleteQueryNoprune | Unset = UNSET) -> commands.ImageDeleteCommand:
        return commands.ImageDeleteCommand(self, name=name, force=force, noprune=noprune)

    def image_search(self, *, term: models.ImageSearchQueryTerm | Unset = UNSET, limit: models.ImageSearchQueryLimit | Unset = UNSET, filters: models.ImageSearchQueryFilters | Unset = UNSET) -> commands.ImageSearchCommand:
        return commands.ImageSearchCommand(self, term=term, limit=limit, filters=filters)

    def image_prune(self, *, filters: models.ImagePruneQueryFilters | Unset = UNSET) -> commands.ImagePruneCommand:
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

    def image_commit(self, *, container_config: models.ContainerConfig | Unset = UNSET, container: models.ImageCommitQueryContainer | Unset = UNSET, repo: models.ImageCommitQueryRepo | Unset = UNSET, tag: models.ImageCommitQueryTag | Unset = UNSET, comment: models.ImageCommitQueryComment | Unset = UNSET, author: models.ImageCommitQueryAuthor | Unset = UNSET, pause: models.ImageCommitQueryPause | Unset = UNSET, changes: models.ImageCommitQueryChanges | Unset = UNSET) -> commands.ImageCommitCommand:
        return commands.ImageCommitCommand(self, container_config=container_config, container=container, repo=repo, tag=tag, comment=comment, author=author, pause=pause, changes=changes)

    def system_events(self, *, since: models.SystemEventsQuerySince | Unset = UNSET, until: models.SystemEventsQueryUntil | Unset = UNSET, filters: models.SystemEventsQueryFilters | Unset = UNSET) -> commands.SystemEventsCommand:
        return commands.SystemEventsCommand(self, since=since, until=until, filters=filters)

    def system_data_usage(self, *, type: models.SystemDataUsageQueryType | Unset = UNSET) -> commands.SystemDataUsageCommand:
        return commands.SystemDataUsageCommand(self, type=type)

    def image_get(self, *, name: models.ImageGetPathName | Unset = UNSET) -> commands.ImageGetCommand:
        return commands.ImageGetCommand(self, name=name)

    def image_get_all(self, *, names: models.ImageGetAllQueryNames | Unset = UNSET) -> commands.ImageGetAllCommand:
        return commands.ImageGetAllCommand(self, names=names)

    def image_load(self, *, images_tarball: models.ImageLoadRequest | Unset = UNSET, quiet: models.ImageLoadQueryQuiet | Unset = UNSET) -> commands.ImageLoadCommand:
        return commands.ImageLoadCommand(self, images_tarball=images_tarball, quiet=quiet)

    def container_exec(self, *, exec_config: models.ContainerExecRequest | Unset = UNSET, id: models.ContainerExecPathId | Unset = UNSET) -> commands.ContainerExecCommand:
        return commands.ContainerExecCommand(self, exec_config=exec_config, id=id)

    def exec_start(self, *, exec_start_config: models.ExecStartRequest | Unset = UNSET, id: models.ExecStartPathId | Unset = UNSET) -> commands.ExecStartCommand:
        return commands.ExecStartCommand(self, exec_start_config=exec_start_config, id=id)

    def exec_resize(self, *, id: models.ExecResizePathId | Unset = UNSET, h: models.ExecResizeQueryH | Unset = UNSET, w: models.ExecResizeQueryW | Unset = UNSET) -> commands.ExecResizeCommand:
        return commands.ExecResizeCommand(self, id=id, h=h, w=w)

    def exec_inspect(self, *, id: models.ExecInspectPathId | Unset = UNSET) -> commands.ExecInspectCommand:
        return commands.ExecInspectCommand(self, id=id)

    def volume_list(self, *, filters: models.VolumeListQueryFilters | Unset = UNSET) -> commands.VolumeListCommand:
        return commands.VolumeListCommand(self, filters=filters)

    list_volumes = volume_list

    def volume_create(self, *, volume_config: models.VolumeCreateOptions | Unset = UNSET) -> commands.VolumeCreateCommand:
        return commands.VolumeCreateCommand(self, volume_config=volume_config)

    def volume_inspect(self, *, name: models.VolumeInspectPathName | Unset = UNSET) -> commands.VolumeInspectCommand:
        return commands.VolumeInspectCommand(self, name=name)

    def volume_update(self, *, name: models.VolumeUpdatePathName | Unset = UNSET, body: models.VolumeUpdateRequest | Unset = UNSET, version: models.VolumeUpdateQueryVersion | Unset = UNSET) -> commands.VolumeUpdateCommand:
        return commands.VolumeUpdateCommand(self, name=name, body=body, version=version)

    def volume_delete(self, *, name: models.VolumeDeletePathName | Unset = UNSET, force: models.VolumeDeleteQueryForce | Unset = UNSET) -> commands.VolumeDeleteCommand:
        return commands.VolumeDeleteCommand(self, name=name, force=force)

    def volume_prune(self, *, filters: models.VolumePruneQueryFilters | Unset = UNSET) -> commands.VolumePruneCommand:
        return commands.VolumePruneCommand(self, filters=filters)

    def network_list(self, *, filters: models.NetworkListQueryFilters | Unset = UNSET) -> commands.NetworkListCommand:
        return commands.NetworkListCommand(self, filters=filters)

    list_networks = network_list

    def network_inspect(self, *, id: models.NetworkInspectPathId | Unset = UNSET, verbose: models.NetworkInspectQueryVerbose | Unset = UNSET, scope: models.NetworkInspectQueryScope | Unset = UNSET) -> commands.NetworkInspectCommand:
        return commands.NetworkInspectCommand(self, id=id, verbose=verbose, scope=scope)

    def network_delete(self, *, id: models.NetworkDeletePathId | Unset = UNSET) -> commands.NetworkDeleteCommand:
        return commands.NetworkDeleteCommand(self, id=id)

    def network_create(self, *, network_config: models.NetworkCreateRequest | Unset = UNSET) -> commands.NetworkCreateCommand:
        return commands.NetworkCreateCommand(self, network_config=network_config)

    def network_connect(self, *, id: models.NetworkConnectPathId | Unset = UNSET, container: models.NetworkConnectRequest | Unset = UNSET) -> commands.NetworkConnectCommand:
        return commands.NetworkConnectCommand(self, id=id, container=container)

    def network_disconnect(self, *, id: models.NetworkDisconnectPathId | Unset = UNSET, container: models.NetworkDisconnectRequest | Unset = UNSET) -> commands.NetworkDisconnectCommand:
        return commands.NetworkDisconnectCommand(self, id=id, container=container)

    def network_prune(self, *, filters: models.NetworkPruneQueryFilters | Unset = UNSET) -> commands.NetworkPruneCommand:
        return commands.NetworkPruneCommand(self, filters=filters)

    def plugin_list(self, *, filters: models.PluginListQueryFilters | Unset = UNSET) -> commands.PluginListCommand:
        return commands.PluginListCommand(self, filters=filters)

    list_plugins = plugin_list

    def get_plugin_privileges(self, *, remote: models.GetPluginPrivilegesQueryRemote | Unset = UNSET) -> commands.GetPluginPrivilegesCommand:
        return commands.GetPluginPrivilegesCommand(self, remote=remote)

    def plugin_pull(self, *, remote: models.PluginPullQueryRemote | Unset = UNSET, name: models.PluginPullQueryName | Unset = UNSET, x_registry_auth: models.PluginPullHeaderXRegistryAuth | Unset = UNSET, body: models.PluginPullRequest | Unset = UNSET) -> commands.PluginPullCommand:
        return commands.PluginPullCommand(self, remote=remote, name=name, x_registry_auth=x_registry_auth, body=body)

    def plugin_inspect(self, *, name: models.PluginInspectPathName | Unset = UNSET) -> commands.PluginInspectCommand:
        return commands.PluginInspectCommand(self, name=name)

    def plugin_delete(self, *, name: models.PluginDeletePathName | Unset = UNSET, force: models.PluginDeleteQueryForce | Unset = UNSET) -> commands.PluginDeleteCommand:
        return commands.PluginDeleteCommand(self, name=name, force=force)

    def plugin_enable(self, *, name: models.PluginEnablePathName | Unset = UNSET, timeout: models.PluginEnableQueryTimeout | Unset = UNSET) -> commands.PluginEnableCommand:
        return commands.PluginEnableCommand(self, name=name, timeout=timeout)

    def plugin_disable(self, *, name: models.PluginDisablePathName | Unset = UNSET, force: models.PluginDisableQueryForce | Unset = UNSET) -> commands.PluginDisableCommand:
        return commands.PluginDisableCommand(self, name=name, force=force)

    def plugin_upgrade(self, *, name: models.PluginUpgradePathName | Unset = UNSET, remote: models.PluginUpgradeQueryRemote | Unset = UNSET, x_registry_auth: models.PluginUpgradeHeaderXRegistryAuth | Unset = UNSET, body: models.PluginUpgradeRequest | Unset = UNSET) -> commands.PluginUpgradeCommand:
        return commands.PluginUpgradeCommand(self, name=name, remote=remote, x_registry_auth=x_registry_auth, body=body)

    def plugin_create(self, *, name: models.PluginCreateQueryName | Unset = UNSET, tar_context: models.PluginCreateRequest | Unset = UNSET) -> commands.PluginCreateCommand:
        return commands.PluginCreateCommand(self, name=name, tar_context=tar_context)

    def plugin_push(self, *, name: models.PluginPushPathName | Unset = UNSET) -> commands.PluginPushCommand:
        return commands.PluginPushCommand(self, name=name)

    def plugin_set(self, *, name: models.PluginSetPathName | Unset = UNSET, body: models.PluginSetRequest | Unset = UNSET) -> commands.PluginSetCommand:
        return commands.PluginSetCommand(self, name=name, body=body)

    def node_list(self, *, filters: models.NodeListQueryFilters | Unset = UNSET) -> commands.NodeListCommand:
        return commands.NodeListCommand(self, filters=filters)

    list_nodes = node_list

    def node_inspect(self, *, id: models.NodeInspectPathId | Unset = UNSET) -> commands.NodeInspectCommand:
        return commands.NodeInspectCommand(self, id=id)

    def node_delete(self, *, id: models.NodeDeletePathId | Unset = UNSET, force: models.NodeDeleteQueryForce | Unset = UNSET) -> commands.NodeDeleteCommand:
        return commands.NodeDeleteCommand(self, id=id, force=force)

    def node_update(self, *, id: models.NodeUpdatePathId | Unset = UNSET, body: models.NodeSpec | Unset = UNSET, version: models.NodeUpdateQueryVersion | Unset = UNSET) -> commands.NodeUpdateCommand:
        return commands.NodeUpdateCommand(self, id=id, body=body, version=version)

    def swarm_inspect(self) -> commands.SwarmInspectCommand:
        return commands.SwarmInspectCommand(self)

    def swarm_init(self, *, body: models.SwarmInitRequest | Unset = UNSET) -> commands.SwarmInitCommand:
        return commands.SwarmInitCommand(self, body=body)

    def swarm_join(self, *, body: models.SwarmJoinRequest | Unset = UNSET) -> commands.SwarmJoinCommand:
        return commands.SwarmJoinCommand(self, body=body)

    def swarm_leave(self, *, force: models.SwarmLeaveQueryForce | Unset = UNSET) -> commands.SwarmLeaveCommand:
        return commands.SwarmLeaveCommand(self, force=force)

    def swarm_update(self, *, body: models.SwarmSpec | Unset = UNSET, version: models.SwarmUpdateQueryVersion | Unset = UNSET, rotate_worker_token: models.SwarmUpdateQueryRotateWorkerToken | Unset = UNSET, rotate_manager_token: models.SwarmUpdateQueryRotateManagerToken | Unset = UNSET, rotate_manager_unlock_key: models.SwarmUpdateQueryRotateManagerUnlockKey | Unset = UNSET) -> commands.SwarmUpdateCommand:
        return commands.SwarmUpdateCommand(self, body=body, version=version, rotate_worker_token=rotate_worker_token, rotate_manager_token=rotate_manager_token, rotate_manager_unlock_key=rotate_manager_unlock_key)

    def swarm_unlockkey(self) -> commands.SwarmUnlockkeyCommand:
        return commands.SwarmUnlockkeyCommand(self)

    def swarm_unlock(self, *, body: models.SwarmUnlockRequest | Unset = UNSET) -> commands.SwarmUnlockCommand:
        return commands.SwarmUnlockCommand(self, body=body)

    def service_list(self, *, filters: models.ServiceListQueryFilters | Unset = UNSET, status: models.ServiceListQueryStatus | Unset = UNSET) -> commands.ServiceListCommand:
        return commands.ServiceListCommand(self, filters=filters, status=status)

    list_services = service_list

    def service_create(self, *, body: models.ServiceCreateRequest | Unset = UNSET, x_registry_auth: models.ServiceCreateHeaderXRegistryAuth | Unset = UNSET) -> commands.ServiceCreateCommand:
        return commands.ServiceCreateCommand(self, body=body, x_registry_auth=x_registry_auth)

    def service_inspect(self, *, id: models.ServiceInspectPathId | Unset = UNSET, insert_defaults: models.ServiceInspectQueryInsertDefaults | Unset = UNSET) -> commands.ServiceInspectCommand:
        return commands.ServiceInspectCommand(self, id=id, insert_defaults=insert_defaults)

    def service_delete(self, *, id: models.ServiceDeletePathId | Unset = UNSET) -> commands.ServiceDeleteCommand:
        return commands.ServiceDeleteCommand(self, id=id)

    def service_update(self, *, id: models.ServiceUpdatePathId | Unset = UNSET, body: models.ServiceUpdateRequest | Unset = UNSET, version: models.ServiceUpdateQueryVersion | Unset = UNSET, registry_auth_from: models.ServiceUpdateQueryRegistryAuthFrom | Unset = UNSET, rollback: models.ServiceUpdateQueryRollback | Unset = UNSET, x_registry_auth: models.ServiceUpdateHeaderXRegistryAuth | Unset = UNSET) -> commands.ServiceUpdateCommand:
        return commands.ServiceUpdateCommand(self, id=id, body=body, version=version, registry_auth_from=registry_auth_from, rollback=rollback, x_registry_auth=x_registry_auth)

    def service_logs(self, *, id: models.ServiceLogsPathId | Unset = UNSET, details: models.ServiceLogsQueryDetails | Unset = UNSET, follow: models.ServiceLogsQueryFollow | Unset = UNSET, stdout: models.ServiceLogsQueryStdout | Unset = UNSET, stderr: models.ServiceLogsQueryStderr | Unset = UNSET, since: models.ServiceLogsQuerySince | Unset = UNSET, timestamps: models.ServiceLogsQueryTimestamps | Unset = UNSET, tail: models.ServiceLogsQueryTail | Unset = UNSET) -> commands.ServiceLogsCommand:
        return commands.ServiceLogsCommand(self, id=id, details=details, follow=follow, stdout=stdout, stderr=stderr, since=since, timestamps=timestamps, tail=tail)

    def task_list(self, *, filters: models.TaskListQueryFilters | Unset = UNSET) -> commands.TaskListCommand:
        return commands.TaskListCommand(self, filters=filters)

    list_tasks = task_list

    def task_inspect(self, *, id: models.TaskInspectPathId | Unset = UNSET) -> commands.TaskInspectCommand:
        return commands.TaskInspectCommand(self, id=id)

    def task_logs(self, *, id: models.TaskLogsPathId | Unset = UNSET, details: models.TaskLogsQueryDetails | Unset = UNSET, follow: models.TaskLogsQueryFollow | Unset = UNSET, stdout: models.TaskLogsQueryStdout | Unset = UNSET, stderr: models.TaskLogsQueryStderr | Unset = UNSET, since: models.TaskLogsQuerySince | Unset = UNSET, timestamps: models.TaskLogsQueryTimestamps | Unset = UNSET, tail: models.TaskLogsQueryTail | Unset = UNSET) -> commands.TaskLogsCommand:
        return commands.TaskLogsCommand(self, id=id, details=details, follow=follow, stdout=stdout, stderr=stderr, since=since, timestamps=timestamps, tail=tail)

    def secret_list(self, *, filters: models.SecretListQueryFilters | Unset = UNSET) -> commands.SecretListCommand:
        return commands.SecretListCommand(self, filters=filters)

    list_secrets = secret_list

    def secret_create(self, *, body: models.SecretCreateRequest | Unset = UNSET) -> commands.SecretCreateCommand:
        return commands.SecretCreateCommand(self, body=body)

    def secret_inspect(self, *, id: models.SecretInspectPathId | Unset = UNSET) -> commands.SecretInspectCommand:
        return commands.SecretInspectCommand(self, id=id)

    def secret_delete(self, *, id: models.SecretDeletePathId | Unset = UNSET) -> commands.SecretDeleteCommand:
        return commands.SecretDeleteCommand(self, id=id)

    def secret_update(self, *, id: models.SecretUpdatePathId | Unset = UNSET, body: models.SecretSpec | Unset = UNSET, version: models.SecretUpdateQueryVersion | Unset = UNSET) -> commands.SecretUpdateCommand:
        return commands.SecretUpdateCommand(self, id=id, body=body, version=version)

    def config_list(self, *, filters: models.ConfigListQueryFilters | Unset = UNSET) -> commands.ConfigListCommand:
        return commands.ConfigListCommand(self, filters=filters)

    list_configs = config_list

    def config_create(self, *, body: models.ConfigCreateRequest | Unset = UNSET) -> commands.ConfigCreateCommand:
        return commands.ConfigCreateCommand(self, body=body)

    def config_inspect(self, *, id: models.ConfigInspectPathId | Unset = UNSET) -> commands.ConfigInspectCommand:
        return commands.ConfigInspectCommand(self, id=id)

    def config_delete(self, *, id: models.ConfigDeletePathId | Unset = UNSET) -> commands.ConfigDeleteCommand:
        return commands.ConfigDeleteCommand(self, id=id)

    def config_update(self, *, id: models.ConfigUpdatePathId | Unset = UNSET, body: models.ConfigSpec | Unset = UNSET, version: models.ConfigUpdateQueryVersion | Unset = UNSET) -> commands.ConfigUpdateCommand:
        return commands.ConfigUpdateCommand(self, id=id, body=body, version=version)

    def distribution_inspect(self, *, name: models.DistributionInspectPathName | Unset = UNSET) -> commands.DistributionInspectCommand:
        return commands.DistributionInspectCommand(self, name=name)

    def session(self) -> commands.SessionCommand:
        return commands.SessionCommand(self)
