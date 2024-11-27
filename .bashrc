# ~/.bashrc
# by Ben Orozco <github.com/benoror>

# If not running interactively, don't do anything
#Test1
case $- in
    *i*) ;;
      *) return;;
esac
#Test2
[ -z "$PS1" ] && return

# bash options ------------------------------------
#set -o vi                  # vi input mode
shopt -s autocd &> /dev/null             # cd by naming directory
shopt -s cdable_vars        # if cd arg is not valid, assumes its a var defining a dir
shopt -s cdspell            # autocorrects cd misspellings
shopt -s checkwinsize       # update the value of LINES and COLUMNS after each command if altered
shopt -s cmdhist            # save multi-line commands in history as single line
shopt -s dotglob            # include dotfiles in pathname expansion
shopt -s expand_aliases     # expand aliases
shopt -s extglob            # enable extended pattern-matching features
shopt -s histappend         # append to (not overwrite) the history file
shopt -s hostcomplete       # attempt hostname expansion when @ is at the beginning of a word
shopt -s nocaseglob         # pathname expansion will be treated as case-insensitive
shopt -s globstar &> /dev/null           # match all files and zero or more directories and subdirectories.

# set PATH so it includes user's private bin if it exists
if [ -d ~/bin ] ; then
    PATH=~/bin:"${PATH}"
fi

# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

export MAILCHECK=0
export EDITOR="vim"
export FCEDIT="vim"
export VISUAL=$EDITOR
export PAGER=less
export LESS='-iMnQR'
export PRINTER=lp
export CVS_RSH=ssh
export HISTSIZE=10000
export HISTFILESIZE=100000
export HISTCONTROL=ignoreboth:erasedups
export TERM=xterm-256color
export DISPLAY=":0"
export GPGKEY="07D46DA6"

# share history across all terminals
shopt -s histappend
PROMPT_COMMAND='history -a'

# ls Color
ls --color 2> /dev/null > /dev/null
LSCOLOR="$?"
if [ "$LSCOLOR" -eq "0" ]
then
    alias ls='ls --color -C'
else
    alias ls='ls -CG'
fi

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    #alias dir='dir --color=auto'
    #alias vdir='vdir --color=auto'
    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

# colored GCC warnings and errors
export GCC_COLORS='error=01;31:warning=01;35:note=01;36:caret=01;32:locus=01:quote=01'

# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "${debian_chroot:-}" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

# Alias definitions.
# You may want to put all your additions into a separate file
if [ -f ~/.shell_aliases ]; then
    . ~/.shell_aliases
fi

# Extract Files
extract () {
  if [ -f $1 ] ; then
      case $1 in
          *.tar.bz2)   tar xvjf $1    ;;
          *.tar.gz)    tar xvzf $1    ;;
          *.tar.xz)    tar xvJf $1    ;;
          *.bz2)       bunzip2 $1     ;;
          *.rar)       unrar x $1     ;;
          *.gz)        gunzip $1      ;;
          *.tar)       tar xvf $1     ;;
          *.tbz2)      tar xvjf $1    ;;
          *.tgz)       tar xvzf $1    ;;
          *.zip)       unzip $1       ;;
          *.Z)         uncompress $1  ;;
          *.7z)        7z x $1        ;;
          *.xz)        unxz $1        ;;
          *.exe)       cabextract $1  ;;
          *)           echo "\`$1': unrecognized file compression" ;;
      esac
  else
      echo "\`$1' is not a valid file"
  fi
}

# Completion. (bash only)
complete -A alias         alias unalias
complete -A command       which
complete -A export        export printenv
complete -A hostname      ssh telnet ftp ncftp ping dig nmap
complete -A helptopic     help
complete -A job -P '%'    fg jobs
complete -A setopt        set
complete -A shopt         shopt
complete -A signal        kill killall
complete -A user          su userdel passwd
complete -A group         groupdel groupmod newgrp
complete -A directory     cd rmdir
complete -f -X '!*.@(gif|GIF|jpg|JPG|jpeg|JPEG|png|PNG|xcf|bmp|BMP|pcx|PCX)'   gimp
complete -f -X '!*.@(mp?(e)g|MP?(E)G|wma|avi|AVI|asf|vob|VOB|bin|dat|vcd|ps|pes|fli|viv|rm|ram|yuv|mov|MOV|qt|QT|wmv|mp3|MP3|ogg|OGG|ogm|OGM|mp4|MP4|wav|WAV|asx|ASX|mng|MNG|m4v)' mplayer

# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi

#------------------------------------------------------------------------------
# Prompt
#------------------------------------------------------------------------------

# If this is an xterm set the title to user@host:dir
case "$TERM" in
xterm*|rxvt*)
    PS1="\[\e]0;${debian_chroot:+($debian_chroot)}\u@\h: \w\a\]$PS1"
    ;;
*)
    ;;
esac

# set a fancy prompt (non-color, unless we know we "want" color)
case "$TERM" in
    xterm-color) color_prompt=yes;;
esac

# uncomment for a colored prompt, if the terminal has the capability; turned
# off by default to not distract the user: the focus in a terminal window
# should be on the output of commands, not on the prompt
force_color_prompt=yes
if [ -n "$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
  # We have color support; assume it's compliant with Ecma-48
  # (ISO/IEC-6429). (Lack of such support is extremely rare, and such
  # a case would tend to support setf rather than setaf.)
  color_prompt=yes
    else
  color_prompt=
    fi
fi

if [ "$color_prompt" = yes ]; then
    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
else
    PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
fi
unset color_prompt force_color_prompt

# Run twolfson/sexy-bash-prompt
. ~/.bash_prompt

#------------------------------------------------------------------------------
# Message.
#------------------------------------------------------------------------------
. ~/.message

