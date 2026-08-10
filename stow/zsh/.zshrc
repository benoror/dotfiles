# If you come from bash you might have to change your $PATH.
export PATH=$HOME/bin:$HOME/.local/bin:$HOME/.docker/bin:$PATH

#------------------------------------------------------------------------------
# Oh My Zsh
#------------------------------------------------------------------------------

# Path to your Oh My Zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Set name of the theme to load --- if set to "random", it will
# load a random theme each time Oh My Zsh is loaded, in which case,
# to know which specific one was loaded, run: echo $RANDOM_THEME
# See https://github.com/ohmyzsh/ohmyzsh/wiki/Themes
ZSH_THEME=""

# Set list of themes to pick from when loading at random
# Setting this variable when ZSH_THEME=random will cause zsh to load
# a theme from this variable instead of looking in $ZSH/themes/
# If set to an empty array, this variable will have no effect.
# ZSH_THEME_RANDOM_CANDIDATES=( "robbyrussell" "agnoster" )

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to use hyphen-insensitive completion.
# Case-sensitive completion must be off. _ and - will be interchangeable.
# HYPHEN_INSENSITIVE="true"

# Uncomment one of the following lines to change the auto-update behavior
# zstyle ':omz:update' mode disabled  # disable automatic updates
# zstyle ':omz:update' mode auto      # update automatically without asking
# zstyle ':omz:update' mode reminder  # just remind me to update when it's time

# Uncomment the following line to change how often to auto-update (in days).
# zstyle ':omz:update' frequency 13

# Uncomment the following line if pasting URLs and other text is messed up.
# DISABLE_MAGIC_FUNCTIONS="true"

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"
COLORTERM=truecolor

# Uncomment the following line to disable auto-setting terminal title.
# DISABLE_AUTO_TITLE="true"

# Uncomment the following line to enable command auto-correction.
# ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
# You can also set it to another string to have that shown instead of the default red dots.
# e.g. COMPLETION_WAITING_DOTS="%F{yellow}waiting...%f"
# Caution: this setting can cause issues with multiline prompts in zsh < 5.7.1 (see #5765)
# COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
# DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# You can set one of the optional three formats:
# "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
# or set a custom format using the strftime function format specifications,
# see 'man strftime' for details.
# HIST_STAMPS="mm/dd/yyyy"

# Would you like to use another custom folder than $ZSH/custom?
# ZSH_CUSTOM=/path/to/new-custom-folder

# Which plugins would you like to load?
# Standard plugins can be found in $ZSH/plugins/
# Custom plugins may be added to $ZSH_CUSTOM/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
plugins=(git asdf)

source $ZSH/oh-my-zsh.sh

#------------------------------------------------------------------------------
# Prompt
# https://github.com/sindresorhus/pure
#------------------------------------------------------------------------------
fpath+=($HOME/.zsh/pure)
autoload -U promptinit; promptinit
prompt pure

#------------------------------------------------------------------------------
# ASDF
#------------------------------------------------------------------------------
if [ -d "$HOME/.asdf" ]; then
  export PATH="${ASDF_DATA_DIR:-$HOME/.asdf}/shims:$PATH"
fi

#------------------------------------------------------------------------------
# Homebrew
#------------------------------------------------------------------------------
if [ -d "/opt/homebrew" ]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
fi

#------------------------------------------------------------------------------
# NVM
#------------------------------------------------------------------------------
if [ -d "$HOME/.nvm" ]; then
  export NVM_DIR="$HOME/.nvm"
  [ -s "/opt/homebrew/opt/nvm/nvm.sh" ] && \. "/opt/homebrew/opt/nvm/nvm.sh"  # This loads nvm
  [ -s "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm" ] && \. "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm"  # This loads nvm bash_completion
fi

#------------------------------------------------------------------------------
# pyenv
#------------------------------------------------------------------------------
if [ -d "$HOME/.pyenv" ]; then
  export PYENV_ROOT="$HOME/.pyenv"
  [[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
  eval "$(pyenv init - zsh)"
fi

#------------------------------------------------------------------------------
# mise (https://mise.jdx.dev/) — vault Node pin lives in ~/vaults/personal/mise.toml
#------------------------------------------------------------------------------
if command -v mise >/dev/null 2>&1; then
  eval "$(mise activate zsh)"
elif [ -x /opt/homebrew/bin/mise ]; then
  eval "$(/opt/homebrew/bin/mise activate zsh)"
fi

#------------------------------------------------------------------------------
# OpenClaw
#------------------------------------------------------------------------------
if [ -d "$HOME/.openclaw" ]; then
  # Completions path differs on Linux VMs; skip quietly if missing on macOS.
  if [ -f "$HOME/.openclaw/completions/openclaw.zsh" ]; then
    source "$HOME/.openclaw/completions/openclaw.zsh"
  fi
fi

#------------------------------------------------------------------------------
# Obsidian
#------------------------------------------------------------------------------
if [ -d "/Applications/Obsidian.app" ]; then
  export PATH="$PATH:/Applications/Obsidian.app/Contents/MacOS"
fi

#------------------------------------------------------------------------------
# gpg-agent
#------------------------------------------------------------------------------
GPG_TTY=$(tty)
export GPG_TTY

#------------------------------------------------------------------------------
# Google Cloud SDK
#------------------------------------------------------------------------------
# The next line updates PATH for the Google Cloud SDK.
if [ -f '/Users/benoror/Downloads/google-cloud-sdk/path.zsh.inc' ]; then . '/Users/benoror/Downloads/google-cloud-sdk/path.zsh.inc'; fi

# The next line enables shell command completion for gcloud.
if [ -f '/Users/benoror/Downloads/google-cloud-sdk/completion.zsh.inc' ]; then . '/Users/benoror/Downloads/google-cloud-sdk/completion.zsh.inc'; fi


#------------------------------------------------------------------------------
# Message.
#------------------------------------------------------------------------------
if [ -f ~/.message ]; then
  . ~/.message
fi

#------------------------------------------------------------------------------
# User configuration
#------------------------------------------------------------------------------

# You may need to manually set your language environment
# export LANG=en_US.UTF-8

# Preferred editor for local and remote sessions
if [[ -n $SSH_CONNECTION ]]; then
  export EDITOR='vim'
else
  export EDITOR='nvim'
fi

# Compilation flags
# export ARCHFLAGS="-arch $(uname -m)"

# Set personal aliases, overriding those provided by Oh My Zsh libs,
# plugins, and themes. Aliases can be placed here, though Oh My Zsh
# users are encouraged to define aliases within a top-level file in
# the $ZSH_CUSTOM folder, with .zsh extension. Examples:
# - $ZSH_CUSTOM/aliases.zsh
# - $ZSH_CUSTOM/macos.zsh
# For a full list of active aliases, run `alias`.
#
# Example aliases
# alias zshconfig="mate ~/.zshrc"
# alias ohmyzsh="mate ~/.oh-my-zsh"
if [ -f ~/.shell_aliases ]; then
    . ~/.shell_aliases
fi

# Reverse-search History
bindkey '^r' history-incremental-search-backward
bindkey '^R' history-incremental-pattern-search-backward

# Don't share history across open terminals
# https://github.com/robbyrussell/oh-my-zsh/issues/2537
unsetopt share_history

# pnpm
export PNPM_HOME="/Users/benoror/Library/pnpm"
case ":$PATH:" in
  *":$PNPM_HOME:"*) ;;
  *) export PATH="$PNPM_HOME:$PATH" ;;
esac
# pnpm end
