# Dotfiles

```text
            __
           /\ \
           \_\ \____     __    ___     ___   _ __   ___   _ __
          /\___  __ \  /'__`\/' _ `\  / __`\/\`'__\/ __`\/\`'__\
          \/__/\ \_\ \/\  __//\ \/\ \/\ \_\ \ \ \//\ \_\ \ \ \/
              \ \____/\ \____\ \_\ \_\ \____/\ \_\\ \____/\ \_\
               \/___/  \/____/\/_/\/_/\/___/  \/_/ \/___/  \/_/
```

Personal machine config (`benoror@gmail.com`). Often linked as `~/dotfiles`.
Managed with [GNU Stow](https://www.gnu.org/software/stow/) (`stow/.stowrc` → `--target=~`).

## Index

| Path | Role |
| --- | --- |
| [`stow/`](stow/) | Stow packages (linked into `$HOME`) |
| [`stow/agents/`](stow/agents/) | AI agent hub — [README](stow/agents/README.md) · [TODO](stow/agents/TODO.md) |
| [`stow/zsh/`](stow/zsh/) | Shell, Oh My Zsh, Pure |
| [`stow/git/`](stow/git/) | Git config & global ignore |
| [`stow/nvim/`](stow/nvim/) | Neovim / LazyVim |
| [`stow/ghostty/`](stow/ghostty/) | Terminal (macOS + Linux) |
| [`stow/iterm2/`](stow/iterm2/) | Terminal (macOS) |
| [`stow/vscode/`](stow/vscode/), [`stow/cursor/`](stow/cursor/) | Editor User settings |
| [`stow/ssh/`](stow/ssh/), [`stow/gnupg/`](stow/gnupg/), [`stow/asdf/`](stow/asdf/) | SSH, GPG, asdf |
| [`stow/kde/`](stow/kde/), [`stow/konsole/`](stow/konsole/) | Linux desktop leftovers |
| [`Makefile`](Makefile) | Stow install/restow/uninstall (groups + per package) |
| [`macos/`](macos/) | macOS extras (BetterMouse, Rectangle, …) |
| [`fonts/`](fonts/) | Font files |
| [`nixos/`](nixos/) | NixOS / UTM experiments |
| [`linux_old/`](linux_old/) | Archived Linux configs |

```bash
cd ~/dotfiles
make help                 # targets
make install              # core + editors + mac (no secrets/linux)
make install-zsh          # one package
make install-secrets      # ssh + gnupg (explicit)
make agents-verify        # agents entrypoints
stow -n -v -d ~/dotfiles/stow -t ~ zsh   # dry-run any package
```
