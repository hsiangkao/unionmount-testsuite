from tool_box import *

def remount_union(ctx, rotate_upper=False, cold_cache=False):
    cfg = ctx.config()
    union_mntroot = cfg.union_mntroot()
    lower_mntroot = cfg.lower_mntroot()
    upper_mntroot = cfg.upper_mntroot()
    snapshot_mntroot = cfg.snapshot_mntroot()
    testdir = cfg.testdir()

    first_snapshot = False
    if not ctx.have_more_layers():
        rotate_upper = False
    # --sn --remount implies start with nosnapshot setup until first recycle
    # so don't add a new layer on first recycle
    elif cfg.testing_snapshot() and ctx.remount() and ctx.mid_layers() is None:
        rotate_upper = False
        first_snapshot = True

    # --sn default behavior is remount unless --recycle was requested
    cycle_mount = False
    if not cfg.testing_snapshot() or ctx.remount() is False:
        cycle_mount = True
    # With snapshot fs mount we must cycle mount to clean cache
    # With fsnotify snapshot it is enough to drop caches
    if cfg.is_metacopy() and cold_cache:
        cycle_mount = True

    if cfg.testing_overlayfs() or cfg.testing_snapshot():
        if cycle_mount:
            system("umount " + cfg.union_mntroot())
        if cycle_mount or cold_cache:
            system("echo 3 > /proc/sys/vm/drop_caches")
            check_not_tainted()

        mid_layers = ctx.mid_layers() or ""
        if rotate_upper:
            # Current upper is added to head of overlay mid layers
            mid_layers = ctx.upper_layer() + ":" + mid_layers
            layer_mntroot = upper_mntroot + "/" + ctx.next_layer()
            upperdir = layer_mntroot + "/u"
            workdir = layer_mntroot + "/w"
            os.mkdir(layer_mntroot)
            # Create unique fs for upper/N if N < maxfs
            if ctx.have_more_fs():
                system("mount -t tmpfs " + ctx.curr_layer() + "_layer " + layer_mntroot)
            os.mkdir(upperdir)
            os.mkdir(workdir)
            if not cfg.testing_snapshot():
                # Create pure upper file
                write_file(upperdir + "/f", "pure");
        else:
            layer_mntroot = upper_mntroot + "/" + ctx.curr_layer()
            upperdir = layer_mntroot + "/u"
            workdir = layer_mntroot + "/w"

        if cfg.testing_snapshot():
            # Keep old snapshots mounted unless mount cycle was requested
            # Old snapshot fs implementation does not support concurrent snapshots
            # so in that case and in case of cycle_mount, we need to re-stack old
            # snapshots as lower layers to get the desired outcome
            restack_old_snapshots = (rotate_upper and cfg.is_metacopy()) or cycle_mount
            if restack_old_snapshots:
                # Unmount old snapshots when mount cycling snapshot mount
                # and when rotating latest snapshot into old snapshot stack
                try:
                    system("umount " + snapshot_mntroot + "/*/ 2>/dev/null")
                except RuntimeError:
                    pass
                check_not_tainted()

            curr_snapshot = snapshot_mntroot + "/" + ctx.curr_layer()
            if rotate_upper:
                os.mkdir(curr_snapshot)
            # --sn --remount implies start with nosnapshot setup until first recycle
            # make first backup on first cycle instead of after setup and after
            # every rotate of upper
            if cfg.is_verify() and (rotate_upper or first_snapshot):
                ctx.make_backup()

            if rotate_upper or cycle_mount:
                if cfg.is_metacopy():
                    # Old overlay snapshot for snapshot fs mount
                    mntopt = " -oredirect_dir=origin"
                else:
                    # New overlay snapshot mount with fsnotify watch
                    mntopt = " -owatch"
                # This is the latest snapshot of lower_mntroot:
                cmd = ("mount -t overlay overlay " + curr_snapshot + mntopt +
                       ",lowerdir=" + lower_mntroot + ",upperdir=" + upperdir + ",workdir=" + workdir)
                system(cmd)
                if cfg.is_verbose():
                    write_kmsg(cmd);

            # This is the snapshot mount where tests are run
            if not cfg.is_metacopy():
                # There is no snapshot fs mount with overlay fsnotify snapshot
                if cycle_mount:
                    system("mount -o bind " + lower_mntroot + " " + union_mntroot)
            elif cycle_mount:
                snapmntopt = " -onoatime,snapshot=" + curr_snapshot
                # don't copy files to snapshot only directories
                snapmntopt = snapmntopt + ",metacopy=on"
                system("mount -t snapshot " + lower_mntroot + " " + union_mntroot + snapmntopt)
                ctx.note_upper_fs(upper_mntroot, testdir, testdir)
            else:
                # Remount snapshot mount to configure the new curr_snapshot
                system("mount -t snapshot " + lower_mntroot + " " + union_mntroot + " -oremount,snapshot=" + curr_snapshot)
                # freeze/thaw snapshot mount to activate the new curr_snapshot
                system("fsfreeze -f " + union_mntroot)
                system("fsfreeze -u " + union_mntroot)

            if restack_old_snapshots:
                # Remount latest snapshot readonly
                system("mount " + curr_snapshot + " -oremount,ro")
                mid_layers = ""
                # Mount old snapshots, possibly pushing the rotated previous snapshot into stack
                for i in range(ctx.layers_nr() - 1, -1, -1):
                    mid_layers = upper_mntroot + "/" + str(i) + "/u:" + mid_layers
                    cmd = ("mount -t overlay overlay " + snapshot_mntroot + "/" + str(i) + "/" +
                           " -oro,lowerdir=" + mid_layers + curr_snapshot)
                    system(cmd)
                    if cfg.is_verbose():
                        write_kmsg(cmd);
        else:
            mntopt = " -orw" + cfg.mntopts()
            cmd = ("mount -t " + cfg.fstype() + " " + cfg.fsname() + " " + union_mntroot + mntopt +
                   ",lowerdir=" + mid_layers + ctx.lower_layer() + ",upperdir=" + upperdir + ",workdir=" + workdir)
            system(cmd)
            if cfg.is_verbose():
                write_kmsg(cmd);
            # Record st_dev of merge dir and pure upper file
            ctx.note_upper_fs(upper_mntroot, testdir, union_mntroot + "/f")
        ctx.note_mid_layers(mid_layers)
        ctx.note_upper_layer(upperdir)
