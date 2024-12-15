Restore the layout of your windows in sway.

Currently in alpha, not expected to work on anyone's machine except mine.

I needed this because I usually work with many workspaces, at least one per
project, and each workspace is usually tiled with multiple things (e.g.
terminals, browsers, CAD programs). I was tired of restoring that layout every
time I restarted.

This lets me define functions for taking snapshots of my applications and their
state, and then define corresponding functions that restores that state after a
restart and places windows back in the correct workspace and location.

### Important TODOs
- [ ] Add top-level script for constantly saving snapshots, and recovering from a new one on startup
- [ ] Installation instructions for scripts like zshrc-snapshot and vimrc-snapshot
- [ ] Make the logic & executables work as a standalone python module that you install, i.e. remove paths to executables & manually installing scripts on $PATH
- [ ] Allow defining custom logic for recreating an app, e.g. launch firefox, launch terminal zsh, launch vim
- [ ] Basic automated testing (initialize a workspace, blow half of it away, restore it)

### Less important TODOs
- [ ] Config for adding new snapshot/recover pairs
- [ ] Replace bash scripts with python for restore-vim-session and restore-zsh-session
- [ ] Improve the naming around snapshot/recover/restore/capture before they ossify
- [ ] Support other terminal emulators than kitty
- [ ] Flag to disable auto-capture
- [ ] Get to the bottom of nohup.out *still* being emitted

### Other TODOs
- [ ] "Audit" stage, where you can see what it plans on doing & edit that, similarly to `git rebase -i`
- [ ] Use env file for shell in which vim runs
- [ ] Restore history for each shell, not just its env
- [ ] Utility programs for inspecting current and older snapshots
- [ ] Config for changing roots of zsh-sessions, vim-sessions
- [ ] Installers for the zsh/vim via oh-my-zsh/plug respectively
- [ ] Rewrite zsh/vim hooks in python3/lua respectively
- [ ] Restore monitor layout (other tools exist for this, like Kanshi, so not as urgent)
