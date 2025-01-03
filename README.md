### What It Does

Restore the layout of your windows in sway. This lets me define functions for
taking snapshots of my applications and their state, and then define
corresponding functions that restores that state after a restart and places
windows back in the correct workspace and location.

### Background

I needed this because I usually work with many workspaces, at least one per
project, and each workspace is usually tiled with multiple things (e.g.
terminals, browsers, CAD programs). I was tired of restoring that layout every
time I restarted.

### Usage

~~Currently in alpha, not expected to work on anyone's machine except mine.~~

Currently in alpha, may work on your machine, no guarantees whatsoever though.

- Take a snapshot of your system with `restore-sway-layout snapshot`
- Currently, this doesn't restart all your applications from a snapshot.
  However, there are script for restarting your vim and zsh instances, assuming
  you've copied zshrc-snapshot to the **end** of your `.zshrc`, and
  vimrc-snapshot to the end of your `.vimrc`.

  More detailed instructions on how to do this, as well as an installer, are on
  the nice to have TODOs list.
- Once you've restarted your applications (e.g. firefox) manually, relocate them
  to the correct workspaces with `restore-sway-layout relocate <snapshot>`.
- Launch a long-running daemon which places snapshots periodically with

  ```sh
  > restore-sway-layout daemon --output <directory for snapshots> --rate 30
  ```

  You can update the snapshot rate, or force a snapshot, with the `ctl`
  subcommand:

  ```sh
  > restore-sway-layout ctl --dbus --update-snapshot
  > restore-sway-layout ctl --dbus --set-rate 10
  ```

  If you don't have Dbus running, you can communicate directly with the running
  daemon via IPC, by telling the daemon to dump the path to its socket into a
  file:

  ```sh
  > restore-sway-layout daemon --output <directory for snapshots> --write-socket-to sockfile --rate 30
  # Sockfile now contains path to socket for IPC with the daemon
  > cat sockfile
  /tmp/tmpyknk869l/restore-sway-layout-50107167095afd9f47dc-ipc.sock
  > restore-sway-layout ctl --socket-file $(cat sockfile) --update-snapshot
  ```

### Important TODOs
- [X] Add top-level script for constantly saving snapshots, and recovering from a new one on startup
  - Added `--watch` flag to snapshot for taking snapshots every `x` seconds
  - [X] Add auto-recovery, logic to avoid overwriting files from last session
  - Daemonized, you now provide a target directory into which to place sessions
- [X] Installation instructions for scripts like zshrc-snapshot and vimrc-snapshot
  - Done for now, should be improved in the long term
- [X] Make the logic & executables work as a standalone python module that you install, i.e. remove paths to executables & manually installing scripts on $PATH
  - Core snapshot/relocate functionality are now all bundled in python
- [ ] Allow defining custom logic for recreating an app, e.g. launch firefox, launch terminal zsh, launch vim
- [ ] Basic automated testing (initialize a workspace, blow half of it away, restore it)

### Less important TODOs
- [ ] Config for adding new snapshot/restart/relocate pairs
- [ ] Replace bash scripts with python for restore-vim-session and restore-zsh-session
- [X] Improve the naming around snapshot/recover/restore/capture before they ossify
  - Improved to snapshot/restart/relocate
  - The tool itself is now `restore_sway_layout`
- [ ] Support other terminal emulators than kitty
- [X] Flag to disable auto-capture
- [X] Get to the bottom of nohup.out *still* being emitted
  - Haven't seen it since, it may have been a holdover from worse times

### Other TODOs
- [ ] "Audit" stage, where you can see what it plans on doing & edit that, similarly to `git rebase -i`
- [ ] Use env file for shell in which vim runs
- [ ] Restore history for each shell, not just its env
- [ ] Utility programs for inspecting current and older snapshots
- [ ] Config for changing roots of zsh-sessions, vim-sessions
- [ ] Installers for the zsh/vim via oh-my-zsh/plug respectively
- [ ] Rewrite zsh/vim hooks in python3/lua respectively
- [ ] Restore monitor layout (other tools exist for this, like Kanshi, so not as urgent)
